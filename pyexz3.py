# Copyright: see copyright.txt
# -*- coding: utf-8 -*-  
import os
import sys
import logging
import traceback
from optparse import OptionParser

from symbolic.loader import *
from symbolic.explore import ExplorationEngine

print("PyExZ3 (Python Exploration with Z3)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

usage = "usage: %prog [options] <path to a *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
parser.add_option("-g", "--graph", dest="dot_graph", action="store_true", help="Generate a DOT graph of execution tree")
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)
parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3", default=False)
parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")
parser.add_option("-t", "--type", dest="params_type", action="store", help="Split params type", default="")

(options, args) = parser.parse_args()

if not (options.logfile == ""):
	logging.basicConfig(filename=options.logfile,level=logging.DEBUG)

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)

solver = "cvc" if options.cvc else "z3"

filename = os.path.abspath(args[0])
	
# Get the object describing the application
app = loaderFactory(filename, options.entry, options.params_type)
if app == None:
	sys.exit(1)

print ("Exploring " + app.getFile() + "." + app.getEntry())

result = None
try:
	inv = app.createInvocation()
	print ("py3 inv : ",inv)
	engine = ExplorationEngine(inv, solver=solver) #初始化，把目标函数的参数都符号化，并且赋予一个初始值，一般为0
	generatedInputs, returnVals, path = engine.explore(options.max_iters)
	print ("py3 CJH1")
	print (generatedInputs)
	print (returnVals)
	print (path.__dict__)
	print ("py3 CJH11")
	# check the result
	result = app.executionComplete(returnVals)

	# output DOT graph
	if (options.dot_graph):
		file = open(filename+".dot","w")
		file.write(path.toDot())	
		file.close()

except ImportError as e:
	# createInvocation can raise this
	logging.error(e)
	sys.exit(1)

if result == None or result == True:
	sys.exit(0);
else:
	sys.exit(1);	
