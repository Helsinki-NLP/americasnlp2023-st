#! /usr/bin/env python3

import re

tsvfile = open("ctp-eng.tsv", "r")
cfile = open("ctp-eng.ctp", "w")
efile = open("ctp-eng.en", "w")

for line in tsvfile:
	elements = line.split("\t")
	eng = elements[-1].strip()
	all_ctp = [x for x in elements[2:-1] if x != ""]
	if len(all_ctp) == 2:
		ctp = all_ctp[0]
	else:
		ctp = " ".join(all_ctp[:len(all_ctp)//2])

	eng = eng.replace("˜", "").replace("ĩ", "i").replace("ã", "a").replace("Ĩ", "I").replace("õ", "o").replace("ỹ", "y")
	ctp = re.sub(r'\s+', ' ', ctp)
	ctp = ctp.strip()
	eng = re.sub(r'\s+', ' ', eng)
	eng = eng.strip()
	if ctp =="" or eng == "":
		continue
	if ctp[0] == "_" or eng[0] == "_":
		continue
	cfile.write(ctp + "\n")
	efile.write(eng + "\n")

tsvfile.close(); cfile.close(); efile.close()
