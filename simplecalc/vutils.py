from simplecalc import tools
from simplecalc import config

def relaxCalc(root, poscar, common = config.COMMON["nodeParams"]):
	from simplecalc import tools
	job = root / poscar / "relax"
	job.params["common"] = common
	job.params["optcell"] = [1,1,1]
	job.params["incar"] = "./incar/INCAR_RELAX_PBE"
	job.params["maxLoop"] = 10
	job.params["kpoints"] = "./kpoints/KPOINTS_RELAX"
	job.params["poscar"] = "./poscar_all/" + poscar
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.looptorelax
	job.compute(outdir = job.name[1:], maxLoop = job.params["maxLoop"])

	

def scfCalc(root, poscar,inherit = True, common = config.COMMON["nodeParams"]):
	import os
	job = root / poscar / "scf"
	if inherit:
		relaxCalc(root, poscar, common = common)
		job.params["poscar"] = os.path.join(job.parent.name[1:],"relax","CONTCAR")
		job.params["kpoints"] = os.path.join(job.parent.name[1:],"relax","KPOINTS")
	else:
		job.params["poscar"] = "./poscar_all/" + poscar
		job.params["kpoints"] = "./kpoints/KPOINTS_SCF"
	job.params["common"] = common
	job.params["optcell"] = [1,1,1]
	job.params["incar"] = "./incar/INCAR_SCF"
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:],common = common)


