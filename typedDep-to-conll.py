# -*- coding: utf-8 -*-
__author__ = 'arenduchintala'

"""
this script converts the stanford typed dependency file to conll dependency format

typed dependency format:
advmod(没有-4, 为什么-1)
nn(主妇-3, 家庭-2)
top(没有-4, 主妇-3)
root(ROOT-0, 没有-4)
det(退休俸-8, 任何-5)
conj(退休俸-8, 薪水-6)
cc(退休俸-8, 与-7)
dobj(没有-4, 退休俸-8)
"""
import re
import sys, codecs
from optparse import OptionParser


def split_type_dep_line(l):
    # arc_label, from_tok, to_tok, emp = re.split('[\(\)]|, ', l)
    arc_label, rest = l.split('(', 1)
    from_tok, to_tok = rest.split(', ')
    from_tok, from_tok_id = re.split('\-(?=[0-9]+$)', from_tok)
    to_tok, to_tok_id = re.split('\-(?=[0-9]+\)$)', to_tok)
    to_tok_id, emp = to_tok_id.split(')')
    return arc_label.strip(), int(from_tok_id), int(to_tok_id)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stdin = codecs.getwriter('utf-8')(sys.stdin)
    opt = OptionParser()
    opt.add_option("-t", dest="typedDep", help="the typed dependency file location", default="typed.deps")
    opt.add_option("-p", dest="tags", help="the pos tag file location", default="pos.tags")
    (options, args) = opt.parse_args()
    typed_deps = re.split('\n\n', codecs.open(options.typedDep, 'r', 'utf-8').read().strip())
    tags = re.split('\n\n', codecs.open(options.tags, 'r', 'utf-8').read().strip())

    for td, ta in zip(typed_deps, tags):
        ta = [tuple(s.split('/')) for s in ta.split()]
        seen = {}
        for l in td.strip().split('\n'):
            try:
                arc_label, from_tok_id, to_tok_id = split_type_dep_line(l)
            except:
                print 'failed to split', l
            try:
                conll_line = [str(to_tok_id), ta[to_tok_id - 1][0], '_', ta[to_tok_id - 1][1], ta[to_tok_id - 1][1],
                              '_', str(from_tok_id), arc_label, '_', '_']
                # print '\t'.join(conll_line)
                seen[to_tok_id - 1] = '\t'.join(conll_line)
            except:
                print 'failed to list', l
        for i in range(len(ta)):
            if i in seen:
                print seen[i]
            else:
                print str(i) + '\t' + ta[i][0] + '\t_\t' + ta[i][1] + '\t' + ta[i][
                    1] + '\t_\t' + '0' + '\t' + 'DUMMY' + '\t_\t_'

        print ''



