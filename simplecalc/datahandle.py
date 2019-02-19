def bandDrawing(vasppath):
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
	xaxisList = [0];yaxisList = [0]
	for data in dataList:
		xaxisList.append(data[xaxis] - stand[xaxis])
		yaxisList.append(data[yaxis] - stand[yaxis])
	xaxisList.sort();yaxisList.sort()
	return {"xaxis":xaxisList,"yaxis":yaxisList}

