__author__ = 'arenduchintala'
"""
This script takes word-alignment file and AMR file as input.
From the AMR file the target side phrases are used.
Then the script enforces the alignments to comply to 2 constrains
1. no phrase in the target gets dropped
2. no two phrases in the source side is over lapping
see : https://www.writelatex.com/articles/phrase-projection-for-cross-lingual-jamr-training/ttrvffrkrtjy#.VAh9_mRdUpw
"""
from optparse import OptionParser
from pprint import pprint
from heapq import heapify, heappop, heappush
from AMRMetadata import AMRMetadata
import pdb


def check_alignment(word_alignment, target_spans):
    if len(word_alignment) == 0:
        return False
    # s2t.keys = token index in source
    # s2t.val = token index in target
    s2t = {}
    t2s = {}
    for s, t in word_alignment:
        t_list = s2t.get(int(s), [])
        s_list = t2s.get(int(t), [])
        t_list.append(int(t))
        s_list.append(int(s))
        s2t[int(s)] = t_list
        t2s[int(t)] = s_list

    target_spans.sort()
    target_spans = [t[0] for t in target_spans]
    ts2s = {}  # target spans to source alignments

    idxspans = [(idx, range(t[0], t[1])) for idx, t in enumerate(target_spans)]
    # target_token_to_span.keys  = token idx of target token
    # target_token_to_span.val = span idx to while the token belongs
    target2spanid = {}
    for idx, span in idxspans:
        for s in span:
            target2spanid[s] = idx

    src2targetspans = {}
    for src in range(max(s2t) + 1):  # iterate over source tokens and assign their target phrase membership
        for t in s2t.get(src, []):
            if target2spanid.get(t) is not None:
                tp_set = src2targetspans.get(src, set([]))
                tp_set.add(target2spanid.get(t))
                src2targetspans[src] = tp_set

    for ts in target_spans:
        tokens = range(ts[0], ts[1])
        src = None
        for t in tokens:
            if t2s.get(t, None) is not None:
                src = t2s[t]
                break
        if src is None:
            return False  # all alignments from a target phrase have been lost
        else:
            src = src[0]  # assuming model 1 style alignments TODO what about giza++ alignments??
            tp_set = src2targetspans[src]
            for tok in tokens[1:]:
                # 3 should map to just 2
                # 4 shoudl map to 1,2
                if t2s.get(tok, None) is not None:
                    if tp_set != src2targetspans[t2s.get(tok, None)[0]]:
                        return False

    return True


def remove_alignment(a, word_alignment, src_sentence=None, target_sentence=None):
    new_word_alignment = [p for p in word_alignment if p != a]
    return len(new_word_alignment), new_word_alignment  # score, alignment


def search_alignments(init_alignment, target_spans):
    accepted_alignments = []
    Q = []
    heappush(Q, (-len(init_alignment), init_alignment))  # len(A) is sub for score of an alignment which we want to max/minimize
    while len(Q) > 0:
        score_alignment, alignment = heappop(Q)
        if not check_alignment(alignment, target_spans):
            for a in alignment:
                score_new_alignment, new_alignment = remove_alignment(a, alignment)
                heappush(Q, (-score_new_alignment, new_alignment))
        else:
            accepted_alignments.append((score_alignment, alignment))
            break
    return accepted_alignments


def test():
    t_spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    w_aligns = [(2, 0), (1, 1), (4, 2), (4, 3), (4, 4)]
    assert check_alignment(w_aligns, t_spans) == True

    t_spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    w_aligns = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    assert check_alignment(w_aligns, t_spans) == False

    t_spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    w_aligns = [(2, 0), (3, 2), (4, 3), (4, 4)]
    assert check_alignment(w_aligns, t_spans) == False

    t_spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    w_aligns = [(2, 0), (3, 2), (4, 3)]
    assert check_alignment(w_aligns, t_spans) == False
    pass


if __name__ == '__main__':
    test()
    opt = OptionParser()
    opt.add_option("-a", dest="src_target_alignments", help="source-target alignments (of full sentences) from fast_align",
                   default="data/Little_Prince/zh-en.alignments")

    opt.add_option("-f", dest="amr_file", help="amr file with target phrases", default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned")
    opt.add_options("-l", dest="lex_file", help="lexical translation probs", default=)
    (options, args) = opt.parse_args()

    word_alignments = open(options.src_target_alignments, 'r').readlines()
    amrs = open(options.amr_file, 'r').read().split('\n\n')
    """
    for amr, word_alignment in zip(amrs, word_alignments):
        if amr.strip() != '':
            c = AMRMetadata(amr)
            c.parse_graph()
            # these are the alignments between the target and amr graph
            # sometimes there are no alignments that's why there is a default
            # of ''
            spans = c.attributes.get('alignments', '')
            #spans = [(int(t.split('-')[0]), t.split('|')[0]) for t in target_spans.strip().split()]
            check_alignment(word_alignment, spans)
    """

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    A = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    print search_alignments(A, spans)







