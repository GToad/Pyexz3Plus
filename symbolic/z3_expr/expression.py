#coding=utf-8
import utils

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_type import SymbolicType
from symbolic.symbolic_types.symbolic_str import SymbolicStr
#from .string import Z3String
#from .integer import Z3Integer
from z3 import *
import codecs

class Z3Expression(object):
	def __init__(self):
		self.z3_vars = {}
		print ("exp self.__dict__",self.__dict__)

	def toZ3(self,solver,asserts,query):
		self.z3_vars = {}
		tmp_list = [self.predToZ3(p,solver) for p in asserts]
		#should concat with Or()
		tmp_bool = BoolVal(False)
		for a in tmp_list:
			if isinstance(a,list):
				for b in a:
					tmp_bool = Or(b,tmp_bool)
			else:
				solver.assert_exprs(a)
				
		
		if not is_false(tmp_bool):
			solver.assert_exprs(tmp_bool)
		#query for opposite condition 	
		#print("in z3,finish asserts",tmp_list)
		tmp_list =self.predToZ3(query,solver)
		if not isinstance(tmp_list,list): solver.assert_exprs(Not(tmp_list))
		else:
			for a in tmp_list:
				solver.assert_exprs(Not(a))
		#print("in z3,finish query, not",tmp_list)
		#print('-----------------------')
		#print(solver)

	def predToZ3(self,pred,solver,env=None):
		print ("exp pred : ",pred.__dict__)
		sym_expr = self._astToZ3Expr(pred.symtype,solver,env)
		print ("exp init sym_expr : ",sym_expr)

		if isinstance(sym_expr,list):
			for i in range(len(sym_expr)):
				if env == None:
					if not is_bool(sym_expr[i]):
						print ("exp cons flag1")
						sym_expr[i] =  sym_expr[i] != self._constant(0,solver)
					if not pred.result:
						sym_expr[i] = Not(sym_expr[i])
				else:
					if not pred.result:
						sym_expr[i] = not sym_expr[i]
		else:
			if env == None:
				if not is_bool(sym_expr):
					print ("exp constant flag2")
					sym_expr = sym_expr != self._constant(0,solver)
				if not pred.result:
					sym_expr = Not(sym_expr)
			else:
				if not pred.result:
					sym_expr = not sym_expr
			print ("exp final sym_expr : ",sym_expr)
			print ("exp predtoz3 solver : ",solver)
		return sym_expr

	def getIntVars(self):
		return [ v[1] for v in self.z3_vars.items() if self._isIntVar(v[1]) ]

	# ----------- private ---------------

	def _isIntVar(self, v):
		raise NotImplementedException

	def _getIntegerVariable(self,name,solver):
		if name not in self.z3_vars:
			print ("exp name : ",name)
			#print ("exp name self._variable(name,solver) : ",self._variable(name,solver).__dict__)
			self.z3_vars[name] = self._variable(name,solver)
		print ("exp name self.z3_vars",self.z3_vars)
		return self.z3_vars[name]

	def _getStrVariable(self,name,length,solver):
		print("exp z3vars : ",self.z3_vars)
		print("exp name : ",name)
		if name not in self.z3_vars:
			# create as used
			#print("z3vars:",self.z3_vars)
			#self.z3_vars[name] = Z3String(solver,name = name,length = length,a = [],sub = [])
			self.z3_vars[name] = String(name,solver.ctx)
		print("exp getStrVariable return")
		return self.z3_vars[name]

	def _variable(self,name,solver):
		raise NotImplementedException

	def _constant(self,v,solver):
		print ("exp _constant")
		raise NotImplementedException

	def _wrapIf(self,e,solver,env):
		print ("exp flag1")
		if env == None:
			return If(e,self._constant(1,solver),self._constant(0,solver))
		else:
			return e


	# add concrete evaluation to this, to check
	def _astToZ3Expr(self,expr,solver,env=None):
		print ("exp "+"1"*20)
		print ("exp env : ",env)
		print ("exp init expr : ",expr)
		#print ("exp init expr dict : ",expr.__dict__)
		print ("exp type of expr : ",type(expr))
		if isinstance(expr, list):
			print ("exp init expr list : ", expr)
			op = expr[0]
			print ("exp init op : ",op)
			for cjh in expr:
				print (cjh)
			args = [ self._astToZ3Expr(a,solver,env) for a in expr[1:] ]
			#z3_l,z3_r = args[0],args[1]
			print ("exp op : ",op)
			print ("exp args : ",args)
			num = len(args)
			print ("exp num : ",num)
			#print("in asttoz3expr,args:",args)
			if num == 2:
				z3_l,z3_r = args[0],args[1]
				print ("exp z3_l type1 : ",type(z3_l))
				print ("exp z3_l : ",z3_l)
				print ("exp z3_r type1 : ",type(z3_r))
				print ("exp z3_r : ",z3_r)
			elif num == 1:
				z3_l = args[0]
				print("exp z3_l : ",z3_l.__dict__)
				print("exp z3_l : ",type(z3_l))
			elif num == 3:
				z3_3 = args[2] #cjh 那z3_r z3_l怎么办
				z3_l,z3_r = args[0],args[1] #cjh 补一句这个吧

			# handle string separately
			if(isinstance(z3_l,z3.z3.SeqRef)): #z3 String()
				print ("exp enter the process of string !")
				print("self type : ",type(self))
				print("op : ",op)
				if op == "==":
					print ("exp z3_r : ",z3_r)
					print ("exp z3_l : ",z3_l)
					return self._wrapIf(z3_l == z3_r,solver,env)
					#return self.equalbak(z3_l,z3_r)
					#return z3_l.equal(z3_r,env)
				elif op == "str.len":
					return self.length(z3_l)
				elif op == "getitem":
					if num == 3:
						return z3_l.getitem(z3_r,z3_3)
					else:
						return z3_l.getitem(z3_r)
				elif op == "+":
					tmp =  z3_l.add(z3_r)
					return tmp
				elif op == "slice":
					print ("exp z3_r : ",z3_r)
					print ("exp z3_l : ",z3_l)
					print ("exp z3_3 : ",z3_3)
					return self.slice(z3_l,z3_r,z3_3)

				

			# arithmetical operations
			if op == "+":
				print("self type : ",type(self))
				print("exp symint op + : ")
				print("exp symint op + z3_l : ",z3_l)
				print("exp symint op + z3_l : ",z3_l.__dict__)
				print("exp symint op + z3_r : ",z3_r)
				print("exp symint op + z3_r : ",z3_r.__dict__)
				tmp = self._add(z3_l, z3_r, solver)
				print("exp symint op + _add(z3_l, z3_r, solver) : ",tmp)
				print("exp symint op + _add(z3_l, z3_r, solver) : ",tmp.__dict__)
				return tmp
			elif op == "-":
				return self._sub(z3_l, z3_r, solver)
			elif op == "*":
				return self._mul(z3_l, z3_r, solver)
			elif op == "//":
				return self._div(z3_l, z3_r, solver)
			elif op == "%":
				return self._mod(z3_l, z3_r, solver)

			# bitwise
			elif op == "<<":
				return self._lsh(z3_l, z3_r, solver)
			elif op == ">>":
				return self._rsh(z3_l, z3_r, solver)
			elif op == "^":
				return self._xor(z3_l, z3_r, solver)
			elif op == "|":
				return self._or(z3_l, z3_r, solver)
			elif op == "&":
				return self._and(z3_l, z3_r, solver)

			# equality gets coerced to integer
			elif op == "==":
				if z3_r == None:
					z3_r = z3_l
				print ("exp env2 : ",type(env))
				print ("exp z3_l : ",type(z3_l))
				print ("exp z3_r : ",type(z3_r))
				print ("exp solver:",type(solver))
				return self._wrapIf(z3_l == z3_r,solver,env)
			elif op == "!=":
				return self._wrapIf(z3_l != z3_r,solver,env)
			elif op == "<":
				return self._wrapIf(z3_l < z3_r,solver,env)
			elif op == ">":
				return self._wrapIf(z3_l > z3_r,solver,env)
			elif op == "<=":
				return self._wrapIf(z3_l <= z3_r,solver,env)
			elif op == ">=":
				return self._wrapIf(z3_l >= z3_r,solver,env)
			else:

				utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % op)

		elif isinstance(expr, SymbolicInteger):
			print("exp SymbolicInteger !")
			print ("exp init expr dict : ",expr.__dict__)
			if expr.isVariable():
				if env == None:
					tmp = self._getIntegerVariable(expr.name,solver)
					print("exp symint self._getIntegerVariable(expr.name,solver) : ",tmp.__dict__)
					return tmp
				else:
					return env[expr.name]
			else:
				return self._astToZ3Expr(expr.expr,solver,env)

		#TO DO:parse python symbolicStr to Z3.Str
		elif isinstance(expr,SymbolicStr):
			print("exp SymbolicStr !")
			print("exp expr : ",expr.__dict__)
			if expr.isVariable():
				if env == None:
					print("exp expr.isVarible() & env==None")
					# need to create Z3String ,store in z3_vars
					tmp = self._getStrVariable(expr.name,expr.getLength(),solver)
					print ("exp tmp1 : ",tmp.__dict__)
					return tmp
				elif len(env)==0:
					print("exp expr.isVarible() & env==None")
					# need to create Z3String ,store in z3_vars
					tmp = self._getStrVariable(expr.name,expr.getLength(),solver)
					print ("exp tmp2 : ",tmp.__dict__)
					return tmp
				else:
					print("exp expr.isVarible() & env!=None")
					print("exp env : ",env)
					print("exp expr.name : ",expr.name)
					return env[expr.name]
			else:
				print("exp not expr.isVarible()")
				return self._astToZ3Expr(expr.expr,solver,env)


		elif isinstance(expr, SymbolicType):
			print("exp SymbolicType !")
			utils.crash("{} is an unsupported SymbolicType of {}".
						format(expr, type(expr)))

		elif isinstance(expr, int):
			print("exp SymbolicInt !")
			if env == None:
				print ("exp cons flag3")
				#print ("exp z3_l to jadge : ",z3_l)
				#tmp = IntVal(expr,solver.ctx) #cjh 这个_constant真的坑，会自动去用bitvector的_constant,所以强行让它变intval
				#tmp = Z3Integer._constant(expr,solver)
				tmp = self._constant(expr,solver)
				#tmp = IntVal(expr,solver.ctx) #cjh 坑，有这行str可以，没这行int可以 
				print (tmp.__dict__)
				return tmp
			else:
				return expr
		# TO DO: rewrite
		elif isinstance(expr,str):
			tmp_list = []
			print ("exp str expr : ",expr)
			for ch in expr:
				i = self._strtoint(ch)
				print ("exp i : ",i)
				print ("exp cons flag4")
				tmp_list.append(self._constant(i,solver))
			if env == None:
				print ("exp str env==None")
				#return Z3String(solver,a = tmp_list,length = len(expr),sub = [])
				#return String(expr,solver.ctx)
				return StringVal(expr)
			else:
					#not sure
				return expr
		#TO DO :handle None expression
		elif expr == None:
			return None
		else:
			utils.crash("Unknown node during conversion from ast to Z3 (expressions): %s" % expr)

	def _add(self, l, r, solver):
		return l + r

	def _sub(self, l, r, solver):
		tmp = l - r
		print ("exp tmp=l-r : ",tmp)
		return tmp

	def _mul(self, l, r, solver):
		return l * r

	def _div(self, l, r, solver):
		return l / r

	def _mod(self, l, r, solver):
		print("exp _mod")
		return l % r

	def _lsh(self, l, r, solver):
		return l << r

	def _rsh(self, l, r, solver):
		return l >> r

	def _xor(self, l, r, solver):
		return l ^ r

	def _or(self, l, r, solver):
		return l | r

	def _and(self, l, r, solver):
		return l & r

	#convert str to int 
	def _strtoint(self,s):
		return int(codecs.encode(s.encode('utf8'),'hex_codec'),16)

'''
		if env == None:
			tmp = If(e,self._constant(1,solver),self._constant(0,solver))
			print ("exp tmp== : ",tmp)
			return tmp
		else:
			return e
			'''

'''
	def toZ3(self,solver,asserts,query):
		print("exp toZ3 start")
		self.z3_vars = {}
		solver.assert_exprs([self.predToZ3(p,solver) for p in asserts])
		solver.assert_exprs(Not(self.predToZ3(query,solver)))
		print ("exp toz3 solver : ",solver)
		print("exp toZ3 end")
'''
