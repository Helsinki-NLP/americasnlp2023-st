from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfReader
from sentence_splitter import SentenceSplitter, split_text_into_sentences
import pandas as pd

#from langdetect import detect
import pathlib, subprocess, requests, re


# NAHWATL
extracted = pd.DataFrame(columns=['spa','nah'])
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
            aux = {'nah':[],'spa':[]}
            for idx, verse in enumerate(verses):
                #if detect(verse.text) == 'es':
                if (idx+1)%2:
                    if verse.text.find('Origen')>=0 or verse.text.find('Náhuatl')>=0:
                        print(verse.text)
                        break                        
                    aux['nah'].append(verse.text.lstrip('01234567890. '))
                else:
                    aux['spa'].append(verse.text.lstrip('01234567890. '))
            aux = pd.DataFrame(aux)
            #print(f'{t.text} \n {aux.shape} \n {aux}')
            extracted = extracted.append(aux, ignore_index=True)


extracted.to_csv('data/nahuatl/texts.nah-spa.tsv', sep='\t', index=False, header=False)

# UNAM - nah-spa
opath=pathlib.Path('./data/pdfs/cuentos_nah-spa')
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

splitter = SentenceSplitter(language='en')
nah = nahfull.replace('...',',').strip('.')
nah = splitter.split(text=nah)

splitter = SentenceSplitter(language='es')
spa = spafull.replace('...',',').strip('.')
spa = splitter.split(text=spa)

with open('data/nahuatl-spanish/cuentos.doclevel.spa','w') as fout:
    fout.write('\n'.join(spa))
with open('data/nahuatl-spanish/cuentos.doclevel.nah','w') as fout:
    fout.write('\n'.join(nah))

print(""" HUOM! From this point, you need to run an sent-alignment tool. 
    E.g., using HUNALIGN
    # Install: 
    currentdir=`pwd`
    cd ~/git
    git clone https://github.com/danielvarga/hunalign.git
    cd hunalign/src/hunalign/
    make
    # create an empty dict
    touch /tmp/null.dict
    # align with hunalign
    cd $currentdir/data/nahuatl-spanish
    ~/git/hunalign/src/hunalign/hunalign /tmp/null.dict cuentos.doclevel.{nah,spa} -text > cuentos.nah-spa.tsv
    cut -f1-2 cuentos.nah-spa.tsv > file.temp
    mv file.temp cuentos.nah-spa.tsv
    """)

# INPI - nah monolingual 
url='https://www.gob.mx/inpi/documentos/libros-en-lenguas-indigenas'
