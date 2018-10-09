# Copyright: copyright.txt

from . symbolic_type import SymbolicObject
from z3 import *

# we use multiple inheritance to achieve concrete execution for any
# operation for which we don't have a symbolic representation. As
# we can see a SymbolicInteger is both symbolic (SymbolicObject) and 
# concrete (int)

class SymbolicInteger(SymbolicObject,int):
	# since we are inheriting from int, we need to use new
	# to perform construction correctly
	def __new__(cls, name, v, expr=None):
		print("\033[1;33;40m","int","\033[0m")
		print("symint v : ",type(v))
		print("symint v : ",v)
		print("symint cls : ",type(cls))
		print("symint cls : ",cls)
		if isinstance(v,z3.z3.IntNumRef):
			v = v.as_long()
		#if type(v)==IntNumRef:
			#print("symint IntNumRef")
		return int.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		print("\033[1;33;40m","int","\033[0m")
		SymbolicObject.__init__(self, name, expr)
		self.val = v

	def getConcrValue(self):
		return self.val

	def wrap(conc,sym):
		return SymbolicInteger("se",conc,sym)

	def __hash__(self):
		return hash(self.val)

	def _op_worker(self,args,fun,op):
		return self._do_sexpr(args, fun, op, SymbolicInteger.wrap)

# now update the SymbolicInteger class for operations we
# will build symbolic terms for

ops =  [("add",    "+"  ),\
	("sub",    "-"  ),\
	("mul",    "*"  ),\
	("mod",    "%"  ),\
	("floordiv", "//" ),\
	("and",    "&"  ),\
	("or",     "|"  ),\
	("xor",    "^"  ),\
	("lshift", "<<" ),\
	("rshift", ">>" ) ]

def make_method(method,op,a):
	code  = "def %s(self,other):\n" % method
	code += "   print('sym_int make method %s')\n" % method
	code += "   return self._op_worker(%s,lambda x,y : x %s y, \"%s\")" % (a,op,op)
	locals_dict = {}
	#print ("code : ",code)
	#print (code)
	exec(code, globals(), locals_dict)
	setattr(SymbolicInteger,method,locals_dict[method])

for (name,op) in ops:
	method  = "__%s__" % name
	make_method(method,op,"[self,other]")
	rmethod  = "__r%s__" % name
	make_method(rmethod,op,"[other,self]")

