import os
from simplecalc import tools
NOMATCHERROR = "no match error"
MATCHERROR = "match error in "
BACKERROR = "back error"
QUITERROR = "quit error"
NODIRERROR = "NODIR"
VASPKPTHEADER = "# vaspkit kpoints\n"
HSEKPTHEADER = "# hse kpoints\n"
CELLKPTHEADER = "# cell kpoints\n"
CANTFINDKPOINTS = "can't find "
DATABASE = "./database"
NFRESOURCE = "can't find resource "
NFKPTFILE = "can't find kpoints "
NFPOSCARFILE = "can't find poscar "

title='''=================================================================
=                                                               =
=                                                               =
=                                                               =
=                                                               =
=                                                               =
=                                                               =
=                                                               =
================================================================='''
screen_size = 65
title_func = lambda x: "=" * ((65-len(x)) // 2) + x + "=" * ((65-len(x)) // 2)
pre_func_title = " Pre Data "
calc_func_title = " Start Calc "
post_func_title = " Post Data "
back_func_title = " " * screen_size
footer = '''
'''
startCalc = []
resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"resource")
copyorlinkfile = tools.copyorlinkfile

def showopt(func):  # 输出选项
	g = [j.title for j in func]
	tmp = []
	tmp_length = 0
	into = 1
	for i in g:
		print(i)
	print()

def getResource(file):
	resource = os.path.join(resource_path,file)
	if not os.path.exists(resource):
		raise ValueError(NFRESOURCE + file)
	return resource

def getInput(info,default):
	tmp = input(info)
	if tmp == "":
		tmp = default
	return eval(tmp)


def quit_func():
	raise ValueError(QUITERROR)

def back_func():
	pass

back_func.id = 9
back_func.title = "9) Back"
quit_func.id = 0
quit_func.title = "0) Quit"

def createKpoints(kpointsName = "KPOINTS"):
	def getkpointsdir():
		kpointsdir = os.path.join(DATABASE,"kpoints")
		if not os.path.exists(kpointsdir):
			os.path.makedirs(kpointsdir)
		return kpointsdir

	def vaspkitKpoints(kpointsName = kpointsName):
		kpointsdir = getkpointsdir()
		while True:
			try:
				ktype,kspacing = getInput("default(2,0.03):  ","2,0.03")
				if type(ktype) == int and type(kspacing) == float:
					break
				else:
					raise ValueError()
			except Exception as e:
				print("plz input int,float like 1,0.03")
		with open(os.path.join(kpointsdir,kpointsName),"w") as wfile:
			wfile.write(VASPKPTHEADER)
			wfile.write("%d,%.5f" % (ktype,kspacing))

	def cellKpoints(kpointsName = kpointsName):
		kpointsdir = getkpointsdir()
		while True:
			try:
				a,b,c = getInput("default(40,40,0):  ","40,40,0")
				if type(a) == int and type(b) == int and type(c) == int:
					break
				else:
					raise ValueError()
			except Exception as e:
				print("plz input int,int,int like 40,40,0")
		with open(os.path.join(kpointsdir,kpointsName),"w") as wfile:
			wfile.write(CELLKPTHEADER)
			wfile.write()

	def hseKpoints(kpointsName = kpointsName):
		kpointsdir = getkpointsdir()
		with open(os.path.join(kpointsdir,kpointsName),"w") as wfile:
			wfile.write(HSEKPTHEADER)

	def copyyourfile(kpointsName = kpointsName):
		kpointsdir = getkpointsdir()
		while True:
			path = input("path:  ")
			if not os.path.exists(path):
				print(CANTFINDKPOINTS + " %s" % path)
			else:
				copyorlinkfile(kpointsdir,kpointsName,path,"cp")
				break
		
	vaspkitKpoints.id = 1
	vaspkitKpoints.title = "1) vaspkit parameter"
	cellKpoints.id = 3
	cellKpoints.title = "3) kpointscell parameter"
	copyyourfile.id = 4
	copyyourfile.title = "4) copy from path"
	kpoint_func = [vaspkitKpoints,cellKpoints,copyyourfile] 
	excuteFunc(kpoint_func," set kpoints ")

def setCalcFunc():
	print(title_func(" Calc Func "))
	line = ["1) pbe","2) scan","3) soc","4) hse"]
	print(title_func(" Set Func"))
	print(line[0] + "\t\t\t\t" + line[1])
	print(line[2] + "\t\t\t\t" + line[3])
	opt = getInput("default(1):","1")
	if opt == 1:
		return "PBE"
	elif opt == 2:
		return "SCAN"
	elif opt == 3:
		return "SOC"
	elif opt == 4:
		return "HSE"

def createCalcFile(): # OPTCELL KPOINTSCELL
	def getincardir():
		incardir = os.path.join(DATABASE,"incar")
		if not os.path.exists(incardir):
			os.makedirs(incardir)
		return incardir
	def relax():
		incardir = getincardir()
		calcFunc = setCalcFunc()
		copyorlinkfile(incardir,"INCAR_RELAX",getResource("INCAR_RELAX_" + calcFunc),"cp")
		createKpoints("KPOINTS_RELAX")
	def scf():
		incardir = getincardir()
		calcFunc = setCalcFunc()
		copyorlinkfile(incardir,"INCAR_SCF",getResource("INCAR_SCF_" + calcFunc),"cp")
		createKpoints("KPOINTS_SCF")
	def band():
		incardir = getincardir()
		calcFunc = setCalcFunc()
		copyorlinkfile(incardir,"INCAR_BAND",getResource("INCAR_BAND_" + calcFunc),"cp")
		createKpoints("KPOINTS_BAND")
	def dos():
		incardir = getincardir()
		calcFunc = setCalcFunc()
		copyorlinkfile(incardir,"INCAR_DOS",getResource("INCAR_DOS_" + calcFunc),"cp")
		createKpoints("KPOINTS_DOS")
	def poisson():
		incardir = getincardir()
		calcFunc = setCalcFunc()
		copyorlinkfile(incardir,"INCAR_POI",getResource("INCAR_POI_" + calcFunc),"cp")
		createKpoints("KPOINTS_POI")
	relax.id = 1
	relax.title = "1) INCAR_RELAX"
	scf.id = 2
	scf.title = "2) INCAR_SCF"
	band.id = 3
	band.title = "3) INCAR_BAND"
	dos.id = 4
	dos.title = "4) INCAR_DOS"
	poisson.id = 5
	poisson.title = "5) INCAR_POISSON"
	incar_func = [relax,scf,band,dos,poisson]
	excuteFunc(incar_func," Set Incar and Kpoints ")

potcar_dict = None
if potcar_dict is None:
    potcar_dict = {}
    with open(os.path.join(resource_path,"potcar_config"),"r") as rfile:
        q = rfile.readlines()
    for i in q:
        print(i)
        i = i.replace("\n","")
        key,value = i.split("\t")
        potcar_dict[key] = value

def rename_pocar(pocarname):
    global potcar_dict
    import re
    with open(pocarname,"r") as rfile:
        tmp = rfile.readlines()
    atom = re.findall(r"[\S]+",tmp[5])
    atomnum = re.findall(r"[\S]+",tmp[6])
    potcarname = ""
    for i,j in zip(atom,atomnum):
        if not i in potcar_dict.keys():
            potcar_dict[i] = i
        potcarname += potcar_dict[i]+j
    newname = pocarname.split("-")
    if len(newname) > 1:
        newname[1] = potcarname
    else:
        newname.append(potcarname)
    return "-".join(newname)


def createPoscar():
	from  pylada.crystal import read,write
	from copy import deepcopy 
	while True:
		poscarpath = input("poscar path: ")
		if poscarpath == "":
			poscarpath = "POSCAR"
		if not os.path.exists(poscarpath):
			print(NFPOSCARFILE + poscarpath)
		else:
			try:
				structure = read.poscar(poscarpath)
				break
			except Exception as e:
				print(e)
	atomset = set([atom.type for atom in structure])
	replace_dict = {}
	for atom in atomset:
		atom_list = input("%s to:" % atom).split(" ")
		replace_dict[atom] = [ i for i in atom_list if i != ""]
	def replace_atom(structures,org,dsts):
		for i in structures:
			structure = deepcopy(i)
			for dst in dsts:
				for atom in structure:
					if atom.type == org:
						atom.type = dst
				yield structure
	structures = [structure]
	for key,value in replace_dict.items():
		structures = replace_atom(structures,key,value)
	index = 0
	for structure in structures:
		tmp = "POSCAR%d" % index
		write.poscar(structure, tmp,vasp5=True)
		new = rename_pocar(tmp)
		os.rename(tmp,new)
		index += 1

def getopt(total_func):  # 利用action.id 解析输入
	optlist = input("")
	action_func = []
	for i in optlist.split("-"):
		i = int(i)
		tmp_action = [action for action in total_func if action.id == i]
		if len(tmp_action) > 1:
			raise ValueError(MATCHERROR + i)
		elif len(tmp_action) == 0:
			raise ValueError(NOMATCHERROR)
		elif tmp_action[0].id == 9:
			raise ValueError(BACKERROR)
		action_func.extend(tmp_action)
	return action_func

def relaxCalc():
	startCalc.append("relax")

def scfCalc():
	startCalc.append("scf")

def dosCalc():
	startCalc.append("dos")

def bandCalc():
	startCalc.append("band")

def findDirs(dirname):
	g = (i + "/" + dirname for i in os.listdir() if os.path.exists(i + "/" + dirname))

def drawingBand():
	from simplecalc.datatools import post_processing
	for i in findDirs("band"):
		currentpath = os.getcwd()
		os.chdir(i)
		post_processing.create_plot_band_structure()
		os.chdir(currentpath)

def drawingDos():
	from simplecalc.datatools import post_processing
	for i in findDirs("dos"):
		currentpath = os.getcwd()
		os.chdir(i)
		post_processing.create_plot_total_dos()
		os.chdir(currentpath)
	

def qsub_func():
	print(title_func(" vasp program "))
	vasp_program = input("default (vasp_std):")
	copyorlinkfile(".","start.py",os.path.join(DATABASE,"start.py"),"cp")
	tmp = getInput("nodes and ppn (default 1,28)","1,28")
	nodes,ppn = eval(tmp)
	queue = input("queue:")
	cmd = "python start.py "
	for i in startCalc:
		cmd += i + " "
	cmd += str(optcell)
	with open("pbs-config","w") as wfile:
		wfile.write('''#!/bin/bash
#PBS -N %s
#PBS -l nodes=%d:ppn=%d
#PBS -l walltime=3600:00:00
#PBS -q %s
#PBS -o ./out
#PBS -j oe
#PBS -V

cd $PBS_O_WORKDIR
NP=`cat $PBS_NODEFILE|wc -l`
cat $PBS_NODEFILE | sed 's/node/nodeib/' > ./pbsnode

pushd `pwd`
%s
popd
''')



createCalcFile.id = 1
createCalcFile.title = "1) create calc file"
createPoscar.id = 2
createPoscar.title = "2) create poscar"
relaxCalc.id = 3
relaxCalc.title = "3) start relax"
scfCalc.id = 4
scfCalc.title = "4) start scf"
dosCalc.id = 5
dosCalc.title = "5) start dos"
bandCalc.id = 6
bandCalc.title = "6) start band"
drawingBand.id = 27
drawingBand.title = "27) drawing band"
drawingDos.id = 28
drawingDos.title = "28) drawing dos"
pre_func = [createCalcFile,createPoscar]
calc_func = [relaxCalc,scfCalc,dosCalc,bandCalc]
post_func = [drawingBand,drawingDos]
total_func = []
total_func.extend(pre_func)
total_func.extend(calc_func)
total_func.extend(post_func)
total_func.append(quit_func)

def excuteFunc(func_list, title, back_func = back_func, quit_func = quit_func):
	while True:
		try:
			print(title_func(title))
			showopt(func_list)
			back_quit_func = []
			if hasattr(back_func,"__call__"):
				back_quit_func.append(back_func)
			if hasattr(quit_func,"__call__"):
				back_quit_func.append(quit_func)
			if len(back_quit_func) > 0:
				showopt(back_quit_func)
			total_func = []
			total_func.extend(func_list)
			total_func.extend(back_quit_func)
			actions = getopt(total_func)
		except ValueError as e:
			if NOMATCHERROR in e.args[0]:
				pass
			else:
				raise e

		for action in actions:
			try:
				action()
				break
			except ValueError as e:
				if BACKERROR in e.args[0]:
					pass
				elif NFKPTFILE in e.args[0]:
					os.makedirs(os.path.join(DATABASE,"kpoints"))
				else:
					raise e

def main():
	def show():
		print(title)
		print(title_func(pre_func_title))
		showopt(pre_func)
		print(title_func(calc_func_title))
		showopt(calc_func)
		print(title_func(post_func_title))
		showopt(post_func)
		print(title_func(back_func_title))
		showopt([quit_func])
	while True:
		try:
			show()
			actions = getopt(total_func)
		except ValueError as e:
			if NOMATCHERROR in e.args[0]:
				pass
			else:
				raise e

		for action in actions:
			try:
				action()
			except ValueError as e:
				if QUITERROR in e.args[0]:
					exit(0)
				elif BACKERROR in e.args[0]:
					pass
				else:
					raise e
	if len(startCalc) > 0:
		qsub_func()
	print(footer)

if __name__ == "__main__":
	main()