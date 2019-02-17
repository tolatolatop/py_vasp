from simplescalc import vutils
from pylada.jobfolder import JobFolder
import pylada
pylada.vasp_program="vasp_std"
root = JobFolder()
root = root / "database"
for poscar in vutils.poscarLoadingTools("./database/poscar_all"):
	print(poscar)
	vutils.relaxcalc(root,poscar)