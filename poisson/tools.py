#from . import DEF
import numpy as np
from poisson import DEF

import os
from copy import deepcopy 
from pylada.jobfolder import JobFolder
from pylada.misc import Changedir

def showIODebug(func):
	def new(*args,**kwargs):
		print("----------start-----------")
		print(args)
		print(kwargs)
		tmp = func(*args,**kwargs)
		print(tmp)
		print("-----------end------------")
		return tmp
	return new


class job(object):
	"""docstring for job"""
	def __init__(self, name = os.getcwd()):
		super(job, self).__init__()
		self.name = name
		self.params = {"call":self._blank}
	
	def __truediv__(self, other):
		if isinstance(other, str):
			return job(name = os.path.join(self.name, other))
		else:
			raise ValueError()

	@staticmethod
	def _blank(job):
		return [job]

	def __str__(self):
		tmp = "job name = %s\n" % (self.name)
		for key,value in self.params.items():
			tmp += "    %s = %s\n" % (key,str(value))
		return tmp[:-1]

def _blank(job):
	"""do noting"""
	return [job]

def rootJob():
	"""create a root Job"""
	job = JobFolder()
	job.params["call"] = _blank
	return job


def layer(func):
	def new(jobs):
		for s_job in jobs:
			for r_job in func(s_job):
				yield r_job
	return new

def cellcall(beforeCall):
	def www(func):
		def new(job):
			beforeCall(job)
			return func(job)
		return new
	return www


def interface(func):
	def new(inputLayer, **kwargs):
		if inputLayer == None:
			inputLayer = _blank
		call = func(**kwargs) # layer
		def rlink(i):
			return call(inputLayer(i))
		return rlink
	return new


def loopToRelax(maxLoop = 10):
	def www(func):
		def new(job):
			print("-----------COMPUTE:start-----------")
			print("name:" + job.name[1:])
			if maxLoop > 0:
				for i in range(maxLoop - 1):
					with Changedir("Relax_%02d" % i) as pwd:
						func(job)
					structure = deepcopy(job.params["result"].structure)
					job.params["structure"] = structure
					if len(job.params["result"].total_energies) == 1 :
						break
				else:
					raise Exception("It's not convergence")
			func(job)
			print("-----------COMPUTE:end-------------")
		return new
	return www

def fallback(r_job):
	def www(func):
		def new(job):
			with Changedir(r_job) as pwd:
				func(r_job)
			job.params['structure'] = r_job.params['result'].structure
			job.params['vasp'] = r_job.params['vasp']
			job.params['result'] = r_job.params['result']
			job.params['optcell'] = r_job.params['optcell']
		return new
	return www


def atom_replace(atoms_type,init = "None"):
	init = [init]
	#@showIODebug
	def new(atom):
		if init[-1] == "None":
			init.append(atom.type)
			return atoms_type[0]
		elif init[-1] == atom.type:
			return atoms_type[0]
		else:
			atoms_type.remove(atoms_type[0])
			init.append(atom.type)
			return atoms_type[0]
	return new 

def strainScan(minStrain, maxStrain, stepStrain, DIRECTION = DEF.BOTH_AB):
	"""
		to create names and scales list for strain layer
		@params minStrain,maxStrain,stepStrain : use to np.arange
		@params DIRECTION : a Enum type for DEF.ONLY_A DEF.ONLY_B DEF.BOTH_AB
		@return names,scales
	"""
	assert DIRECTION in [DEF.ONLY_A,DEF.ONLY_B,DEF.BOTH_AB]

	direction = [["A"],["B"],["A","B"]][DIRECTION]
	strainList = list(np.arange(minStrain,maxStrain,stepStrain))
	names = [];scales = [];optcells = []
	for direct,strain in [(x,y) for x in direction for y in strainList]:
		names.append("strain_%g_%s" % (strain,direct))
		scale = np.ones(3)
		scale[0 if direct == "A" else 1] = strain
		scales.append(scale)

		optcell = [1,1,0]
		optcell[0 if direct == "A" else 1] = 0
		optcells.append(optcell)
	return [names,scales,optcells]

def elementScan(elements):
	"""
		e.g : elementScan([["C","Si","Ge","Sn","Pt"],["O","S","Se","Te"]])
	"""
	def into(elements):
		if len(elements) == 1:
			return elements
		materials = []
		for ele,nele in [(x,y) for x in elements[0] for y in elements[1]]:
			materials.append(ele + "-" + nele)
		if len(elements) == 2:
			return materials
		f = [materials]
		f.extend(elements[2:])
		return into(f)
	names = [];materials = []
	for intoElement in into(elements):
		names.append(intoElement.replace("-",""))
		materials.append(intoElement)
	return names,materials

def writeOPTCELL(optcell):
	with open("OPTCELL","w") as wfile:
		wfile.write("%d%d%d" % tuple(optcell))


def poissonCalc(xData,yData):
	from scipy import polyfit
	value = polyfit(xData,yData,3)
	return value

def poissonShow(name,xData,yData,zData,energry):
	print("---------" + name + "---------")
	print("poly: %.3fx**3 + %.3fx**2 + %.3fx + %.3f" % tuple(poissonCalc(xData,yData)))
	print("stretch:%s" % " ".join(["%.3f " % i for i in xData]))
	print("strain:%s" % " ".join(["%.3f " % i for i in yData]))
	print("vacuum:%s" % " ".join(["%.3f " % i for i in zData]))
	print("energry:%s" % " ".join(["%.3f " % i for i in energry]))
	print("---------------------------------------------")

def getSpaceGroupName(path = "POSCAR"):
	import os
	abspath = os.path.abspath(path)
	for i in os.popen("aflow --kpath < POSCAR | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
		spacegroupname = i[:-1]
	return spacegroupname
