from copy import deepcopy 
import numpy as np
from pylada.misc import Changedir

#import sys
#AbsolutePath = os.path.abspath(__file__)
#SuperiorCatalogue = os.path.dirname(AbsolutePath)
#sys.path.insert(0,SuperiorCatalogue)
from poisson.exception import vaspruntime
from poisson import tools

@tools.interface
def vasp(name, incar):
	"""
		return a function to set a new vasp form incar
		@param inputlayer : a function created by front layer
		@param names : layer name
		@param incar : path of incar for loading
	"""
	from pylada.vasp import read_incar
	vasp = read_incar(incar)
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			job.params["vasp"] = vasp
		t_job = job / name
		t_job.params["call"] = func
		return [t_job]
	return new


@tools.interface
def structure_layer(name, struct):
	"""
		return a function to set structure cell and atom pos
		@param inputlayer : a function created by front layer
		@param name : layer name
		@param struct : a struct from read.poscar
	"""
	struct = deepcopy(struct)
	from pylada.crystal import read
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job): # before changing params we should deepcopy it. 
			if "structure" in job.params.keys():
				job.params['structure'] = deepcopy(job.params['structure'])
				job.params['structure'].cell = struct.cell
				job.params['optcell'] = [1,1,1]
				for source_atom,destination_atom in zip(struct,job.params['structure']):
					destination_atom.pos = source_atom.pos
			else:
				job.params["structure"] = struct
				job.params['optcell'] = [1,1,0]
		t_job = job / name
		t_job.params["call"] = func
		return [t_job]
	return new

@tools.interface
def materials(names, species):
	"""
		return a function to set atom type
		@param inputlayer : a function created by front layer
		@param names : a list composed of name
		@param speices : a list composed of species and their potcar like "Re_v-Se"
	"""
	species = deepcopy(species)
	@tools.layer
	def new(job):
		for name,specie in zip(names, species):
			pot_type = [pot for pot in specie.split("-")]
			atoms_type = [atom_type.split("_")[0] for atom_type in pot_type]
			@tools.cellcall(job.params["call"])
			def func(job): # before changing params we should deepcopy it. 
				job.params['structure'] = deepcopy(job.params['structure'])
				job.params['vasp'] = deepcopy(job.params['vasp'])
				call = tools.atom_replace(deepcopy(atoms_type))
				for destination_atom in job.params["structure"]:
					destination_atom.type = call(destination_atom)
				for atom,pot in zip(atoms_type,pot_type):
					job.params['vasp'].add_specie = atom,"$PAW/" + pot
			t_job = job / name
			t_job.params["call"] = func
			yield t_job
	return new

@tools.interface
def strain(names, scales, optcells):
	"""
		return a funciton to set job 
		@param inputlayer: a function created by front layer
		@param names: a list composed of name
		@param scales: a list composed of strain scale
	"""
	scales = deepcopy(scales)
	optcells = deepcopy(optcells)
	@tools.layer
	def new(job):
		for name,scale,optcell in zip(names, scales, optcells):
			A = np.diag(scale)
			@tools.cellcall(job.params["call"])
			def func(job):
				job.params['structure'] = deepcopy(job.params['structure'])
				job.params['structure'].cell = job.params['structure'].cell * A
				job.params['optcell'] = optcell # new feature
				for destination_atom in job.params['structure']:
					destination_atom.pos = destination_atom.pos * scale
			t_job = job / name
			t_job.params["call"] = func
			yield t_job
	return new

@tools.interface
def maxcellKpoints(name, maxcell):
	"""
		return a function to set vasp.kpoints by maxcell
		like maxcell // np.diag(structure.cell) only for orthogonal
		@param inputlayer : a function created by front layer
		@param name : a layer list
		@param maxcell : like [40, 40 , 1]
	"""
	kpoint = "Automatic generation\n0\nMonkhorst\n%d %d %d\n0 0 0"
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			job.params["vasp"] = deepcopy(job.params["vasp"])
			diag = np.diag(job.params["structure"].cell)
			tmp = maxcell // diag
			tmp[2] = 1 # a bug
			job.params["vasp"].kpoints = kpoint % (tuple(tmp))
		t_job = job / name
		t_job.params['call'] = func
		yield t_job
	return new

@tools.interface
def compute(common, maxLoop = 0):
	"""
		return a function to set a compute mission in job
		note that please make sure you really know how it works
		@param inputlayer : a function created by front layer
		@param common : a common configuration for vasp
		@param maxLoop : a maximum number of looping to relax
	"""
	
	from poisson import collect
	@tools.layer
	def new(job):
		@tools.fallback(job) # redirect to compute
		@tools.cellcall(job.params["call"])
		@tools.loopToRelax(maxLoop = maxLoop)
		@vaspruntime.vaspRunTime
		def func(job):
			vasp = job.params["vasp"]
			vasp.system = job.name[1:].replace("/","-")
			structure = job.params["structure"]
			if "optcell" in job.params.keys():
				tools.writeOPTCELL(job.params["optcell"])
			job.params["result"] = vasp(structure, comm = common) #vasp_std
			#collect.resultInfo(job)
		job.params['call'] = func
		yield job
	return new

@tools.interface
def extract(collect, box):
	"""
		return a function to collect result
		@param inputlayer : a function created by front layer
		@param collect : a function to handle with result
		@param box : a box to collect result , having a "apppend" function
	"""
	@tools.layer
	def new(job):
		@tools.fallback(job)
		@tools.cellcall(job.params["call"])
		def func(job):
			box.append(collect(job))
		job.params['call'] = func
		yield job
	return new

@tools.interface
def setoptcell(optcell):
	optcell = deepcopy(optcell)
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			job.params["optcell"] = optcell
		job.params["call"] = func
		yield job
	return new

@tools.interface
def setspecie(specie):
	"""
		return a function to set atom type
		@param inputlayer : a function created by front layer
		@param speice : specie and their potcar like "Re_v-Se"
	"""
	specie = deepcopy(specie)
	@tools.layer
	def new(job):
		pot_type = [pot for pot in specie.split("-")]
		atoms_type = [atom_type.split("_")[0] for atom_type in pot_type]
		@tools.cellcall(job.params["call"])
		def func(job): # before changing params we should deepcopy it. 
			job.params['structure'] = deepcopy(job.params['structure'])
			job.params['vasp'] = deepcopy(job.params['vasp'])
			call = tools.atom_replace(deepcopy(atoms_type))
			for destination_atom in job.params["structure"]:
				destination_atom.type = call(destination_atom)
			for atom,pot in zip(atoms_type,pot_type):
				job.params['vasp'].add_specie = atom,"$PAW/" + pot
		job.params["call"] = func
		yield job
	return new

@tools.interface
def getincar(incar):
	from pylada.vasp import read_incar
	vasp = read_incar(incar)
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			job.params['vasp'] = vasp
		job.params["call"] = func
		yield job
	return new

@tools.interface
def doublekpoints(times = 2):
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			current_kpoints = vasp.kpoints
		job.params["call"] = func
		yield job
	return new


@tools.interface
def copyorlinkfile(dirpath,filename,cmd = "cp"):
	import os
	path = os.path.join(dirpath,filename)
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			abspath = os.path.abspath(path)
			if not os.path.exists(abspath):
				raise IOError("Can't found " + abspath)
			res =  os.system("%s %s %s" % (cmd,abspath,os.path.join(job.name[1:],filename)))
			if not res == 0:
				raise RuntimeError("code %d when %s %s in %s" % (res,cmd,filename,job.name[1:]))
		job.params["call"] = func
		yield job
	return new

@tools.interface
def loadkpoints(filename):
	import os
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			vasp = deepcopy(job.params["vasp"])
			abspath = os.path.abspath(filename)
			if not os.path.exists(abspath):
				raise IOError("Can't found " + abspath)
			with open(abspath,"r") as rfile:
				vasp.kpoints = rfile.read()

			job.params["vasp"] = vasp
		job.params["call"] = func
		yield job
	return new

@tools.interface
def loadstructure(filename):
	import os
	from pylada.crystal import read
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			abspath = os.path.abspath(filename)
			if not os.path.exists(abspath):
				raise IOError("Can't found " + abspath)
			structure = read.poscar(abspath)
			job.params["structure"] = structure
		job.params["call"] = func
		yield job
	return new

@tools.interface
def aflowkpoints(poscarname = "POSCAR"):
	@tools.layer
	def new(job):
		@tools.cellcall(job.params["call"])
		def func(job):
			import os
			tools.getSpaceGroupName(poscarname)
			syml_path = os.path.join(os.environ["SYML"] ,"syml_"+ spacegroupname +"_original")
			print("syml_" + spacegroupname + "_original")
			shutill.copy(syml_path, job.name[1:] + "/syml")
			os.system("ln -s %s %s;adogk" % (cmd,syml_path,"syml"))
		job.params["call"] = func
		yield job
	return new


def copychgcarfrom(inputlayer,dirname):
	return copyorlinkfile(inputlayer,dirpath = dirname,filename = "CHGCAR", cmd = "cp")

def copywavecarfrom(inputlayer,dirname):
	return copyorlinkfile(inputlayer,dirpath = dirname,filename = "WAVECAR", cmd = "cp")


