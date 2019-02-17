import os
import sys
from poisson import layer
from poisson import config
from poisson import tools

def nametospecie(poscar):
	import re
	specie = re.findall("[a-zA-Z_]+",poscar)
	specie = "-".join(specie[1:])
	print(specie)
	return specie

def bandCalc(poscar, root, inherit = True, common = config.COMMON["nodeParams"]):
	job = root / poscar / "band"
	job.params["call"] = tools.job._blank
	if inherit:
		scfCalc(poscar, root, common = common)
	rlayer = layer.getincar(None,incar = "../../incar/INCAR_BAND")
	rlayer = layer.copychgcarfrom(rlayer,dirname = "../scf")
	rlayer = layer.copywavecarfrom(rlayer,dirname = "../scf")
	rlayer = layer.loadstructure(rlayer,filename = "../relax/CONTCAR")
	rlayer = layer.aflowkpoints(rlayer)
	rlayer = layer.setoptcell(rlayer, optcell = [1,1,0])
	#rlayer = layer.aflowkpoints(rlayer,filename = "../relax/KPOINTS")
	rlayer = layer.setspecie(rlayer,specie = nametospecie(poscar))
	rlayer= layer.compute(rlayer,common = common)
	for i in rlayer(job):
		i.params["call"](i)

def relaxCalc(poscar, root, common = config.COMMON["nodeParams"]):
	job = root / poscar / "relax"
	job.params["call"] = tools.job._blank
	rlayer = layer.getincar(None, incar = "../../incar/INCAR_RELAX_PBE")
	rlayer = layer.loadstructure(rlayer,filename = "../../poscar_all/" + poscar)
	rlayer = layer.loadkpoints(rlayer,filename = "../../kpoints/KPOINTS_RELAX")
	rlayer = layer.setspecie(rlayer,specie = nametospecie(poscar))
	rlayer = layer.setoptcell(rlayer, optcell = [1,1,0])
	rlayer = layer.compute(rlayer,common = common, maxLoop = 10)
	for i in rlayer(job):
		i.params["call"](i)

	

def scfCalc(poscar, root, inherit = True, common = config.COMMON["nodeParams"]):
	job = root / poscar / "scf"
	job.params["call"] = tools.job._blank
	if inherit:
		relaxCalc(poscar, root, common = common)
	rlayer = layer.getincar(None,incar = "../../incar/INCAR_SCF")
	rlayer = layer.loadkpoints(rlayer,filename = "../relax/KPOINTS")
	rlayer = layer.loadstructure(rlayer,filename = "../relax/CONTCAR")
	rlayer = layer.setspecie(rlayer,specie = nametospecie(poscar))
	rlayer = layer.setoptcell(rlayer, optcell = [1,1,0])
	rlayer= layer.compute(rlayer,common = common)
	for i in rlayer(job):
		i.params["call"](i)


def dosCalc(poscar, root, inherit = True, common = config.COMMON["nodeParams"]):
	job = root / poscar / "dos"
	job.params["call"] = tools.job._blank
	if inherit:
		scfCalc(poscar, root, common = common)
	rlayer = layer.getincar(None,incar = "../../incar/INCAR_DOS")
	rlayer = layer.copychgcarfrom(rlayer,dirname = "../scf")
	rlayer = layer.copywavecarfrom(rlayer,dirname = "../scf")
	rlayer = layer.loadkpoints(rlayer,filename = "../relax/KPOINTS")
	rlayer = layer.loadstructure(rlayer,filename = "../relax/CONTCAR")
	rlayer = layer.setspecie(rlayer,specie = nametospecie(poscar))
	rlayer = layer.setoptcell(rlayer, optcell = [1,1,0])
	rlayer= layer.compute(rlayer,common = common)
	for i in rlayer(job):
		i.params["call"](i)


def socscfCalc(poscarpath):
	pass

def socbandCalc(poscarpath):
	pass

def opticCalc(poscarpath):
	pass

def strainCalc(poscarpath):
	pass

def hsebandCalc(poscar, root, inherit = True, common = config.COMMON["nodeParams"]):
	job = root / poscar / "dos"
	job.params["call"] = tools.job._blank
	if inherit:
		scfCalc(poscar, root, common = common)
	rlayer = layer.getincar(None,incar = "$INCAR/INCAR_HSE_BAND")
	rlayer = layer.copywavecarfrom(rlayer,dirname = "../scf")
	rlayer = layer.loadkpoints(rlayer,filename = "../relax/KPOINTS")
	#rlayer = layer.specialkpoints(rlayer,filename = "../relax/KPOINTS")
	rlayer = layer.loadstructure(rlayer,filename = "../relax/CONTCAR")
	rlayer = layer.setspecie(rlayer,specie = nametospecie(poscar))
	rlayer = layer.setoptcell(rlayer, optcell = [1,1,0])
	#rlayer= layer.compute(rlayer,common = common)
	for i in rlayer(job):
		i.params["call"](i)


def poscarLoadingTools(path):
	"""
		@param inputlayer : front layer 
		@param path : path of POSCAR_ALL
		@return a dict of outputLayer 
	"""
	poscarList = []
	from pylada.crystal import read
	for r,d,files in os.walk(path):
		for filename in files:
			poscarList.append(filename)

	outLayerDict = {}
	for poscar in poscarList:
		yield poscar

