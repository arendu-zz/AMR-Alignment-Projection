#!/bin/bash
python generate-caveman.py -f data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned > data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned.caveman

python extract-attributes.py -f data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned -a zh > data/Little_Prince/zh.unseg

python extract-attributes.py -f data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned.caveman -a caveman_string > data/Little_Prince/caveman.segmented

segment.sh ctb data/Little_Prince/zh.unseg UTF-8 0 > data/Little_Prince/zh.segmented

rm  data/Little_Prince/zh.unseg

python join.py -z data/Little_Prince/zh.segmented  -c data/Little_Prince/caveman.segmented  > data/Little_Prince/zh-caveman

fast_align ctb -i data/Little_Prince/zh-caveman UTF-8 0 > data/Little_Prince/zh-caveman.alignment