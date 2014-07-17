__author__ = 'arenduchintala'
import sys
from optparse import OptionParser
from AMRMetadata import AMRMetadata

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-f", dest="attribute_file", help="a file with some attribute (single attribute per line)", )
    opt.add_option("-a", dest="amr_file", help="the amr file that is going to accept the new attribute",
                   default="data/Little_Prince/test.aligned")
    opt.add_option("-n", dest="attribute_name", help="name of the attribute that is being added")
    (options, args) = opt.parse_args()
    for item, attr in zip(open(options.amr_file, 'r').read().split('\n\n'),
                          open(options.attribute_file, 'r').readlines()):
        if item.strip() != '':
            c = AMRMetadata(item)
            c.add_attribute(options.attribute_name, attr.strip())
            sys.stdout.write(str(c) + '\n')