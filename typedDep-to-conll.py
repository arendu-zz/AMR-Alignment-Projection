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
from optparse import OptionParser


def split_type_dep_line(l):
    arc_label, from_tok, to_tok, emp = re.split('[\(,\)]', l)
    return arc_label.strip(), int(from_tok.strip().split('-')[1]), int(to_tok.strip().split('-')[1])


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-f", dest="typedDep", help="the typed dependency file location", )
    opt.add_option("-a", dest="tags", help="the pos tag file location")
    (options, args) = opt.parse_args()
    typed_deps = re.split('^$', open(options.typedDep, 'r').read())
    tags = re.split('^$', open(options.tags, 'r').read())

    for td, ta in zip(typed_deps, tags):
        ta = [tuple(s.split('/')) for s in ta.split()]
        for l in td.strip().split('\n'):
            arc_label, from_tok_id, to_tok_id = split_type_dep_line(l)
            conll_line = [str(to_tok_id), ta[to_tok_id - 1][0], '_', ta[to_tok_id - 1][1], ta[to_tok_id - 1][1], '_',
                          str(from_tok_id), arc_label, '_', '_']
            print '\t'.join(conll_line)
        print ''




