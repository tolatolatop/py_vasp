from collections import namedtuple
from pylada.misc import Changedir
from pickle import load,dump
import os

def standabc(job):
	a = job.params['structure'].cell[0,0]
	b = job.params['structure'].cell[1,1]
	tmp = []
	for atom in job.params['structure']:
		tmp.append(atom.pos[2])
	maxc = max(tmp);minc = min(tmp)
	c = (maxc - minc) 
	return a,b,c


def standInfo(job):
	"""
		information : success path energy x y z
	"""
	with Changedir(job.name[1:]) as pwd:
		Extract = namedtuple('standInfo',['success','path','energy','a','b','c'])
		if not os.path.exists("STANDINFO"):
			with open("STANDINFO","wb") as wfile:
				energy = job.params['result'].total_energy
				a,b,c = standabc(job)
				path = job.name[1:]
				Et = Extract(True, path, energy, a, b, c)
				dump((True,path,energy,a,b,c),wfile)
			return Et
		else:
			with open("STANDINFO","rb") as rfile:
				success,path,energy,a,b,c = load(rfile)
			return Extract(success,path,energy,a,b,c)

def resultInfo(job):
	"""
		information : success path energy structure
	"""
	with Changedir(job.name[1:]) as pwd:
		Extract = namedtuple('resultInfo',['success','path','energy','structure'])
		if not os.path.exists("RESULTINFO"):
			with open("RESULTINFO","wb") as wfile:
				energy = job.params['result'].total_energy
				structure = job.params['result'].structure
				path = job.name[1:]
				Et = Extract(True, path, energy, structure)
				dump((True,path,energy,structure),wfile)
			return Et
		else:
			with open("RESULTINFO","rb") as rfile:
				success,path,energy,structure = load(rfile)
			return Extract(success,path,energy,structure)


