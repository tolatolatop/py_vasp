from poisson import vutils
from pylada.jobfolder import JobFolder
from poisson import tools
import pylada
pylada.vasp_program="$pylada_vasp"
root = tools.rootJob()
root = root / "database"
for poscar in vutils.poscarLoadingTools("./database/poscar_all"):
	print(poscar)
	vutils.scfCalc(poscar,root)

