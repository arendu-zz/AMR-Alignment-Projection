__author__ = 'arenduchintala'

from optparse import OptionParser
from AMRMetadata import AMRMetadata
from pprint import pprint

global verbose
verbose = False

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-a", dest="source_caveman_alignments", help="source-caveman alignments from fast_align",
                   default="data/Little_Prince/zh-caveman.alignments")
    opt.add_option("-c", dest="parallel_corp", help="parallel corpus that was used by fast align",
                   default="data/Little_Prince/zh-caveman")
    opt.add_option("-f", dest="amr_file", help="AMR File with alignments with caveman alignments",
                   default="data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned.caveman")
    (options, args) = opt.parse_args()

    pc = open(options.parallel_corp, 'r').readlines()
    source_to_caveman_alignment = open(options.source_caveman_alignments, 'r').readlines()
    source = []
    caveman = []  # target
    for src_tar in open(options.parallel_corp, 'r').readlines():
        src, tar = src_tar.split(' ||| ')
        source.append(src.strip())
        caveman.append(tar.strip())

    metadata = []
    caveman_to_amr_alignments = []
    for item in open(options.amr_file, 'r').read().split('\n\n'):
        if item.strip() != '':
            c = AMRMetadata(item)
            metadata.append(c)
            c2a = c.attributes['caveman_alignment']
            caveman_to_amr_alignments.append(c2a)

    for idx, (s2c, c2a) in enumerate(zip(source_to_caveman_alignment, caveman_to_amr_alignments)):
        # make a dictionary of caveman tokens as keys and source tokens (via alignment) as values
        c2src = dict((int(g.split('-')[1]), str(int(g.split('-')[0])) + '-' + str(int(g.split('-')[0]) + 1)) for g in
                     [x for x in s2c.split()])
        source2amr = {}
        if verbose:
            print caveman[idx]
            print source[idx]
            print'source-to-caveman alignment (caveman : source-range)'
            pprint(c2src)
            print 'caveman-to-amr alignment'

        for s in c2a.split():
            r = s.split('|')[0]
            caveman_indexes = range(int(r.split('-')[0]), int(r.split('-')[1]))  # all indexes in range
            # this range will mostly just span 1
            amr_paths = s.split('|')[1]  # we don't touch this - this part looks like 0.0.1+0.0.0.1 etc
            for c in caveman_indexes:
                if c in c2src:
                    if c2src[c] in source2amr:
                        source2amr[c2src[c]] = source2amr[c2src[c]] + '+' + amr_paths
                    else:
                        source2amr[c2src[c]] = amr_paths
                else:
                    if verbose:
                        print c, 'is not in ', c2src
        s2a = [str(x) + '|' + str(y) for x, y in source2amr.items()]
        s2a = ' '.join(s2a)
        metadata[idx].add_attribute('alignments', s2a)
        metadata[idx].add_attribute('tok', source[idx])
        metadata[idx].remove_attribute('caveman_string')
        metadata[idx].remove_attribute('caveman_alignment')
        print str(metadata[idx])



