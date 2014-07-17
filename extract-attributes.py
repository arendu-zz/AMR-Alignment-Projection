__author__ = 'arenduchintala'
import sys
from optparse import OptionParser
from AMRMetadata import AMRMetadata

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-f", dest="amr_file", help="AMR File with alignments", default="data/Little_Prince/test.aligned")
    opt.add_option("-a", dest="attribute2extract", help="name of the attribute to extract from amr file", default="tok")
    (options, args) = opt.parse_args()
    for item in open(options.amr_file, 'r').read().split('\n\n'):
        if item.strip() != '':
            c = AMRMetadata(item)
            attr = c.attributes[options.attribute2extract]
            sys.stdout.write(str(attr) + '\n')