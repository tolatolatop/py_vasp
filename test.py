from simplecalc import vutils,func,tools
from simplecalc.datahandle import poissonData
from simplecalc.datatools import create_plot_band_structure
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

		job_band = root / poscar / "band"
		list_file,list_figure = create_plot_band_structure(file_xml = os.path.join(job_band.name[1:],"vasprun.xml"), 
								file_k = os.path.join(job_band.name[1:],"KPOINTS"))

	except Exception as e:
		print(e)