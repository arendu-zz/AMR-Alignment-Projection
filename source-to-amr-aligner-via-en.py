__author__ = 'arenduchintala'

from optparse import OptionParser
from AMRMetadata import AMRMetadata
from pprint import pprint

global verbose
verbose = False

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="source_en_alignments", help="source-caveman alignments from fast_align",
                   default="data/Little_Prince/zh-en.alignments")

    opt.add_option("-f", dest="amr_file", help="AMR File with alignments with caveman alignments",
                   default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned")
    (options, args) = opt.parse_args()

    source_to_en_alignment = open(options.source_en_alignments, 'r').readlines()
    source = []
    en = []  # target
    for src_tar in open(options.parallel_corp, 'r').readlines():
        src, tar = src_tar.split(' ||| ')
        source.append(src.strip())
        en.append(tar.strip())

    metadata = []
    en_to_amr_alignments = []
    for item in open(options.amr_file, 'r').read().split('\n\n'):
        if item.strip() != '':
            c = AMRMetadata(item)
            metadata.append(c)
            e2a = c.attributes['alignments']
            en_to_amr_alignments.append(e2a)

    for idx, (s2e, e2a) in enumerate(zip(source_to_en_alignment, en_to_amr_alignments)):
        # make a dictionary of caveman tokens as keys and source tokens (via alignment) as values
        e2src = dict((int(g.split('-')[1]), str(int(g.split('-')[0])) + '-' + str(int(g.split('-')[0]) + 1)) for g in
                     [x for x in s2e.split()])
        source2amr = {}
        if verbose:
            print en[idx]
            print source[idx]
            print'source-to-caveman alignment (caveman : source-range)'
            pprint(e2src)
            print 'caveman-to-amr alignment'

        for s in e2a.split():
            r = s.split('|')[0]
            caveman_indexes = range(int(r.split('-')[0]), int(r.split('-')[1]))  # all indexes in range
            # this range will mostly just span 1
            amr_paths = s.split('|')[1]  # we don't touch this - this part looks like 0.0.1+0.0.0.1 etc
            for c in caveman_indexes:
                if c in e2src:
                    if e2src[c] in source2amr:
                        source2amr[e2src[c]] = source2amr[e2src[c]] + '+' + amr_paths
                    else:
                        source2amr[e2src[c]] = amr_paths
                else:
                    if verbose:
                        print c, 'is not in ', e2src
        s2a = [str(x) + '|' + str(y) for x, y in source2amr.items()]
        s2a = ' '.join(s2a)
        metadata[idx].add_attribute('alignments', s2a)
        metadata[idx].add_attribute('tok', source[idx])
        metadata[idx].remove_attribute('caveman_string')
        metadata[idx].remove_attribute('caveman_alignment')
        print str(metadata[idx])



