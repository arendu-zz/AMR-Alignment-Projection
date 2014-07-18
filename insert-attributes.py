__author__ = 'arenduchintala'
import sys
from optparse import OptionParser
from AMRMetadata import AMRMetadata

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-f", dest="attribute_files", help="files with some attribute (single attribute per line) comma "
                                                      "seperated if multiple files", )
    opt.add_option("-a", dest="amr_file", help="the amr file that is going to accept the new attribute",
                   default="data/Little_Prince/test.aligned")
    opt.add_option("-n", dest="attribute_names", help="name of the attribute that is being added, comma seperated for "
                                                      "multiple attributes")
    (options, args) = opt.parse_args()
    attr_files = options.attribute_files.split(',')
    attr_list = []
    attr_names = options.attribute_names.split(',')
    for af in attr_files:
        attr_list.append(open(af.strip(), 'r').readlines())

    for idx, item in enumerate(open(options.amr_file, 'r').read().split('\n\n')):
        if item.strip() != '':
            c = AMRMetadata(item)
            for al, an in zip(attr_list, attr_names):
                attr = al[idx]
                c.add_attribute(an, attr.strip())
            sys.stdout.write(str(c) + '\n')