from simplecalc import vutils,func
from poisson.vutils import poscarLoadingTools
from pylada.jobfolder import JobFolder
import pylada
pylada.vasp_program="vasp_std"
root = JobFolder()
root = root / "database"
for poscar in poscarLoadingTools("./database/poscar_all"):
	#print(poscar)
	#vutils.relaxCalc(root,poscar)
	func.poissonCalc(root,poscar,(40,40,0),[1.02,1.01,1.05,0.95,0.99,0.98])