#! /bin/sh

SRCDIR=/users/yvessche/scratch_fotran/yves/americas/americasnlp2021-st/processed_data
BTDIR=/users/yvessche/scratch_fotran/yves/americas/pretrainToEs2/bt

# aym - aymara
mkdir data/aymara-spanish/synt
scp puhti:$SRCDIR/aymara/monolingual.aym.txt data/aymara-spanish/synt/bt_yves21.aym
scp puhti:$BTDIR/mono_aym.es.txt data/aymara-spanish/synt/bt_yves21.es

# cni - ashaninka
mkdir data/ashaninka-spanish/synt
scp puhti:$SRCDIR/ashaninka/monolingual.cni.txt data/ashaninka-spanish/synt/bt_yves21.cni
scp puhti:$BTDIR/mono_cni.es.txt data/ashaninka-spanish/synt/bt_yves21.es

# gn - guarani
mkdir data/guarani-spanish/synt
scp puhti:$SRCDIR/guarani/monolingual.gn.txt data/guarani-spanish/synt/bt_yves21.gn
scp puhti:$BTDIR/mono_gn.es.txt data/guarani-spanish/synt/bt_yves21.es

# hch - wixarika
mkdir data/wixarika-spanish/synt
scp puhti:$SRCDIR/wixarika/monolingual.hch.txt data/wixarika-spanish/synt/bt_yves21.hch
scp puhti:$BTDIR/mono_hch.es.txt data/wixarika-spanish/synt/bt_yves21.es

# nah - nahuatl
mkdir data/nahuatl-spanish/synt
scp puhti:$SRCDIR/nahuatl/monolingual.nah.txt data/nahuatl-spanish/synt/bt_yves21.nah
scp puhti:$BTDIR/mono_nah.es.txt data/nahuatl-spanish/synt/bt_yves21.es

# oto - hñähñu
mkdir data/hñähñu-spanish/synt
scp puhti:$SRCDIR/hñähñu/monolingual.oto.txt data/hñähñu-spanish/synt/bt_yves21.oto
scp puhti:$BTDIR/mono_oto.es.txt data/hñähñu-spanish/synt/bt_yves21.es

# quy - quechua
#mkdir data/quechua-spanish/synt
#scp puhti:$SRCDIR/quechua/monolingual.quy.txt data/quechua-spanish/synt/bt_yves21.quy
#scp puhti:$BTDIR/mono_quy.es.txt data/quechua-spanish/synt/bt_yves21.es

# shp - shipibo_konibo
mkdir data/shipibo_konibo-spanish/synt
scp puhti:$SRCDIR/shipibo_konibo/monolingual.shp.txt data/shipibo_konibo-spanish/synt/bt_yves21.shp
scp puhti:$BTDIR/mono_shp.es.txt data/shipibo_konibo-spanish/synt/bt_yves21.es
