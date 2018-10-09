# Copyright: see copyright.txt
#coding=utf-8
import sys
import ast
import logging

from z3 import *
from .z3_expr.integer import Z3Integer
from .z3_expr.bitvector import Z3BitVector
from .z3_expr.string import Z3String

log = logging.getLogger("se.z3")

class Z3Wrapper(object):
	def __init__(self):
		self.N = 32
		self.asserts = None
		self.query = None
		self.use_lia = True
		self.z3_expr = None

	def findCounterexample(self, asserts, query,expl=False): #self就是solver，并输入了asserts和query（predicate）
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		print ("z3w findCounterexample start")
		self.solver = Solver()
		self.query = query
		self.asserts = self._coneOfInfluence(asserts,query)
		res = self._findModel(expl) #cjh a lot of output from here，求出了结果
		print ("z3w flag 11111111111111111111111")
		print("z3w Query -- %s" % self.query)
		print("z3w Asserts -- %s" % asserts)
		print("z3w Cone -- %s" % self.asserts)
		print("z3w Result -- %s" % res)
		
		print ("z3w res1 : ",res)
		print ("z3w findCounterexample end")
		return res

	# private

	# this is very inefficient
	def _coneOfInfluence(self,asserts,query):
		cone = []
		cone_vars = set(query.getVars())
		ws = [ a for a in asserts if len(set(a.getVars()) & cone_vars) > 0 ]
		remaining = [ a for a in asserts if a not in ws ]
		while len(ws) > 0:
			a = ws.pop()
			a_vars = set(a.getVars())
			cone_vars = cone_vars.union(a_vars)
			cone.append(a)
			new_ws = [ a for a in remaining if len(set(a.getVars()) & cone_vars) > 0 ]
			remaining = [ a for a in remaining if a not in new_ws ]
			ws = ws + new_ws
		return cone

	def _findModel3(self):
		self.solver.push()
		#self.z3_expr = Z3Integer()
		self.z3_expr = Z3String()
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)
		res = self.solver.check()
		if res != unsat:
			model = self._getModel2()
		else:
		# TO DO: what should return if model is not available
		# Current predicate should be marked with True
			print("*****  There could be path which is infeasible")
			model = {}
		self.solver.pop()
		return model

	def _findModel(self,expl):
		print("\033[1;32;40m","z3w findmodel start","\033[0m")
		print ("z3w use_lia",self.use_lia)
		# Try QF_LIA first (as it may fairly easily recognize unsat instances)
		if expl:
			return self._findModel3() #cjh simplely explore the program
		#这一部分并没有对约束进行求解，而只是判断其是sat或unsat。个人理解是这部分的判断算法较为高效，可以快速找出unsat从而节省之后的开销
		if self.use_lia:
			self.solver.push()
			#self.z3_expr = Z3Integer() #CJH这里应该算是又一个只用int的罪魁祸首吧 坑,这边固定只用Z3Integer就没Z3String啥事了
			self.z3_expr = Z3String()
			print ("z3w z3_expr : ",self.z3_expr.__dict__)
			print ("z3w asserts : ",self.asserts)
			print ("z3w query : ",self.query)
			self.z3_expr.toZ3(self.solver,self.asserts,self.query)
			#print ("z3w flag")

		res = self.solver.check()
		print ("z3w res2 : ",res)
		#print(self.solver.assertions)
		self.solver.pop()
		if res == unsat:
			print("\033[1;32;40m","z3w findmodel end","\033[0m")
			return None

		# now, go for SAT with bounds
		"""
		self.N = 32
		self.bound = (1 << 4) - 1
		while self.N <= -1:
			self.solver.push()
			(ret,mismatch) = self._findModel2()
			print ("z3w ret,mismatch : ", (ret,mismatch))
			if (not mismatch): #如果完全没问题的话就可以不用继续这个循环了。有问题的话可能是overflow，就增加点位数
				break
			self.solver.pop()
			self.N = self.N+8
			if self.N <= 64: print("expanded bit width to "+str(self.N)) 
		#print("Assertions")
		#print(self.solver.assertions())
		"""
		if res == unsat:
			print ("z3w unsat")
			res = None
		elif res == unknown:
			print ("z3w unknown")
			res = None
		#elif not mismatch: #如果又是sat，又’不是mismatch‘=’验算符合‘，那就重新计算一下求解结果吧.....这里浪费计算效率了.....
		#	#print ("z3w flag1")
		#	res = self._getModel() #根据输出的参数来看，这里的getmodel和findmodel2里调用的那次计算的完全是一个东西......完全是多此一举
		#	print ("z3w res3 : ",res) #这个就算是最终的答案了
		else:
			res = None
		res = self._getModel()
		#if self.N<=64: self.solver.pop()
		print("\033[1;32;40m","z3w findmodel end","\033[0m")
		return res

	def _setAssertsQuery(self):
		self.z3_expr = Z3BitVector(self.N) #CJH用bitvector来表示int，并且通过调整长度N来判断有没有overflow
		print ("zw3 z3bitvector z3_expr : ",self.z3_expr.__dict__)
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)
		print ("zw3 toz3 asserts query : ",self.asserts,self.query)
		print ("zw3 toz3 z3_expr : ",self.z3_expr.__dict__)
		print ("zw3 toz3 z3_expr z3_vars['a'] :", self.z3_expr.z3_vars['a'].__dict__)

	def _findModel2(self): #第二次再判断一下，这次判断会比较费时间
		print("\033[1;31;40m","z3w findmodel2 start","\033[0m")
		self._setAssertsQuery()
		int_vars = self.z3_expr.getIntVars()
		res = unsat
		while res == unsat and self.bound <= (1 << (self.N-1))-1:
			self.solver.push()
			constraints = self._boundIntegers(int_vars,self.bound)
			self.solver.assert_exprs(constraints)
			res = self.solver.check()
			print ("z3w res4 : ",res)
			if res == unsat:
				self.bound = (self.bound << 1)+1
				self.solver.pop()
		if res == sat: #再次判断为sat的话就继续用getmodel来求解
			# Does concolic agree with Z3? If not, it may be due to overflow
			model = self._getModel() #model就是求解结果，如{’x‘：2}
			print ("z3w model : ",model)
			#print("Match?")
			#print(self.solver.assertions)
			self.solver.pop()
			mismatch = False
			for a in self.asserts:
				print ("z3w flag a")
				eval = self.z3_expr.predToZ3(a,self.solver,model)
				if (not eval):
					mismatch = True
					break
			if (not mismatch):
				print ("z3w flag not mismatch")
				tmp = self.z3_expr.predToZ3(self.query,self.solver,model) 
				print ("z3w tmp : ",tmp) 
				mismatch = not (not tmp) #这里是把求解的答案带入后验算这个约束条件的T/F是否符合要求。
				print ("z3w mismatch",mismatch)
			#print(mismatch)
			print("\033[1;31;40m","z3w findmodel2 end1","\033[0m")
			#print ("z3w findmodel2 end")
			return (res,mismatch)
		elif res == unknown:
			self.solver.pop()
		print("\033[1;31;40m","z3w findmodel2 end2","\033[0m")
		return (res,False)

	def _getModel2(self):
		res = {}
		model = self.solver.model()
		#print("in get model",model)
		length = len(model)
		for i in range(length):
			try:
				name = str(model[i])
				ce = model[model[i]]
				res[name] = ce
				
			except:
				pass
		return res

	def _getModel(self):
		print ("\033[1;31;40m","z3w z3 getModel start !!!!!!!!!!!!!!!!!!!!","\033[0m")
		print (self.__dict__)
		print (self.z3_expr.__dict__) 
		res = {}
		model = self.solver.model()
		print ("z3w model : ",model)
		print ("z3w model.dict : ",model.__dict__)
		print ("z3w model.model",model.model.__dict__)
		print ("z3w model.ctx",model.ctx.__dict__)
		print ("z3w model.ctx.ctx",model.ctx.ctx.__dict__)
		print ("z3w model.ctx.eh",model.ctx.eh.__dict__)
		for name in self.z3_expr.z3_vars.keys():
			print ("z3w name : ",name)
			print ("z3w self.z3_expr.z3_vars : ",self.z3_expr.z3_vars)
			print ("z3w self.z3_expr.z3_vars[name] : ",self.z3_expr.z3_vars[name].__dict__)
			#print ("z3w self.z3_expr.z3_vars[name] : ",self.z3_expr.z3_vars[name].ctx.__dict__)
			#print ("z3w self.z3_expr.z3_vars[name] : ",self.z3_expr.z3_vars[name].ast.__dict__)
			#print ("z3w self.z3_expr.z3_vars[name] : ",self.z3_expr.z3_vars[name].ctx.eh.__dict__)
			#print ("z3w self.z3_expr.z3_vars[name] : ",self.z3_expr.z3_vars[name].ctx.ctx.__dict__)


			ce = model.eval(self.z3_expr.z3_vars[name])
			#res[name] = ce.as_signed_long() #坑，没有as_signed_long就会int报错
			res[name] = ce
			#try:
				#print("z3w trying")
				#ce = model.eval(self.z3_expr.z3_vars[name])
				#print ("z3w ce : ",ce)
				#res[name] = ce.as_signed_long()
				#res[name] = ce
			#except Exception as e:
				#print(e)
		print ("z3w res5 : ",res[name])
		print ("\033[1;31;40m","z3w z3 getModel end !!!!!!!!!!!!!!!!!!!!","\033[0m")
		return res
	
	def _boundIntegers(self,vars,val):
		bval = BitVecVal(val,self.N,self.solver.ctx)
		bval_neg = BitVecVal(-val-1,self.N,self.solver.ctx)
		return And([ v <= bval for v in vars]+[ bval_neg <= v for v in vars])

