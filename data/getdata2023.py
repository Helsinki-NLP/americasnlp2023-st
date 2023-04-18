from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfReader
from sentence_splitter import SentenceSplitter, split_text_into_sentences
import pandas as pd

#from langdetect import detect
import pathlib, subprocess, requests, re

# NAHWATL
#extracted = pd.DataFrame(columns=['spa','nah'])
splitterspa = SentenceSplitter(language='es')
splitternah = SentenceSplitter(language='es')

nahfull, spafull = "",""
with requests.Session() as session:
    # get the XML feed and extract the link
    urlbase='https://nawatl.com/category/textos/page/'
    for i in range(1,7):
        response = session.get(f"{urlbase}/{str(i)}")
        # find the links
        soup = bs(response.text, 'html.parser')
        titles = soup.select('h2')
        for t in titles:
            link = t.a['href']
            # follow the link and extract the link to the zip file
            response2 = session.get(link)
            soup2 = bs(response2.text, 'html.parser')
            # parallel texts are in tables in td: nahuatl is emphasized inside <em>...<\em>
            #there are numbers to refer to verses
            verses = soup2.find_all('td')
            #aux = {'nah':[],'spa':[]}
            nah,spa = "[NEW_DOCUMENT]. ","[NEW_DOCUMENT]. "
            for idx, verse in enumerate(verses):
                #if detect(verse.text) == 'es':
                if (idx+1)%2:
                    if verse.text.find('Origen')>=0 or verse.text.find('Náhuatl')>=0:
                        #print(verse.text)
                        break                        
                    nah += verse.text.lstrip('01234567890. ').replace(',',', ').replace('.','. ')
                else:
                    spa += verse.text.lstrip('01234567890. ').replace(',',', ').replace('.','. ')
            
            #print(f'{t.text} \n {aux.shape} \n {aux}')
            nahfull += nah
            spafull += spa

nah = splitternah.split(text=nahfull)
spa = splitternah.split(text=spafull)

with open('nahuatl-spanish/extra/verses.doclevel.spa','w') as fout:
    fout.write('\n'.join(spa))
with open('nahuatl-spanish/extra/verses.doclevel.nah','w') as fout:
    fout.write('\n'.join(nah))

#extracted.to_csv('nahuatl-spanish/extra/texts.nah-spa.tsv', sep='\t', index=False, header=False)


# UNAM - nah-spa
opath=pathlib.Path('./pdfs/cuentos_nah-spa')
opath.mkdir(exist_ok=True)
# Blocking parsers
#url = "https://nahuatl.org.mx/cuentos-nahuatl-14-ejemplares-para-descargar/"
#response = requests.get(f"{url}") 
urlbase="http://www.historicas.unam.mx/publicaciones/publicadigital/libros/cuentos_indigenas"
pdfnames= ["04_07_culebra.pdf", "04_09_zorrito_lobo.pdf", "04_11_conejito_culebra.pdf",
        "04_13_muchacho_perezoso.pdf", "04_08_leon_cacomizcle_zorra.pdf", "04_14_leon_grillo.pdf",
        "04_10_zorra_liebre.pdf", "04_10_zorra_liebre.pdf", "04_15_coyotito_zorrito.pdf", 
        "04_17_perro_viejo.pdf", "04_19_nino_horticultor.pdf", "04_16_saltamontes_colorado.pdf",
        "04_12_hombre_rico.pdf", "04_18_doncella_fiera.pdf", "04_20_muchacho_desobediente.pdf"]
nahfull = ""
spafull = ""
for idx, f in enumerate(pdfnames):
    subprocess.run(["wget", "-nc", "-P", str(opath), f"{urlbase}/{f}"])
    #wget.download(f"{urlbase}/{f}", out=str(opath))
    reader = PdfReader(f'{str(opath)}/{f}')
    npag=len(reader.pages)
    title = reader.pages[1].extract_text().replace('\n','| ').split('|')
    nahfull += f" [NEW_DOCUMENT:  DOCid={idx}, lang=nah, DOCNAME={title[0]}]. "
    spafull += f" [NEW_DOCUMENT:  DOCid={idx}, lang=spa, DOCNAME={title[1]}]. "
    nahfull += f" {title[0]}. "
    spafull += f" {title[1]}. "
    for i,j in zip(range(2,npag,2), range(3,npag,2)):
        # first two pages are not useful
        # always starts with nahuatl in page 3 (i=2)
        # the spanish translation is in the odd page index
        nah,spa = reader.pages[i].extract_text().replace('\n',''), reader.pages[j].extract_text().replace('\n','')
        # clean headers and footers
        nah = re.sub(r' DR©.*','',nah)
        nah = re.sub( r'^.*[0-9] CUENTOS IND.GENAS ', '',nah)
        spa = re.sub(r' DR©.*','',spa)
        spa = re.sub( r'^.*[0-9] ', '',spa)
        # delete hyphens to break sentences
        nah = nah.replace('-', '')
        spa = spa.replace('-', '')
        spa = spa.replace(u'\xad','')
        nah = nah.replace(u'\xad','')
        nahfull += nah
        spafull += spa
    nahfull += f" [END OF DOCUMENT]."
    spafull += f" [END OF DOCUMENT]."

splitternah = SentenceSplitter(language='en') # here the opening question and exclamation marks are NOT used 
nah = nahfull.replace('...',',').strip('.')
nah = nah.replace('.', '. ')
nah = splitternah.split(text=nah)

splitterspa = SentenceSplitter(language='es')
spa = spafull.replace('...',',').strip('.')
spa = spa.replace('.', '. ')
spa = splitterspa.split(text=spa)

with open('nahuatl-spanish/extra/cuentos.doclevel.spa','w') as fout:
    fout.write('\n'.join(spa))
with open('nahuatl-spanish/extra/cuentos.doclevel.nah','w') as fout:
    fout.write('\n'.join(nah))



maintext = []
chaptertitles = []
captions = []
quotes = []
def visitor_body(text, cm, tm, fontDict, fontSize):
    fs = tm[0]
    x = tm[4]
    y = tm[5]
    # skip header
    #if y < 600:
    #    print(text, tm)
    #    parts.append(text)
    # main text is fontsize = 9.5
    if fs == 9.5 or fs == 8.075 or fs == 5.7 or fs == 9.0:
        maintext.append(text)
    elif fs == 22.0:
        chaptertitles.append(text)
    elif fs == 7.0 or fs == 3.9:
        captions.append(text)
    elif fs == 12.0 or fs == 11.0:
        if text.find('http://www.cdi.gob.mx') == -1:
            quotes.append(text)
    # skip page numbering always fontsize = 8.0
    elif fs == 8.0:
        pass 
    elif text:
        pass
        #print("SKIIIIPED:     ",text, tm)


# INPI - nah monolingual 
url='https://www.gob.mx/inpi/documentos/libros-en-lenguas-indigenas'

opath=pathlib.Path('./pdfs/cuentos_nah-spa')
#SPANISH
subprocess.run(["wget", "-nc", "-P", str(opath), f"https://www.gob.mx/cms/uploads/attachment/file/255517/monografia_nacional_pueblos_indigenas_mexico.pdf"])
subprocess.run(["mv", f"{str(opath)}/monografia_nacional_pueblos_indigenas_mexico.pdf", f"{str(opath)}/monografia_nacional_espanol.pdf"])
#https://www.gob.mx/cms/uploads/attachment/file/255517/monografia_nacional_pueblos_indigenas_mexico.pdf
# NAHUATL
subprocess.run(["wget", "-nc", "-P", str(opath), f"https://www.gob.mx/cms/uploads/attachment/file/37204/monografia_nacional_nahuatl.pdf"])
#https://www.gob.mx/cms/uploads/attachment/file/37204/monografia_nacional_nahuatl.pdf

rdrspa = PdfReader(f'{str(opath)}/monografia_nacional_espanol.pdf')
rdrnah = PdfReader(f'{str(opath)}/monografia_nacional_nahuatl.pdf')

nahfull, spafull = "", ""
spacaps, nahcaps = "", ""
spaquot, nahquot = "", ""
splitternah = SentenceSplitter(language='es')
splitterspa = SentenceSplitter(language='es')
# SPANISH
for i in range(5,139):
    maintext, chaptertitles, captions, quotes = [],[],[],[]
    rdrspa.pages[i].extract_text(visitor_text=visitor_body)
    if chaptertitles:
        spa = ".\n [NEW DOCUMENT]. "+''.join(chaptertitles)+'. '+''.join(maintext)
    else:
        spa = ''.join(maintext)
    if captions:
        spacaps += ''.join(captions)
    if quotes:
        spaquot += ''.join(quotes)
    
    # rip footnote
    spa = re.sub(r'http.*','',spa)

    # contents table
    if 5 <= i <= 6:
        spa = re.sub(' *\d+\n','. ',spa).replace('\n','')
    else:
        spa = spa.replace(' -','').replace('\n','')
    spafull += spa    


# NAHUATL
for j in range(4,159):
    maintext, chaptertitles, captions, quotes = [],[],[],[]
    rdrnah.pages[j].extract_text(visitor_text=visitor_body)
    if chaptertitles:
        nah = ".\n [NEW DOCUMENT]. "+''.join(chaptertitles)+'. '+''.join(maintext)
    else:
        if j == 4:
            maintext[0] = maintext[0].replace('\n','. ')
        nah = ''.join(maintext)
    if captions:
        nahcaps += ''.join(captions)
    if quotes:
        nahquot += ''.join(quotes)
    
    # rip footnote
    nah = re.sub(r'http.*','',nah)
    # contents table
    if 4 <= j <= 5:
        nah = re.sub(' *\d+\n','. ',nah).replace('\n','') 
        if j==4:
              nah = ".\n [NEW DOCUMENT]. "+nah
    else:
        nah = nah.replace(' -','').replace('\n','')
    
    nahfull += nah
    

nahquot = nahquot.replace('\n','').replace('.', '. ')
spaquot = spaquot.replace('\n','').replace('.', '. ')

nahfull = nahfull +"[NEW_DOCUMENT]"+''.join(nahquot)
spafull = spafull +"[NEW_DOCUMENT]"+''.join(spaquot)
nahfull = nahfull.replace('.', '. ')
spafull = spafull.replace('.', '. ')
nah = splitternah.split(text=nahfull)
spa = splitterspa.split(text=spafull)

with open('nahuatl-spanish/extra/monografia.doclevel.spa','w') as fout:
    fout.write('\n'.join(spa))
with open('nahuatl-spanish/extra/monografia.doclevel.nah','w') as fout:
    fout.write('\n'.join(nah))

print(""" HUOM! From this point, you need to run an sent-alignment tool. 
    RUN THE FOLLOWING TO UNSTALL HUNALIGN
    # Install: 
    currentdir=`pwd`
    cd ~/git
    git clone https://github.com/danielvarga/hunalign.git
    cd hunalign/src/hunalign/
    make """)

subprocess.run(['chmod','770','align_datasets.sh'])
subprocess.run('`pwd`/align_datasets.sh', shell=True)
