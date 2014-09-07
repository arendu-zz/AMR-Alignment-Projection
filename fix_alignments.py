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
import heapq
from pprint import pprint
from heapq import heappop, heappush
from AMRMetadata import AMRMetadata


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

    span_error = [False] * len(target_spans)
    for ts_id, ts in enumerate(target_spans):
        tokens = range(ts[0], ts[1])
        src = []
        for t in tokens:
            if t2s.get(t, None) is not None:
                src += t2s[t]

        if len(src) == 0:
            span_error[ts_id] = True  # all alignments from a target phrase have been lost
        else:
            tp_set = src2targetspans[src[0]]
            for s in range(min(src), max(src) + 1):
                if s in src2targetspans and tp_set != src2targetspans[s]:
                    span_error[ts_id] = True
            """
            s = src[0]  # assuming model 1 style alignments TODO what about giza++ alignments??
            tp_set = src2targetspans[s]
            for tok in tokens[1:]:
                # 3 should map to just 2
                # 4 shoudl map to 1,2
                if t2s.get(tok, None) is not None:
                    if tp_set != src2targetspans[t2s.get(tok, None)[0]]:
                        span_error[ts_id] = True
            """

    alignment_error = [False] * len(word_alignment)
    for ts_id, (ts, se) in enumerate(zip(target_spans, span_error)):
        tokens = range(ts[0], ts[1])
        for t in tokens:
            if t in t2s:
                srcs = t2s[t]
                for s in srcs:
                    alignment_error[word_alignment.index((s, t,))] = se

    return alignment_error, span_error


def remove_alignment(a, word_alignment, word_alignment_score):
    new_word_alignment_score = [s for i, s in enumerate(word_alignment_score) if i != word_alignment.index(a)]
    new_word_alignment = [p for i, p in enumerate(word_alignment) if a != p]
    return sum(new_word_alignment_score), new_word_alignment_score, new_word_alignment  # score, alignment


def search_alignments(init_alignment, init_alignment_score, target_spans):
    ini_alignment_chk, init_chk_span = check_alignment(init_alignment, target_spans)
    accepted_alignments = []
    Q = []
    heappush(Q, (-len(init_alignment), sum(init_alignment_score), init_alignment_score, init_alignment))  # len(A) is sub for score of an alignment which we
    # want to
    # max/minimize
    # heapq._heapify_max(Q)
    while len(Q) > 0:
        len_alignment, total_score, score_alignment, alignment = heappop(Q)
        chk_word_align, chk_spans = check_alignment(alignment, target_spans)
        if True in chk_word_align or sum(chk_spans) > sum(init_chk_span):
            for a, chk in zip(alignment, chk_word_align):
                if chk:
                    total_new_score, score_new_alignment, new_alignment = remove_alignment(a, alignment, score_alignment)
                    heappush(Q, (-len(new_alignment), total_new_score, score_new_alignment, new_alignment))
        else:
            accepted_alignments.append((len_alignment, total_score, score_alignment, alignment))
            # return (len_alignment, total_score, score_alignment, alignment)
            break
    return accepted_alignments


def format_spans(span_str):
    span_str = [((int(s.split('|')[0].split('-')[0]), int(s.split('|')[0].split('-')[1])), s.split('|')[1]) for s in span_str.split()]
    return span_str


def format_alignment(alignment_str, src_sentence, target_sentence, lexp):
    fmt_alignment = []
    fmt_scores = []
    for a in alignment_str.split():
        i, j = a.split('-')
        src_i = src_sentence[int(i)]
        target_j = target_sentence[int(j)]
        score = -lexp.get((src_i, target_j), float('-inf'))
        fmt_alignment.append((int(i), int(j)))
        fmt_scores.append(score)
    return fmt_alignment, fmt_scores


def test():
    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    A = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    As = [5, 2, 3, 1, 6]
    assert search_alignments(A, As, spans) == [(-4, 14, [5, 2, 1, 6], [(2, 0), (1, 1), (4, 3), (4, 4)])]

    t_spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    w_aligns = [(0, 0), (2, 1), (4, 2), (1, 3), (4, 4)]
    As = [1, 2, 4, 1, 3]
    a = search_alignments(w_aligns, As, t_spans)
    assert a == [(-4, 10, [1, 2, 4, 3], [(0, 0), (2, 1), (4, 2), (4, 4)])]

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    A = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    As = [5, 2, 3, 1, 6]
    assert search_alignments(A, As, spans) == [(-4, 14, [5, 2, 1, 6], [(2, 0), (1, 1), (4, 3), (4, 4)])]

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    A = [(2, 0), (1, 1), (3, 2)]
    As = [5, 2, 3]
    assert search_alignments(A, As, spans) == [(-3, 10, [5, 2, 3], [(2, 0), (1, 1), (3, 2)])]

    spans = [((0, 2), "X"), ((2, 4), "W"), ((4, 5), "F")]
    A = [(0, 0), (2, 1), (1, 2), (4, 3)]
    As = [1, 2, 3, 4]
    assert search_alignments(A, As, spans) == [(-3, 7, [1, 2, 4], [(0, 0), (2, 1), (4, 3)])]

    spans = [((0, 2), "X"), ((2, 4), "W"), ((4, 5), "F")]
    A = [(0, 0), (2, 1), (1, 2), (4, 3)]
    As = [1, 2, 3, 4]
    assert search_alignments(A, As, spans) == [(-3, 7, [1, 2, 4], [(0, 0), (2, 1), (4, 3)])]

    t_spans = [((3, 4), '0.0'), ((4, 5), '0')]
    w_aligns = [(3, 0), (1, 1), (1, 2), (1, 4), (2, 5), (3, 6)]
    As = [1, 2, 4, 1, 3, 1]
    assert search_alignments(w_aligns, As, t_spans) == [(-6, 12, [1, 2, 4, 1, 3, 1], [(3, 0), (1, 1), (1, 2), (1, 4), (2, 5), (3, 6)])]

    pass


if __name__ == '__main__':
    test()
    opt = OptionParser()
    opt.add_option("-a", dest="src_target_alignments", help="source-target alignments (of full sentences) from fast_align",
                   default="data/Little_Prince/zh-en.alignments")
    opt.add_option("-e", dest="target_segmented", help="text file with target sentence per line", default="data/Little_Prince/train.en")
    opt.add_option("-f", dest="src_segmented", help="text file with source sentences per line", default="data/Little_Prince/train.zh")
    opt.add_option("-l", dest="lex_probs", help="lexical translation probabilities", default="data/Little_Prince/zh-en.lex")
    opt.add_option("-r", dest="amr_file", help="amr file with target phrases", default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned")
    (options, args) = opt.parse_args()
    lex = dict(((l.split()[0], l.split()[1]), float(l.split()[2]) ) for l in open(options.lex_probs, 'r').readlines())
    word_alignments = open(options.src_target_alignments, 'r').readlines()
    en = open(options.target_segmented, 'r').readlines()
    zh = open(options.src_segmented, 'r').readlines()
    amrs = open(options.amr_file, 'r').read().split('\n\n')

    for amr, wa, z, e in zip(amrs, word_alignments, zh, en):
        if amr.strip() != '' and z.strip() != '' and e.strip() != '' and wa.strip() != '':
            c = AMRMetadata(amr)
            c.parse_graph()
            span_str = c.attributes.get('alignments', '')
            fmt_span = format_spans(span_str)
            fmt_alignment, fmt_scores = format_alignment(wa, z.strip().split(), e.strip().split(), lex)
            f = search_alignments(fmt_alignment, fmt_scores, fmt_span)
            if len(f) == 0:
                print z
                print e
                print 'spans', fmt_span
                print 'alignment', len(fmt_alignment), fmt_alignment
                print wa
                print 'scores', fmt_scores
                print 'fixed', f
                print 'ok'

            if -f[0][0] != len(fmt_alignment):
                print 'spans', fmt_span
                print 'alignment  :', fmt_alignment
                print 'f alignment:', f[0][3]
                print 'scores     :', fmt_scores
                print 'fixed score:', f[0][2]
                print 'ok'



