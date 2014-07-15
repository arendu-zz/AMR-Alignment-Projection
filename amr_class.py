
NE_ONTOLOGY = ["person", "name"]
class Amr:
	def __init__(self, unparsed, parents = [0]):
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
				self.depth +=1
				#self.buffer += its_char
			
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
			elif self.state == "hasconceptneedchildren" and its_char == ":" and len(self.buffer.strip()) == 0   and self.lastchar == " ":
				self.state = "learningedge"

				self.buffer += its_char
			
			elif self.state == "hasconceptneedchildren" and its_char == ")" and len(self.buffer.strip()) == 0:
				#print ">>", self.buffer
				self.depth -= 1
			elif self.state == "learningedge" and its_char == " ":
				self.edge = self.buffer.strip()
				self.state = "learningchild"
				self.buffer = "" 
			
			elif self.state == "learningchild" and its_char == ":" and self.lastchar == " ":
				this_loc = len(self.children)
				self.children.append([self.edge.strip(" "), AmrConst(self.buffer, self.parentnodes+[this_loc])])
				
				self.state = "learningedge"
				self.buffer = its_char
			elif self.state == "learningchild" and its_char == ")":
				this_loc = len(self.children)
				self.children.append([self.edge.strip(" "), AmrConst(self.buffer, self.parentnodes+[this_loc])])
				
				self.state = "learningedge"
				self.depth -= 1
				self.buffer = ""
			elif self.state == "learningchild" and its_char == "(" and self.depth ==1:
				
				self.state = "insidechild"
				self.depth +=1
				self.buffer += its_char
			elif self.state == "insidechild" and its_char == "(":
				self.depth +=1
				self.buffer += its_char
			elif self.state == "insidechild" and its_char == ")" and self.depth > 2:
				self.depth -=1
				self.buffer += its_char
			
			elif self.state == "insidechild" and ")" == its_char and self.depth == 2:
				self.buffer += its_char
				self.depth += -1
				this_loc = len(self.children)
				if not ":" in self.buffer:
					self.children.append([self.edge.strip(" "), Amr(self.buffer, self.parentnodes+[this_loc])])
					
				else:
					self.children.append([self.edge.strip(" "), Amr(self.buffer, self.parentnodes+[this_loc])])
					
				self.state = "hasconceptneedchildren"
				self.buffer=  ""
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
				y= []
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
				vars.append( [self.variable, each_child[0], "REENTRANCE_"+each_child[1].concept.strip()])
				vars += each_child[1].tuple_list()
			else:
				vars.append( [self.variable, each_child[0], each_child[1].variable])
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
	def code_reentrancies(self, concept_table = []):
		if len(concept_table) == 0:
			concept_table = self.concept_table()
		for each_child in self.children:
			each_child[1].code_reentrancies(concept_table)
		self.fullct =  concept_table
	
	def __getitem__(self, call):
		if not call[0] == 0:
			raw_input("not root")
		if len(call) == 1:
			
			return self
		elif len(call) ==2:
			target = call[1] 
			rem =  [0]
		else:
			target = call[1] 
			rest = call[2:]
			rem =  [0] + rest
		real_index = 0
		
		for each_child in self.children:
			if each_child[1].isconstant and each_child[1].concept.strip() in self.fullct:
				continue
			elif target == real_index:
				return each_child[1][rem]
			else:
				real_index +=1
		
	def __str__(self, depth = 0):
		out = ""
		out += " ("+self.variable +" / "+self.concept+" "
		for term in self.children:
			out += term[0]+" "+str(term[1])+" "
		out += ")"
		return out
	def check_for_reentrant_predicates(self):
		outs = []
		ht =  self.tuple_list()
		ct = self.concept_table()
		for term in ht:
			if "REENTRANCE_" in term[2]:
				if term[2].replace("REENTRANCE_","") in ct:
					outs.append(ct[term[2].replace("REENTRANCE_","")])
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
						#print "\t", y[-1]
						#print tok
				first, second = wordspan.split("-")
				spandict.append([int(first), int(second), wordspan_correlates])
				
		spandict.sort()
		allterms = []
		for term in spandict:
			for each_concept in term[2]:
				if "-" in each_concept and each_concept.split("-")[-1].isdigit():
					allterms.append("-".join(each_concept.split("-")[:-1]))
				else:
					if each_concept in NE_ONTOLOGY:
						pass
					else:
						allterms.append(each_concept)
		return " ".join(allterms)
				
						#print tok[int(first):int(second)]


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
			self.concept = self.concept.replace('"',"")
			self.isname =True
		self.children = []
		self.isconstant = True
		self.isreentrancy = False
	def __str__(self, depth = 0):		
		return self.concept
	def amrcfg(self):
		pass
	def code_reentrancies(self, concept_table):
		if self.concept in concept_table:
			self.isreentrancy = True
		self.fullct =  concept_table
	def concept_table(self):
		return {}
	def __getitem__(self, call):
		print call
		if call == [0]:
			return self
		else:
			raw_input("incorrectpath")
	
						
				

class AmrDoc:
	def __init__(self, unparsed_document):
		rest  = ""
		self.ids = {}
		buffer = ""
		tempid = ""
		tempsent = ""
		temptok = ""
		tempalign = ""
		totalid = ""
		tempzh = ""
		tempdate  = ""
		for each_line in unparsed_document.split("\n"):
			if "# ::id" in each_line:
				
				self.ids[tempid] = [tempsent, Amr(buffer), temptok, tempalign, totalid, tempzh, tempdate, buffer]
				buffer= ""
				tempsent = ""
				tempid = each_line[:each_line.find("::date")]
				if "::annotator" in tempid:
					tempid = tempid[:tempid.find("::annotator")]
				if "::script" in tempid:
					tempid = tempid[:tempid.find("::script")]
				totalid = each_line
			elif "# ::snt" in each_line:
				tempsent =  each_line
			elif "# ::zh" in each_line:
				tempzh =  each_line
			elif "# ::save-date" in each_line:
				tempdate =  each_line
			elif "# ::tok" in each_line:
				temptok =  each_line.replace("# ::tok ", "").split(" ")
			elif "# ::alignments" in each_line:
				tempalign =  each_line[:each_line.find("::annotator")].replace("# ::alignments", "").strip()
				
			elif "# :" in each_line:
				print each_line
				
			else:
				buffer += each_line +"\n"
	def print_amrtized_strings(self):
		allk = self.ids.keys()
		y = []
		for term in allk:
			if "." in term:
				y.append([int(term.split(".")[-1]), term])
			else:
				print term
				#raw_input()
		y.sort()
		for index, each_id in y:
			
			t = self.ids[each_id][1]
			t.code_reentrancies()
			#print each_id
			u =  t.amrtized_string(self.ids[each_id][2], self.ids[each_id][3])
			box = self.ids[each_id]
			totalid = box[4]
			newu = "# ::caveman-string "+u
			header= box[4].replace("\n","")+"\n"+box[0].replace("\n","")+"\n"+box[5].replace("\n","")+"\n"+box[6].replace("\n","")+"\n"+"# ::tok "+' '.join(box[2]).replace("\n","")+"\n# ::alignments "+box[3].replace("\n","")+"\n"+newu+"\n"+box[7]+"\n"
			print header
			
			#[tempsent, Amr(buffer), temptok, tempalign, totalid, tempzh, tempdate]
			
			
	def check_predicates(self): # class for testing and empircal question; should replace with some grep approximation
		for each_id in self.ids:
			each_amr = self.ids[each_id][1]
			each_sent = self.ids[each_id][0]
			outs=  each_amr.check_for_reentrant_predicates()
			for item in outs:
				if "-0" in item:
					print each_amr
					print item, each_sent
	
		
#u = open("/home/tim/Corpora/ChineseParalle/test.amr.txt").read()
#tok ="Once when I was six years old I saw a magnificent picture in a book , called True Stories from Nature , about the primeval forest ."
#aligns ="17-21|0.1.1.0+0.1.1.0.0+0.1.1.0.1+0.1.1.0.2+0.1.1.0.3 8-9|0 4-5|0.3.0.0 5-6|0.3.0+0.3.0.1 0-1|0.2 11-12|0.1 14-15|0.1.1 25-26|0.1.1.1 24-25|0.1.1.1.0 10-11|0.1.0 2-3|0.0"
#t = Amr(u)
#t.check_for_reentrant_predicates()


#test = "/home/tim/NLP_Programs/AMR-Alignment-Projection/data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned"
#test = "/home/tim/Corpora/ChineseParalle/deft-p1-amr-r4-xinhua.txt"
#y = AmrDoc(open(test).read())
#y.print_amrtized_strings()