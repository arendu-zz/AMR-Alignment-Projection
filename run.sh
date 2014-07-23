#!/bin/bash
INPUT_ALIGNED="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned"
OUTPUT_ZH_ALIGNED="data/Little_Prince/amr-bank-struct-v1.3.txt.zh-aligned"
TEMP_FOLDER="data/Little_Prince/"
python generate-caveman.py -f $INPUT_ALIGNED > $TEMP_FOLDER"aligned.caveman"

python extract-attributes.py -f $INPUT_ALIGNED  -a zh > $TEMP_FOLDER"zh.unseg"

python extract-attributes.py -f $TEMP_FOLDER"aligned.caveman" -a caveman_string > $TEMP_FOLDER"caveman.segmented"

segment.sh ctb $TEMP_FOLDER"zh.unseg" UTF-8 0 > $TEMP_FOLDER"zh.segmented"

rm  $TEMP_FOLDER"zh.unseg"

python join.py -z  $TEMP_FOLDER"zh.segmented"  -c  $TEMP_FOLDER"caveman.segmented"  >  $TEMP_FOLDER"zh-caveman"

fast_align ctb -i $TEMP_FOLDER"zh-caveman" UTF-8 0 > $TEMP_FOLDER"zh-caveman.alignments"

python source-to-amr-aligner.py -a $TEMP_FOLDER"zh-caveman.alignments" -f $TEMP_FOLDER"aligned.caveman" -c $TEMP_FOLDER"zh-caveman" > $OUTPUT_ZH_ALIGNED