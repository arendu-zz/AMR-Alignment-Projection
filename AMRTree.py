__author__ = 'arenduchintala'
import re
from pprint import pprint

global RE_ENTERENCY, ROOT
RE_ENTERENCY = 'RE-ENTERENCY'
ROOT = 'ROOT'


class Node():
    def __init__(self, concept, concept_label, parent):
        self.concept = concept
        self.concept_label = concept_label
        self.children = []  # list of tuples (edge_label, nodes)
        self.parent = parent

    def add_child(self, edge_label, node):
        self.children.append((edge_label, node))


class AMRGraph():
    def __init__(self):
        self.stack_nodes = []
        self.stack_edges = [ROOT]
        self.roots = []
        self.nodes_to_concepts = {}
        self.nodes_to_children = {}

    def clear(self):
        self.stack_nodes = []
        self.stack_edges = [ROOT]
        self.roots = []
        self.nodes_to_concepts = {}
        self.nodes_to_children = {}

    def flatten(self, foo):
        for x in foo:
            if hasattr(x, '__iter__'):
                for y in self.flatten(x):
                    yield y
            else:
                yield x

    def make_segment_proper(self, x):
        if len(x.split(':')) > 2:
            # print 'not proper'

            parts = [p.strip() for p in re.split('(\:[a-zA-Z0-9]+)', x) if p.strip() != '']

            for idx, p in enumerate(parts):
                if str(p).startswith(':'):
                    try:
                        parts[idx + 1] = '( ' + parts[idx + 1] + ' )'
                    except IndexError:
                        pass
                else:
                    pass
            index_to_join = []
            mod_parts = []
            for idx, p in enumerate(parts):
                if str(p).startswith(':') and not str(parts[idx - 1]).endswith(')'):
                    print 'join', p, parts[idx - 1]
                    index_to_join.append((idx, idx - 1))
                    mp = parts[idx - 1] + ' ' + p
                    mod_parts.pop()
                    mod_parts.append(mp)
                else:
                    mod_parts.append(p.strip())

            return mod_parts
        else:
            # print 'proper'
            return x

    def append_stacks(self, nv, e2c):
        if nv is not None:
            self.stack_nodes.append(nv)

        if e2c is not None:
            self.stack_edges.append(e2c)

    def fix_graph_string(self, s):
        s = re.split('(\()|(\))', s)
        s = [x.strip() for x in s if x != '' and x is not None]
        s = [self.make_segment_proper(x) for x in s]
        s = list(self.flatten(s))
        return s

    def read_bracketed_string(self, s):
        self.clear()
        s = self.fix_graph_string(s)
        i = 0
        while i < len(s):
            print i, s[i]
            if s[i] == '(':
                try:
                    e4p = self.stack_edges.pop()
                except IndexError:
                    e4p = None

                nv, nc, e2c = self.parse_term(s[i + 1])

                if e4p == 'ROOT':
                    self.roots = nv
                else:
                    p = self.stack_nodes[-1]
                    n2c = self.nodes_to_children.get(p, [])
                    if e2c == RE_ENTERENCY:
                        n2c.append((e2c, e4p, nv))
                    else:
                        n2c.append((e4p, nv))
                    self.nodes_to_children[p] = n2c
                self.append_stacks(nv, e2c)
                i += 2  # move 2 steps forward
            elif s[i] == ')':
                self.stack_nodes.pop()
                i += 1
            else:
                nv, nc, e2c = self.parse_term(s[i])
                self.append_stacks(nv, e2c)
                i += 1
        print 'done'


    def traverse(self, path):
        """
        path is a sequence of children to take and arrive at the destination node
        eg. 0,1,1,3 is a path to take root r-> child 1 c1-> child 1 c2-> child 3 c3
        then return c3
        """
        pass


    def parse_term(self, term):
        # if len(term.split(':')) > 2:
        # self.parse_multilabels(term)
        n_variable, n_concept, edge_term = None, None, None
        try:
            node_term, edge_term = term.split(':')
        except ValueError:
            node_term, edge_term = term, None

        if node_term.strip() != '':
            ns = node_term.split('/')
            n_variable = ns[0].strip()
            if len(ns) == 2:
                n_concept = ns[1].strip()
            else:
                if '"' in ns[0]:
                    print 'const', ns[0]
                    n_variable = ns[0]
                    n_concept = ns[0]
                else:
                    print 'might be re-enterence', ns[0]
                    n_variable = ns[0]
                    edge_term = RE_ENTERENCY

            if n_concept is not None:
                self.nodes_to_concepts[n_variable] = n_concept
        # edge_term is actually a edge waiting for a child
        return n_variable, n_concept, edge_term


if __name__ == '__main__':
    # s = "(t / talk-01   :ARG0 (i / i)   :ARG1 (a / and   :op1 (b / bridge)   :op2 (g / golf)   :op3 (p / politics)   :op4 (n2 / necktie))   :ARG2 (h / he))"
    '''s1 = '(s / see-01 :ARG0 (i / i) :ARG1 (p / picture :mod (m / magnificent) :location (b2 / book :name (n / name ' \
         ':op1 ("True") :op2 ("Stories") :op3 ("from") :op4 ("Nature")) :topic (f / forest :mod (p2 / primeval)))) ' \
         ':mod (o / ' \
         'once) :time (a / age-01 :ARG1 (i) :ARG2 (t / temporal-quantity :quant (6) :unit (y / year))))'

    a = AMRGraph()
    fixed_s1 = ' '.join(a.fix_graph_string(s1))
    a.read_bracketed_string(fixed_s1)
    pprint(a.nodes_to_children)
    pprint(a.nodes_to_concepts)
    '''
    s = '(s / see-01 :ARG0 (i / i) :ARG1 (p / picture :mod (m / magnificent) :location (b2 / book :name (n / name ' \
        ':op1 "True" :op2 "Stories" :op3 "from" :op4 "Nature") :topic (f / forest :mod (p2 / primeval)))) :mod (o / once) :time (a / age-01 :ARG1 i :ARG2 (t / temporal-quantity :quant 6 :unit (y / year))))'

    b = AMRGraph()
    fixed_s = ' '.join(b.fix_graph_string(s))
    b.read_bracketed_string(fixed_s)
    pprint(b.nodes_to_children)
    pprint(b.nodes_to_concepts)
