from simplecalc import vutils
from poisson.vutils import poscarLoadingTools
from pylada.jobfolder import JobFolder
import pylada
pylada.vasp_program="vasp_std"
root = JobFolder()
root = root / "database"
for poscar in poscarLoadingTools("./database/poscar_all"):
	print(poscar)
	vutils.relaxCalc(root,poscar)