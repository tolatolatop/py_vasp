def hsekpoints(ibzkpt = "IBZKPT", symlsource = "syml"):
        import os
        with open(ibzkpt,"r") as rfile:
                kpoints = rfile.readlines()
        os.system("adogk")
        zkpoints = []
        for i in os.popen("cat inp.kpt | awk '{OFS=\"    \";print $1,$2,$3,0.00000}'"):
                zkpoints.append(i)
        kpoints[1] = str(len(kpoints) + len(zkpoints) - 3) + "\n"
        kpoints.extend(zkpoints)
        with open("KPOINTS","w") as wfile:
                wfile.writelines(kpoints)
        kpoints = os.path.abspath("KPOINTS")
        return kpoints

def writeEIGENVAL_HSE():
        import os
        if not (os.path.exists("inp.kpt") and os.path.exists("EIGENVAL")):
                raise IOError("inp.kpt or EIGENVAL don't exists")
        os.system("""if [[ -a EIGENVAL_BAK ]];then mv EIGENVAL_BAK EIGENVAL;fi
cat EIGENVAL > EIGENVAL_BAK
cat EIGENVAL | awk '(NR<6){print $0}' > EIGENVAL_B
KN=`cat inp.kpt | awk 'END{print NR}' | tail -1`
KNF=`cat EIGENVAL | awk '(NR==6){print $2}'`
BN=`cat EIGENVAL | awk '(NR==6){print $3}'`
tmp=`cat EIGENVAL | awk '(NR==6){print $1}'`
echo "     $tmp     $KN     $BN" >> EIGENVAL_B
Q="(NR>(($KNF-$KN)*($BN+2)+6)){print}"
cat EIGENVAL | awk $Q >> EIGENVAL_B
mv EIGENVAL_B EIGENVAL
""")

if __name__ == "__main__":
        import getopt
        import sys
        shortopt = "hm:"
        longopt = ["help","module"]
        optlist,arg = getopt.getopt(sys.argv[1:],shortopt,longopt)
        for key,value in optlist:
                print(key)
                if key in ["--help","-h"]:
                        #printhelp()
                        pass
                elif key in ["-m","--model"]:
                        module = value
        if module == "pre":
                hsekpoints()
        elif module == "after":
                writeEIGENVAL_HSE()