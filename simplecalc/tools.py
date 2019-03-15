def gettmpdir():
	import os
	import uuid
	outdir = os.path.join("/tmp",uuid.uuid4().hex)
	os.makedirs(outdir)
	return outdir

def looptorelax(outdir, maxLoop, **kwargs):
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
	structure = read.poscar(kwargs["poscar"])
	vasp = read_incar(kwargs["incar"])

	for pot in kwargs["potcar"]:
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
	if "dfile" in kwargs.keys():
		if not os.path.exists(os.path.join(outdir,"DFILE")):
			with open(os.path.join(outdir,"DFILE"),"w") as f:
				f.write(kwargs["dfile"])
	if "kpointscell" in kwargs.keys():
		import numpy as np
		kpoint = "Automatic generation\n0\nMonkhorst\n%d %d %d\n0 0 0"
		diag = np.diag(structure.cell)
		tmp = np.array(kwargs["kpointscell"]) // diag
		tmp[tmp == 0] = 1
		vasp.kpoints = kpoint % (tuple(tmp))
	else:
		if hasattr(vasp,"kspacing"):
			vasp.write_kpoints = nowritekpoints
		else:
			with open(kwargs["kpoints"],"r") as rfile:
				vasp.kpoints = rfile.read()
	try:
		result = vasp(structure, outdir = outdir, comm = common)
	except Exception as e:
		print("path:" + outdir)
		raise e
	return result

def stupidcompute(outdir, common, **kwargs):
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
	import os
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	with open(os.path.join(outdir, "OPTCELL"),"w") as f:
		f.write("%d%d%d" % optcell)

def aflowkpoints(outdir, poscarsource):
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
	import os
	for i in os.popen("aflow --kpath < POSCAR | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
		spacegroupname = i[:-1]
	return spacegroupname

def strainstructure(orgposcar, strain , direct):
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
	import os
	outdir = gettmpdir()
	copyorlinkfile(outdir, "POSCAR", poscarsource, "cp")
	from pylada.misc import Changedir
	with Changedir(outdir) as pwd:
		os.system("""vaspkit <<EOF
7
%d
%.2f
EOF
""" % (kpointtype,kspacing))
		kpoints = os.path.abspath("KPOINTS")
	return kpoints


def hsekpoints(poscarsource, ibzkpt, symlsource = None):
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

def getEIGENVAL(path = "EIGENVAL"):
	line = ""
	with open(path,"r") as file:
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
	from pylada.crystal import read
	structure = read.poscar(poscarsource)
	magmom = "%d*0.6" % (len(structure) * 3)
	return magmom