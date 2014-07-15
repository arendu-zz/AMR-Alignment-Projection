#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'arenduchintala'
from optparse import OptionParser
import re
import pdb
from AMRMetadata import AMRMetadata

"""
srcipt generates a string with tokens replaces by AMR concepts.
"""


def step_through_graph(graph, sequence):
    """
    steps through a AMR graph along some branching sequence and returns the concept at the end point
    :param sequence:
    :param graph:
    :return concept:
    """
    s = [x for x in sequence]
    sequence.pop(0)
    node_label = graph.roots[0]
    # TODO: do these graphs always have just one root?
    while len(sequence) > 0:
        branch = int(sequence.pop(0))
        node_labels = []
        for x in sorted(graph[node_label]):
            print x, graph[node_label][x]
            nl = graph[node_label][x][0]
            if len(graph.node_to_parents[nl]) < 2:
                node_labels.append(nl)
            else:
                # this is a re-enterency and the alignment step through counts should ignore it.
                print 're-enterency', nl, graph.node_to_parents[nl]
        node_label = node_labels[branch]
    concept = graph.node_to_concepts[node_label]
    return concept


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
    print tok
    alignments = dict((tuple(x.split('|')[0].split('-')), x.split('|')[1].split('+')) for x in a.split())
    print alignments
    span_concepts = {}
    for span, align in alignments.items():
        for seq in align:
            print 'getting concept at', seq, 'for span', span
            seq = seq.split('.')
            concept = step_through_graph(g, seq)
            current_concepts_at_span = span_concepts.get(span, [])
            current_concepts_at_span.append(concept)
            span_concepts[span] = current_concepts_at_span
    print span_concepts


def read_file(amrfile):
    """
    accepts path to file of amr graphs and metadata in  ISI format.
    :param amrfile:
    :return amr_metadata: returns list of AMRMetadata objects
    """
    amr_metadata = []
    items = open(amrfile, 'r').read().split('\n\n')
    for idx, item in enumerate(items):
        c = AMRMetadata(item)
        amr_metadata.append(c)
    return amr_metadata


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="amr_file", help="AMR File with alignments", default="data/Little_Prince/test.aligned")
    (options, args) = opt.parse_args()
    amr_metadata = read_file(options.amr_file)  # gets a list of meta data plus the string graph
    amr_md = amr_metadata[4]
    pdb.set_trace()
    for idx, amr_md in enumerate(amr_metadata):
        # stringyfied_amr(g=amr_md.graph, a=amr_md.attributes['alignments'], cs=amr_md.attributes['snt'])
        print idx, amr_md.attributes['caveman-string'], '|||', amr_md.attributes['zh']


