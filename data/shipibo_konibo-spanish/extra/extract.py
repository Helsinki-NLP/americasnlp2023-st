#! /usr/bin/env python3

import re, csv


def extractBible(infilename, outfileid):
	f = open(infilename, 'r', encoding='utf-16le')
	out_shp = open(f'{outfileid}.shp', 'w')
	out_es = open(f'{outfileid}.es', 'w')
	for line in f:
		if line.startswith("{"):
			elems = re.search(r'^\{"(.+?)", "(.+?)", "(.+?)", "(.+?)", "(.+?)"\}$', line.strip())
			out_shp.write(elems.group(4) + "\n")
			out_es.write(elems.group(5) + "\n")
	f.close(); out_shp.close(); out_es.close()


def extractTsanas():
	f = open('traduccionTsanas1.csv', 'r', encoding='iso-8859-1')
	out_shp = open('tsanas1.shp', 'w')
	out_es = open('tsanas1.es', 'w')
	rd = csv.reader(f)
	for row in rd:
		out_shp.write(row[2] + "\n")
		out_es.write(row[3] + "\n")
	f.close(); out_shp.close(); out_es.close()


if __name__ == "__main__":
	extractBible("BibleShiSpa_1.txt", 'bible-shispa-1')
	extractBible("BibleShiSpa_2.txt", 'bible-shispa-2')
	extractTsanas()
