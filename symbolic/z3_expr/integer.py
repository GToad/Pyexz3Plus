from z3 import *
from .expression import Z3Expression

class Z3Integer(Z3Expression):
	def _isIntVar(self,v):
		print ("z3int _isIntVar")
		return isinstance(v,IntRef)

	def _variable(self,name,solver):
		print ("z3int _variable")
		return Int(name,solver.ctx)

	def _constant(self,v,solver):
		print ("z3int _constant")
		return IntVal(v,solver.ctx)

	def _mod(self, l, r, solver):
		print ("z3int _mod")
		mod_fun = Function('int_mod', IntSort(), IntSort(), IntSort())
		return mod_fun(l, r)

	def _lsh(self, l, r, solver):
		print ("z3int _lsh")
		lsh_fun = Function('int_lsh', IntSort(), IntSort(), IntSort())
		return lsh_fun(l, r)

	def _rsh(self, l, r, solver):
		print ("z3int _rsh")
		rsh_fun = Function('int_rsh', IntSort(), IntSort(), IntSort())
		return rsh_fun(l, r)

	def _xor(self, l, r, solver):
		print ("z3int _xor")
		xor_fun = Function('int_xor', IntSort(), IntSort(), IntSort())
		return xor_fun(l, r)

	def _or(self, l, r, solver):
		print ("z3int _or")
		or_fun = Function('int_or', IntSort(), IntSort(), IntSort())
		return or_fun(l, r)

	def _and(self, l, r, solver):
		print ("z3int _and")
		and_fun = Function('int_and', IntSort(), IntSort(), IntSort())
		return and_fun(l, r)
