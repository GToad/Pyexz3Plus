# Copyright: copyright.txt
# -*- coding: utf-8 -*-  
import inspect
import re
import os
import sys
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger, SymbolicStr, getSymbolic

# The built-in definition of len wraps the return value in an int() constructor, destroying any symbolic types.
# By redefining len here we can preserve symbolic integer types.
import builtins
#import __builtins__
print ("ldr builtins.len 1")
builtins.len = (lambda x : x.__len__())
print ("ldr builtins.len !")

class Loader:
	def __init__(self, filename, entry, params_type):
		self._fileName = os.path.basename(filename)
		self._fileName = self._fileName[:-3]
		if (entry == ""):
			self._entryPoint = self._fileName
		else:
			self._entryPoint = entry;
		self._resetCallback(True)
		self.types = params_type.split(",")
		self.params_dict = {}

	def get_param_type(self, name):
		if name in self.params_dict.keys():
			return self.params_dict[name]
		else:
			return 'cannot find the name'

	def getFile(self):
		return self._fileName

	def getEntry(self):
		return self._entryPoint
	
	def createInvocation(self): #该函数中载入了目标的基本信息，包括参数符号x,y等
		print ("ldr self : ",self.__dict__)
		inv = FunctionInvocation(self._execute,self._resetCallback)
		#print ("ldr self.app.__dict__ : ",self.app.__dict__) 
		func = self.app.__dict__[self._entryPoint]
		argspec = inspect.getargspec(func) #这里载入了参数符号信息如x，y
		print ("ldr argspec : ",argspec) #eg ldr argspec :  ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=None)
		print ("ldr func.__dict__ : ",func.__dict__)
		# check to see if user specified initial values of arguments
		if "concrete_args" in func.__dict__:
			for (f,v) in func.concrete_args.items():
				if not f in argspec.args:
					print("Error in @concrete: " +  self._entryPoint + " has no argument named " + f)
					raise ImportError()
				else:
					Loader._initializeArgumentConcrete(inv,f,v) #如果这个参数被预设值数值了，那就初始化的时候按照这个数值初始化
		if "symbolic_args" in func.__dict__:
			for (f,v) in func.symbolic_args.items():
				if not f in argspec.args:
					print("Error (@symbolic): " +  self._entryPoint + " has no argument named " + f)
					raise ImportError()
				elif f in inv.getNames():
					print("Argument " + f + " defined in both @concrete and @symbolic")
					raise ImportError()
				else:
					s = getSymbolic(v)
					if (s == None):
						print("Error at argument " + f + " of entry point " + self._entryPoint + " : no corresponding symbolic type found for type " + str(type(v)))
						raise ImportError()
					Loader._initializeArgumentSymbolic(inv, f, v, s) #如果这个参数被指定符号化了，那初始化的时候就按照指定符号初始化
		idx = 0
		for a in argspec.args:
			if not a in inv.getNames(): #剩余没有被任何预设置的参数将默认设定为值为0的int
				#Loader._initializeArgumentSymbolic(inv, a, '0', SymbolicStr) #cjh这就是都变成int的原因
				#Loader._initializeArgumentSymbolic(inv, a, 0, SymbolicInteger)
				if self.types[idx] == 'int':
					Loader._initializeArgumentSymbolic(inv, a, 0, SymbolicInteger)
					self.params_dict[a] = 'int'
				else:
					Loader._initializeArgumentSymbolic(inv, a, "0", SymbolicStr)
					self.params_dict[a] = 'string'
				idx = idx + 1
				print ("ldr _initializeArgumentSymbolic ok")
		print ("ldr inv : ",inv.__dict__)
		return inv

	# need these here (rather than inline above) to correctly capture values in lambda
	def _initializeArgumentConcrete(inv,f,val):
		inv.addArgumentConstructor(f, val, lambda n,v: val)

	def _initializeArgumentSymbolic(inv,f,val,st):
		inv.addArgumentConstructor(f, val, lambda n,v: st(n,v))

	def executionComplete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			return self._check(return_vals, self.app.__dict__["expected_result"]())
		if "expected_result_set" in self.app.__dict__:
			return self._check(return_vals, self.app.__dict__["expected_result_set"](),False)
		else:
			print(self._fileName + ".py contains no expected_result function")
			return None

	# -- private

	def _resetCallback(self,firstpass=False):
		self.app = None
		if firstpass and self._fileName in sys.modules:
			print("There already is a module loaded named " + self._fileName)
			raise ImportError()
		try:
			if (not firstpass and self._fileName in sys.modules):
				del(sys.modules[self._fileName])
			self.app =__import__(self._fileName)
			if not self._entryPoint in self.app.__dict__ or not callable(self.app.__dict__[self._entryPoint]):
				print("File " +  self._fileName + ".py doesn't contain a function named " + self._entryPoint)
				raise ImportError()
		except Exception as arg:
			#print(Exception)
			print("Couldn't import " + self._fileName)
			print(arg)
			raise ImportError()

	def _execute(self, **args):
		print ("ldr self._entryPoint", self._entryPoint)
		print ("ldr args", args) #在这里，输入依然是字符串，但是在下面这个报错的函数中字符串却又变成了int
		print ("ldr self.app.__dict__[self.entryPoint]", self.app.__dict__[self._entryPoint])
		tmp = self.app.__dict__[self._entryPoint](**args)
		print ("ldr tmp : ",tmp)
		return tmp

	def _toBag(self,l):
		bag = {}
		for i in l:
			if i in bag:
				bag[i] += 1
			else:
				bag[i] = 1
		return bag

	def _check(self, computed, expected, as_bag=True):
		b_c = self._toBag(computed)
		b_e = self._toBag(expected)
		if as_bag and b_c != b_e or not as_bag and set(computed) != set(expected):
			print("-------------------> %s test failed <---------------------" % self._fileName)
			print("Expected: %s, found: %s" % (b_e, b_c))
			return False
		else:
			print("%s test passed <---" % self._fileName)
			return True
	
def loaderFactory(filename,entry,params_type):
	if not os.path.isfile(filename) or not re.search(".py$",filename):
		print("Please provide a Python file to load")
		return None
	try: 
		dir = os.path.dirname(filename)
		sys.path = [ dir ] + sys.path
		ret = Loader(filename,entry,params_type)
		return ret
	except ImportError:
		sys.path = sys.path[1:]
		return None


