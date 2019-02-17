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
	if "optcell" in kwargs.keys():
		writeoptcell(outdir, kwargs["optcell"])
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
		copyorlinkfile(outdir, "syml", os.path.join(os.environ["SYML"],"syml_" + spacegroupname + "_original"))
		os.system("adogk")
		with open("KPOINTS","r") as rfile:
			kpoints = rfile.read()
	return kpoints



def copyorlinkfile(outdir, filename, file, cmd):
	if cmd not in ["cp","ln -s"]:
		raise Exception("only cp and ln -s")
	if not os.path.exists(filename):
		raise IOError("Can't found " + filename)
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	res =  os.system("%s %s %s" % (cmd,filename,os.path.join(outdir, filename)))
	if not res == 0:
		raise RuntimeError("code %d when %s %s in %s" % (res,cmd,filename,outdir))
	job.params["call"] = func


def getSpaceGroupName():
	import os
	for i in os.popen("aflow --kpath < POSCAR | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
		spacegroupname = i[:-1]
	return spacegroupname