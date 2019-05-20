exit_flag = False
action_parameter = {}
gdict = {}
gdict["history"] = []
screen_size = 65
resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"resource")
copyorlinkfile = tools.copyorlinkfile
DATABASE = "./database"


title_func = lambda x: "=" * ((screen_size-len(x)) // 2) + x + "=" * ((screen_size-len(x)) // 2)

def getincardir():
	incardir = os.path.join(DATABASE,"incar")
	if not os.path.exists(incardir):
		os.makedirs(incardir)
	return incardir

def getkpointsdir():
	kpointsdir = os.path.join(DATABASE,"kpoints")
	if not os.path.exists(kpointsdir):
		os.makedirs(kpointsdir)
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
		wfile.write("%d,%d,%d" % (a,b,c))

def hseKpoints(kpointsName = kpointsName):
	kpointsdir = getkpointsdir()
	with open(os.path.join(kpointsdir,kpointsName),"w") as wfile:
		wfile.write(HSEKPTHEADER)

def aflowKpoints(kpointsName = kpointsName):
	kpointsdir = getkpointsdir()
	with open(os.path.join(kpointsdir,kpointsName),"w") as wfile:
		wfile.write(AFLOWHEADER)

def copyyourfile(kpointsName = kpointsName):
	kpointsdir = getkpointsdir()
	while True:
		path = input("path:  ")
		if not os.path.exists(path):
			print(CANTFINDKPOINTS + " %s" % path)
		else:
			copyorlinkfile(kpointsdir,kpointsName,path,"cp")
			break

def getResource(file):
	resource = os.path.join(resource_path,file)
	if not os.path.exists(resource):
		raise ValueError(NFRESOURCE + file)
	return resource

def getInput(info, default):
	tmp = input(info)
	if tmp == "":
		return default
	return tmp

class metapage(object):
	"""docstring for metapage"""
	def __init__(self, title, screen_size = screen_size):
		super(metapage, self).__init__()
		self.__links = []
		self.__pages = []
		self.screen_size = screen_size
		self.title = title


	def getLink(self):
		return self.__links

	def getInput(self):
		print("------------------------->>")
		return input("")

	def show(self):
		self.showTitle(self)
		for pid,page in self.__pages:
			page.show()
		links = [(i[0],i[1]) for i in self.__links]
		self.showLink(self.__links)

	def action(self,tinput):
		tinput = eval(tinput)
		if tinput == 0:
			self.quit()
		elif tinput == 9:
			self.back()
			return 
		for pid,page in self.__pages:
			for pid, text, callback in page.getLink():
				if tinput == pid:
					callback()
		for pid, text, callback in self.__links:
			if tinput == pid:
				callback()

	def showLink(self, links):
		screen_size = self.screen_size
		tmp_length = 0
		into = 1
		for link_id,link_text,_ in links:
			text = "%d) %s" % (link_id,link_text)
			if tmp_length == 0:
				print(text, end="")
				tmp_length += len(text)
			elif tmp_length < (screen_size // 2):
				print(" " * (screen_size // 2 - tmp_length),end ="")
				print(text)
				tmp_length = 0
			else:
				print()
				print(text,end="")
				tmp_length = len(i)
		if len(links) > 0:
			print()
		if tmp_length > 0:
			print()

	def showTitle(self, page):
		title = page.title
		screen_size = page.screen_size
		tmp = "=" * ((screen_size-len(title)) // 2) + title + "=" * ((screen_size-len(title)) // 2)
		print(tmp)

	def link_error(self):
		print("no link")

	def back(self):
		gdict["history"] = gdict["history"][:-1]

	def showBack(self):
		if len(gdict["history"]) > 1:
			print("9)\tBack")

	def quit(self):
		raise ValueError("to Exit!")

	def addLink(self, lid, text, callback):
		self.__links.append((lid,text,callback))

	def addPage(self, pid, page):
		self.__pages.append((pid,page))

def nav(startPage):
	gdict["history"].append(startPage)
	while len(gdict["history"]) > 0:
		gdict["history"][-1].show()
		print("0)\tQuit")
		gdict["history"][-1].showBack()
		print()
		tinput = gdict["history"][-1].getInput()
		for i in tinput.split("-"):
			gdict["history"][-1].action(i)

def gotoPage(page):
	def new():
		gdict["history"].append(page)
	return new

def setValue(key,value,nextPage):
	def new():
		gdict[key] = value
		to = gotoPage(nextPage)
		to()
	return new

def setIncar(value):
	def new():
		to = setValue("incar",value,setFuncPage)
		to()
	return new

def setFunc(value):
	def new():
		to = setValue("func",value,setKpointsPage)
		to()
	return new

def setKpoints(value):
	def new():
		gdict["kpoints"] = value
		if value == "vaspkit":
			gdict["kpoints_value"] = eval(getInput("default(2,0.03):","2,0.03"))
		elif value == "kpointscell":
			gdict["kpoints_value"] = eval(getInput("default(40,40,0):","40,40,0"))
		elif value == "hsekpt":
			gdict["kpoints_value"] = ""
		elif value == "aflowkpt":
			gdict["kpoints_value"] = ""
		elif value == "frompath":
			gdict["kpoints_value"] = input("")
		createCalcFile()
		gdict["history"] = [indexPage]
	return new

def createCalcFile():
	print(gdict["incar"])
	print(gdict["func"])
	print(gdict["kpoints"])
	print(gdict["kpoints_value"])

def setQsub(value):
	if "start" not in gdict.keys():
		gdict["start"] = ""
	def new():
		gdict["start"] += value + " "
	return new

def createQsub():
	print(title_func(" vasp program "))
	vasp_program = input("default (vasp_std):")
	if vasp_program == "":
		vasp_program = "vasp_std"
	copyorlinkfile(".","start.py",os.path.join(resource_path,"start.py"),"cp")
	nodes,ppn = getInput("nodes and ppn (default 1,28)","1,28")
	queue = input("queue: ")
	mission = input("mission: ")
	optcell = input("optcell (None):")
	if optcell == "":
		optcell = "None"
	cmd = "python start.py " + vasp_program + " "
	cmd += gdict["start"]
	cmd += optcell
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
''' % (mission,nodes,ppn,queue,cmd))

def draw(value):
	def new():
		print("draw!!")
	return new


indexPage = metapage(" this is index page title ")
prePage = metapage(" this is pre page title ")

createInputPage = metapage(" create Incar ")
createInputPage.addLink(1,"INCAR_RELAX",setIncar("INCAR_RELAX"))
createInputPage.addLink(2,"INCAR_SCF",setIncar("INCAR_SCF"))
createInputPage.addLink(3,"INCAR_BAND",setIncar("INCAR_BAND"))
createInputPage.addLink(4,"INCAR_DOS",setIncar("INCAR_DOS"))


setKpointsPage = metapage(" set Kpoints ")
setKpointsPage.addLink(1,"vaspkit parameter",setKpoints("vaspkit"))
setKpointsPage.addLink(2,"kpointscell parameter",setKpoints("kpointscell"))
setKpointsPage.addLink(3,"hse kpoints",setKpoints("hsekpt"))
setKpointsPage.addLink(4,"aflow kpoints",setKpoints("aflowkpt"))
setKpointsPage.addLink(5,"from path",setKpoints("frompath"))


setFuncPage = metapage(" set Func ")
setFuncPage.addLink(1,"pbe",setFunc("pbe"))
setFuncPage.addLink(2,"soc",setFunc("soc"))
setFuncPage.addLink(3,"hse",setFunc("hse"))
setFuncPage.addLink(4,"scan",setFunc("scan"))


createPoscarPage = metapage(" this is create poscar page ")

prePage.addLink(1," create calc file ", gotoPage(createInputPage))
prePage.addLink(2," create poscar ", gotoPage(createPoscarPage))

calcPage = metapage(" this is calc page title ")
calcPage.addLink(11,"start relax",setQsub("relax"))
calcPage.addLink(12,"start scf",setQsub("scf"))
calcPage.addLink(13,"start band",setQsub("band"))
calcPage.addLink(14,"start dos",setQsub("dos"))


postPage = metapage(" this is post page title")
postPage.addLink(21,"draw band",draw)
postPage.addLink(22,"draw dos",draw)

indexPage.addPage(1,prePage)
indexPage.addPage(2,calcPage)
indexPage.addPage(3,postPage)

nav(indexPage)