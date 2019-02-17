def looptorelax(outdir, maxLoop, **kwargs):
	for i in range(maxloop):
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
	structure = read.poscar(kwargs["poscar"])
	vasp = read_incar(kwargs["incar"])
	for pot in kwargs["potcar"]:
		vasp.add_species = pot.split("_")[0], "$PAW/" + pot
	if "optcell" in kwargs.keys():
		writeoptcell(outdir, kwargs["optcell"])
	with open(kwargs["kpoints"],"r") as rfile:
		vasp.kpoints = rfile.read()
	return vasp(structure, outdir = outdir)

def writeoptcell(outdir, optcell):
	import os
	with open(os.path.join(outdir, "OPTCELL"),"w") as f:
		f.write("%d%d%d" % optcell)