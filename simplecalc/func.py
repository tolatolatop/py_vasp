from simplecalc import vutils,tools
from simplecalc import config
def poissonCalc(root, orgposcar, kpointsCell, scales = [1.01, 0.09], inherit = True,
		direction = ['a','b'], vacuum = "c", common = config.COMMON["nodeParams"],
		scan = False):
	import os
	import re
	potcar = re.findall("[a-zA-Z_]+",orgposcar.split("-")[1])
	poissonJob = root / orgposcar / "poisson"

	if inherit:
		vutils.relaxCalc(root, orgposcar, common = common)
		poscarpath = os.path.join(poissonJob.parent.name[1:],"relax","CONTCAR")
	else:
		poscarpath = os.path.join(root.name[1:],"poscar_all",orgposcar)

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
		pjob = poissonJob / ("strian_1_%s" % (direct))
		vutils.strainCalc(pjob, poscarpath, potcar, r_optcell, 1, direct, kpointsCell, common = common, scan = scan)
		poscar = os.path.join(pjob.name[1:], "CONTCAR")
		for scale in scales:
			pjob = poissonJob / ("strain%.2f_%s" % (scale, direct))
			vutils.strainCalc(pjob, poscar, potcar, r_optcell, scale, direct, kpointsCell, common = common, scan = scan)