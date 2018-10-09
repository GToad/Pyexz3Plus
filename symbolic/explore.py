# Copyright: see copyright.txt
# -*- coding: utf-8 -*-  
from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type, SymbolicType

log = logging.getLogger("se.conc")

def z3str_to_pystr(z3str):
    first = ord(z3str[0])
    last = ord(z3str[len(z3str)-1])
    if((first==34)and(last==34))or((first==39)and(last==39)):
        print("quote")
        z3str = z3str[1:-1]
    index = 0
    result = ''
    while(index<len(z3str)):
        hex_index = z3str.find("\\x",index)
        print("hex_index",hex_index)
        if hex_index != -1:
            hex_value = (ord(z3str[hex_index+2]) - 48) * 16 + ord(z3str[hex_index+3]) - 48
            print("high",ord(z3str[hex_index+2]))
            print("low",ord(z3str[hex_index+3]))
            print("hex_value",hex_value)
            hex_char = chr(hex_value)
            result = result + z3str[index:hex_index]
            index = hex_index + 4
            result = result + hex_char
        else:
            result = result + z3str[index:]
            break
    return result

class ExplorationEngine:
	def __init__(self, funcinv, solver="z3"):
		self.invocation = funcinv
		print ("epl funcinv : ",funcinv.__dict__) #funcinv中已经包含了x,y等符号信息
		# the input to the function
		self.symbolic_inputs = {}  # string -> SymbolicType
		
		print ("epl before funcinv : ",funcinv.__dict__)
		# initialize
		for n in funcinv.getNames():
			print ("epl n : ",n)
			self.symbolic_inputs[n] = funcinv.createArgumentValue(n)
			print ("epl self.symbolic_inputs[n] : ",self.symbolic_inputs[n])
		print ("epl after funcinv : ",funcinv.__dict__)

		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0

		print ("epl cjh constraint start")
		self.path = PathToConstraint(lambda c : self.addConstraint(c)) #通过上下的输出和addConstraint中的输出，这行并没有实际的代码执行？！
		#这是什么语法？看样子应该是某种关联链接
		print ("epl cjh constraint end")
		print ("epl self.path : ",self.path.__dict__)
		# link up SymbolicObject to PathToConstraint in order to intercept control-flow
		symbolic_type.SymbolicObject.SI = self.path

		if solver == "z3":
			self.solver = Z3Wrapper()
		elif solver == "cvc":
			from .cvc_wrap import CVCWrapper
			self.solver = CVCWrapper()
		else:
			raise Exception("Unknown solver %s" % solver)

		# outputs
		self.generated_inputs = []
		self.execution_return_values = []

	def addConstraint(self, constraint):
		self.constraints_to_solve.append(constraint)
		print ("epl cjh constraint : ",constraint)
		# make sure to remember the input that led to this constraint
		constraint.inputs = self._getInputs()

	def explore(self, max_iterations=0,expl=False,timeout = 5):
		print ("epl explore() start !")
		
		self._oneExecution() #一开始先根据初始的参数先运行一遍这个函数
		self.timeout = timeout
		
		iterations = 1 #迭代次数记为1
		if max_iterations != 0 and iterations >= max_iterations: #判断是否超过了最大的迭代次数。
			log.debug("Maximum number of iterations reached, terminating") 
			return self.execution_return_values #是的话就直接返回当前已经获得的结果

		while not self._isExplorationComplete(): #判断是否还有没有解决的约束条件，有的话就继续
			selected = self.constraints_to_solve.popleft() #取队列里新的待解决的约束条件
			print ("epl selected : ",selected)
			if selected.processed:
				continue
			self._setInputs(selected.inputs)			
			print ("epl CJH2")
			log.info("epl Selected constraint %s" % selected)
			print ("epl Selected constraint %s" % selected)
			print ("epl cjh2")
			asserts, query = selected.getAssertsAndQuery() #每个约束条件selected都有三个组成：parent，asserts，predicate(query),详情进入这个函数
			print ("epl asserts : ",asserts)
			print ("epl query : ",query)
			
			model = self.solver.findCounterexample(asserts, query,expl)#CJH该函数有大量输出，并且最终Z3求解的结果也由它产生！
			print ("epl model: ",model)
			if model == None:
				continue
			else:
				for name in model.keys():
					self._updateSymbolicParameter(name,model[name])

			self._oneExecution(selected)

			iterations += 1
			print ("iterations : ", iterations)			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.info("Maximum number of iterations reached, terminating")
				break

		print ("epl explore() end !")
		self.path.f.close()
		return self.generated_inputs, self.execution_return_values, self.path

	# private

	def _updateSymbolicParameter(self, name, val):
		self.symbolic_inputs[name] = self.invocation.createArgumentValue(name,val)

	def _getInputs(self):
		return self.symbolic_inputs.copy()

	def _setInputs(self,d):
		self.symbolic_inputs = d

	def _isExplorationComplete(self): #是否还有待解决的约束
		num_constr = len(self.constraints_to_solve)
		if num_constr == 0:
			log.info("Exploration complete")
			return True
		else:
			log.info("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
			return False

	def _getConcrValue(self,v):
		if isinstance(v,SymbolicType):
			return v.getConcrValue()
		else:
			return v

	def _recordInputs(self):
		args = self.symbolic_inputs
		inputs = [ (k,self._getConcrValue(args[k])) for k in args ]
		self.generated_inputs.append(inputs)
		print("\033[1;31;40m",inputs,"\033[0m")
		
	def _oneExecution(self,expected_path=None):
		print ("_oneExecution start !")
		self._recordInputs() #输入
		self.path.reset(expected_path)
		print ("epl oneexecution self.path : ",self.path.__dict__)
		print ("epl oneexecution self.symbolic_inputs : ",type(self.symbolic_inputs))
		print ("epl oneexecution self.symbolic_inputs before handle: ",self.symbolic_inputs)
		for i in self.symbolic_inputs:
			print(self.symbolic_inputs[i])
			print(type(self.symbolic_inputs[i]))
			#if type(self.symbolic_inputs[i]) == str :
			#self.symbolic_inputs[i] = z3str_to_pystr(self.symbolic_inputs[i])
		print ("epl oneexecution self.symbolic_inputs after handle: ",self.symbolic_inputs)
		try:
			ret = self.invocation.callFunction(self.symbolic_inputs) #这里输出了一大堆东西，并最终获得本次执行的输出结果
		except e:
			print(e)
		print("\033[1;31;40m",ret,"\033[0m")
		self.execution_return_values.append(ret)
		print ("_oneExecution end !")

