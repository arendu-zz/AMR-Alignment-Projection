ISSUES DISCUSSED
================

- We are dropping tokens from the target side sentences, this might screw up alignments (maybe?)

TODOs
=====
- NE rules, dates , quants etc
When generating the caveman string we should drop the Named entity ontology nodes, since these
are not likely to have surface realizations in the source language.
Once fast align has be run, then the source tokens that get aligned to the leaf of NE subgraphs, should
in turn also be aligned to nodes in the NE ontology. (this needs to be implemented)

- Multiple concepts aligned to single source token.
In this case that source token gets mapped to both concepts in the AMR. (this needs to be implemented)
