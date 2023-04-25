#! /usr/bin/env python3

# extracts the two first columns from a tsv file into two separate text files
# also removes document boundary tags and Hunalign markers
# also skips sentence pairs where one side is empty

def extractData(tsvfile, src_outfile, tgt_outfile):
    f = open(tsvfile, 'r')
    f_src = open(src_outfile, 'w')
    f_tgt = open(tgt_outfile, 'w')
    for line in f:
        elements = line.split("\t")
        # get rid of document boundary tags :)
        if elements[0].startswith("["):
            continue
        t_src = elements[0].strip().replace(" ~~~ ", " ")
        t_tgt = elements[1].strip().replace(" ~~~ ", " ")
        if t_src == "" or t_tgt == "":
            continue
        f_src.write(t_src + "\n")
        f_tgt.write(t_tgt + "\n")
    f.close()
    f_src.close(); f_tgt.close()


if __name__ == "__main__":
    #extractData("nahuatl/extra/texts.nah-spa.tsv", "nahuatl/extra/texts.nah", "nahuatl/extra/texts.spa")
    extractData("guarani-spanish/extra/noticias_final.tsv", "guarani-spanish/extra/noticias.gn", "guarani-spanish/extra/noticias.es")
