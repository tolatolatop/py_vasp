from simplecalc import vutils,tools
from simplecalc import config
def poissonCalc(root, orgposcar, optcell = None ,kpointsCell = [40,40,0],
		scales = [1.01, 0.99], direction = ['a','b'],
		vacuum = "c", common = config.COMMON["nodeParams"]):

	"""
	@param root: pylada.jobfolder 
	@param orgposcar: original poscar
	@param optcell: optcell to relax
	@param scales: float list to strain  
	@param direction: direct list like ['a','b'] to strain
	@param kpointsCell: set kpointsCell to create kpoints. zero for vacuum
	@param vacuum: to set vacuum for relax
	@warning you must prepare CONTCAR in relax
	"""
	import os
	import re
	potcar = re.findall("[a-zA-Z_]+",orgposcar.split("-")[1])
	poissonJob = root / orgposcar / "poisson"
	poscarpath = os.path.join(poissonJob.parent.name[1:],"relax","CONTCAR")

	for direct in direction:
		if vacuum == "c":
			optcell = [1,1,0]
		else:
			optcell = [1,1,1]
		if direct == "a":
			optcell[0] = 0
		elif direct == "b":
			optcell[1] = 0
		r_optcell = tuple(optcell)
		pjob = poissonJob / ("strain_1_%s" % (direct))
		vutils.strainCalc(pjob, poscarpath, potcar, r_optcell, 1, direct, kpointsCell, common = common, scan = scan)
		poscar = os.path.join(pjob.name[1:], "CONTCAR")
		for scale in scales:
			pjob = poissonJob / ("strain%.2f_%s" % (scale, direct))
			vutils.strainCalc(pjob, poscar, potcar, r_optcell, scale, direct, kpointsCell, common = common, scan = scan)