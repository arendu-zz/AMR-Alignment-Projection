#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'arenduchintala'
from optparse import OptionParser
from AMRMetadata import AMRMetadata
from collections import defaultdict


def stringyfied_amr(g, s, a):
    """
    places to the concepts from the graph 'g' in the order of the actual string 's' using the
    alingment 'a'
    :param g: amr graph
    :param s:
    :param a:
    :return:
    """
    alignments = dict((tuple(x.split('|')[0].split('-')), x.split('|')[1].split('+')) for x in a.split())
    # print alignments
    span_concepts = defaultdict(list)
    caveman_alignments = {}
    for span, align in alignments.items():
        caveman_alignments[int(span[0]), int(span[1])] = '+'.join(align)
        for seq in align:
            print 'getting concept at', seq, 'for span', span
            concept = g.get_concept(seq.split('.'))
            span_concepts[int(span[0]), int(span[1])].append(concept)
    caveman_string = ''
    caveman_alignments_string = ''
    i = 0
    for k in sorted(span_concepts):
        j = i + len(span_concepts[k])
        caveman_string += ' '.join(span_concepts[k]) + ' '
        caveman_alignments_string += str(i) + '-' + str(j) + '|' + caveman_alignments[k] + ' '
        i = j
    return caveman_string, caveman_alignments_string


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-f", dest="amr_file", help="AMR File with alignments", default="data/Little_Prince/test.aligned")
    (options, args) = opt.parse_args()
    for item in open(options.amr_file, 'r').read().split('\n\n'):
        if item.strip() != '':
            c = AMRMetadata(item)
            c.parse_graph()
            cs, cs_alignment = stringyfied_amr(c.graph, c.attributes['tok'], c.attributes['alignments'])
            c.add_attribute('caveman_string', cs)
            c.add_attribute('caveman_alignment', cs_alignment)
            print str(c)



