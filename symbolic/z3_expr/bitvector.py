from z3 import *
from .expression import Z3Expression

class Z3BitVector(Z3Expression):
	def __init__(self,N):
		print("\033[1;31;40m","Z3BITVECTOR","\033[0m")
		Z3Expression.__init__(self)
		self.N = N

	def _isIntVar(self,v):
		return isinstance(v,BitVecRef)

	def _variable(self,name,solver):
		return BitVec(name,self.N,solver.ctx)

	def _constant(self,v,solver):
		print ("bitvector _constant")
		return BitVecVal(v,self.N,solver.ctx)
