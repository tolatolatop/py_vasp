from simplecalc import tools
import os
abspath = os.path.dirname(__file__)
poscar = os.path.join(abspath,"test_resource","strainPOSCAR")
with open(poscar,"r") as rfile:
	for line in rfile.readlines():
		print(line[:-1])
poscar = tools.strainstructure(poscar, strain = 2, direct = "a")
with open(poscar,"r") as rfile:
	for line in rfile.readlines():
		print(line[:-1])