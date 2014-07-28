#!/bin/bash
INPUT_ALIGNED="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned"
OUTPUT_ZH_ALIGNED="data/Little_Prince/amr-bank-struct-v1.3.txt.zh-aligned"
TEMP_FOLDER="data/Little_Prince/"

python extract-attributes.py -f $INPUT_ALIGNED  -a zh > $TEMP_FOLDER"zh.unseg"

python extract-attributes.py -f $INPUT_ALIGNED  -a tok > $TEMP_FOLDER"tok.segmented"

segment.sh ctb $TEMP_FOLDER"zh.unseg" UTF-8 0 > $TEMP_FOLDER"zh.segmented"

rm  $TEMP_FOLDER"zh.unseg"

python join.py -z  $TEMP_FOLDER"zh.segmented"  -c   $TEMP_FOLDER"tok.segmented"  >  $TEMP_FOLDER"zh-en"

fast_align ctb -i $TEMP_FOLDER"zh-en" UTF-8 0 > $TEMP_FOLDER"zh-en.alignments"

#now we take the alignments and for each span in the en side find a corresponding span in zh


