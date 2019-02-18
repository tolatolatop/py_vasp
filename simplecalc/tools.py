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
	vasp.lcharg = True
	vasp.lwave = True
	for pot in kwargs["potcar"]:
		vasp.add_specie = pot.split("_")[0], os.path.join(os.environ["PAW"], pot)

	if "optcell" in kwargs.keys():
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
		with open(kwargs["kpoints"],"r") as rfile:
			vasp.kpoints = rfile.read()
	return vasp(structure, outdir = outdir, comm = common)

def writeoptcell(outdir, optcell):
	import os
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	with open(os.path.join(outdir, "OPTCELL"),"w") as f:
		f.write("%d%d%d" % optcell)

def aflowkpoints(outdir, poscarsource):
	import os
	copyorlinkfile(outdir, "POSCAR", poscarsource, "cp")
	from pylada.misc import Changedir
	with Changedir(outdir) as pwd:
		spacegroupname = getSpaceGroupName()
		copyorlinkfile("." ,"syml", os.path.join(os.environ["SYML"],"syml_" + spacegroupname + "_original"), "ln -s")
		os.system("adogk")
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
	import uuid
	import os
	import numpy as np
	from pylada.crystal import write,read
	root = "/tmp"
	uuid_str = uuid.uuid4().hex
	tmp_file_name = 'tmpfile_%s.txt' % uuid_str
	tmp_path = os.path.join(root,tmp_file_name)
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
	write.poscar(structure, tmp_path, vasp = 5)
	return tmp_path