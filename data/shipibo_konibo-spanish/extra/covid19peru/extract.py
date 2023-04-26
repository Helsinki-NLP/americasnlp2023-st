#! /usr/bin/env python3

import os, csv, re

out_shp = open("../covid19.shp", "w")
out_spa = open("../covid19.spa", "w")

for filename in sorted(os.listdir(".")):
    if not filename.endswith(".tsv"):
        continue
    f = open(filename, "r")
    rd = csv.reader(f, delimiter="\t")
    first = True
    for row in rd:
        if first:
            first = False
            continue
        spa = row[0].strip()
        shp = row[1].strip()
        if shp == "" or shp == ".":
            continue
        spa = re.sub(r'^\d+\.\s+', '', spa)
        out_shp.write(shp + "\n")
        out_spa.write(spa + "\n")
    f.close()

out_shp.close(); out_spa.close()
