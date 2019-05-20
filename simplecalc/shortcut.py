def printHelp():
    print("""Usage: simplecalc
  -h, --help\tshow this page
  -r, --relax\tstart relax calculation
  -s, --scf\tstart scf calculation
  -b, --band\tstart band calculation
  -d, --dos\tstart dos calculation
""")

def main():
    from simplecalc import vutils,func,tools
    from pylada.jobfolder import JobFolder
    import pylada
    import getopt
    import sys
    shortsopt = "hr:s:b:"
    longopt = ["help","relax=","scf=","band=","dos=","vasp="]
    vasp_program = "vasp_std";
    relax = False;scf = False; band = False; dos = False;
    for opt,value in getopt.getopt(sys.argv[1:],shortsopt,longopt):
        if opt in ["-h","--help"]:
            printHelp()
            sys.exit(0)
        elif opt in ["-r","--ralex"]:
            if value.lower() in ["t","true"]:
                relax = True
        elif opt in ["-s","--scf"]:
            if value.lower() in ["t","true"]:
                scf = True
        elif opt in ["-b","--band"]:
            if value.lower() in ["t","true"]:
                band = True 
        elif opt in ["-d","--dos"]:
            if value.lower() in ["t","true"]:
                dos = True
        elif opt in ["--vasp"]:
            vasp_program = value    
    pylada.vasp_program= vasp_program
    root = JobFolder()
    root = root / "database"
    for poscar in tools.poscarLoadingTools("./database/poscar_all"):
        if relax:
            vutils.relaxCalc(root,poscar)
        if scf:
            vutils.scfCalc(root,poscar)
        if band:
            vutils.bandCalc(root,poscar)
        if dos:
            vutils.dosCalc(root,poscar)

if __name__ == "__main__":
    main()