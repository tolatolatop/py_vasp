def bandDrawing(vasppath):
	import os,re
	with open(os.path.join(vasppath,"KPOINTS"),"r") as rfile:
		tmp = rfile.readlines()
	head = tmp[0];kint = int(tmp[1])
	re_str = re.complie("[A-Z\-]+")
	kpath = re_str.findall(head)
	kpath = [i.splite("-") for i in kpath]
	for line in kpath:
		for keypoints in line:
			pass

def dosDrawing(vasppath):
	pass

def strainData(vasppath):
	from pylada.vasp import Extract
	from numpy.linalg import norm
	structure = Extract(vasppath).structure
	cell = structure.cell
	result = {"a-length": norm(cell[0,:]),"b-length": norm(cell[1,:]),"c-length":norm(cell[2,:])}
	xslength = [];yslength = [];zslength = []
	for atom in structure:
		xslength.append(atom.pos[0])
		yslength.append(atom.pos[1])
		zslength.append(atom.pos[2])
	result["x-length"] = max(xslength) - min(xslength)
	result["y-length"] = max(yslength) - min(yslength)
	result["z-length"] = max(zslength) - min(zslength)
	return result

def poissonData(vasppathList, standpath, xaxis = "a-length", yaxis = "b-length"):
	stand = strainData(standpath)
	dataList = []
	for vasppath in vasppathList:
		tmp = strainData(vasppath)
		dataList.append(tmp)
	xaxisList = [];yaxisList = []
	for data in dataList:
		xaxisList.append(data[xaxis] - stand[xaxis])
		yaxisList.append(data[yaxis] - stand[yaxis])
	datalist = list(zip(xaxisList,yaxisList))
	datalist.sort(key = lambda x:x[0])
	return {"xaxis":[i[0] for i in datalist],"yaxis":[j[1] for j in datalist]}