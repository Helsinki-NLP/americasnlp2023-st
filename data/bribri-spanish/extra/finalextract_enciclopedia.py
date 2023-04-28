#! /usr/bin/env python3

# extracts the Bribri parts from enciclopedia.bzd-spa.tsv and enciclopedia.bzd2-spa.tsv

outfile_bzd = open("enciclopedia_final.bzd", "w")
outfile_spa = open("enciclopedia_final.es", "w")
added1, added2 = 0, 0

infile1 = open("enciclopedia.bzd-spa.tsv", "r")
for line in infile1:
    if line.startswith("PARTE II"):
        break
    if line.startswith("["):
        continue
    elements = line.split("\t")
    if elements[0].strip() != "" and elements[1].strip() != "":
        outfile_bzd.write(elements[0].replace(" ~~~ ", " ").strip() + "\n")
        outfile_spa.write(elements[1].replace(" ~~~ ", " ").strip() + "\n")
        added1 += 1
infile1.close()

infile2 = open("enciclopedia.bzd2-spa.tsv", "r")
skip = True
for line in infile2:
    if line.startswith("[NEW CHAPTER: Los Bribris"):
        skip = False
    if skip:
        continue
    if line.startswith("["):
        continue
    elements = line.split("\t")
    if elements[0].strip() != "" and elements[1].strip() != "":
        outfile_bzd.write(elements[0].replace(" ~~~ ", " ").strip() + "\n")
        outfile_spa.write(elements[1].replace(" ~~~ ", " ").strip() + "\n")
        added2 += 1
infile2.close()

outfile_bzd.close(); outfile_spa.close()
print("Added pairs from file 1:", added1)
print("Added pairs from file 2:", added2)
