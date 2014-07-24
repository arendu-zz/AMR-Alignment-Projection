HOW TOs
=======

- install fast_align https://github.com/clab/fast_align
- install stanford chinese segmenter http://nlp.stanford.edu/software/segmenter.shtml
- (run.sh assumes fast_align and segment.sh is in $PATH)
- sh run.sh

ISSUES DISCUSSED
================

- We are dropping tokens from the target side sentences, this might screw up alignments (maybe?)


- NE rules, dates , quants etc When generating the caveman string we drop the Named entity ontology nodes, since these
are not likely to have surface realizations in the source language. 

- In some instances however the concepts/nodes should be preserved in the caveman string.
for example if the english string contains a reference like "planet Earth", the NE concept planet should appear in the 
caveman string. (taken care of)
Once fast align has be run, then the source tokens that get aligned to the leaf of NE subgraphs, should
in turn also be aligned to nodes in the NE ontology.

- also did the same for all quant-entity 

- Multiple concepts aligned to single source token.
In this case that source token gets mapped to both concepts in the AMR.

- getting path in graph for concepts - right now we are just using the alignments from the english-amr alignment in 
concept-amr paths, this might cause some issues, the path could be compute from the graph itself.

TODOs
=====

- filtering NE concepts is not straight forward all the time.
- suppose we want to filter out a NE concept 'city'
- if the word 'city' also appears in the en string, we don't remove the concept
- but what if a word like 'cities' appears instead? we can do string match to check 
if the concept 'city' is present in the en sentence.
- we probably need some kind of stemmer to check. (how does this scale to other languages?)
