from simplecalc import vutils,func,tools
from simplecalc.datahandle import poissonData
from pylada.jobfolder import JobFolder
import pylada
pylada.vasp_program="vasp_std"
root = JobFolder()
root = root / "database"
for poscar in tools.poscarLoadingTools("./database/poscar_all"):
	#print(poscar)
	#vutils.relaxCalc(root,poscar)
	try:
		func.poissonCalc(root,poscar,(40,40,0),(1,1,0),[1.02,1.01,1.05,0.95,0.99,0.98])
		poijob = root / poscar / "poisson"
		standjob = poijob / "strian_1_a"
		alist = [standjob.name[1:]]
		for name in poijob.children.keys():
			if "_a" in name:
				job = poijob / name
				alist.append(job.name[1:])
		result = poissonData(alist, alist[0], xaxis = "a-length", yaxis = "b-length")
		print(result["xaxis"])
		print(result["yaxis"])
	except Exception as e:
		print(e)