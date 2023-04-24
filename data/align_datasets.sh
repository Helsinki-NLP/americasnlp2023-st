#! /bin/bash

currentdir=`pwd`
touch /tmp/null.dict


cd $currentdir/bribri-spanish/extra
###   DATASET: enciclopedia
ls enciclopedia.*.spa -v > fnames.temp
rm enciclopedi*bzd-spa.tsv
 while read -r line; do
    ~/git/hunalign/src/hunalign/hunalign /tmp/null.dict ${line%.spa}.bzd $line -text > ${line%.doclevel.spa}.bzd-spa.tsv
    cut -f1-2 ${line%.doclevel.spa}.bzd-spa.tsv > file.temp
    #mv file.temp cuentos.nah-spa.tsv
    cat file.temp  >> enciclopedia.bzd-spa.tsv
done < fnames.temp
cd $currentdir

cd $currentdir/nahuatl-spanish/extra

# create an empty dict needed to run hunalign
rm texts.nah-spa.tsv
# align with hunalign
###   DATASET: cuentos
~/git/hunalign/src/hunalign/hunalign /tmp/null.dict cuentos.doclevel.nah cuentos.doclevel.spa -text > cuentos.nah-spa.tsv
cut -f1-2 cuentos.nah-spa.tsv > file.temp
#mv file.temp cuentos.nah-spa.tsv
cat file.temp  >> texts.nah-spa.tsv

###   DATASET: monografia
~/git/hunalign/src/hunalign/hunalign /tmp/null.dict monografia.doclevel.nah cuentos.doclevel.spa -text > monografia.nah-spa.tsv
cut -f1-2 monografia.nah-spa.tsv > file.temp
cat file.temp  >> texts.nah-spa.tsv
#mv file.temp monografia.nah-spa.tsv

###   DATASET: verses
~/git/hunalign/src/hunalign/hunalign /tmp/null.dict verses.doclevel.nah verses.doclevel.spa -text > verses.nah-spa.tsv
cut -f1-2 verses.nah-spa.tsv > file.temp
cat file.temp  >> texts.nah-spa.tsv
#mv file.temp texts.nah-spa.tsv

cd $currentdir

echo "dataset texts.nah-spa.tsv created in data/nahuatl-spanish/extra/"
    
