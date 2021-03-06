from simplecalc import tools
from simplecalc import config

def relaxCalc(root, poscar, common = config.COMMON["nodeParams"], scan = False, optcell = None):
	"""
	@param root: pylada.jobfolder.Jobfolder a root job for vasp file
	@param poscar: standard vasp5 poscar file path with special name,like "POSCAR-Mo2Se"
	@param commom: common set for pylada.vasp compute
	@param scan: whether use INCAR_RELAX_SCAN as INCAR
	@param optcell: optcell for relax
	"""
	import re
	from simplecalc import tools
	job = root / poscar / "relax"
	job.params["common"] = common
	job.params["optcell"] = optcell
	if scan:
		job.params["incar"] = root.name[1:] + "/incar/INCAR_RELAX_SCAN_0"
		job.params["dfile"] = "incar_scan" 
	else:
		job.params["incar"] = root.name[1:] + "/incar/INCAR_RELAX_PBE"
	job.params["writechg"] = False
	job.params["writechg"] = False
	job.params["maxLoop"] = 10
	job.params["kpoints"] = tools.vaspkitkpoints(,job.params["poscar"])
	job.params["poscar"] = root.name[1:] + "/poscar_all/" + poscar
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.looptorelax
	job.compute(outdir = job.name[1:], maxLoop = job.params["maxLoop"])

	

def scfCalc(root, poscar,inherit = True, common = config.COMMON["nodeParams"],**kwargs):
	"""
	@param root: pylada.jobfolder.Jobfolder a root job for vasp file
	@param poscar: standard vasp5 poscar file path with special name,like "POSCAR-Mo2Se"
	@param commom: common set for pylada.vasp compute
	@param inherit: whether loading relax contcar from poscar/relax
	@param kwargs: other parameter of relaxCalc
	"""
	import os
	import re
	job = root / poscar / "scf"
	if inherit:
		relaxCalc(root, poscar, common = common, **kwargs)
		job.params["poscar"] = os.path.join(job.parent.name[1:],"relax","CONTCAR")
		if os.path.exists(root.name[1:] + "/kpoints/KPOINTS_SCF"):
			job.params["kpoints"] = root.name[1:] + "/kpoints/KPOINTS_SCF"
		else:
			job.params["kpoints"] = os.path.join(job.parent.name[1:],"relax","KPOINTS")
	else:
		job.params["poscar"] = root.name[1:] + "/poscar_all/" + poscar
		job.params["kpoints"] = root.name[1:] + "/kpoints/KPOINTS_SCF"
	job.params["common"] = common
	job.params["incar"] = root.name[1:] + "/incar/INCAR_SCF"
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])

def socscfCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"], **kwargs):
	"""
	@param root: pylada.jobfolder.Jobfolder a root job for vasp file
	@param poscar: standard vasp5 poscar file path with special name,like "POSCAR-Mo2Se"
	@param commom: common set for pylada.vasp compute
	@param inherit: whether loading relax contcar from poscar/relax
	@param kwargs: other parameter of relaxCalc
	"""
	import os
	import re
	job = root / poscar / "socscf"
	if inherit:
		relaxCalc(root, poscar, common = common, **kwargs)
		job.params["poscar"] = os.path.join(job.parent.name[1:],"relax","CONTCAR")
		if os.path.exists(root.name[1:] + "/kpoints/KPOINTS_SCF"):
			job.params["kpoints"] = root.name[1:] + "/kpoints/KPOINTS_SCF"
		else:
			job.params["kpoints"] = os.path.join(job.parent.name[1:],"relax","KPOINTS")
	else:
		job.params["poscar"] = root.name[1:] + "/poscar_all/" + poscar
		job.params["kpoints"] = root.name[1:] + "/kpoints/KPOINTS_SCF"
	job.params["common"] = common
	job.params["magmom"] = tools.magmom(job.params["poscar"])
	job.params["incar"] = root.name[1:] + "/incar/INCAR_SOC_SCF"
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])

def socbandCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"], **kwargs):
	"""
	@param root: pylada.jobfolder.Jobfolder a root job for vasp file
	@param poscar: standard vasp5 poscar file path with special name,like "POSCAR-Mo2Se"
	@param commom: common set for pylada.vasp compute
	@param inherit: whether loading relax contcar from poscar/relax
	@param kwargs: other parameter of scfCalc
	"""
	import os
	import re
	job = root / poscar / "socband"
	socscfCalc(root, poscar, common = common, **kwargs)
	job.params["poscar"] = os.path.join(job.parent.name[1:],"socscf","CONTCAR")
	job.params["chgcar"] = os.path.join(job.parent.name[1:],"socscf","CHGCAR")
	job.params["wavecar"] = os.path.join(job.parent.name[1:],"socscf","WAVECAR")
	job.params["magmom"] = tools.magmom(job.params["poscar"])
	job.params["writewave"] = False
	job.params["writechg"] = False
	job.params["common"] = common
	job.params["kpoints"] = tools.aflowkpoints(job.name[1:],job.params["poscar"])
	job.params["incar"] = root.name[1:] + "INCAR_SOC_BAND" 
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])

def bandCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"], **kwargs):
	"""
	@param root: pylada.jobfolder.Jobfolder a root job for vasp file
	@param poscar: standard vasp5 poscar file path with special name,like "POSCAR-Mo2Se"
	@param commom: common set for pylada.vasp compute
	@param inherit: whether loading relax contcar from poscar/relax
	@param kwargs: other parameter of scfCalc
	"""
	import os
	import re
	job = root / poscar / "band"
	scfCalc(root, poscar, common = common, **kwargs)
	job.params["poscar"] = os.path.join(job.parent.name[1:],"scf","CONTCAR")
	job.params["chgcar"] = os.path.join(job.parent.name[1:],"scf","CHGCAR")
	job.params["wavecar"] = os.path.join(job.parent.name[1:],"scf","WAVECAR")
	job.params["writewave"] = False
	job.params["writechg"] = False
	job.params["common"] = common
	job.params["kpoints"] = tools.aflowkpoints(job.name[1:],job.params["poscar"])
	job.params["incar"] = root.name[1:] + "/incar/INCAR_BAND"
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])

def dosCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"], **kwargs):
	import os
	import re
	job = root / poscar / "dos"
	scfCalc(root, poscar, common = common, **kwargs)
	job.params["poscar"] = os.path.join(job.parent.name[1:],"scf","CONTCAR")
	job.params["chgcar"] = os.path.join(job.parent.name[1:],"scf","CHGCAR")
	job.params["wavecar"] = os.path.join(job.parent.name[1:],"scf","WAVECAR")
	job.params["kpoints"] = os.path.join(job.parent.name[1:],"scf","KPOINTS")
	job.params["writewave"] = False
	job.params["writechg"] = False
	job.params["common"] = common
	job.params["incar"] = root.name[1:] + "/incar/INCAR_DOS"
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])

def strainCalc(job, poscar, potcar, optcell, scale, direct, kpointsCell, common = config.COMMON["nodeParams"], scan = False):
	import os
	from simplecalc import tools
	job.params["common"] = common
	if scan:
		job.params["incar"] = job.parent.parent.parent.name[1:] + "/incar/INCAR_RELAX_SCAN_0"
		job.params["dfile"] = "incar_scan" 
	else:
		job.params["incar"] = job.parent.parent.parent.name[1:] + "/incar/INCAR_RELAX_PBE"
	poscar = tools.strainstructure(poscar, strain = scale, direct = direct)
	job.params["writechg"] = False
	job.params["writechg"] = False
	job.params["maxLoop"] = 10
	job.params["poscar"] = poscar
	job.params["optcell"] = optcell
	job.params["kpointscell"] = kpointsCell
	job.params["potcar"] = potcar
	job.functional = tools.looptorelax
	job.compute(outdir = job.name[1:], maxLoop = job.params["maxLoop"])

def hsebandCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"], **kwargs):
	import os
	import re
	job = root / poscar / "hseband"
	scfCalc(root, poscar, common = common, **kwargs)
	job.params["poscar"] = os.path.join(job.parent.name[1:],"scf","CONTCAR")
	job.params["wavecar"] = os.path.join(job.parent.name[1:],"scf","WAVECAR")
	job.params["chgcar"] = os.path.join(job.parent.name[1:],"scf","CHGCAR")
	ibzkpt = os.path.join(job.parent.name[1:],"scf","IBZKPT")
	job.params["kpoints"] = tools.hsekpoints(job.name[1:],job.params["poscar"],ibzkpt)
	job.params["writewave"] = False
	job.params["writechg"] = False
	job.params["common"] = common
	job.params["incar"] = root.name[1:] + "/incar/INCAR_HSE_BAND"
	job.params["potcar"] = os.path.join(job.parent.name[1:],"scf","POTCAR")
	#job.functional = tools.compute
	job.functional = tools.stupidcompute
	job.compute(outdir = job.name[1:])

def optiCalc(root, poscar, inherit = True, common = config.COMMON["nodeParams"]):
	import os
	import re
	job = root / poscar / "optic"
	job.params["poscar"] = os.path.join(job.parent.name[1:],"relax","CONTCAR")
	if inherit:
		job.params["poscar"] = os.path.join(job.parent.name[1:],"relax","CONTCAR")
	else:
		job.params["poscar"] = root.name[1:] + "/poscar_all/" + poscar
	job.params["kpoints"] = root.name[1:] + "/kpoints/KPOINTS_ABS"
	job.params["writechg"] = False
	job.params["writewave"] = False
	job.params["writeoptics"] = True
	job.params["common"] = common
	job.params["incar"] = root.name[1:] + "/incar/INCAR_ABS"
	job.params["wavecar"] = os.path.join(job.parent.name[1:],"scf","WAVECAR")
	job.params["chgcar"] = os.path.join(job.parent.name[1:],"scf","CHGCAR")
	job.params["potcar"] = re.findall("[a-zA-Z_]+",poscar.split("-")[1])
	#job.params["magmom"] = magmom(poscar)
	job.functional = tools.compute
	job.compute(outdir = job.name[1:])