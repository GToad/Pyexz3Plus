
from z3 import *
from .expression import Z3Expression
import codecs
#from .integer import Z3Integer

class Z3String(Z3Expression):
	"""
	def __init__(self,solver,name = "",a = [],length = 0,sub = []):
		self.name = name
		self.strs = a
		# concrete length
		self.c_l = length		
		self.l_n = name+"_l"
		#print ("Z3str l_n type : ",type(self.l_n))
		self.solver = solver
		self.sub = sub
		
		# symbolic length
		if sub != []:
	 		return None
			#c_l remain 0
			#self.c_l += s.c_l
		elif a == []:
			print("string.py s_l")
			self.s_l = self._variable(self.l_n,self.solver)
			print(self.s_l.__dict__)
			d = String(name)
			self.s_l = Length(d)
			self._initZ3Variable()
		else:
			if(isinstance(a[0],z3.ArithRef)):
				# Int()
				#self.s_l = self._variable(self.l_n,self.solver)
				print ("string.py flag1")
				self.s_l = self._constant(self.c_l,solver)
				print ("string.py flag2")
				self.c_l = len(self.strs)
				#self._initZ3Variable() 
			# constant string have constant length
			else:
				self.s_l = self._constant(self.c_l,solver)
		print ("Z3str l_n type : ",type(self.l_n))
		"""

	def isVariable(self):
		name_array = [str(a) for a in self.strs]
		if self.sub != []: return True
		for a in name_array:
			if a.isdigit():
				return False
		return True
	
	# expand to str  length
	def expandLength(self,length):
		if(self.sub == []):
			if(self.isVariable()):
				self._createZ3Variable(self.name,length,self.solver)
				return True
			else:
				return False
		else:
			t_n = 0
			sl = 0
			for s in self.sub:
				if s.isVariable():
					t_n += 1
				else:
					sl += s.getLength()
			length = length - sl
			for i in range(t_n):
				s = self.sub[i]
				
				if(i == t_n -1):
					s.expandLength(int(length/t_n) + length%t_n)
				else:
					s.expandLength(int(length/t_n))

	def getLength(self):
		tmp_l = 0
		if(self.sub == []):
			tmp_l += self.c_l
			return tmp_l
		else:
			for s in self.sub:
				tmp_l += s.getLength()
			return tmp_l

	def getStr(self):
		return self.strs

	def length(self):
		
		return self.s_l
	def Index(self,i):
		return self.strs[i]
	def add(self,other):
		#print('Add,',self.strs,other.strs)
		return Z3Str(self.solver,'Concat',a=[],length = 0,sub = [self,other])
	def contain(self,other):
		# need to operate on original str
		tmp_list = []
		if self.sub == []:
			self._createZ3Variable(self.name,self.c_l+other.c_l,1)
			tmp = Z3Str(self.solver,self.name, a = [self.strs[c_l+1:]],length = other.c_l,sub = [])
			return self.equal(tmp,other)

	def getitem(self,i,j = -1):
		if (j == -1):
			try:
				# create item
				i = i.as_long()
				if(i < self.c_l):
					
					tmp = Z3String(self.solver,self.name,a = [self.strs[i]],length = 1,sub = [])
				else:
					self._createZ3Variable(self.name,i+1,1)
					tmp = Z3String(self.solver,self.name,a = [self.strs[i]],length = 1,sub = [])
					
				return tmp
			except:
				print('in getitem error')
				return self.strs[0]
		else:
			i = i.as_long()
			j = j.as_long()
			if j > self.c_l:
				# TO DO : change it to sub
				self._createZ3Variable(self.name,j+1,1)
			tmp = Z3String(self.solver,self.name,a = [self.str[i:j]],length = j-i,sub = [])
			return tmp

	def equalbak(self,z3_l,z3_r):
		return 0

				
			
	def equal(self,other,env = 0):
		tmp_list = []
		if isinstance(other,Z3String):
			#TO DO: APPEND LENGTH
			#Notice: we just adjust length to the target's length
			
			if self.sub == []:
				tmp_length = other.getLength()
				self._createZ3Variable(self.name,tmp_length,self.solver)
				
				for i in range(tmp_length):
					print("string.py self.strs : ",self.strs)
					print("string.py other.strs : ",other.strs)
					print("string.py self.strs : ",type(self.strs[i]))
					print("string.py other.strs : ",type(other.strs[i]))
					tmp_list.append(self._wrapIf(self.strs[i] == other.strs[i],self.solver,env))
				tmp_list.append(self._wrapIf(self.s_l == other.s_l,self.solver,env))
				tmp_list.append(self._wrapIf(self.s_l >= self._constant(0,self.solver),self.solver,env))
				return tmp_list
			else:
				# other is not substring divide other str into n parts
				# assume each part's length is the same
				if(other.sub == []):
					o_l = other.getLength()
					sl = 0
					t_n = 0
					for s in self.sub:
						if s.isVariable():t_n += 1
						else:sl += s.getLength()
					# calc the extra length
					if o_l < sl: return []
					t_t = int((o_l - sl) / t_n)
					self.expandLength(o_l)
					j = 0
					for i in range(len(self.sub)):
						sub_length = self.sub[i].getLength()
						if(i != t_n -1):
							if(self.sub[i].isVariable()):
								re = self.sub[i].equal(Z3String(self.solver,a = other.strs[j:j+sub_length]\
									,sub = [],length = sub_length))
									
							else:
								re = self.sub[i].equal(Z3String(self.solver,a = other.strs[j:j+sub_length]\
									,sub = [],length = sub_length))
							
						else:
							#print('sub_length',sub_length)
							re = self.sub[i].equal(Z3String(self.solver,a = other.strs[j:j+sub_length],sub = [],length =sub_length))
						j = j+self.sub[i].getLength()
						#print('re',re)
						tmp_list.extend(re)
					return tmp_list
				else:
					print("TO DO")
				
	def _strtoint(self,s):
		return int(codecs.encode(s.encode('utf8'),'hex_codec'),16)
	def _initZ3Variable(self):
		self._createZ3Variable(self.name,self.c_l,self.solver)

	def _ItembyName(self,name):
		name_array = [str(a) for a in self.strs]
		if name in name_array:
			return True
		else:
			return False
	def _createZ3Variable(self,name,length,solver):
		tmp_i = len(self.strs)
		if tmp_i <= length:
			for i in range (tmp_i,length):
			# get last item's name and append
				t_n = name + '_' + str(i)
				if(not self._ItembyName(t_n)):
					self.strs.append(self._variable(t_n,solver))
		else:
			for i in range (tmp_i - length):
				self.strs.pop()
		self.c_l = length

	def _wrapIf(self,e,solver,env):
		print ("Z3Str flag1")
		if env == None:
			return If(e,self._constant(1,solver),self._constant(0,solver))
		else:
			return e
			
	def _variable(self,name,solver):
		return Int(name,solver.ctx)

	def _isZ3(self,o):
		if o == [] or o == 0:
			return False
		return True

	def _isStrVar(self,v):
		return isinstance(v,StrRef)

	def length(self,s_l):
		return Length(s_l)

	def slice(self,z3_l,z3_r,z3_3):
		#substr111 = String("subtr1111")
		#self.solver.add(Length(substr111)==z3_r)
		#substr222 = String("subtr2222")
		return Extract(z3_l,z3_r,z3_3-z3_r)

	#def _variable(self,name,solver): #cjh 这里有个坑，这个类下面的_variable依然要用int，不能用String
		#return String(name,solver.ctx)

	def _constant(self,v,solver):
		print("string.py v : ",v)
		print("string.py solver.ctx : ",solver.ctx.ctx.__dict__)
		#print ("string.py v : " , v)
		#print ("string.py solver.ctx : " , solver.ctx)
		return IntVal(v,solver.ctx)

