
from AMRMetadata import *
NE_ONTOLOGY = ["person", "family", "animal", "language", "nationality", "ethnic-group,regional-group",
               "religious-group", "organization", "company", "government-organization",
               "military,criminal-organization", "political-party", "school", "university", "research-institute",
               "team", "league", "location", "city", "city-district", "county", "state", "province",
               "territory,country", "local-region", "country-region", "world-region", "continent", "ocean", "sea",
               "lake", "river", "gulf", "bay", "strait", "canal", "peninsula", "mountain", "volcano", "valley",
               "canyon", "island", "desert", "forest", "moon", "planet", "star", "constellation", "facility", "airport",
               "station", "port", "tunnel", "bridge", "road", "railway-line", "canal", "building", "theater", "museum",
               "palace", "hotel", "worship-place,sports-facility", "market", "park", "zoo", "amusement-park", "event",
               "incident", "natural-disaster", "earthquake", "war", "conference,game", "festival", "product", "vehicle",
               "ship", "aircraft", "aircraft-type", "spaceship", "car-make", "work-of-art", "picture", "music", "show",
               "broadcast-program", "publication", "book", "newspaper", "magazine", "journal", "natural-object", "law",
               "treaty", "award", "food-dish", " disease", "dna-sequence", "gene", "pathway", "protein", "thing",
               "name"]


class Amr:
    def __init__(self, unparsed, parents=[0]):
        self.parentnodes = parents
        self.remainder = unparsed.replace("\n", " ")

        self.depth = 0
        self.buffer = ""
        self.children = []
        self.state = "needvar"
        self.variable = ""
        self.concept = ""
        self.edge = ""
        self.parse(self.remainder)
        self.root_loc = []
        self.nonreentrant_children = {}
        self.isreentrancy = False
        self.isconstant = False
        self.lastchar = ""

    def parse_char(self):
        if len(self.remainder) == 0:
            return True
        else:

            its_char = self.remainder[0]
            if self.remainder[0] == "(" and self.state == "needvar":
                self.depth += 1
                # self.buffer += its_char

            elif self.state == "needvar" and not its_char == " ":

                self.buffer += its_char
            elif self.state == "needvar" and its_char == " " and len(self.buffer.strip()) > 0:
                self.state = "hasvarneedslash"
                self.variable = self.buffer

                self.buffer = ""
            elif self.state == "hasvarneedslash" and its_char == "/":

                self.state = "hasvarneedconcept"
                self.buffer = ""

            elif self.state == "hasvarneedconcept" and its_char == " " and len(self.buffer.strip()) > 0:
                self.concept = self.buffer.strip()
                self.state = "hasconceptneedchildren"
                self.buffer = ""
            elif self.state == "hasvarneedconcept" and its_char == ")" and len(self.buffer.strip()) > 0:
                self.concept = self.buffer.strip()
                self.state = "hasconceptneedchildren"
                self.buffer = ""
            elif self.state == "hasconceptneedchildren" and its_char == ":" and len(
                    self.buffer.strip()) == 0 and self.lastchar == " ":
                self.state = "learningedge"

                self.buffer += its_char

            elif self.state == "hasconceptneedchildren" and its_char == ")" and len(self.buffer.strip()) == 0:
                # print ">>", self.buffer
                self.depth -= 1
            elif self.state == "learningedge" and its_char == " ":
                self.edge = self.buffer.strip()
                self.state = "learningchild"
                self.buffer = ""

            elif self.state == "learningchild" and its_char == ":" and self.lastchar == " ":
                this_loc = len(self.children)
                self.children.append([self.edge.strip(" "), AmrConst(self.buffer, self.parentnodes + [this_loc])])

                self.state = "learningedge"
                self.buffer = its_char
            elif self.state == "learningchild" and its_char == ")":
                this_loc = len(self.children)
                self.children.append([self.edge.strip(" "), AmrConst(self.buffer, self.parentnodes + [this_loc])])

                self.state = "learningedge"
                self.depth -= 1
                self.buffer = ""
            elif self.state == "learningchild" and its_char == "(" and self.depth == 1:

                self.state = "insidechild"
                self.depth += 1
                self.buffer += its_char
            elif self.state == "insidechild" and its_char == "(":
                self.depth += 1
                self.buffer += its_char
            elif self.state == "insidechild" and its_char == ")" and self.depth > 2:
                self.depth -= 1
                self.buffer += its_char

            elif self.state == "insidechild" and ")" == its_char and self.depth == 2:
                self.buffer += its_char
                self.depth += -1
                this_loc = len(self.children)
                if not ":" in self.buffer:
                    self.children.append([self.edge.strip(" "), Amr(self.buffer, self.parentnodes + [this_loc])])

                else:
                    self.children.append([self.edge.strip(" "), Amr(self.buffer, self.parentnodes + [this_loc])])

                self.state = "hasconceptneedchildren"
                self.buffer = ""
            elif self.state == "insidechild":
                self.buffer += its_char
            else:
                self.buffer += its_char
            self.lastchar = its_char
            self.remainder = self.remainder[1:]

    def span_table(self, tok, ali):
        self.tokens = tok.split(" ")
        self.alignments = {}

        for each_alignment in ali.split(" "):
            targets = each_alignment.split("|")[0]
            codes = each_alignment.split("|")[1]
            word_range = range(int(targets.split("-")[0]), int(targets.split("-")[1]))
            if "+" in codes:
                allcodes = codes.split("+")
            else:

                allcodes = [codes]
            paths = []
            for term in allcodes:
                y = []
                for item in term.split("."):
                    y.append(int(item))
                paths.append(y)

            if not "-".join(word_range) in self.alignments:
                self.alignments["-".join(word_range)] = []
            self.alignments["-".join(word_range)].append(y)
        return self.alignments

    def parse(self, unparsed):
        for __ in range(len(unparsed)):
            self.parse_char()

    def isnonreentrantconstant(self, term):
        if term == "+" or term == "-" or term.strip().isdigit() or "True" in term or "False" in term or '"' in term or "imperative" in term:
            return True
        else:
            return False

    def tuple_list(self):
        vars = []

        for each_child in self.children:
            if each_child[1].variable == "n/a" and not self.isnonreentrantconstant(each_child[1].concept):
                vars.append([self.variable, each_child[0], "REENTRANCE_" + each_child[1].concept.strip()])
                vars += each_child[1].tuple_list()
            else:
                vars.append([self.variable, each_child[0], each_child[1].variable])
                vars += each_child[1].tuple_list()
        return vars

    def concept_table(self):
        vars = {}
        if not self.variable in vars:
            vars[self.variable] = ""
        if len(self.concept) > 0:
            vars[self.variable] = self.concept
        for each_child in self.children:


            y = each_child[1].concept_table()
            for term in y:
                if not term in vars:
                    vars[term] = y[term]
        return vars

    def code_reentrancies(self, concept_table=[]):
        if len(concept_table) == 0:
            concept_table = self.concept_table()
        for each_child in self.children:
            each_child[1].code_reentrancies(concept_table)
        self.fullct = concept_table

    def __getitem__(self, call):
        if not call[0] == 0:
            raw_input("not root")
        if len(call) == 1:

            return self
        elif len(call) == 2:
            target = call[1]
            rem = [0]
        else:
            target = call[1]
            rest = call[2:]
            rem = [0] + rest
        real_index = 0

        for each_child in self.children:
            if each_child[1].isconstant and each_child[1].concept.strip() in self.fullct:
                continue
            elif target == real_index:
                return each_child[1][rem]
            else:
                real_index += 1

    def __str__(self, depth=0):
        out = ""
        out += " (" + self.variable + " / " + self.concept + " "
        for term in self.children:
            out += term[0] + " " + str(term[1]) + " "
        out += ")"
        return out

    def check_for_reentrant_predicates(self):
        outs = []
        ht = self.tuple_list()
        ct = self.concept_table()
        for term in ht:
            if "REENTRANCE_" in term[2]:
                if term[2].replace("REENTRANCE_", "") in ct:
                    outs.append(ct[term[2].replace("REENTRANCE_", "")])
        return outs

    def amrtized_string(self, tok, span):
        spandict = []
        for element in span.split(" "):
            if len(element) == 0:
                continue
            else:
                wordspan = element.split("|")[0]
                otherspan = []
                if "+" in element.split("|")[1]:
                    for term in element.split("|")[1].split("+"):
                        otherspan.append(term)
                else:
                    otherspan = [element.split("|")[1]]
                maps = []

                wordspan_correlates = []
                for term in otherspan:
                    y = []
                    for word in term.split("."):
                        y.append(int(word))
                    maps.append(y)

                for item in maps:

                    uu = self[item]

                    wordspan_correlates.append(uu.concept)
                    # print "\t", y[-1]
                # print tok
                first, second = wordspan.split("-")
                spandict.append([int(first), int(second), wordspan_correlates, element.split("|")[1]])

        spandict.sort()
        allterms = []
        caveman_mappings = []
        for term in spandict:
            print term
            caveman_start = len(allterms)
            for each_concept in term[2]:
                if "-" in each_concept and each_concept.split("-")[-1].isdigit():
                    allterms.append("-".join(each_concept.split("-")[:-1]))
                else:
                    if each_concept in NE_ONTOLOGY and not each_concept in ' '.join(tok):
                        pass
                    else:

                        allterms.append(each_concept)
            caveman_end = len(allterms)
            caveman_mappings.append(str(caveman_start) + "-" + str(caveman_end) + "|" + term[3])

        return " ".join(allterms), " ".join(caveman_mappings)

        # print tok[int(first):int(second)]


class AmrConst(Amr):
    def __init__(self, unparsed, parentnodes):
        self.parentnodes = parentnodes
        self.remainder = unparsed

        self.concept = self.remainder.strip()
        self.depth = 0
        self.isname = False

        self.variable = "n/a"
        self.concept = unparsed.strip()
        if '"' in self.concept:
            self.concept = self.concept.replace('"', "")
            self.isname = True
        self.children = []
        self.isconstant = True
        self.isreentrancy = False

    def __str__(self, depth=0):
        return self.concept

    def amrcfg(self):
        pass

    def code_reentrancies(self, concept_table):
        if self.concept in concept_table:
            self.isreentrancy = True
        self.fullct = concept_table

    def concept_table(self):
        return {}

    def __getitem__(self, call):

        if call == [0]:
            return self
        else:
            raw_input("incorrectpath")

