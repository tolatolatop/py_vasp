import os
import re

not_INCAR_DICT = ["CONCAT","KPOINTS","CHGCAR","WAVECAR","POSCAR","POTCAR","pbs-config"]
file_List = ["CONTCAR","KPOINTS","CHGCAR","WAVECAR","POSCAR","POTCAR","pbs-config"]
# CONTCAR

def get_from_INCAR(key,path):
	re_test = re.compile(key + " *= *([\\w.*]+)")
	with open(path + "/INCAR","r") as file:
		for i in file.readlines():
			if re_test.search(i):
				return re_test.findall(i)[0]
		return None

def get_param(key,path):
	if not key in not_INCAR_DICT:
		return get_from_INCAR(key,path)
	elif key in file_List:
		if key == "POSCAR":
			key = "CONTCAR"
		if not os.path.exists(path + "/" + key):
			raise ValueError
		return path + "/" + key

def setincarparam(incar,key,value):
	for tag in incar:
		if tag[0] == key:
			tag[1] = value
			return "sucess"
	else:
		raise ValueError

def getincarparam(mission,key):
	incar = mission._inconfig
	for tag in incar:
		if tag[0] == "key":
			return tag[1]
	return None


def getOUTCARparam(path,key):
	path = path + "/OUTCAR"
	if key == "EDIFF":
		with open(path,"r") as file:
			line = 0
			while(line < 426):
				i = file.readline()
				line = line + 1
			result = float(re.findall("[\\S]+",i)[2])
		return result

def doublekpoints(path):
	path = path + "/KPOINTS"
	with open(path,"r") as file:
		temp = file.readlines()
	line = temp[3].split(" ")
	line = [str(2*int(i)) for i in line]
	temp[3] = " ".join(line)
	with open(path,"w") as file:
		file.writelines(temp)

def createkpoints(path):
	Ppath = path + "/POSCAR"
	for i in os.popen("aflow --kpath < " + Ppath + " | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
		t = i[:-1]
	syml_path = "~/exe/syml/" + "syml_"+ t +"_original"
	print(Ppath)
	print(syml_path)
	import shutil
	shutill.copy(syml_path, path + "/syml")
	os.system("cd " + path +";~/exe/")

def createBAND(path1 = "EIGENVAL",path2 = "syml",fermi = None, INCAR_path = None ,savepath = "./bnd.dat"):
	meta,title,data = getBandData(path1)
	_,l2 = getBandXaxis()
	with open("bnd.dat","w") as file:
		for i in range(meta[1]):
			mystr = str(l2[i])
			for j in range(meta[2]):
				mystr += "    %f" % data[i*meta[2]+j][1]
			mystr += "\n"
			file.write(mystr)


'''
                for item in T.get("aflow --kpath < POSCAR | grep Line -B 2 | head -n 1 | awk '{print $1}'"):
                        temp = item
                name = "syml_" + temp + "_original"
                print(name)
                T.do("cp ~/exe/syml/" + name + " ./syml")
                tempList = None


                T.show("cat OUTCAR | grep 'reciprocal lattice vectors' -A 3")
                P = []
                for item in T.get("cat OUTCAR | grep 'reciprocal lattice vectors' -A 3 | tail -3"):
                        P.append(item)
                T.do("sed -i 's/#P0/" + P[0] + "/' syml")
                T.do("sed -i 's/#P1/" + P[1] + "/' syml")
                T.do("sed -i 's/#P2/" + P[2] + "/' syml")
                for item in T.get("grep 'BZINTS: Fermi energy:' OUTCAR | tail -1 | awk '{printf \"%f\\n\",$4}'"):
                        Fermi = item
                T.do("sed -i 's/#Fermi/" + Fermi + "/' syml")
                T.show("cat syml")
                T.show("grep Fermi OUTCAR | tail -1")

                T.confirm()
                T.do("~/exe/adogk syml")
'''


def getBandData(path = "EIGENVAL"):
	line = ""
	with open(path,"r") as file:
		for i in range(5):
			file.readline() # Discard the first 5 lines
		line = file.readline()
		meta = get_number(line,3,dtype="int")
		data ,title = list() , list()
		for i in range(meta[1]):
			file.readline()
			title.append(get_number(file.readline(),4,dtype="float"))
			for j in range(meta[2]):
				data.append(get_number(file.readline(),None,dtype="float"))
	return meta,title,data


def getBandXaxis(path = "syml"):
	mkn,sn,mk,recip = get_syml(path)
	recip = trans_T(recip)[3:]
	l = [0]
	l.extend(re_dPosition(recip,mk))
	temp = list_sum(l)
	steps = [l[i] / sn[i-1] for i in range(1,len(l))]
	l2 = list_step(0,sn,steps)
	return temp,l2


def getDosData(mission, format="file"):
	pass

def getStepDiffEnergy(mission):
	path = mission._path + "/OSZICAR"
	with open(path, "r") as file:
		t = file.readlines()[-2:-1][0]
	try:
		result = float(re.findall("[\\S]+",t)[3])
	except:
		print(re.findall("[\\S]+",t)[3])
		raise ValueError
	return result

def Rsplit(start,end,number = 1):
	assert number > 0 
	number = int(number)
	result = []
	dimension = len(start)
	RL = [(end[i] - start[i])/ float(number) for i in range(dimension)]
	result.append(RL)
	for i in range(1,number):
		result.append([result[i-1][j]+RL[j] for j in range(dimension)])
	return result

def re_dPosition(transform,positions):
	from math import sqrt
	dPositions = [[positions[i][j] - positions[i-1][j] for j in range(3)] for i in range(1,len(positions))]
	t_dPositions = []
	Vmultiply = lambda x,y : x[0] * y[0] + x[1] * y[1] + x[2] * y[2]
	for dPosition in dPositions:
		t_dPositions.append([Vmultiply(dPosition,t) for t in transform])
	Rlength = lambda x: sqrt(x[0]**2 + x[1]**2 + x[2]**2)
	dLength = [Rlength(t) for t in t_dPositions]
	return dLength

def get_number(tstr ,number = 1,dtype = "float"):
	if dtype == "float":
		re_test = re.compile("[0-9.\+\-E]+")
		convert = float
	elif dtype == "int":
		re_test = re.compile("[0-9]+")
		convert = int
	r = re_test.findall(tstr)[0:number]
	if number == None:
		number = len(r)
	if len(r) != number:
		raise ValueError("Error in %s" % (tstr))
	else:
		result = [convert(i) for i in r]
	return result


def get_param(tstr):
	pass


def get_syml(path = "syml"):
	with open(path,"r") as file:
		temp = file.readlines()
	mainkpointnumber = get_number(temp[0],1,dtype="int")[0]
	spacingnumbers = get_number(temp[1],mainkpointnumber -1,dtype="int")
	mainkpoints = [ get_number(temp[i+2],3,dtype="float") for i in range(mainkpointnumber)]
	reciprocal = [get_number(temp[mainkpointnumber + 2 + i],6,dtype = "float") for i in range(3)]
	return [mainkpointnumber, spacingnumbers, mainkpoints,reciprocal]

def convert_syml_to_KPOINTS(path = "syml", savepath = "KPOINTS", FValue = 1 ,iswrite = True):
	mkn,sn,mk,_ = get_syml(path)
	steps = [[(mk[i+1][j] - mk[i][j])/float(sn[i]) for j in range(3)] for i in range(len(mk)-1)]
	ckp = [mk[0]]
	ind = 0
	for i in range(mkn - 1):
		for j in range(sn[i]):
			ckp.append([ckp[ind][k] + steps[i][k] for k in range(3)])
			ind += 1
	sumsn = 0
	if iswrite: 
		with open(savepath,"w") as file:
			file.write("k-points along high symmetry lines created by vsap_tools\n  %d\nReciprocal\n" % (len(ckp)))
			for line in ckp:
				file.write("  %.5f  %.5f  %.5f  %.5f\n" % (line[0],line[1],line[2],FValue))
	return ckp

def trans_T(tlist):
	temp = []
	for i in range(len(tlist[0])):
		for j in range(len(tlist)):
			try:
				temp[i].append(tlist[j][i])
			except:
				temp.append([tlist[j][i]])
	return temp

def list_sum(tlist):
	temp = tlist.copy()
	for i in range(1,len(temp)):
		temp[i] = temp[i-1] + temp[i]
	return temp


def list_step(start,steps,step_list):
	assert len(steps) == len(step_list)
	result = [start]
	for i in range(len(steps)):
		temp = result[-1]
		result.extend([temp + step_list[i]*(j+1) for j in range(steps[i])])
	return result


if __name__ == "__main__":
	createBAND()
	# l1,l2 = getBandXaxis()
	# print(l1)	