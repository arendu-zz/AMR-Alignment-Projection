__author__ = 'arenduchintala'

from optparse import OptionParser
import pdb

"""
This script uses the alignments between source and target sentences.
(full sentences not caveman versions of them)
It finds corresponding source-spans for every span in the target.
We know the alignment from target-span to nodes in the amr, thus we map
nodes in the amr to souce-spans.
"""


def get_zh_span(from_id, to_id, st_dict, concepts_covered):
    zh_token_indexes = []
    for r in range(from_id, to_id):
        if r in st_dict:
            zh_token_indexes.append(st_dict[r])
        else:
            pass
    if len(zh_token_indexes) > 0:
        span_st = min(zh_token_indexes)
        span_end = max(zh_token_indexes) + 1
        sp = str(span_st) + '-' + str(span_end)
        return sp
    else:
        return None


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="src_target_alignments", help="source-target alignments (of full sentences) from "
                                                            "fast_align", default="data/Little_Prince/zh-en.alignments")

    opt.add_option("-t", dest="target_concept_alignments", help="file with target - concepts in amr file format",
                   default="data/Little_Prince/span.alignments")
    (options, args) = opt.parse_args()

    src_target_alignments = open(options.src_target_alignments, 'r').readlines()
    target_concept_alignments = open(options.target_concept_alignments, 'r').readlines()

    for idx, (st, tc) in enumerate(zip(src_target_alignments, target_concept_alignments)):
        st = st.strip()
        tc = tc.strip()
        if st != '' and tc != '':
            st_dict = dict((int(s.split('-')[1]), int(s.split('-')[0])) for s in st.strip().split())
            tc_tup = [(int(s.split('|')[0].split('-')[0]), int(s.split('|')[0].split('-')[1]), s.split('|')[1]) for s in
                      tc.strip().split()]
            tc_tup = sorted(tc_tup)
            zh_span = {}
            for t in tc_tup:
                # current span is t[0] to t[1], its nodes are t[2]
                from_id, to_id = t[0], t[1]
                concepts_covered = t[2]
                src_sp = get_zh_span(from_id, to_id, st_dict, concepts_covered)
                if src_sp is not None:
                    if src_sp in zh_span:
                        zh_span[src_sp] += '+' + concepts_covered
                    else:
                        zh_span[src_sp] = concepts_covered

            zh_alignment = ' '.join([str(sp + '|' + con) for sp, con in zh_span.items()])
            print zh_alignment.strip()
        else:
            print ''


