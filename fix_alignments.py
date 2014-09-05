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
from AMRMetadata import AMRMetadata
import pdb


def check_alignment(word_alignment, target_spans):
    word_alignment = word_alignment.strip()
    target_spans = target_spans.strip()
    # s2t.keys = token index in source
    # s2t.val = token index in target
    s2t = {}
    t2s = {}
    for st in word_alignment.strip().split():
        s, t = st.split('-')
        t_list = s2t.get(int(s), [])
        s_list = t2s.get(int(t), [])
        t_list.append(int(t))
        s_list.append(int(s))
        s2t[int(s)] = t_list
        t2s[int(t)] = s_list

    target_spans = [(int(t.split('-')[0]), t.split('|')[0]) for t in target_spans.split()]
    target_spans.sort()
    target_spans = [t[1] for t in target_spans]
    idxspans = [(idx, range(int(t.split('|')[0].split('-')[0]), int(t.split('|')[0].split('-')[1]))) for idx, t in enumerate(target_spans)]
    # target_token_to_span.keys  = token idx of target token
    # target_token_to_span.val = span idx to while the token belongs
    target_token_to_span = {}
    for idx, span in idxspans:
        for s in span:
            target_token_to_span[s] = idx

    source_token_to_span = {}
    for src in range(max(s2t) + 1):  # iterate over source tokens and assign their target phrase membership
        for t in s2t.get(src, []):
            if target_token_to_span.get(t) is not None:
                tp_set = source_token_to_span.get(src, set([]))
                tp_set.add(target_token_to_span.get(t))
                source_token_to_span[src] = tp_set
    print source_token_to_span
    for ts in target_spans:
        tokens = range(int(ts.split('-')[0]), int(ts.split('-')[1]))
        src = t2s.get(tokens[0], None)
        src = src[0]  # assuming model 1 style alignments TODO what about giza++ alignments??
        tp_set = source_token_to_span[src]
        for tok in tokens[1:]:
            # 3 should map to just 2
            # 4 shoudl map to 1,2
            if tp_set != source_token_to_span[t2s.get(tok, None)[0]]:
                return False

    return True


def remove_alignment(a, A):
    pass


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="src_target_alignments", help="source-target alignments (of full sentences) from fast_align",
                   default="data/Little_Prince/zh-en.alignments")

    opt.add_option("-f", dest="amr_file", help="amr file with target phrases", default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned")
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
            check_alignment(word_alignment, spans)
    """
    t_spans = "0-2|X 2-4|Y 4-5|Z"
    w_aligns = "2-0 1-1 3-2 4-3 4-4"
    assert check_alignment(w_aligns, t_spans) == False

    t_spans = "0-2|X 2-4|Y 4-5|Z"
    w_aligns = "2-0 1-1 4-2 4-3 4-4"
    assert check_alignment(w_aligns, t_spans) == True





