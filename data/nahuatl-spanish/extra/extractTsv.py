#! /usr/bin/env python3

def extractData(fileid):
    f = open(f'{fileid}.nah-spa.tsv', 'r')
    f_nah = open(f'{fileid}.nah', 'w')
    f_spa = open(f'{fileid}.spa', 'w')
    for line in f:
        elements = line.split("\t")
        # get rid of document boundary tags :)
        if elements[0].startswith("["):
            continue
        t_nah = elements[0].strip().replace(" ~~~ ", " ")
        t_spa = elements[1].strip().replace(" ~~~ ", " ")
        if t_nah == "" or t_spa == "":
            continue
        f_nah.write(t_nah + "\n")
        f_spa.write(t_spa + "\n")
    f.close()
    f_nah.close(); f_spa.close()


if __name__ == "__main__":
    extractData("cuentos")
    extractData("texts")
    