import os
def vaspRunTime(func):
	def new(job):
		while True:
			try:
				func(job)
			except RuntimeError as e:
				print("-----Debug Info-----")
				print("PATH:" + os.getcwd())
				stdout_error = os.popen("cat stdout | grep error")
				stdout_error = stdout_error.read()
				stdout_error = stdout_error.split("\n")[:-1]
				stdout_error = sorted(set(stdout_error),key = stdout_error.index)
				for error in stdout_error: 
					print("stderror:" + error)
					f = True
					f = f & symmetryAtomNotFound(error,job)
					f = f & ZBRENTError(error,job)
					if f:
						raise e
				print("-------end----------")
			break
	return new

def symmetryAtomNotFound(error,job):
	if "symmetry equivalent atom not found" in error:
		vasp = job.params["vasp"]
		new_symprec = vasp.symprec * 0.1
		print("repair:set symprec" + str(vasp.symprec) + " to " + str(new_symprec))
		vasp.symprec = new_symprec
		return False
	return True

def ZBRENTError(error,job):
	if "fatal error in bracketing" in error:
		vasp = job.params["vasp"]
		new_ediff = vasp.ediff * 0.1
		print("repair:set ediff " + str(vasp.ediff) + " to " + str(new_ediff))
		vasp.ediff = new_ediff
		return False
	return True
