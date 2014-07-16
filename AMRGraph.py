__author__ = 'arenduchintala'
import re
from pprint import pprint
from collections import defaultdict

global RE_ENTERENCY, ROOT
RE_ENTERENCY = 'RE-ENTERENCY'
ROOT = 'ROOT'


class Node():
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
        if len(re.split('(\:[a-zA-Z0-9]+\s)', x)) > 2:
            # print 'not proper'
            parts = [p.strip() for p in re.split('(\:[a-zA-Z0-9]+)', x) if p.strip() != '']
            for idx, p in enumerate(parts):
                if str(p).startswith(':'):
                    try:
                        parts[idx + 1] = '( ' + parts[idx + 1] + ' )'
                    except IndexError:
                        pass  # this error can be ignored its trying to fix a part that dosent exist
            index_to_join = []
            mod_parts = []
            for idx, p in enumerate(parts):
                if str(p).startswith(':') and not str(parts[idx - 1]).endswith(')'):
                    # print 'join', p, parts[idx - 1]
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
        s = [self.make_segment_proper(x.strip()) for x in s if x != '' and x is not None]
        s = list(self.flatten(s))
        s = ' '.join(s)
        s = re.split('(\()|(\))', s)
        s = [x.strip() for x in s if x != '' and x is not None]
        return s

    def parse_bracketed_list(self, s):
        self.clear()
        i = 0
        while i < len(s):
            if s[i] == '(':
                # try:
                e4p = self.stack_edges.pop()
                # except IndexError:
                # e4p = None

                nv, nc, e2c = self.parse_term(s[i + 1])

                if e4p == ROOT:
                    self.roots.append(nv)
                else:
                    p = self.stack_nodes[-1]
                    if e2c == RE_ENTERENCY:
                        self.nodes_to_children[p].append((e2c, e4p, nv))
                    else:
                        self.nodes_to_children[p].append((e4p, nv))

                self.append_stacks(nv, e2c)
                i += 2  # move 2 steps forward

            elif s[i] == ')':
                self.stack_nodes.pop()
                i += 1

            else:
                nv, nc, e2c = self.parse_term(s[i])
                self.append_stacks(nv, e2c)
                i += 1


    def get_concept(self, sequence):
        """
        path is a sequence of children to take and arrive at the destination node
        eg. 0,1,1,3 is a path to take root r-> child 1 c1-> child 1 c2-> child 3 c3
        then return c3
        """
        s = [x for x in sequence]  # just to look at full sequence
        sequence.pop(0)
        node_label = self.roots[0]
        # TODO: do these graphs always have just one root? - yes
        while len(sequence) > 0:
            branch = int(sequence.pop(0))
            node_labels = []
            for x in self.nodes_to_children[node_label]:
                if x[0] == RE_ENTERENCY and x[-1] in self.nodes_to_concepts:
                    pass  # 'this is a re-enterency so we skip this
                else:
                    node_labels.append(x[-1])
            node_label = node_labels[branch]
        concept = self.nodes_to_concepts[node_label]
        return concept


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
                    # print 'const', ns[0]
                    n_variable = ns[0]
                    n_concept = ns[0]
                else:
                    # print 'might be re-enterence', ns[0]
                    n_variable = ns[0]
                    edge_term = RE_ENTERENCY

            if n_concept is not None:
                self.nodes_to_concepts[n_variable] = n_concept
        # edge_term is actually a edge waiting for a child
        return n_variable, n_concept, edge_term


if __name__ == '__main__':
    s = '(s / see-01 :ARG0 (i / i) :ARG1 (p / picture :mod (m / magnificent) :location (b2 / book :name (n / name ' \
        ':op1 "True" :op2 "Stories" :op3 "from" :op4 "Nature") :topic (f / forest :mod (p2 / primeval)))) :mod (o / once) :time (a / age-01 :ARG1 i :ARG2 (t / temporal-quantity :quant 6 :unit (y / year))))'
    b = AMRGraph()
    b.parse_string(s)
    assert b.get_concept('0.3.0.1'.split('.')) == 'year'

    s = '(c / chapter :mod 1)'
    c = AMRGraph()
    c.parse_string(s)
    print c.get_concept('0.0'.split())
