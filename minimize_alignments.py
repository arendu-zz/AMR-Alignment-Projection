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

    return alignment_error, span_error, src2targetspans


def remove_alignment(a, word_alignment, word_alignment_score):
    new_word_alignment_score = [s for i, s in enumerate(word_alignment_score) if i != word_alignment.index(a)]
    new_word_alignment = [p for i, p in enumerate(word_alignment) if a != p]
    return sum(new_word_alignment_score), new_word_alignment_score, new_word_alignment  # score, alignment


def search_alignments(init_alignment, init_alignment_score, target_spans):
    ini_alignment_chk, init_chk_span, ignore = check_alignment(init_alignment, target_spans)
    accepted_alignments = []
    Q = []
    heappush(Q, (-len(init_alignment), sum(init_alignment_score), init_alignment_score,
                 init_alignment))  # len(A) is sub for score of an alignment which we
    # want to
    # max/minimize
    # heapq._heapify_max(Q)
    while len(Q) > 0:
        len_alignment, total_score, score_alignment, alignment = heappop(Q)
        chk_word_align, chk_spans, ignore = check_alignment(alignment, target_spans)
        if (True in chk_word_align or sum(chk_spans) > sum(init_chk_span)) and (len(Q) < 100000):
            for a, chk in zip(alignment, chk_word_align):
                if chk:
                    # print 'trying to remove ', a
                    total_new_score, score_new_alignment, new_alignment = remove_alignment(a, alignment,
                                                                                           score_alignment)
                    cws, cs, s2ts = check_alignment(new_alignment, target_spans)
                    if sum(cs) > sum(init_chk_span):
                        pass  # print 'hmm this is a problem'
                    else:
                        heappush(Q, (-len(new_alignment), total_new_score, score_new_alignment, new_alignment))
        else:
            accepted_alignments.append((len_alignment, total_score, score_alignment, alignment))
            # return (len_alignment, total_score, score_alignment, alignment)
            break
    return accepted_alignments


def format_spans(span_str):
    span_str = [(int(s.split('|')[0].split('-')[0]), int(s.split('|')[0].split('-')[1])) for s in span_str.split()]
    span_str.sort()
    target_tokens = []
    for s, e in span_str:
        target_tokens += range(s, e)
    return span_str, target_tokens


def check_input_spans(target_tokens):
    # if there is overlap here, then we are not going to get a solution
    # if there is no overlap here, then there should not be any duplicates in the target_tokens
    return len(target_tokens) == len(set(target_tokens))


def format_alignment(alignment_str, target_tokens, src_sentence, target_sentence, lexp):
    fmt_alignment = []
    fmt_scores = []
    for a in alignment_str.split():
        i, j = a.split('-')
        if int(j) in target_tokens:
            fmt_alignment.append((int(i), int(j)))
        else:
            pass  # this alignment is not important it simply adds to the complexity of the alg

        if lexp is None:
            fmt_scores.append(1)
        else:
            src_i = src_sentence[int(i)]
            target_j = target_sentence[int(j)]
            score = -lexp.get((src_i, target_j), float('-inf'))
            fmt_scores.append(score)
    return fmt_alignment, fmt_scores


def test():
    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    spans = [s[0] for s in spans]
    A = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    As = [5, 2, 3, 1, 6]
    assert search_alignments(A, As, spans) == [(-4, 14, [5, 2, 1, 6], [(2, 0), (1, 1), (4, 3), (4, 4)])]

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    spans = [s[0] for s in spans]
    w_aligns = [(0, 0), (2, 1), (4, 2), (1, 3), (4, 4)]
    As = [1, 2, 4, 1, 3]
    a = search_alignments(w_aligns, As, spans)
    assert a == [(-4, 10, [1, 2, 4, 3], [(0, 0), (2, 1), (4, 2), (4, 4)])]

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    spans = [s[0] for s in spans]
    A = [(2, 0), (1, 1), (3, 2), (4, 3), (4, 4)]
    As = [5, 2, 3, 1, 6]
    assert search_alignments(A, As, spans) == [(-4, 14, [5, 2, 1, 6], [(2, 0), (1, 1), (4, 3), (4, 4)])]

    spans = [((0, 2), "X"), ((2, 4), "Y"), ((4, 5), "Z")]
    spans = [s[0] for s in spans]
    A = [(2, 0), (1, 1), (3, 2)]
    As = [5, 2, 3]
    assert search_alignments(A, As, spans) == [(-3, 10, [5, 2, 3], [(2, 0), (1, 1), (3, 2)])]

    spans = [((0, 2), "X"), ((2, 4), "W"), ((4, 5), "F")]
    spans = [s[0] for s in spans]
    A = [(0, 0), (2, 1), (1, 2), (4, 3)]
    As = [1, 2, 3, 4]
    assert search_alignments(A, As, spans) == [(-3, 7, [1, 2, 4], [(0, 0), (2, 1), (4, 3)])]

    spans = [((0, 2), "X"), ((2, 4), "W"), ((4, 5), "F")]
    spans = [s[0] for s in spans]
    A = [(0, 0), (2, 1), (1, 2), (4, 3)]
    As = [1, 2, 3, 4]
    assert search_alignments(A, As, spans) == [(-3, 7, [1, 2, 4], [(0, 0), (2, 1), (4, 3)])]

    spans = [((3, 4), '0.0'), ((4, 5), '0')]
    spans = [s[0] for s in spans]
    w_aligns = [(3, 0), (1, 1), (1, 2), (1, 4), (2, 5), (3, 6)]
    As = [1, 2, 4, 1, 3, 1]
    assert search_alignments(w_aligns, As, spans) == [
        (-6, 12, [1, 2, 4, 1, 3, 1], [(3, 0), (1, 1), (1, 2), (1, 4), (2, 5), (3, 6)])]

    pass


if __name__ == '__main__':
    test()
    opt = OptionParser()
    opt.add_option("-a", dest="src_target_alignments",
                   help="source-target alignments (of full sentences) from fast_align",
                   default="data/Little_Prince/zh-en.alignments")
    opt.add_option("-e", dest="target_segmented", help="text file with target sentence per line",
                   default="data/Little_Prince/train.en")
    opt.add_option("-f", dest="src_segmented", help="text file with source sentences per line",
                   default="data/Little_Prince/train.zh")
    opt.add_option("-l", dest="lex_probs", help="lexical translation probabilities",
                   default="data/Little_Prince/zh-en.lex")
    opt.add_option("-r", dest="amr_file", help="amr file with target phrases",
                   default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned")
    opt.add_option("-g", dest="log_file", help="where to save log file", default="")
    (options, args) = opt.parse_args()
    lex = dict(((l.split()[0], l.split()[1]), float(l.split()[2]) ) for l in open(options.lex_probs, 'r').readlines())
    word_alignments = open(options.src_target_alignments, 'r').readlines()
    en = open(options.target_segmented, 'r').readlines()
    zh = open(options.src_segmented, 'r').readlines()
    amrs = open(options.amr_file, 'r').read().split('\n\n')
    log_txt = ""
    l = 0
    msg = ""
    for amr, wa, z, e in zip(amrs, word_alignments, zh, en):
        l += 1
        msg = ""
        if amr.strip() != '':
            c = AMRMetadata(amr)
            c.parse_graph()
            span_str = c.attributes.get('alignments', '')
            if z.strip() != '' and e.strip() != '' and wa.strip() != '' and span_str != '':
                fmt_span, target_tokens = format_spans(span_str)
                fmt_alignment, fmt_scores = format_alignment(wa, target_tokens, z.strip().split(), e.strip().split(),
                                                             lex)
                if check_input_spans(target_tokens) and len(fmt_alignment) > 0:
                    f = search_alignments(fmt_alignment, fmt_scores, fmt_span)
                    fixed_alignment = [str(a[0]) + '-' + str(a[1]) for a in f[0][3]]
                    final_alignment = ' '.join(fixed_alignment)
                    print final_alignment
                    msg = str(len(fmt_alignment)) + "\t" + str(len(fixed_alignment))
                else:
                    final_alignment = ' '.join([str(a[0]) + '-' + str(a[1]) for a in fmt_alignment])
                    print final_alignment
                    msg = "target spans have overlap or no alignments exist for target spans"
            else:
                msg = "empty target or source or amr or alignments"
                print wa.strip()
        if options.log_file != '':
            log_txt = log_txt + str(l) + "\t" + msg + "\n"
    if options.log_file != '':
        log_file = open(options.log_file, 'w')
        log_file.write(log_txt)
        log_file.flush()
        log_file.close()

    """
    span_str = "18-19|0.0.0.0.0.0.1 0-1|0.0.0.0 38-39|0.1.1.0+0.1.1 17-18|0.0.0.0.0.0.1.0 24-25|0.0.2.1 25-26|0.0.2 3-4|0.0.0 26-27|0.1.0 37-38|0.1.1.0.1 7-8|0.0.0.0.0.0+0.0.0.0.0.0.1.0.0.0.1.0+0.0.0.0.0.0.1.0.0.0.1+0.0.0.0.0.0.1.0.0.0+0.1+0.0.1 19-20|0.0.0.0.0.0.1.0.0.0.0.0+0.0.0.0.0.0.1.0.0.0.0+0.0.2.0+0.0.2.0.0 16-17|0.0.0.0.0.0.1.0.0 20-21|0.0 6-7|0 33-34|0.1.1.0.0 16-23|0.1.0.0.0.0+0.1.0.0.0.1+0.1.0.0.0+0.1.0.0 1-2|0.0.0.0.0.1+0.0.0.0.0 4-5|0.0.0.0.0.0.0"
    w_align = "3-0 0-1 28-2 1-3 1-4 4-5 7-6 5-7 9-8 7-9 7-10 7-11 9-12 12-13 6-14 10-15 18-16 17-17 18-18 18-19 18-20 16-21 16-22 17-23 15-24 19-25 19-26 15-27 7-28 2-29 20-30 6-31 6-32 24-33 25-34 25-35 35-36 26-37 18-38 18-39 16-40 22-41 7-42 7-43 38-44 38-45 15-46 35-47 35-48 7-49 37-50 33-51 18-52 33-53 18-54 29-55 19-56 19-57 39-58 29-59"
    fmt_span, target_tokens = format_spans(span_str)
    fmt_alignment, fmt_scores = format_alignment(w_align, target_tokens, None, None, None)
    if check_input_spans(target_tokens):
        f = search_alignments(fmt_alignment, fmt_scores, fmt_span)
        fixed_alignment = [str(a[0]) + '-' + str(a[1]) for a in f[0][3]]
        fixed_alignment = ' '.join(fixed_alignment)
    else:
        print 'bail'
        fixed_alignment = ' '.join([str(a[0]) + '-' + str(a[1]) for a in fmt_alignment])
        print fixed_alignment
    """




