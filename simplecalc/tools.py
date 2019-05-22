def gettmpdir():
	"""
	@return a tmpdir path
	"""
	import os
	import uuid
	outdir = os.path.join("/tmp",uuid.uuid4().hex)
	os.makedirs(outdir)
	return outdir

def looptorelax(outdir, maxLoop, **kwargs):
	"""
	relax to until one step stop.
	@param maxLoop: to raise when arrive maxloop.  
	"""
	for i in range(maxLoop):
		result = compute(outdir + "relax_%d" % i, **kwargs)
		kwargs["poscar"] = outdir + "relax_%d/" % i + "CONTCAR"
		if len(result.total_energies) == 1:
			break
	else:
		raise Exception("It's not convergence")
	return compute(outdir, **kwargs)

def compute(outdir, common ,**kwargs):
	from pylada.vasp import read_incar
	from pylada.crystal import read
	import os
	structure = read.poscar(kwargs["poscar"]) # get structure from poscar
	vasp = read_incar(kwargs["incar"]) # get vasp from incar

	for pot in kwargs["potcar"]: # set species
		vasp.add_specie = pot.split("_")[0], os.path.join(os.environ["PAW"], pot)
	if "writechg" in kwargs.keys():
		vasp.lcharg = kwargs["writechg"]
	else:
		vasp.lcharg = True
	if "writewave" in kwargs.keys():
		vasp.lwave = kwargs["writewave"]
	else:
		vasp.lwave = True
	if "writeoptics" in kwargs.keys():
		vasp.loptics = kwargs["writeoptics"]
	else:
		vasp.loptics = False
	if "optcell" in kwargs.keys():
		if kwargs["optcell"] is not None:
			writeoptcell(outdir, kwargs["optcell"])
	if "chgcar" in kwargs.keys():
		copyorlinkfile(outdir, "CHGCAR", kwargs["chgcar"], "cp")
	if "wavecar" in kwargs.keys():
		copyorlinkfile(outdir, "WAVECAR", kwargs["wavecar"], "cp")
	with open(kwargs["kpoints"],"r") as rfile:
		vasp.kpoints = rfile.read()
	try:
		result = vasp(structure, outdir = outdir, comm = common)
	except Exception as e:
		print("path:" + outdir)
		raise e
	if "dfile" in kwargs.keys(): # write a describe file
		if not os.path.exists(os.path.join(outdir,"DFILE")):
			with open(os.path.join(outdir,"DFILE"),"w") as f:
				f.write(kwargs["dfile"])
	return result

def stupidcompute(outdir, common, **kwargs):
	"""
	a stupid function to temporarily hse calculation
	"""
	import os
	import pylada
	from pylada.misc import Changedir
	copyorlinkfile(outdir,"POSCAR",kwargs["poscar"],"cp")
	copyorlinkfile(outdir,"INCAR",kwargs["incar"],"cp")
	copyorlinkfile(outdir,"POTCAR",kwargs["potcar"],"cp")
	copyorlinkfile(outdir,"CHGCAR",kwargs["chgcar"],"cp")
	copyorlinkfile(outdir,"WAVECAR",kwargs["wavecar"],"cp")
	#copyorlinkfile(outdir,"KPOINTS",kwargs["kpoints"],"cp")
	try:
		with Changedir(outdir) as pwd:
			tmp = []
			for i in os.popen(pylada.vasp_program):
				tmp.append(i)
			with open("stdout","w") as wfile:
				wfile.writelines(i)
	except Exception as e:
		print("path:" + outdir)
		raise e
	return result

def writeoptcell(outdir, optcell):
	"""
	write optcell in outdir. optcell is a list
	"""
	import os
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	with open(os.path.join(outdir, "OPTCELL"),"w") as f:
		f.write("%d%d%d" % optcell)


def cellkpoints(poscar, kpointscell):
	import numpy as np
	from pylada.crystal import read
	import os
	structure = read.poscar(poscar)
	kpoint = "Automatic generation\n0\nMonkhorst\n%d %d %d\n0 0 0"
	diag = np.diag(structure.cell)
	tmp = np.array(kpointscell) // diag
	tmp[tmp == 0] = 1
	outdir = gettmpdir()
	with open(os.path.join(outdir,"KPOINTS"),"w") as wfile:
		wfile.write(kpoint % tuple(tmp))
	return os.path.join(outdir,"KPOINTS")

def aflowkpoints(poscarsource):
	"""
	using aflow to create kpoints
	@param poscarsource: poscar path
	"""
	import os
	outdir = gettmpdir()
	copyorlinkfile(outdir, "POSCAR", poscarsource, "cp")
	from pylada.misc import Changedir
	with Changedir(outdir) as pwd:
		with open("KPOINTS","w") as wfile:
			tmp = []
			try:
				for i in os.popen("aflow --kpath < POSCAR "):
					tmp.append(i)
				index = tmp.index("Line-mode\n")
				kpoints = tmp[index-2:-1]
				if len(kpoints) < 1:
					raise Exception("aflow error")
			except Exception as e:
				raise e
			wfile.writelines(kpoints)
		kpoints = os.path.abspath("KPOINTS")
	return kpoints


def copyorlinkfile(outdir, filename, file, cmd):
	"""
	copying file with os.system
	"""
	import os
	if cmd not in ["cp","ln -s"]:
		raise Exception("only cp and ln -s")
	if not os.path.exists(file):
		raise IOError("Can't found " + file)
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	res =  os.system("%s %s %s" % (cmd,file,os.path.join(outdir, filename)))
	if not res == 0:
		raise RuntimeError("code %d when %s %s in %s" % (res,cmd,filename,outdir))


def getSpaceGroupName():
	"""
	@return spacegroup of poscar
	"""
	import os
	for i in os.popen("aflow --kpath < POSCAR | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
		spacegroupname = i[:-1]
	return spacegroupname

def strainstructure(orgposcar, strain , direct):
	"""
	@param orgposcar: original poscar
	@param strain: strain scale
	@param direct: strain direction
	@return poscar path of 
	"""
	import os
	import numpy as np
	from pylada.crystal import write,read
	outdir = gettmpdir()
	tmp_file_name = "POSCAR"
	tmp_path = os.path.join(outdir,tmp_file_name)
	structure = read.poscar(orgposcar)
	a = np.array([1.0,1.0,1.0])
	if direct == "a":
		a[0] = strain
	elif direct == "b":
		a[1] = strain
	elif direct == "c":
		a[2] = strain
	A = np.diag(a)
	structure.cell = structure.cell * A
	for atom in structure:
		atom.pos = atom.pos * a
	write.poscar(structure, tmp_path, vasp5 = True)
	return tmp_path

def poscarLoadingTools(path):
	import os
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

def vaspkitkpoints(poscarsource, kpointtype = 2, kspacing = 0.03):
	"""
	@param poscarsource: poscar path
	@param kpointtype: 1:Monkhorst 2:gamma(defualt) 
	@param kspacing: vaspkit kspacing 0.03(default)
	@return kpoints path
	"""
	import os
	import simplecalc
	outdir = gettmpdir()
	copyorlinkfile(outdir, "POSCAR", poscarsource, "cp")
	from pylada.misc import Changedir
	with Changedir(outdir) as pwd:
		os.system("""%s >/dev/null <<EOF
7
%d
%.2f
EOF
""" % (simplecalc.vaspkit,kpointtype,kspacing))
		kpoints = os.path.abspath("KPOINTS")
	return kpoints


def hsekpoints(poscarsource, ibzkpt, symlsource = None):
	"""
	@param poscarsource: original poscar 
	@param ibzkpt: ibzkpt for creating kpoints
	@param symlsource: syml for creating kpoints
	@return kpoints path in tmp
	"""
	import os
	outdir = gettmpdir()
	copyorlinkfile(outdir, "POSCAR", poscarsource, "cp")
	with open(ibzkpt,"r") as rfile:
		kpoints = rfile.readlines()
	line = int(kpoints[1].strip())
	kpoints = kpoints[:3+line]
	from pylada.misc import Changedir
	with Changedir(outdir) as pwd:
		if symlsource == None:
			symlsource = "syml_" + getSpaceGroupName() + "_hse"
			symlsource = os.path.join(os.environ["SYML"],symlsource)
			copyorlinkfile("./","syml",symlsource,"ln -s")
		os.system("adogk")
		zkpoints = []
		for i in os.popen("cat inp.kpt | awk '{print $1,$2,$3,0.00000}'"):
			zkpoints.append(i)
		kpoints[1] = str(len(kpoints) + len(zkpoints) - 3) + "\n"
		kpoints.extend(zkpoints)
		with open("KPOINTS","w") as wfile:
			wfile.writelines(kpoints)
		kpoints = os.path.abspath("KPOINTS")
	return kpoints

def nowritekpoints(self, file, structure, kpoints=None):
	pass


def loadKpoints(kpointsdir,calc_func,poscar,ibzkpt = None):
	VASPKPTHEADER = "# vaspkit kpoints\n"
	HSEKPTHEADER = "# hse kpoints\n"
	CELLKPTHEADER = "# cell kpoints\n"
	AFLOWHEADER = "# aflow kpoints\n"
	if calc_func == "relax":
		kpoints = "KPOINTS_RELAX"
	elif calc_func == "scf":
		kpoints = "KPOINTS_SCF"
	elif calc_func == "band":
		kpoints = "KPOINTS_BAND"
	elif calc_func == "dos":
		kpoints = "KPOINTS_DOS"
	with open(kpointsdir + "/" + kpoints,"r") as rfile:
		hline = rfile.readline()
		pline = rfile.readline()
	if hline == VASPKPTHEADER:
		ktype,kspacing = eval(pline)
		return vaspkitkpoints(poscar,ktype,kspacing)
	elif hline == HSEKPTHEADER:
		return hsekpoints(poscar,ibzkpt)
	elif hline == CELLKPTHEADER:
		kpointscell = eval(pline)
		return cellkpoints(poscar,kpointscell)
	elif hline == AFLOWHEADER:
		return aflowkpoints(poscar)
	else:
		return kpointsdir + "/" + kpoints



def get_number(tstr ,number = 1,dtype = "float"):
	"""
	a simple function to get number
	"""
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

def getEIGENVAL(eigenvalpath = "EIGENVAL"):
	"""
	@param: path of EIGENVAL (default EIGENVAL)
	@return meta is data size, title is kpoints list, data is band data list.
	"""
	line = ""
	with open(eigenvalpath,"r") as file:
		[file.readline() for i in range(5)] # Discard the first 5 lines
		line = file.readline()
		meta = get_number(line,3,dtype="int")
		data ,title = list() , list()
		for i in range(meta[1]):
			file.readline()
			title.append(get_number(file.readline(),4,dtype="float"))
			for j in range(meta[2]):
				data.append(get_number(file.readline(),None,dtype="float"))
	return meta,title,data

def magmom(poscarsource):
	"""
	@param poscarsource: poscar path
	@return string type magmom
	"""
	from pylada.crystal import read
	structure = read.poscar(poscarsource)
	magmom = "%d*0.6" % (len(structure) * 3)
	return magmom