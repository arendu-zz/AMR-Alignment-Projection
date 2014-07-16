#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'arenduchintala'
from optparse import OptionParser
from AMRMetadata import AMRMetadata
from pprint import pprint


def stringyfied_amr(g, s, a):
    """
    places to the concepts from the graph 'g' in the order of the actual string 's' using the
    alingment 'a'
    :param g: amr graph
    :param s:
    :param a:
    :return:
    """
    tok = s.split()
    # print tok
    alignments = dict((tuple(x.split('|')[0].split('-')), x.split('|')[1].split('+')) for x in a.split())
    # print alignments
    span_concepts = {}
    for span, align in alignments.items():
        for seq in align:
            # print 'getting concept at', seq, 'for span', span
            concept = g.get_concept(seq.split('.'))
            current_concepts_at_span = span_concepts.get(span, [])
            current_concepts_at_span.append(concept)
            span_concepts[int(span[0]), int(span[1])] = current_concepts_at_span
    return span_concepts


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="amr_file", help="AMR File with alignments", default="data/Little_Prince/test.aligned")
    (options, args) = opt.parse_args()

    for item in open(options.amr_file, 'r').read().split('\n\n'):
        if item.strip() != '':
            c = AMRMetadata(item)
            # pprint(dict(c.graph.nodes_to_children))
            caveman_map = stringyfied_amr(c.graph, c.attributes['snt'], c.attributes['alignments'])
            for k in sorted(caveman_map):
                print caveman_map[k],
            print ''


