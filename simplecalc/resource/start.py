from simplecalc import vutils,func,tools
from pylada.jobfolder import JobFolder
import pylada
import sys
pylada.vasp_program = sys.argv[1]
root = JobFolder()
root = root / "database"
start = sys.argv[2:-1]
optcell = eval(sys.argv[-1])
for poscar in tools.poscarLoadingTools("./database/poscar_all"):
	if "relax" in start:
		vutils.relaxCalc(root,poscar,optcell = optcell)
	if "scf" in start:
		vutils.scfCalc(root,poscar)
	if "dos" in start:
		vutils.dosCalc(root,poscar)
	if "band" in start:
		vutils.bandCalc(root,poscar)