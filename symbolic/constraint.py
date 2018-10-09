# Copyright: see copyright.txt
# -*- coding: utf-8 -*-  
import logging

log = logging.getLogger("se.constraint")

class Constraint:
	cnt = 0
	"""A constraint is a list of predicates leading to some specific
	   position in the code."""
	def __init__(self, parent, last_predicate):
		self.inputs = None
		self.outinputs = None
		self.predicate = last_predicate
		self.processed = False
		self.parent = parent
		self.children = []
		self.id = self.__class__.cnt
		self.__class__.cnt += 1
		self.height = -1

	def __eq__(self, other):
		"""Two Constraints are equal iff they have the same chain of predicates"""
		if isinstance(other, Constraint):
			if not self.predicate == other.predicate:
				return False
			return self.parent is other.parent
		else:
			return False

	def getAssertsAndQuery(self): #CJH本函数非常重要！可以看出，每个约束条件都有三个部分：parent，asserts，predicate
		self.processed = True #将其标为已经处理过了

		# collect the assertions
		asserts = []    #asserts代表的是这个约束条件的前置条件，也就是之前已经被确定的那些
		tmp = self.parent  #并且asserts的一个重要来源就是下面代码中可以看出的：parent的predicate（query）
		print ("cst parent : ",tmp) #因为父节点的predicate肯定是子节点所需要满足的先决条件。
		while tmp.predicate is not None:
			asserts.append(tmp.predicate)
			tmp = tmp.parent
		print ("cst asserts : ",asserts)
		print ("cst predicate : ",self.predicate)
		return asserts, self.predicate	       #最后返回asserts和predicate（query） ，因为这两个对于Z3求解器来说是一样的
											#都是Z3求解的时候必须满足的条件，对于Z3来说，它们是“与”的关系
											#所以这个函数就是将输入的selected给转换成Z3实际这次需要解决的问题

	def getLength(self):
		if self.parent == None:
			return 0
		return 1 + self.parent.getLength()

	def __str__(self):
		return str(self.predicate) + "  (processed: %s, path_len: %d)" % (self.processed,self.getLength())

	def __repr__(self):
		s = repr(self.predicate) + " (processed: %s)" % (self.processed)
		if self.parent is not None:
			s += "\n  path: %s" % repr(self.parent)
		return s

	def searchPredicate(self,target,root):
		length = 1
		
		if isinstance(target,Constraint):
			while( target != root):
				if( self.predicate.ln != target.predicate.ln):
					target = target.parent
					length += 1
					continue
				else:
					# simply compare ln
					if self.predicate.result != target.predicate.result and self.predicate.symtype.symbolicEq(target.predicate.result):
						return -1
					else:
						return length
						
			return -1

	def findChild(self, predicate):
		for c in self.children:
			if predicate == c.predicate:
				return c
		return None

	def addChild(self, predicate,h=0):
		assert(self.findChild(predicate) is None)
		c = Constraint(self, predicate)
		self.children.append(c)
		c.height = h
		return c

