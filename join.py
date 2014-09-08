__author__ = 'arenduchintala'
from optparse import OptionParser

"""
because sed s/\t/ ||| /g' is doing something funny
"""

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option("-z", dest="zh_file", help="zh file", default="data/Little_Prince/zh.segmented")
    opt.add_option("-c", dest="en_file", help="en file", default="data/Little_Prince/caveman.segmented")
    (options, args) = opt.parse_args()
    for z, c in zip(open(options.zh_file, 'r').readlines(), open(options.en_file, 'r').readlines()):
        print z.strip() + ' ||| ' + c.strip()