from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfReader
from sentence_splitter import SentenceSplitter, split_text_into_sentences
import pandas as pd

#from langdetect import detect
import pathlib, subprocess, requests, re, random, pickle



def naheng_dictionary():
    # NAH-ENG DICTIONARY: 
    urlbase="https://nahuatl.wired-humanities.org/"
    currchar=ord('a') # convert char to ascii
    nahE,eng,spa,nahS = [],[],[],[] 
    engtransl, spatransl = [],[]
    engprobl, spaprobl = [],[]

    while currchar <= ord('z'):
        #my_url=url+chr(my_char)
        with requests.Session() as session: 
            response = session.get(f"{urlbase}/choose-letter/{chr(currchar)}")  # convert ascii to char
            # no entries for K and W
            if not((chr(currchar) == "k") or  (chr(currchar)=="w")):
                soup = bs(response.text, 'html.parser')
                letterurl, numpages =  soup.find('li', {'class':'pager-last'}).a['href'].split('=')
                print(f'letter {chr(currchar)} has {numpages} pages')
                for page in range(int(numpages)+1):
                    response = session.get(f"{urlbase}{letterurl}={page}")  # convert ascii to char
                    soup = bs(response.text, 'html.parser')
                    words = soup.find_all('section')[0].find_all('h2')
                
                    for wrd in words:
                        link = wrd.a['href']
                        response2 = session.get(f"{urlbase}/{link}")
                        #sp2=bs(session.get("https://nahuatl.wired-humanities.org/content/xacalli").text,'html.parser')
                        soup2 = bs(response2.text, 'html.parser')
                        noteseng = soup2.select('section')[0].find("div", {"class": "field-name-field-additionalnotes-lang1"})
                        notesspa = soup2.select('section')[0].find("div", {"class": "field-name-field-additionalnotes-lang2"})

                        #noteseng = sp2.select('section')[0].find("div", {"class": "field-name-field-additionalnotes-lang1"})
                        #notesspa = sp2.select('section')[0].find("div", {"class": "field-name-field-additionalnotes-lang2"})

                        if noteseng:
                            for idx, note in enumerate(noteseng.find_all('p')):
                                if note.bibl:
                                    note.bibl.extract()
                                ntransl = note.text.count('=')
                                if ntransl >= 1:
                                    engtransl.append(note.text.strip())
                                    sents = note.text.split('\n')
                                    if (len(sents) == 1) or (( len(sents)==2) and (sents[-1].strip()=="" )):
                                        sents = re.split(r"[.;\n]",note.text)
                                    ntransl = min(ntransl, len(sents))
                                    for t in range(ntransl):
                                        if sents[t].find('=') > -1:
                                            if len(sents[t].split('='))>2:
                                                print(f'        PROBLEMATIC MATCH: word {wrd.text} at index {len(engtransl)}. Sentence =  {sents[t]}')
                                                nah, trg = sents[t].split('=',1)
                                                nah = nah if nah[-3:].find('.') > -1 else nah.strip()+'. '
                                                trg = trg.strip() if trg[-5:].find(')') == -1 else trg.strip().rsplit('(',maxsplit=1)[0]
                                                engprobl.append((len(engtransl),wrd.text,nah,trg))# idx in engtransl, src,trg
                                            else:
                                                nah, trg = sents[t].split('=')
                                                nah = nah if nah[-3:].find('.') > -1 else nah.strip()+'. '
                                                trg = trg.strip() if trg[-5:].find(')') == -1 else trg.strip().rsplit('(',maxsplit=1)[0]
                                                nahE.append(nah)  
                                                eng.append(trg)
                                    

                        if notesspa:
                            for idx, note in enumerate(notesspa.find_all('p')):
                                if note.bibl:
                                    note.bibl.extract()
                                ntransl = note.text.count('=')
                                if ntransl >= 1:
                                    spatransl.append(note.text.strip())                            
                                    sents = note.text.split('\n')
                                    if (len(sents) == 1) or (( len(sents)==2) and (sents[-1].strip()=="" )):
                                        sents = re.split(r"[.;\n]",note.text)
                                    ntransl = min(ntransl, len(sents))
                                    for t in range(ntransl):
                                        if sents[t].find('=') > -1:
                                            if len(sents[t].split('='))>2:
                                                print(f'        PROBLEMATIC MATCH: word {wrd.text} at index {len(spatransl)}. Sentence = {sents[t]}')
                                                nah, trg = sents[t].split('=',1)
                                                nah = nah if nah[-3:].find('.') > -1 else nah.strip()+'. '
                                                trg = trg.strip() if trg[-5:].find(')') == -1 else trg.strip().rsplit('(',maxsplit=1)[0]
                                                spaprobl.append((len(spatransl),wrd.text,nah,trg)) # idx in spatransl, src,trg
                                            else:
                                                nah, trg = sents[t].split('=')
                                                nah = nah if nah[-3:].find('.') > -1 else nah.strip()+'. '
                                                trg = trg.strip() if trg[-5:].find(')') == -1 else trg.strip().rsplit('(',maxsplit=1)[0]
                                                nahS.append(nah)  
                                                spa.append(trg)
                                        

                    print(f'    page{page+1}/{numpages+1} done')
            print(f'done with {chr(currchar)}')
        currchar+=1 # iterate over abc


    SPA = [sent.strip('.') if sent[-5:].find(')') == -1 else sent.strip().rsplit('(',maxsplit=1)[0].strip('.') for sent in spa]
    ENG = [sent.strip('.') if sent[-5:].find(')') == -1 else sent.strip().rsplit('(',maxsplit=1)[0].strip('.') for sent in eng]
    with open('nahuatl-spanish/extra/dictexamplesents.spa-nah.spa','w') as fout:
        fout.write('. \n'.join(SPA))
    with open('nahuatl-spanish/extra/dictexamplesents.spa-nah.nah','w') as fout:
        fout.write('\n'.join(nahS))
    with open('nahuatl-spanish/extra/dictexamplesents.eng-nah.eng','w') as fout:
        fout.write('. \n'.join(ENG))
    with open('nahuatl-spanish/extra/dictexamplesents.eng-nah.nah','w') as fout:
        fout.write('\n'.join(nahE))


    #with open('nahuatl-spanish/extra/dictexamplesents.spa-nah.temp','w') as fout:
    #    fout.write(' <EoEx>\n'.join(spatransl))
    #with open('nahuatl-spanish/extra/dictexamplesents.eng-nah.temp','w') as fout:
    #    fout.write(' <EoEx>\n'.join(engtransl))

    # EXAMPLES THAT NEED EXTRA CARE TO BE ALIGNED PROPERLY:
    df_spaprob = pd.DataFrame(spaprobl, columns=('id','word','nah','spa'))
    df_engprob = pd.DataFrame(engprobl, columns=('id','word','nah','eng'))
    df_spaprob.to_csv('nahuatl-spanish/extra/dictexamplesents.outliers.spa-nah.tsv', sep='\t', index=False, header=False)
    df_engprob.to_csv('nahuatl-spanish/extra/dictexamplesents.outliers.eng-nah.tsv', sep='\t', index=False, header=False)


def nawatldotcom():
    # NAHWATL.com
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


def cuentosunam():
    # UNAM - nah-spa
    opath=pathlib.Path('./pdfs/cuentos_nah-spa')
    opath.mkdir(exist_ok=True)
    # Page is blocking scrappers
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


def inpi():
    # INPI - nah-spa monografia 
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




def spl_ng_es():
    # GUARANÍ
    urles = 'https://spl.gov.py/es/index.php/noticias'
    urlgn = 'https://www.spl.gov.py/gn/index.php/marandukuera'
    user_agents = [
      "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
      "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
      "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
      ]

    esfull, gnfull = [], []

    iterdic = {'SPANISH': {'url':urles, 'texts':esfull}, 'GUARANI': {'url':urlgn, 'texts':gnfull}, }
    with requests.Session() as session:
        for key,lang in iterdic.items():
            print(f"processing {key}")
            url = lang['url'] 
            numpages =  67 # sorry, I was lazy here
            for page in range(numpages):
                print(f'page {page+1}/{numpages}')
                random_user_agent = random.choice(user_agents)
                headers = {'User-Agent': random_user_agent }
                response = session.get(f'{url}?ccm_paging_p={page}', headers = headers)

                soup = bs(response.text, 'html.parser')

            
                articles = soup.find_all('span', {'class':'card-title'})

                for art in articles:
                    link = art.a['href']
                    response2 = session.get(f"{link}", headers = headers)
                    soup2 = bs(response2.text, 'html.parser')
                    
                    lang['texts'].append(f"[NEW_DOCUMENT DOCid= {soup2.find('blockquote').text} ]. ") # use publication date as ID
                    lang['texts'].append(f"{soup2.find('h5', {'class':'page-title'}).text}. ".replace('\u200b', ' ').strip()) # append the document title

                    #sentences = soup2.find_all('p')
                    
                    content = soup2.find('div', {'class':'section contenido_principal'})
                    lang['texts'].append(content.p.text)


    with open('guarani-spanish/extra/scrapped_news.pkl', 'wb') as f:
        pickle.dump(iterdic, f)

    esfull= ' '.join(iterdic['SPANISH']['texts'])
    gnfull= ' '.join(iterdic['GUARANI']['texts'])

    splitterspa = SentenceSplitter(language='es')
    splittergn = SentenceSplitter(language='en') 

    es = splitterspa.split(text=esfull)
    gn = splittergn.split(text=gnfull)

    with open('guarani-spanish/extra/noticias.doclevel.es','w') as fout:
        fout.write('\n'.join(es))
    with open('guarani-spanish/extra/noticias.doclevel.gn','w') as fout:
        fout.write('\n'.join(gn))

    gnarts = gnfull.split('[NEW_DOCUMENT DOCid= Publicado: ')
    esarts = esfull.split('[NEW_DOCUMENT DOCid= Publicado: ')
    estimes = [ re.sub(' ..\:.*m','',k.split('. ].  ')[0]) for k in esarts]
    gntimes = [ re.sub(' ..\:.*m','',k.split('. ].  ')[0]) for k in gnarts]
    # TODO: insert a dummy in the index of estimes or gntimes where the two entries don't match


    estimes = [ k.split('. ].  ')[0] for k in esarts]
    gntimes = [ k.split('. ].  ')[0] for k in gnarts]

    for i in range(len(estimes)):
        print(re.sub(' ..\:.*m','',estimes[i]), re.sub(' ..\:.*m','',gntimes[i]))
        # if this two are not the same, insert a dummy in the side that is missing that article ()



# BRIBRI


maintextspa = []
maintextbzd = []
chaptertitles = []
capitals = []
def visitor_body_BZD(text, cm, tm, fontDict, fontSize):
    fs = tm[0]
    x = tm[4]
    y = tm[5]
    if pag == 57:
        print(tm, len(text), text[:100])
    # main text is fontsize 12 or 15
    if fs == 12.0 or fs == 15.0: # or fs == 5.7 or fs == 9.0:
        if x > 300:
            maintextspa.append(text)
        if x < 300:
            maintextbzd.append(text)
    elif fs == 24.0:
        chaptertitles.append(text)
    # skip page numbering always fontsize = 8.0
    elif fs >= 70.0:
        if text != '\n':
            capitals.append(text)
    elif text:
        pass
        #print("SKIIIIPED:     page",pag,text, tm)

def enciclopedia_bzdspa():
    # BRIBRI enciclopedia - bzd-spa
    opath=pathlib.Path('./pdfs/enciclopedia_bzd-spa')
    opath.mkdir(exist_ok=True)

    urlbase='https://mep.go.cr/sites/default/files/tomo'
    print( '''HUOM! YOU NEED A VPN IN CR!!! To download the books with: 
                for idx in range(1,8):
                    subprocess.run(["wget", "-nc", "-P", str(opath), f"{urlbase}_{idx}.pdf"])
            ''')

    bzdfull, spafull = [], []
    global pag # global for debugging purposes
    for idx in range(2,6):
        # HUOM!
        #      BOOK 1 BEHAVES STRANGE!!! I think that copypaseting the pdf contents and then doing the processing might work better

        reader = PdfReader(f'{str(opath)}/tomo_{idx}.pdf')
        npag=len(reader.pages) if idx!=3 else 73
        title = reader.pages[6].extract_text().split('–')[0]
        bzdchp = f" [NEW_DOCUMENT:  DOCid={idx}, lang=bzd, DOCNAME={title}]. "
        spachp = f" [NEW_DOCUMENT:  DOCid={idx}, lang=spa, DOCNAME={title}]. "
        newfile = True
        for pag in range(11,npag):
            maintextspa, maintextbzd, chaptertitles,capitals = [],[],[],[]

            # first two pages are not useful
            # always starts with nahuatl in page 3 (i=2)
            # the spanish translation is in the odd page index
            print(f"\n####### TOMO {idx}, PAG: {pag}")
            coso = reader.pages[pag].extract_text(visitor_text=visitor_body_BZD)
            if chaptertitles:
                if not capitals:
                    capitals = ['','']
                print(capitals)
                bzd = "[NEW CHAPTER: "+' '.join(chaptertitles).replace('\n',' ')+f' , DOCid={idx},]. '+capitals[-1]+''.join(maintextbzd)
                spa = "[NEW CHAPTER: "+' '.join(chaptertitles).replace('\n',' ')+f' , DOCid={idx},]. '+capitals[-2]+''.join(maintextspa)
                if newfile:
                    newfile=False
                    bzdchp += bzd.replace('\n','')
                    spachp += spa.replace('\n','')
                else:
                    bzdchp += f" [END OF CHAPTER]. "
                    spachp += f" [END OF CHAPTER]. "
                    bzdfull.append(bzdchp)
                    spafull.append(spachp)
                
                    bzdchp = bzd.replace('\n','')
                    spachp = spa.replace('\n','')
            else:
                spa = ''.join(maintextspa).replace('\n','').replace('-', '')
                bzd = ''.join(maintextbzd).replace('\n','').replace('-', '')
                bzdchp += bzd
                spachp += spa
        
        bzdchp = bzdchp.replace('.', '. ')
        spachp = spachp.replace('.', '. ')
        bzdchp += f" [END OF CHAPTER]. "
        spachp += f" [END OF CHAPTER]. "
        bzdchp += f" [END OF DOCUMENT]. "
        spachp += f" [END OF DOCUMENT]. "
        bzdfull.append(bzdchp)
        spafull.append(spachp)

    splitterspa = SentenceSplitter(language='es')
    splitterbzd = SentenceSplitter(language='en') 

    for id, chapter in enumerate(bzdfull):
        txt = splitterbzd.split(text=chapter.replace('.', '. '))
        with open(f'bribri-spanish/extra/enciclopedia.{id}.doclevel.bzd', 'w') as fout:
            fout.write('\n'.join(txt))

    for id, chapter in enumerate(spafull):
        txt = splitterspa.split(text=chapter.replace('.', '. '))
        with open(f'bribri-spanish/extra/enciclopedia.{id}.doclevel.spa', 'w') as fout:
            fout.write('\n'.join(txt))



def main():
    # nahuatl:
    naheng_dictionary()
    nawatldotcom()
    cuentosunam()
    inpi()
    # guarani
    spl_ng_es()
    # bribri
    enciclopedia_bzdspa()

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


if __name__ == '__main__':
    main()

