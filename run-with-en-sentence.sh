#!/bin/sh
python extract-attributes.py -f data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned -a zh > data/Little_Prince/zh.unseg

python extract-attributes.py -f data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned -a tok > data/Little_Prince/en.segmented

segment.sh ctb data/Little_Prince/zh.unseg UTF-8 0 > data/Little_Prince/zh.segmented

rm  data/Little_Prince/zh.unseg

python join.py -z data/Little_Prince/zh.segmented  -c data/Little_Prince/en.segmented  > data/Little_Prince/zh-en

fast_align ctb -i data/Little_Prince/zh-en UTF-8 0 > data/Little_Prince/zh-en.alignments