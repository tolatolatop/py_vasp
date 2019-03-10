import re


if __name__ == "__main__":
	with open("CHGCAR","r") as rfile:
		chgcar = rfile.readlines()
	notnull = re.compile(r"[\S]")
	getnumber = re.compile(r"[0-9Ee+-.]+")
	for i in chgcar:
		if not notnull.findall(i):
			head = chgcar.index(i) + 1
			break
	datasize = [int(i)  for i in getnumber.findall(chgcar[head])]
	import numpy as np
	data = []
	g = 0
	metalength = None
	for i in chgcar[head+1:]:
		if g == datasize[0] * datasize[1] * datasize[2]:
			print(i)
			break
		tmpdata = [float(j) for j in getnumber.findall(i)]
		if metalength is None:
			metalength = len(tmpdata)
		data.extend(tmpdata)
		g += metalength
	data = np.array(data)
	data.reshape(datasize)
	np.save("chgcardata",data)