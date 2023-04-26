#! /bin/bash

currentdir=`pwd`
touch /tmp/null.dict


cd $currentdir/bribri-spanish/extra
cp  manually_revised/* .
###   DATASET: enciclopedia
langs="bzd bzd2 cjp gut gym"
for lang in $langs; do
   echo $lang
   ls enciclopedia.?.doclevel.${lang}-spa.spa -v > fnames.temp
   rm enciclopedia.${lang}-spa.tsv enciclopedia.doclevel.${lang}-spa.???
   while read -r line; do
       cat ${line%.spa}.$lang >> enciclopedia.doclevel.${lang}-spa.$lang
       cat $line              >> enciclopedia.doclevel.${lang}-spa.spa
       ~/git/hunalign/src/hunalign/hunalign /tmp/null.dict ${line%.spa}.$lang $line -text > bzd-spa.tsv.temp
       cut -f1-2 bzd-spa.tsv.temp > file.temp
       cat file.temp  >> enciclopedia.${lang}-spa.tsv
   done < fnames.temp
   rm fnames.temp
done
#TODO: Add all enciclopedias.doclevel into a single file 
#ls enciclopedia.doclevel.*tsv > fnames.temp
#while read -r line; do
#  cat ${line%.spa}.nah >> cuentos.doclevel.nah
#  cat $line            >> cuentos.doclevel.spa
#done < fnames.temp
rm *.temp
cd $currentdir

cd $currentdir/nahuatl-spanish/extra

# create an empty dict needed to run hunalign
rm texts.nah-spa.tsv
# align with hunalign
###   DATASET: cuentos
rm cuentos.doclevel.{nah,spa,tsv}
ls cuento.*.spa > fnames.temp
while read -r line; do
    cat ${line%.spa}.nah >> cuentos.doclevel.nah
    cat $line            >> cuentos.doclevel.spa
    ~/git/hunalign/src/hunalign/hunalign /tmp/null.dict ${line%.spa}.nah $line -text > ${line%.doclevel.spa}.nah-spa.tsv.temp
   cut -f1-2 ${line%.doclevel.spa}.nah-spa.tsv.temp > file.temp
   #rm $line ${line%.spa}.nah
   cat file.temp  >> cuentos.nah-spa.tsv
done < fnames.temp
rm *.temp
cat cuentos.nah-spa.tsv >> texts.nah-spa.tsv

###   DATASET: monografia
rm monografia.doclevel.{nah,spa,tsv}
ls monografia.?.*spa > fnames.temp
while read -r line; do
    cat ${line%.spa}.nah >> monografia.doclevel.nah
    cat $line            >> monografia.doclevel.spa
   ~/git/hunalign/src/hunalign/hunalign /tmp/null.dict ${line%.spa}.nah $line -text > monografia.nah-spa.tsv.temp
   cut -f1-2 monografia.nah-spa.tsv.temp > file.temp
   cat file.temp  >> monografia.nah-spa.tsv
done < fnames.temp
rm *.temp
cat monografia.nah-spa.tsv  >> texts.nah-spa.tsv

#mv file.temp monografia.nah-spa.tsv

###   DATASET: verses
~/git/hunalign/src/hunalign/hunalign /tmp/null.dict verses.doclevel.nah verses.doclevel.spa -text > verses.nah-spa.tsv
cut -f1-2 verses.nah-spa.tsv > file.temp
cat file.temp  >> texts.nah-spa.tsv
#mv file.temp tex
ts.nah-spa.tsv

### DATASET: dictexamplesents
paste dictexamplesents.spa-nah.nah dictexamplesents.spa-nah.spa >> texts.nah-spa.tsv

cd $currentdir

echo "dataset texts.nah-spa.tsv created in data/nahuatl-spanish/extra/"
    
