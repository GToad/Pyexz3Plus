# Copyright: see copyright.txt
#coding=utf-8
class FunctionInvocation:
	def __init__(self, function, reset):
		self.function = function
		self.reset = reset
		self.arg_constructor = {}
		self.initial_value = {}

	def callFunction(self,args): #返回运行的实际结果
		print ("inv self.function : ",self.function.__dict__)
		print ("inv args : ",args)
		self.reset()
		print ("inv callfunction end1")
		tmp = self.function(**args)
		print ("inv tmp : ",tmp)
		return tmp

	def addArgumentConstructor(self, name, init, constructor):
		self.initial_value[name] = init
		self.arg_constructor[name] = constructor

	def getNames(self):
		return self.arg_constructor.keys()

	def createArgumentValue(self,name,val=None):
		if val == None:
			val = self.initial_value[name]
		
		return self.arg_constructor[name](name,val)

	

