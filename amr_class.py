class Amr:
	def __init__(self, unparsed):

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
			elif self.state == "needvar" and its_char == " ":
				self.state = "hasvarneedslash"
				self.variable = self.buffer
				self.buffer = ""
			elif self.state == "hasvarneedslash" and its_char == "/":
				
				self.state = "hasvarneedconcept"
				#print ">>", self.buffer, self.variable
				self.buffer = ""	
			
			elif self.state == "hasvarneedconcept" and its_char == " " and len(self.buffer.strip()) > 0:
				self.concept = self.buffer
				self.state = "hasconceptneedchildren"
				self.buffer = ""	
			elif self.state == "hasvarneedconcept" and its_char == ")" and len(self.buffer.strip()) > 0:
				self.concept = self.buffer
				self.state = "hasconceptneedchildren"
				self.buffer = ""	
			elif self.state == "hasconceptneedchildren" and its_char == ":" and len(self.buffer.strip()) == 0:
				self.state = "learningedge"
				#print ">>", self.buffer
				self.buffer += its_char
			
			elif self.state == "hasconceptneedchildren" and its_char == ")" and len(self.buffer.strip()) == 0:
				#print ">>", self.buffer
				self.depth -= 1
			elif self.state == "learningedge" and its_char == " ":
				self.edge = self.buffer
				self.state = "learningchild"
				self.buffer = "" 
			
			elif self.state == "learningchild" and its_char == ":":
				self.children.append([self.edge.strip(" "), AmrConst(self.buffer)])
				self.state = "learningedge"
				self.buffer = its_char
			elif self.state == "learningchild" and its_char == ")":
				self.children.append([self.edge.strip(" "), AmrConst(self.buffer)])
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
				if not ":" in self.buffer:
					self.children.append([self.edge.strip(" "), Amr(self.buffer)])
				else:
					self.children.append([self.edge.strip(" "), Amr(self.buffer)])
				self.state = "hasconceptneedchildren"
				self.buffer=  ""
			elif self.state == "insidechild":
				self.buffer += its_char
			else:
				self.buffer += its_char
			self.remainder = self.remainder[1:]
			
	def parse(self, unparsed):
		for __ in range(len(unparsed)):
			self.parse_char()
			
	#def __getitem__(self, alignment_set):
	#	remain = alignment_set.split(".")
	#	print remain
	#	return alignment_set
			
		
		
	def __str__(self, depth = 0):
		out = ""
		out += " ("+self.variable +" / "+self.concept+" "
		for term in self.children:
			out += term[0]+" "+str(term[1])+" "
		out += ")"
		return out
class AmrConst(Amr):
	def __init__(self, unparsed):
		self.remainder = unparsed
		self.concept = self.remainder
		self.depth = 0
		
		self.variable = "n/a"
		self.concept = unparsed
		self.children = []
	def __str__(self, depth = 0):		
		return self.concept
	def amrcfg(self):
		pass

