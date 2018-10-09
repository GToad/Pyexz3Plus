import pdb
def cjhtest1(a,b):
	print ("running type(b.val) : ",type(b.val))
	print ("running b.__dict__ : ",b.__dict__)
	print ("running b : ",b)
	print ("running type(b) : ",type(b))

	if (len(str(a))==1):
		if b == "0":
			return 1
		else:
			print ('running b is ',b)
		return 3
	return 0


'''
print (cjhtest1(0,0))
print (cjhtest1("good2","good"))
print (cjhtest1("good3","good"))
entry_point = cjhtest1
args = {'a':'0','b':'0'}
print (entry_point(**args))
'''