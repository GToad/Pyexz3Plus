# Copyright: see copyright.txt
# -*- coding: utf-8 -*-  
import logging
from .global_vars import OUTER_INPUTS,REFLECT_INPUTS,PREPARE_INIT,VARNAME_LIST,VAR_LIST,VARNAME_BACK,SWITCH,SWITCH_LIST,API_TRACK
from .predicate import Predicate
from .constraint import Constraint
from .z3_wrap import Z3Wrapper
import codecs
import time
import traceback
import sys

log = logging.getLogger("se.pathconstraint")

class PathToConstraint:
	def __init__(self, add):
		self.constraints = {}
		self.add = add
		self.root_constraint = Constraint(None, None)
		self.current_constraint = self.root_constraint
		self.expected_path = None
		self.numOfconstraint = 0
		self.pre_solver = Z3Wrapper()
		self.max_height = 10
		self.loop_count = 0
		self.trash_constraint = Constraint(None,None)
		self.last_constraint = self.trash_constraint
		self.exe_trace = []
		self.f = open('ex_path.txt','w')

	def reset(self,expected):
		self.current_constraint = self.root_constraint
		self.loop_count = 0
		self.exe_trace = []
		global VARNAME_BACK,SWITCH_LIST
		VARNAME_BACK = []
		SWITCH_LIST = {}# TRY
		if expected==None:
			self.expected_path = None
		else:
			self.expected_path = []
			tmp = expected
			while tmp.predicate is not None:
				self.expected_path.append(tmp.predicate)
				tmp = tmp.parent

	def isExecuted(self,c):
		for ex in self.exe_trace:
			if ex.predicate.ln == c.predicate.ln:
				if ex.predicate.result == c.predicate.result:
					return True
			else:
				continue
		return False

	def checkName(self,name):
		# output name format: (ThirdPartyClass#number){n}
		if name.find('#'): return True
		return False
	def getVarNameNum(self,name):
		t_i = name.rfind('#')
		if(t_i < 0): return name
		t_n = name[:t_i]
		t_i = int(name[t_i+1:])
		return t_n,t_i
	def findInitValue(self,constraint,switch):
		# the query.processed remain false/true
		
		#asserts, query = constraint.getAssertsAndQuery()
		# need to be processed again
		asserts = []
		query = constraint.predicate
		model = self.pre_solver.findCounterexample(asserts, query,True)
		
		if model == None:
			return False
		else:
			for n in model.keys():
				t_i = n.find('_')
				if t_i == -1:
					#PREPARE_INIT[n] = model[n].as_long()
					PREPARE_INIT[n] = model[n]
				elif t_i >= 0:
					t_n = n[:t_i]
					t_i = n[t_i+1:]
					if t_n in VAR_LIST:
						tmp_str = VAR_LIST[t_n]
					else:
						tmp_str = "InitValue"
					tmp_str = self._reconstructionStr(t_n,t_i,tmp_str,model[n].as_long())
					PREPARE_INIT[t_n] = tmp_str
					VAR_LIST[t_n] =  tmp_str
					if switch == True:
						SWITCH_LIST[t_n] = tmp_str
					#print('after reconstruction',PREPARE_INIT)

	def whichBranch(self, branch, symbolic_type):
		""" This function acts as instrumentation.
		Branch can be either True or False."""
		""" This function acts as instrumentation.
		Branch can be either True or False."""
		global VARNAME_BACK
		global SWITCH
		print ("ptc whichbranch start")
		print ("ptc branch : ",branch)
		print ("ptc symbolic_type : ",symbolic_type)

		# add both possible predicate outcomes to constraint (tree)
		p = Predicate(symbolic_type, branch)
		print ("ptc p : ",p.__dict__)
		p.negate()
		print ("ptc p.negate() : ",p.__dict__)
		cneg = self.current_constraint.findChild(p)
		cn_t = Constraint(self.trash_constraint,p)
		p.negate()
		print ("ptc p.negate().negate() : ",p)
		c = self.current_constraint.findChild(p)
		print ("ptc c : ",c)
		print ("ptc cneg : ",cneg)

		if c is None:
			p.negate()
			cn_t = Constraint(self.trash_constraint,p)
			p.negate()
			c_t = Constraint(self.trash_constraint,p)
			self.findInitValue(cn_t,False)
			self.last_constraint = c_t
			print ("ptc c is None")
			#c = self.current_constraint.addChild(p)

			# we add the new constraint to the queue of the engine for later processing
			log.debug("New constraint: %s; Another:%s;Symbolic Type:%s" % (c_t, cneg,symbolic_type.toString()))
			length = c_t.searchPredicate(self.current_constraint,self.root_constraint)
			Executed = self.isExecuted(c_t)
			c = self.current_constraint
			if  length == -1 and not Executed:
				#c = self.current_constraint.addChild(p)
				if self.loop_count == 0:
					c = self.current_constraint.addChild(p,self.current_constraint.height+1)
					self.add(c)
					if(API_TRACK != []):
		
						self.f.write(str(c.parent.predicate)+':')
						self.f.write(str(c.height)+'\n')
						self.f.write(str(API_TRACK.pop(0)) + '\n')
						self.f.write('..........................')
						self.f.write('\n')
					#print("New constraint: %s;c.getLength():" % (c))
				else:
					self.exe_trace.append(c_t)
					#print("New constraint ,but not add: %s;c.getLength():" % (cn_t),p)
					#print('self.exe_trace',len(self.exe_trace),'c_t.ln',c_t.predicate.ln,'Ex?',Executed)

				if len(VARNAME_LIST) >= len(VARNAME_BACK):
					VARNAME_BACK = VARNAME_LIST.copy()
				#print('VAR_LIST:',VARNAME_LIST.l,'VARNAME_BACK:',VARNAME_BACK)
				
				#self.findInitValue(c)
				self.numOfconstraint += 1
			else:
				self.loop_count = length
				if length == 1:
					self.findInitValue(cn_t,True)
				
				#print('Length:',length,PREPARE_INIT)
				length = len(VARNAME_LIST.l) - len(VARNAME_BACK)
				#VARNAME_LIST.l = list(VARNAME_BACK)
				print('....loop detected....Length:',self.loop_count,length,'VAR_LIST:',VARNAME_LIST.l,'VARNAME_BACK:',VARNAME_BACK)
				if(self.loop_count <=1 or length >= self.loop_count):
					for i in range(length*2):
						VARNAME_LIST.pop()
				
			# This is a new path, current path can't satisfy the 'True' branch
			# and branch == False:
			log.debug("Reconstruction for %s:"%(symbolic_type.rgetName()),"Result:",PREPARE_INIT)
		else:
			#print('Find')
			#print(self.current_constraint.children)
			#print('current_constraint:',self.current_constraint,'constraint:',c)
			if self.current_constraint.children == []:
				self.findInitValue(cn_t,True)
			
		# check for path mismatch
		# IMPORTANT: note that we don't actually check the predicate is the
		# same one, just that the direction taken is the same
		if self.expected_path != None and self.expected_path != []:
			expected = self.expected_path.pop()
			# while not at the end of the path, we expect the same predicate result
			# at the end of the path, we expect a different predicate result
			done = self.expected_path == []
			if ( not done and expected.result != c.predicate.result or \
				done and expected.result == c.predicate.result ):
				print("Replay mismatch (done=",done,")")
				print(expected)
				print(c.predicate)

		if cneg is not None:
			# We've already processed both
			cneg.processed = True
			c.processed = True
			log.debug("Processed constraint: %s" % c)

		self.current_constraint = c

	def toDot(self):
		# print the thing into DOT format
		header = "digraph {\n"
		footer = "\n}\n"
		return header + self._toDot(self.root_constraint) + footer

	def _toDot(self,c):
		if (c.parent == None):
			label = "root"
		else:
			label = c.predicate.symtype.toString()
			if not c.predicate.result:
				label = "Not("+label+")"
		node = "C" + str(c.id) + " [ label=\"" + label + "\" ];\n"
		edges = [ "C" + str(c.id) + " -> " + "C" + str(child.id) + ";\n" for child in c.children ]
		return node + "".join(edges) + "".join([ self._toDot(child) for child in c.children ])
		
	# t_n for name, t_i for 'l' or index, t_v for original value , val for val.as_long()
	def _reconstructionStr(self,t_n,t_i,t_v,val):
		try:
			if (t_i == 'l'):
				tmp_buffer = ""
				# if current length can't applied to do slice operation
				# append the input length
				if (val > len(t_v)):
					for i in range(val - len(t_v)):
						tmp_buffer = tmp_buffer + "."
					t_v =  t_v + tmp_buffer
				elif val >= 0:
					t_v = t_v[:val]
				return t_v
			else:	
				t_i = int(t_i)
				try:
					ch =codecs.decode((hex(val).replace('0x','')).encode('utf8'),'hex_codec').decode('utf8')
				except:
					ch = '.'
					#print("here:",t_i,len(t_v))
				if (t_i < len(t_v)):
					t_v =  t_v[:t_i]+ch+t_v[t_i+1:]
				else:
					tmp_buffer = ""
					for i in range(t_i - len(t_v)):
						tmp_buffer = tmp_buffer + " "
					t_v =  t_v + tmp_buffer
					t_v =  t_v[:t_i]+ch+t_v[t_i+1:]
				return t_v
		except Exception as e:
			print('Error in reconstructing Str P2C:',traceback.print_exc())
			return 'ERROR'

