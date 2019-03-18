def createBAND(fermi = None,savepath = "./bnd.dat"):
	"""
	@savepath 
	"""
	meta,title,data = getBandData("EIGENVAL")
	with open(savepath,"w") as file:
		for i in range(meta[1]):
			mystr = str(l2[i])
			for j in range(meta[2]):
				mystr += "    %f" % data[i*meta[2]+j][1]
			mystr += "\n"
			file.write(mystr)


def getBandData(path = "EIGENVAL"):
	line = ""
	with open(path,"r") as file:
		for i in range(5):
			file.readline() # Discard the first 5 lines
		line = file.readline()
		meta = getnumber(line,3,dtype="int")
		data ,title = list() , list()
		for i in range(meta[1]):
			file.readline()
			title.append(getnumber(file.readline(),4,dtype="float"))
			for j in range(meta[2]):
				data.append(getnumber(file.readline(),None,dtype="float"))
	return meta,title,data


def getnumber(tstr ,number = 1,dtype = "float"):
	import re
	if dtype == "float":
		re_test = re.compile("[0-9.\+\-E]+")
		convert = float
	elif dtype == "int":
		re_test = re.compile("[0-9]+")
		convert = int
	r = re_test.findall(tstr)[0:number]
	if number == None:
		number = len(r)
	if len(r) != number:
		raise ValueError("Error in %s" % (tstr))
	else:
		result = [convert(i) for i in r]
	return result
