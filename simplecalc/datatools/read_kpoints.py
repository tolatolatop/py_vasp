#! /usr/bin/env python3

"""
Tool for processing file KPOINTS and getting the data.

This moduel use python to process file KPOINTS.
Here, I should note that the KPOINTS file was creating by program aflow 
and using for band structure calculation.

Then we can acquire the data in the follow:
high symmetry of k path

Classes:

    KPOINTS

"""

#----------Import packages----------
import smalltool as st
import numpy as np
import os
#----------Finsihed importing packages----------

class KPOINTS:
    """Class for operating the data in file KPOINTS which includes high symmetry of k path.
    """

    def __init__(self, file_k="KPOINTS", folder_save=None):
        #  The default settings folder is stored in the same directory as the file
        if folder_save == None:
            (folder_temp, file_temp) = os.path.split(file_k)
            if folder_temp == "":
                self.folder_save = "."
            else:
                self.folder_save = folder_temp
        else:
            self.folder_save = folder_save
        #  If the custom folder does not exists, the program will create it.
        if not os.path.exists(self.folder_save):
            os.makedirs(self.folder_save)

        self.file_k = file_k

    def __read_file_k(self):
        line_mode   = None
        list_highks = []
        list_tags   = []
        with open(self.file_k, "r") as f:
            # Abandon the first 3 lines
            for i in range(3):
                f.readline()
            # Finshed abandoning the first 3 lines

            # Read the type of line mode
            line = f.readline()
            line_mode = line[0][0].lower()
            # Finshed reading the type of line mode

            # Read the data of k path
            lines = f.readlines()
            for line in lines:
                line_split = line.split()
                if len(line_split) > 0: # Abandon the vaccum line
                    one_kpoint = [float(line_split[0]),
                                  float(line_split[1]),
                                  float(line_split[2])]
                    list_highks.append(one_kpoint)
                    if r"\Gamma" == line_split[-1]:
                        list_tags.append("G")
                    else:
                        list_tags.append(line_split[-1])
            # Finshed reading the data of k path
        return line_mode, list_highks, list_tags

    def __calcu_high_sym_path_data(self, list_reciprocal_lattice):
        (line_mode, 
         list_highks, 
         list_tags) = self.__read_file_k()

        # Calculate the data of high symmetry line points
        if line_mode == "r":
            # Calculate the real location of cartesian axis
            matrix_lattice = np.mat(list_reciprocal_lattice)
            matrix_reciprocal_kpoints = np.mat(list_highks)
            matrix_cartesian_kpoints = (2 * np.pi) * matrix_reciprocal_kpoints * matrix_lattice
            # just for check, compare with the data in file OUTCAR
            #matrix_cartesian_kpoints =  matrix_reciprocal_kpoints * matrix_lattice 
            list_cartesian_kpoints = matrix_cartesian_kpoints.tolist()
            list_cart_highks = list_cartesian_kpoints
            # Finished calculating the real location of cartesian axis
        # Finished calculating the data of high symmetry line points

        list_tags_write = []
        list_highks_write = []
        for n in range(len(list_cart_highks)):
            if n == 0:
                list_highks_write.append(0.0)
                list_tags_write.append(list_tags[0])
            else:
                distance_result = st.calcu_distance_of_two_points(list_cart_highks[n - 1],
                                                                  list_cart_highks[n])
                if distance_result > 0:
                    list_highks_write.append(
                                             list_highks_write[-1] + distance_result
                                            )
                    list_tags_write.append(list_tags[n])

        return list_highks_write, list_tags_write

    def create_file_kpath_dat(self, list_reciprocal_lattice, file_name = "my_kpath.dat", folder_name = "band_structure"):
        if folder_name == None:
            my_file = self.folder_save + "/" + file_name
        else:
            folder_name = self.folder_save + "/" + folder_name
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            my_file = folder_name + "/" + file_name

        list_highks_write, list_tags_write = self.__calcu_high_sym_path_data(list_reciprocal_lattice)
        #print(list_kpoints_write, list_tags_write)
        with open(my_file, "w") as f:
            f.write("%18s\t%18s\n" % ("kpath_tag",
                                      "kpath_data",))
            for i in range(len(list_highks_write)):
                f.write("%18s\t%18f\n" % (list_tags_write[i],
                                          list_highks_write[i]))

        return my_file