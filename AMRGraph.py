__author__ = 'arenduchintala'
import re
from collections import defaultdict

global RE_ENTERENCY, ROOT, POLARITY, NUMERICAL_QUANT, NON_REFERENTIAL_ITEMS
RE_ENTERENCY = 'RE-ENTERENCY'
ROOT = 'ROOT'
POLARITY = 'POLARITY'
NUMERICAL_QUANT = 'NUMERICAL_QUANT'
NON_REFERENTIAL_ITEMS = ['-', 'interrogative', 'imperative', 'expressive']


class Node():  # not used at the moment
    def __init__(self, edge_label, concept_label, parent=None):
        self.edge_label = edge_label
        self.concept_label = concept_label
        self.children = []  # list of nodes
        self.parent = parent

    def add_child(self, node):
        self.children.append(node)

    def __str__(self):
        s = '(' + self.edge_label + ' ' + self.concept_label + ' '
        for n in self.children:
            s += str(n)
        s += ')'
        return s


class AMRGraph():
    def __init__(self):
        self.stack_nodes = []
        self.stack_edges = [ROOT]
        self.roots = []
        self.nodes_to_concepts = {}
        self.nodes_to_parents = defaultdict(list)
        self.nodes_to_children = defaultdict(list)

    def parse_string(self, s):
        self.clear()
        s = self.fix_graph_string(s)
        self.parse_bracketed_list(s)

    def clear(self):
        self.stack_nodes = []
        self.roots = []
        self.stack_edges = [ROOT]
        self.nodes_to_concepts = {}
        self.nodes_to_parents = defaultdict(list)
        self.nodes_to_children = defaultdict(list)

    def flatten(self, foo):
        for x in foo:
            if hasattr(x, '__iter__'):
                for y in self.flatten(x):
                    yield y
            else:
                yield x

    def make_segment_proper(self, x):
        if len(re.split('(\\s:[a-zA-Z0-9\-]+\s)', x)) > 2:
            parts = [p.strip() for p in re.split('(\\s:[a-zA-Z0-9\-]+\s)', x) if p.strip() != '']
            for idx, p in enumerate(parts):
                if str(p).startswith(':'):
                    try:
                        parts[idx + 1] = '( ' + parts[idx + 1] + ' )'
                    except IndexError:
                        pass  # this error can be ignored its trying to fix a part that dosent exist
            index_to_join = []
            mod_parts = []
            for idx, p in enumerate(parts):
                if str(p).startswith(':') and not str(parts[idx - 1]).endswith(')') and len(p.split()) > 1:
                    index_to_join.append((idx, idx - 1))
                    mp = parts[idx - 1] + ' ' + p
                    try:
                        mod_parts.pop()
                    except IndexError:
                        pass  # this happens when we join items at
                    mod_parts.append(mp)
                else:
                    mod_parts.append(p.strip())
            return mod_parts
        else:
            return x  # no need to modify this term

    def append_stacks(self, nv, e2c):
        if nv is not None:
            self.stack_nodes.append(nv)

        if e2c is not None:
            self.stack_edges.append(e2c)

    def fix_graph_string(self, s):  # this is a hack
        s = re.split('(\()|(\))', s)
        s = [self.make_segment_proper(' ' + x.strip() + ' ') for x in s if x != '' and x is not None]
        s = list(self.flatten(s))
        s = ' '.join(s)
        s = re.split('(\()|(\))', s)
        s = [x.strip() for x in s if x is not None and x.strip() != '']
        return s

    def check_label_exceptions(self, e2c):
        a = False
        # a += e2c == POLARITY
        # a += e2c == NUMERICAL_QUANT
        a += e2c == RE_ENTERENCY
        return a

    def parse_bracketed_list(self, s):
        i = 0
        while i < len(s):
            if s[i] == '(':
                e4p = self.stack_edges.pop()
                nv, nc, e2c = self.parse_term(s[i + 1])

                if e4p == ROOT:
                    self.roots.append(nv)
                else:
                    p = self.stack_nodes[-1]
                    if self.check_label_exceptions(e2c):
                        self.nodes_to_children[p].append((e2c, e4p, nv))
                        self.nodes_to_parents[nv].append((e2c, e4p, p))
                    else:
                        self.nodes_to_children[p].append((e4p, nv))
                        self.nodes_to_parents[nv].append((e4p, p))

                self.append_stacks(nv, e2c)
                i += 2  # move 2 steps forward

            elif s[i] == ')':
                self.stack_nodes.pop()
                i += 1

            else:
                nv, nc, e2c = self.parse_term(s[i])
                self.append_stacks(nv, e2c)
                i += 1
        return self


    def get_concept(self, sequence):
        """
        path is a sequence of children to take and arrive at the destination node
        eg. 0,1,1,3 is a path to take root r-> child 1 c1-> child 1 c2-> child 3 c3
        then return c3
        """
        sequence.pop(0)
        node_label = self.roots[0]
        while len(sequence) > 0:
            branch = int(sequence.pop(0))
            node_labels = []
            for x in self.nodes_to_children[node_label]:
                if x[0] == RE_ENTERENCY:
                    if x[-1] in self.nodes_to_concepts:
                        pass  # 'this is a re-enterency so we skip this
                    else:
                        pass  # this is a weird case!
                else:
                    node_labels.append(x[-1])  # the last item in the tuple is the node variable
            node_label = node_labels[branch]
        try:
            concept = self.nodes_to_concepts[node_label]
        except KeyError:
            concept = node_label  # this is weird as hell
        return concept


    def parse_term(self, term):

        n_variable, n_concept, edge_term = None, None, None
        try:
            node_term, edge_term = re.split('^:|\s:', term)  # term.split(':')
        except ValueError:
            node_term, edge_term = term, None

        if node_term.strip() != '':
            ns = node_term.split('/')
            n_variable = ns[0].strip()
            if len(ns) == 2:
                n_concept = ns[1].strip()
            else:
                if '"' in ns[0]:
                    # print 'const', ns[0]
                    n_variable = ns[0]
                    n_concept = ns[0][1:-1]
                else:
                    # print 'might be re-enterence', ns[0]
                    # TODO check variable type if it is pure number or a symbol like '+/-' then its not a RE-Enterency
                    try:
                        float(ns[0])
                        n_variable = ns[0]
                        # edge_term = NUMERICAL_QUANT
                    except ValueError:
                        if ns[0].strip() in NON_REFERENTIAL_ITEMS:
                            n_variable = ns[0]
                            # edge_term = POLARITY
                        else:
                            n_variable = ns[0]
                            edge_term = RE_ENTERENCY

            if n_concept is not None:
                self.nodes_to_concepts[n_variable] = n_concept
        # edge_term is actually a edge waiting for a child
        return n_variable, n_concept, edge_term


if __name__ == '__main__':
    s = '(a  /  and  :op2  (r  /  repeat-01  :ARG0  (h  /  he)  :ARG1  (d  /  draw-01  :mode  imperative  :ARG0  (y2  /  you)  :ARG1  (s3  /  sheep)  :ARG2  (i  /  i)  :condition  (p  /  please-01  :ARG1  (y  /  you)))  :purpose  (a2  /  answer-01  :ARG0  h)  :manner  (s  /  slow  :degree  (v  /  very))  :conj-as-if  (s2  /  speak-01  :ARG0  h  :ARG1  (m  /  matter  :consist-of  (c  /  consequence  :degree  (g  /  great))))))  '
    b = AMRGraph()
    b.parse_string(s)
    assert b.get_concept('0.0.1.4'.split('.')) == 'please-01'

    s = '(s / see-01 :ARG0 (i / i) :ARG1 (p / picture :mod (m / magnificent) :location (b2 / book :name (n / name ' \
        ':op1 "True" :op2 "Stories" :op3 "from" :op4 "Nature") :topic (f / forest :mod (p2 / primeval)))) :mod (o / once) :time (a / age-01 :ARG1 i :ARG2 (t / temporal-quantity :quant 6 :unit (y / year))))'
    b = AMRGraph()
    b.parse_string(s)
    assert b.get_concept('0.3.0.1'.split('.')) == 'year'
    assert b.get_concept('0.1.1.0.0'.split('.')) == 'True'

    s = '(p  /  possible  :domain  (g  /  go-02  :ARG0  y  :ARG3  (d  /  date-entity  :time  "12:00")  :ARG4  (s  /  sunset)  :manner  (s2  /  straight))  :condition  (p2  /  possible  :domain  (f  /  fly-01  :ARG1  (y  /  you)  :duration  (t  /  temporal-quantity  :quant  1  :unit  (m  /  minute))  :destination  (c  /  country  :name  (n  /  name  :op1  "France")))))'
    x = AMRGraph()
    x.parse_string(s)
    assert x.get_concept('0.0.1'.split('.')) == 'sunset'

    s = '(t  /  try-01  :ARG0  (i  /  i)  :ARG1  (e  /  experiment-01  :ARG1  (s  /  show-01  :ARG1  (p2  /  picture  :name  (n  /  name  :op1  "Drawing"  :op2  "Number"  :op3  "One"))  :ARG2  p  :ARG1-of  (k  /  keep-01  :ARG0  i  :time  (a  /  always))))  :time  (m  /  meet-02  :ARG0  i  :ARG1  (p  /  person  :ARG1-of  (i2  /  include-91  :ARG2  (t3  /  they))  :ARG0-of  (s3  /  see-01  :manner  (c2  /  clear)  :ARG1-of  (s4  /  seem-01  :ARG2  i)))))'
    x = AMRGraph()
    x.parse_string(s)
    assert x.get_concept('0.2.0.1.0'.split('.')) == 'clear'

    s = '(a  /  and  :op1  (u  /  understand-01  :polarity  -  :ARG0  (g  /  grown-up)  :ARG1  (a3  /  anything)  :time  (e2  /  ever)  :prep-by  g)  :op2  (t  /  tiresome  :domain  (e  /  explain-01  :ARG0  (c  /  child)  :ARG1  (t2  /  thing)  :ARG2  g  :time  (a4  /  always)  :mod  (f  /  forever))))'
    d = AMRGraph()
    d.parse_string(s)
    assert d.get_concept('0.1.0.3'.split('.')) == 'forever'

    s = '(c / chapter :mod 1)'
    c = AMRGraph()
    c.parse_string(s)
    assert c.get_concept('0.0'.split('.')) == '1'

    s = '(a / and :op1 (p / possible :polarity - :domain (m / move-01 :ARG0 (t / they) :time (a2 / after :op1 (t3 / that)))) :op2 (s / sleep-01 :ARG0 t :duration (t2 / temporal-quantity :quant 6 :unit (m2 / month) :ARG1-of (n / need-01 :ARG0 t :purpose (d / digest-01 :ARG0 t)))))'
    a = AMRGraph()
    a.parse_string(s)
    assert a.get_concept([0, 1, 0, 2]) == 'need-01'
