#! /usr/bin/env python3

"""
Tool for processing file vasprun.xml and getting the data.

This moduel use python to process file vasprun.xml.
Then we can acquire the data in the follow:
list of atoms
band structure
projected band structure
pdos
spin polarization

Classes:

    Vasprunxml

"""

#----------Importing packages-----------
import re
import os
import numpy as np
import shutil
import xml.etree.ElementTree as ET
import smalltool as st
#----------Finished importing packages----------


class Vasprunxml:
    """Class for processing the data in the file vasprun.xml.
    """

    def __init__(self, file_xml="vasprun.xml", fermi_switch=1, folder_save=None):
        #  The default settings folder is stored in the same directory as the file
        if folder_save == None:
            (folder_temp, file_temp) = os.path.split(file_xml)
            if folder_temp == "":
                self.folder_save = "."
            else:
                self.folder_save = folder_temp
        else:
            self.folder_save = folder_save
        #  If the custom folder does not exists, the program will create it.
        if not os.path.exists(self.folder_save):
            os.makedirs(self.folder_save)

        self.file_xml      = file_xml
        self.tree          = ET.parse(self.file_xml)
        self.root          = self.tree.getroot()
        # Save the setting of every calculation parameters
        self.calcu_paras   = self.__acquire_each_setting_of_paras()
        #If fermi_switch = 0, it will not move the VBM.
        #If fermi_switch = 1, it will move the VBM to the fermi levl.
        #If fermi_switch = 2, it will move the VBM to 0.
        self.fermi_switch  = fermi_switch

        self.list_type_ion = self.__acquire_list_type_ion()

        self.num_kpoints_start = 1
        self.k_start = 1
        (self.num_kpoints_end, 
         self.list_reciprocal_kpoints, 
         self.list_cartesian_kpoints) = self.__acquire_kpoints()
        self.k_end = self.num_kpoints_end

        #print("num_kpoints_start", self.k_start)
        #print("num_kpoints_end", self.k_end)

    paras_path = ["./parameters//separator[@name='%s']/i[@name='%s']" % ("electronic", "NELECT"), 
                  "./parameters//separator[@name='%s']/i[@name='%s']" % ("electronic spin", "LSORBIT"), 
                  "./parameters//separator[@name='%s']/i[@name='%s']" % ("electronic spin", "ISPIN"), 
                  "./calculation//dos//i[@name='efermi']",
                  "./atominfo/atoms",
                  "./parameters//separator[@name='%s']/i[@name='%s']" % ("dos", "LORBIT"),
                  "./parameters//separator[@name='%s']/i[@name='%s']" % ("electronic", "NBANDS"),
                  "./calculation/energy/i[@name='e_fr_energy']"]

    paras_name = ["NELECT", 
                  "LSORBIT", 
                  "ISPIN", 
                  "efermi", 
                  "num_atoms", 
                  "LORBIT", 
                  "NBANDS", 
                  "e_fr_energy"]
    


    def __acquire_setting_of_para(self, path_of_tag):
        '''
        Acquire the setting of parameter which sets in the file vasprun.xml

        Args:
            path_of_tag: the path of tag in the file vasprun.xml

        Return:
            if the setting is a number, the type of the text should be changed to float or int.
            if the setting is a string, it will do nothing.
            then, return the number of string of this parameter
        '''
        i = self.root.findall(path_of_tag)
        s = i[0].text.strip() # i is a list which has only one element, but we should delete the whitespace in the two sides.
        if st.is_number(s):
            setting = float(s)
        else:
            setting = s
        return setting

    def __acquire_each_setting_of_paras(self):
        """Acquire each setting of parameters which in the paras_path(a list variable).

        Return:
            A dictionary which includes the name of parameters and the data of parameters.
            For example:
            {"name" : data}

        """
        dict_paras = {}
        for n in range(len(self.paras_path)):
            path = self.paras_path[n]
            setting = self.__acquire_setting_of_para(path)   
            dict_paras[self.paras_name[n]] = setting

        return dict_paras

    def get_calcu_paras(self):
        """Get each setting of parameters which in the dictionary calcu_paras.

        Return:
            A dictionary which includes the name of parameters and the data of parameters.
            For example:
            {"name" : data}
        """
        return self.calcu_paras



    def __acquire_list_atoms(self):
        '''Acquire the element and the number of each atom in the xml file.

        Return:
            A list includes the element and number of each atom, such as:
            [
             ["P", 1],
             ["B", 2]
            ]
            Note: the number of atoms is start from 1.
        '''
        list_atoms = []
        path = "././atominfo/array[@name='atoms']/set/rc"
        at_num = 0
        for rc in self.root.findall(path):
            at_name = rc[0].text # the name of each atom
            at_num += 1 # the number of each atom
            list_atoms.append([at_name, at_num])

        return list_atoms

    def create_atomlist_file(self, file_name = "atoms_list.dat", folder_name = "basis_file"):
        """
        Create a file to save the data of atoms.

        Args:
            file_name: the name of file which can use to save the data of atoms.
            folder_name: the name of folder to save this atom list file. 
                         If this folder does not exist, the program will make a 
                         new folder.

        Return:
            the name of file.
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        list_atoms = self.__acquire_list_atoms()
        path = "././atominfo/array[@name='atoms']/set/rc"
        at_num = 0
        my_file = my_folder + "/" + file_name
        with open(my_file, "w") as f:
            f.write("%18s\t%18s\n" % ("atom_name", "atom_num"))
            for n in range(len(list_atoms)):
                at_name = list_atoms[n][0]
                at_num  = list_atoms[n][1]
                f.write("%18s\t%18s\n" % (at_name, at_num))

        return my_file

    def get_list_atoms(self):
        """Get the data of atoms.

        Return:
            return a list which includes the element and number of each atom, such as:
            [
             ["P", 1],
             ["B", 2]
            ]
            Note: the number of atoms is start from 1.
        """
        list_atoms = self.__acquire_list_atoms()

        return list_atoms

    def __acquire_list_type_ion(self):
        """Acquire the the element and all the tag of this element.

        Return:
            A list which includes the element and all the tag of this element, such as:
            [
             ["Mo", [1, 2]],
             ["Te", [3, 4, 5, 6]]
            ]
        """
        list_type_ion = []
        path_element_atomtype = "./atominfo/array[@name='atomtypes']/set/rc"

        temp_n = 1 # save the sum of the number of one element
        for rc in self.root.findall(path_element_atomtype):
            at_name = rc[1].text
            at_num = int(rc[0].text)
            list_at = []
            for n in range(at_num):
                list_at.append(temp_n + n)
            temp_n = list_at[-1] + 1
            list_type_ion.append([at_name, list_at])

        return list_type_ion

    def get_list_type_ion(self):
        """Get the the element and all the tag of this element.

        Return:
            A list which includes the element and all the tag of this element, such as:
            [
             ["Mo", [1, 2]],
             ["Te", [3, 4, 5, 6]]
            ]
        """
        return self.list_type_ion



    def __acquire_list_reciprocal_lattice(self):
        """Acquire the reciprocal lattice of the crystal in the file Vasprun.xml

        Return:
            A list includes the lattice of the axis, such as:
            [
             [ 0.1, 0.0, 0.0],
             [ 0.0, 0.2, 0.0],
             [ 0.0, 0.0, 0.3]
            ]
        """
        list_reciprocal_lattice = []
        path = "./structure[@name='finalpos']/crystal/varray[@name='rec_basis']/v"    
        for v in self.root.findall(path):
            [l_x, l_y, l_z] = st.get_number(v.text, 3, 'float')
            list_reciprocal_lattice.append([l_x, l_y, l_z])

        return list_reciprocal_lattice

    def get_list_reciprocal_lattice(self):
        """Get the reciprocal lattice of the crystal in the file Vasprun.xml

        Return:
            A list includes the lattice of the axis, such as:
            [
             [ 0.1, 0.0, 0.0],
             [ 0.0, 0.2, 0.0],
             [ 0.0, 0.0, 0.3]
            ]
        """
        list_reciprocal_lattice = self.__acquire_list_reciprocal_lattice()

        return list_reciprocal_lattice

    def __acquire_list_basis_lattice(self):
        """Acquire the basis lattice of the crystal in the file Vasprun.xml

        Return:
            A list includes the lattice of the axis, such as:
            [
             [ 3.0, 0.0, 0.0],
             [ 0.0, 4.0, 0.0],
             [ 0.0, 0.0, 5.0]
            ]
        """
        list_basis_lattice = []
        path = "./structure[@name='finalpos']/crystal/varray[@name='basis']/v"
        for v in self.root.findall(path):
            [l_x, l_y, l_z] = st.get_number(v.text, 3, "float")
            list_basis_lattice.append([l_x, l_y, l_z])

        return list_basis_lattice

    def get_list_basis_lattice(self):
        """Get the basis lattice of the crystal in the file Vasprun.xml

        Return:
            A list includes the lattice of the axis, such as:
            [
             [ 3.0, 0.0, 0.0],
             [ 0.0, 4.0, 0.0],
             [ 0.0, 0.0, 5.0]
            ]
        """
        list_basis_lattice = self.__acquire_list_basis_lattice()

        return list_basis_lattice

    def __acquire_list_positions(self):
        """Acquire the positions of the crystal in the file Vasprun.xml

        Return:
            A list includes the positions of the crystal, such as:
            [
             [ 0.053, 0.999, 0.501],
             [ 0.273, 0.609, 0.501],
             [ 0.663, 0.390, 0.501]
            ]
            Note: the positions were in the direction axis.
        """
        list_positions = []
        path = "./structure[@name='finalpos']/varray[@name='positions']/v"
        for v in self.root.findall(path):
            [p_x, p_y, p_z] = st.get_number(v.text, 3, "float")
            list_positions.append([p_x, p_y, p_z])

        return list_positions

    def get_list_positions(self):
        """Get the positions of the crystal in the file Vasprun.xml

        Return:
            A list includes the positions of the crystal, such as:
            [
             [ 0.053, 0.999, 0.501],
             [ 0.273, 0.609, 0.501],
             [ 0.663, 0.390, 0.501]
            ]
            Note: the positions were in the direction axis.
        """
        list_positions = self.__acquire_list_positions()

        return list_positions

    def __calcu_list_real_positions(self):
        """Calculate the positions of the crystal in the real space.

        Return:
            A list includes the positions of the crystal in the real space, such as:
            [
             [ 1.000, 4.000, 2.500],
             [ 0.600, 3.200, 2.500],
             [ 1.800, 1.800, 2.500]
            ]  
        """
        list_real_positions = []

        list_positions = self.__acquire_list_positions()
        list_basis_lattice = self.__acquire_list_basis_lattice()

        matrix_positions = np.mat(list_positions)
        matrix_basis_lattice = np.mat(list_basis_lattice)
        matrix_real_positions = matrix_positions * matrix_basis_lattice # Care about the order
        list_real_positions = matrix_real_positions.tolist()

        return list_real_positions

    def get_list_real_positions(self):
        """Get the positions of the crystal in the real space.

        Return:
            A list includes the positions of the crystal in the real space, such as:
            [
             [ 1.000, 4.000, 2.500],
             [ 0.600, 3.200, 2.500],
             [ 1.800, 1.800, 2.500]
            ]  
        """
        list_real_positions = self.__calcu_list_real_positions()

        return list_real_positions

    def calcu_distance_of_two_positions(self, list_ions_define = [1, 2]):
        """Calculate the distance of two positions in the real space.

        Args:
            list_ions_define: a list includes the tag of two atoms.
                              Note: the tag of atoms should start from 1.

        Return:
            the distance of two postions in the real space.
            Default: this function will return the distance of first two atoms.
        """
        distance = None
        list_real_positions = self.__calcu_list_real_positions()
        tag1 = list_ions_define[0]
        tag2 = list_ions_define[1]
        position1 = list_real_positions[tag1 - 1]
        position2 = list_real_positions[tag2 - 1]
        distance = st.calcu_distance_of_two_points(position1, position2)

        return distance

    def calcu_angles_of_three_positions(self, list_ions_define = [1, 2, 3]):
        """Calculate angles of three positions in the real space.

        Args:
            list_ions_define: a list includes the tag of three atoms.
                              Note: the tag of atoms should start from 1.

        Return:
            a list includes angles of three atoms in the real space.
            Default: this function will return angles of first three atoms
        """
        list_angles = []
        list_real_positions = self.__calcu_list_real_positions()
        tag1 = list_ions_define[0]
        tag2 = list_ions_define[1]
        tag3 = list_ions_define[2]
        position1 = list_real_positions[tag1 - 1]
        position2 = list_real_positions[tag2 - 1]
        position3 = list_real_positions[tag3 - 1]
        list_angles = st.calcu_angles_of_three_points(position1, position2, position3)

        return list_angles



    def __acquire_kpoints(self):
        """Acquire the k points in direct axes and cartesian axes.

        Return:
            kpoints_num: the total number of k points.
            list_reciprocal_kpoints: a list with k points in direct axes.
            list_cartesion_kpoints: a list with k points in cartesion axes.
            Note: the k points in the file Vasprun.xml was in the direct axes.
        """
        list_reciprocal_lattice = self.__acquire_list_reciprocal_lattice()
        kpoints_num = 0 # the quantity of k points
        list_reciprocal_kpoints = []
        list_cartesion_kpoints = []
        list_kpoints = []
        path = "./kpoints/varray[@name='kpointlist']/v"

        for v in self.root.findall(path):
            [kp_x, kp_y, kp_z] = st.get_number(v.text, 3, 'float')
            kpoints_num += 1
            list_reciprocal_kpoints.append([kp_x, kp_y, kp_z])
        
        # Calculate the real location of cartesian axis
        matrix_lattice = np.mat(list_reciprocal_lattice)
        matrix_reciprocal_kpoints = np.mat(list_reciprocal_kpoints)
        matrix_cartesian_kpoints = (2 * np.pi) * matrix_reciprocal_kpoints * matrix_lattice
        # just for check, compare with the data in file OUTCAR
        #matrix_cartesian_kpoints =  matrix_reciprocal_kpoints * matrix_lattice 
        list_cartesion_kpoints = matrix_cartesian_kpoints.tolist()
        # Finished calculating the real location of cartesian axis

        return kpoints_num, list_reciprocal_kpoints, list_cartesion_kpoints

    def create_kpoints_file(self, file_name = "kpoints_list.dat", folder_name = "basis_file"):
        """Create the file which includes data of k points in the direct axes.

        Args:
            file_name: the name of file to save the data of k points.
            folder_name: the name of folder to save the file.

        Return:
            a string which includes the path of files.
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        (kpoints_num, 
         list_reciprocal_kpoints, 
         list_cartesian_kpoints) = self.__acquire_kpoints()

        my_file = my_folder + "/" + file_name
        with open(my_file, "w") as f:
            f.write("%12s  %12s  %12s  %12s\n" % ("kpoint_num", "kpoint_x", "kpoint_y", "kpoint_z"))

            for n in range(kpoints_num):
                [kp_x, kp_y, kp_z] = list_reciprocal_kpoints[n]
                f.write("%12d  %12.8f  %12.8f  %12.8f\n" % (n + 1, kp_x, kp_y, kp_z))

        return my_file

    def calcu_list_kpoints_distance(self):
        '''This function is using for calculating that the distance of two points in the high symmetry lines.

        The first k point is the original k point, and then calculate the distance of this k point and the next k point. 
        The follow is the same processing.

        Return:
            list_kpoints_distance: a list which includes all the distance of the high symmetry path.
                                   The type of element in the list is float.
        '''
        list_kpoints_distance = [] # the distance in the high symmetry line
        (kpoints_num, 
         list_reciprocal_kpoints, 
         list_cartesian_kpoints) = self.__acquire_kpoints()

        for n in range(kpoints_num):
            if n == 0:
                list_kpoints_distance.append(0.0)
            else:
                distance_result = st.calcu_distance_of_two_points(
                                          list_cartesian_kpoints[n - 1],
                                          list_cartesian_kpoints[n]
                                          )
                # the distance should add to the lastest result.
                list_kpoints_distance.append(
                                list_kpoints_distance[n - 1] + distance_result
                            )

        return list_kpoints_distance



    def __acquire_original_eigenvalues(self):
        """Acquire the data of original eigen values which can use for plotting band structure.

        Return:
            a list which includes the data of eigen values.
            the layer of the data is: spin -> band -> kpoint -> eigen value
        """
        num_kpoints_start = self.num_kpoints_start
        num_kpoints_end   = self.num_kpoints_end

        if self.calcu_paras["ISPIN"] == 1:
            list_spins = [1]
        elif self.calcu_paras["ISPIN"] == 2:
            list_spins = [1, 2]

        path = "./calculation/eigenvalues/array/set/set[@comment='spin %d']/set[@comment='kpoint %d']/r"
        list_original_eigenvalues_each_k = []
        list_original_eigenvalues_each_b = []

        # the layer of data:
        # spin -> kpoint -> band
        for ns in list_spins:
            list_temp_spin = []
            for nk in range(num_kpoints_start, num_kpoints_end + 1):
                list_temp_kpoint = []
                for r in self.root.findall(path % (ns, nk)):
                    [eigene, occ] = st.get_number(r.text, 2, "float")
                    list_temp_kpoint.append(eigene)
                list_temp_spin.append(list_temp_kpoint)
            list_original_eigenvalues_each_k.append(list_temp_spin)

        # the layer of data:
        # spin -> band -> kpoint
        num_spins   = len(list_original_eigenvalues_each_k)
        num_kpoints = len(list_original_eigenvalues_each_k[0])
        num_bands   = len(list_original_eigenvalues_each_k[0][0])
        for ns in range(num_spins):
            list_temp_spin = []
            for nb in range(num_bands):
                list_temp_band = []
                for nk in range(num_kpoints):
                    list_temp_band.append(list_original_eigenvalues_each_k[ns][nk][nb])
                list_temp_spin.append(list_temp_band)
            list_original_eigenvalues_each_b.append(list_temp_spin)

        return list_original_eigenvalues_each_b

    def get_original_eigenvalues(self):
        """Get the data of original eigen values which can use for plotting band structure.

        Return:
            a list which includes the data of eigen values.
            the layer of the data is: spin -> band -> kpoint -> eigen value
        """
        list_original_eigenvalues_each_b = self.__acquire_original_eigenvalues()

        return list_original_eigenvalues_each_b

    def __acquire_vbm_data(self):
        """Acquire the eigen value of vbm.

        Return:
            the eigen value of vbm.
        """
        list_original_eigenvalues_each_b = self.__acquire_original_eigenvalues()
        vbm_data = None
        if self.calcu_paras["LSORBIT"] == "T":
            num_vbm = int(int(self.calcu_paras["NELECT"]) / 2)
            #num_cbm = num_vbm + 1
            # The number of vbm which should substract 1,
            # cause it start from 0.
            # the layer of list_original_eigenvalues_each_b
            # spin -> band -> kpoint
            [vbm_tag, vbm_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1]) 
        else:
            if self.calcu_paras["ISPIN"] == 1:
                num_vbm = int(self.calcu_paras["NELECT"])
                #num_cbm = num_vbm + 1
                # The number of vbm which should substract 1,
                # cause it start from 0.
                # the layer of list_original_eigenvalues_each_b
                # spin -> band -> kpoint
                [vbm_tag, vbm_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1])
            elif self.calcu_paras["ISPIN"] == 2:
                num_vbm = int(self.calcu_paras["NELECT"])
                #num_cbm = num_vbm + 1
                [vbm1_tag, vbm1_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1])
                [vbm2_tag, vbm2_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[1][num_vbm - 1])
                if vbm1_data >= vbm2_data: 
                    [vbm_tag, vbm_data] = [vbm1_tag, vbm1_data]
                else:
                    [vbm_tag, vbm_data] = [vbm2_tag, vbm2_data]

        return vbm_data

    def create_bandgap_file(self, file_name = "band_gap.dat", folder_name = "band_structure"):
        """Create the file includes the data of band gap, vbm and cbm.

        Args:
            file_name: the name of file to save the data of band gap, vbm and cbm.
            folder_name: the name of folder to save the file.

        Return:
            the path of file.
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)

        list_original_eigenvalues_each_b = self.__acquire_original_eigenvalues()
        list_kpoints_distance = self.calcu_list_kpoints_distance()
        list_reciprocal_kpoints = self.list_reciprocal_kpoints
        bandgap_type = None
        bandgap_data = None
        calcu_type = None
        if self.calcu_paras["LSORBIT"] == "T":
            num_vbm = int(self.calcu_paras["NELECT"])
            num_cbm = num_vbm + 1
            # The number of vbm which should substract 1,
            # cause it start from 0.
            # the layer of list_original_eigenvalues_each_b
            # spin -> band -> kpoint
            [vbm_tag, vbm_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1])
            [cbm_tag, cbm_data] = st.get_min_tag_data(list_original_eigenvalues_each_b[0][num_cbm - 1])
            calcu_type = "With SOC"
        else:
            if self.calcu_paras["ISPIN"] == 1:
                num_vbm = int(int(self.calcu_paras["NELECT"]) / 2)
                num_cbm = num_vbm + 1
                # The number of vbm which should substract 1,
                # cause it start from 0.
                # the layer of list_original_eigenvalues_each_b
                # spin -> band -> kpoint
                [vbm_tag, vbm_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1])
                [cbm_tag, cbm_data] = st.get_min_tag_data(list_original_eigenvalues_each_b[0][num_cbm - 1])
                calcu_type = "Without SOC ISPIN = 1"
            elif self.calcu_paras["ISPIN"] == 2:
                num_vbm = int(int(self.calcu_paras["NELECT"]) / 2)
                num_cbm = num_vbm + 1
                [vbm1_tag, vbm1_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[0][num_vbm - 1])
                [vbm2_tag, vbm2_data] = st.get_max_tag_data(list_original_eigenvalues_each_b[1][num_vbm - 1])
                [cbm1_tag, cbm1_data] = st.get_min_tag_data(list_original_eigenvalues_each_b[0][num_cbm - 1])
                [cbm2_tag, cbm2_data] = st.get_min_tag_data(list_original_eigenvalues_each_b[1][num_cbm - 1])
                if vbm1_data >= vbm2_data:
                    [vbm_tag, vbm_data] = [vbm1_tag, vbm1_data]
                else:
                    [vbm_tag, vbm_data] = [vbm2_tag, vbm2_data]
                if cbm1_data <= cbm2_data:
                    [cbm_tag, cbm_data] = [cbm1_tag, cbm1_data]
                else:
                    [cbm_tag, cbm_data] = [cbm2_tag, cbm2_data]
                calcu_type = "Without SOC ISPIN = 2"

        if vbm_tag == cbm_tag:
            bandgap_type = "Direct gap"
        else:
            bandgap_type = "Indirect gap"
        bandgap_data = cbm_data - vbm_data

        distance_vbm = list_kpoints_distance[vbm_tag]
        distance_cbm = list_kpoints_distance[cbm_tag]
        kpoint_vbm = list_reciprocal_kpoints[vbm_tag]
        kpoint_cbm = list_reciprocal_kpoints[cbm_tag]

        my_file = my_folder + "/" + file_name
        with open(my_file, "w") as f:
            f.write("%s\n" % (calcu_type))
            f.write("%18s  %18s\n" % ("bandgap_type:", bandgap_type))
            f.write("%18s  %18.8f\n" % ("bandgap_data:", bandgap_data))
            f.write("\n")
            f.write("%18s  %18d\n" % ("vbm_num:", num_vbm))
            f.write("%18s  %18d\n" % ("vbm_kpoint:", vbm_tag + 1))
            f.write("%18s  %18.6f  %18.6f  %18.6f\n" % ("vbm_kpoint:", kpoint_vbm[0], kpoint_vbm[1], kpoint_vbm[2]))
            f.write("%18s  %18.6f\n" % ("vbm_distance:", distance_vbm))
            f.write("%18s  %18.8f\n" % ("vbm_data:", vbm_data))
            f.write("\n")
            f.write("%18s  %18d\n" % ("cbm_num:", num_cbm))
            f.write("%18s  %18d\n" % ("cbm_kpoint:", cbm_tag + 1))
            f.write("%18s  %18.6f  %18.6f  %18.6f\n" % ("cbm_kpoint:", kpoint_cbm[0], kpoint_cbm[1], kpoint_cbm[2]))
            f.write("%18s  %18.6f\n" % ("cbm_distance:", distance_cbm))
            f.write("%18s  %18.8f\n" % ("cbm_data:", cbm_data))

        return my_file

    def acquire_revise_data(self):
        '''Acquire the revise data to modify the eigen values.

        Return:
            the revise data which can use to modify the eigen values.
            It means it can use to modify the data of energy and move the fermi level.
        '''
        #The revise data was using for correct the data of eigenvalues.
        revise_data = None
        if self.fermi_switch == 0:
            revise_data = 0
        elif self.fermi_switch == 1:
            revise_data = self.calcu_paras["efermi"]
        elif self.fermi_swith == 2:
            revise_data = self.__acquire_vbm_data()
        else:
            revise_data = 0

        return revise_data

    def __acquire_operated_eigenvalues(self):
        '''Acquire the eigen values which were moving the fermi level.

        Return:
            a list which includes the eigen values which were modifyed.
        '''
        list_operated_eigenvalues_each_b = []
        list_original_eigenvalues_each_b = self.__acquire_original_eigenvalues()
        vbm_data = None
        if self.fermi_switch == 0:
            vbm_data = 0
        elif self.fermi_switch == 1:
            vbm_data = self.calcu_paras["efermi"]
        elif self.fermi_swith == 2:
            vbm_data = self.__acquire_vbm_data()
        else:
            vbm_data = 0

        # the layer of dat in list_original_eigenvalues_each_b
        # spin -> band -> kpoint
        num_spins = len(list_original_eigenvalues_each_b)
        num_bands = len(list_original_eigenvalues_each_b[0])
        num_kpoints = len(list_original_eigenvalues_each_b[0][0])
        for ns in range(num_spins):
            list_spin_temp = []
            for nb in range(num_bands):
                list_band_temp = []
                for nk in range(num_kpoints):
                    list_band_temp.append(list_original_eigenvalues_each_b[ns][nb][nk] - (vbm_data))
                list_spin_temp.append(list_band_temp)
            list_operated_eigenvalues_each_b.append(list_spin_temp)

        return list_operated_eigenvalues_each_b

    def create_eigenvalue_file(self, folder_name = "band_structure"):
        """Create the file which includes eigen values.

        Args:
            folder_name: the name of folder to save the files.

        Return:
            the list includes the path of files.
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)

        list_my_file = [] # save the name of file which includes the data of eigenvalues
        list_operated_eigenvalues_each_b = self.__acquire_operated_eigenvalues()
        list_kpoints_distance = self.calcu_list_kpoints_distance()

        num_spins   = len(list_operated_eigenvalues_each_b)
        num_bands   = len(list_operated_eigenvalues_each_b[0])
        num_kpoints = len(list_operated_eigenvalues_each_b[0][0])
        if self.calcu_paras["ISPIN"] == 1:
            list_file_name = ["my_band.dat"]
        elif self.calcu_paras["ISPIN"] == 2:
            list_file_name = ["my_band_spin_up.dat", "my_band_spin_dn.dat"]

        for ns in range(num_spins):
            my_file = my_folder + "/" + list_file_name[ns]
            list_my_file.append(my_file)
            with open(my_file, "w") as f:
                string = "%18s\t" % "kpath"
                for nb in range(1, num_bands + 1):
                    temp = "band_" + str(nb)
                    string += "%18s\t" % temp
                string += "\n"
                f.write(string)

                for nk in range(num_kpoints):
                    string = "%18.8f\t" % list_kpoints_distance[nk]
                    for nb in range(num_bands):
                        string += "%18.8f\t" % list_operated_eigenvalues_each_b[ns][nb][nk]
                    string += "\n"
                    f.write(string)

        return list_my_file



    def __acquire_original_total_dos(self):
        '''Acquire original data of total dos(Never modify the fermi level).

        Return:
            a list includes the data of total dos.
            the layer of data: spin -> eigen value, dos, integrated
        '''
        if self.calcu_paras["ISPIN"] == 1:
            list_spins = [1]
        elif self.calcu_paras["ISPIN"] == 2:
            list_spins = [1, 2]
        list_original_total_dos = []
        path = "./calculation/dos/total/array/set/set[@comment='spin %d']/r"

        # the layer of the data in list_total_dos
        # spin -> eigenvalue
        for ns in list_spins:
            list_spin_temp = []
            for r in self.root.findall(path % ns):
                [energy, total, integrated] = st.get_number(r.text, 3, 'float')
                list_spin_temp.append([energy, total, integrated])
            list_original_total_dos.append(list_spin_temp)

        return list_original_total_dos

    def __acquire_operated_total_dos(self):
        """Acquire operated data of total dos( which had finished modifying the fermi level).
        
        Return:
            a list includes operated data of total dos.
        """
        list_original_total_dos = self.__acquire_original_total_dos()
        vbm_data = self.acquire_revise_data()

        num_spins = len(list_original_total_dos)
        num_eigens = len(list_original_total_dos[0])
        for ns in range(num_spins):
            list_spin_temp = []
            for ne in range(num_eigens):
                # the energy is the first number in the list
                list_original_total_dos[ns][ne][0] -= vbm_data # Note: here, I never deep copy the list

        return list_original_total_dos

    def create_total_dos_file(self, folder_name = "dos_file"):
        """Create the fild for saving the operated data of total dos.

        Args:
            folder_name: the name of folder for saving the files.

        Return:
            a list which includes the name of files.
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        list_operated_total_dos = self.__acquire_operated_total_dos()

        num_spins  = len(list_operated_total_dos)
        num_eigens = len(list_operated_total_dos[0])
        if self.calcu_paras["ISPIN"] == 1:
            list_file_name = ["my_total_dos.dat"]
        elif self.calcu_paras["ISPIN"] == 2:
            list_file_name = ["my_total_dos_spin_up.dat", "my_total_dos_spin_dn.dat"]

        for ns in range(num_spins):
            list_file_name[ns] = my_folder + "/" + list_file_name[ns]
            with open(list_file_name[ns], "w") as f:
                f.write("%18s  %18s  %18s\n" % ("energy", "total", "integrated"))
                for ne in range(num_eigens):
                    f.write("%18.6f  %18.6f  %18.6f\n" % (list_operated_total_dos[ns][ne][0], 
                                                          list_operated_total_dos[ns][ne][1], 
                                                          list_operated_total_dos[ns][ne][2]))
        return list_file_name

    def __acquire_original_part_dos(self):
        """Acquire the original dos data of each orbital.

        Return:
            list_original_part_dos: a list includes the original dos data of each orbital.
                                    the layer of data: ion -> spin -> eigen value, dos, integrated
            dict_original_part_dos: a dictory includes the key(the energy or the orbital) 
                                    and the value(the column of each key),such as:
                                    {"energy" : 0, "s" : 1, "py" : 2}
        """
        list_original_part_dos = []
        dict_original_part_dos = {}

        path_of_field = "./calculation/dos/partial/array/field"
        path = "./calculation/dos/partial/array/set/set[@comment='ion %d']/set[@comment='spin %d']/r"

        # Prepare the list of ions and spins
        list_ions = None
        list_spins = None
        # the first element of list_ions and list_spins should be 1.
        list_ions = [i for i in range(1, int(self.calcu_paras["num_atoms"]) + 1)] # here,  the number of atoms should subplus 1
        if self.calcu_paras["LSORBIT"] == "T":
            list_spins = [1, 2, 3, 4] # spin 1, 2, 3, 4
        else:
            if self.calcu_paras["ISPIN"] == 2:
                list_spins = [1, 2] # spin 1, 2
            else:
                list_spins = [1]
        # Finished preparing the list of ions and spins

        # Acquire the meaning of data in each row
        # the element of dict_dos_partial concludes, energy, s, py, pz, px, dxy, dyz, dz2, dxz, x2-y2
        temp_index = 0
        for field in self.root.findall(path_of_field):
            dict_original_part_dos[field.text.strip()] = temp_index
            temp_index += 1
        # Finished acquiring the meaning of data in each row

        # Acquire the data of each orbit
        # the layer of data
        # ion -> spin -> eigenvalue
        for ni in list_ions:
            list_ion_temp = []
            for ns in list_spins:
                list_spin_temp = []
                for r in self.root.findall(path % (ni, ns)):
                    list_dos_temp = st.get_number(r.text, len(dict_original_part_dos), "float")
                    list_spin_temp.append(list_dos_temp)
                list_ion_temp.append(list_spin_temp)
            list_original_part_dos.append(list_ion_temp)
        #print(list_dos_partial[0])
        #print(np.array(list_dos_partial).shape)
        # Finished acquiring the data of each orbit

        return list_original_part_dos, dict_original_part_dos

    def __acquire_original_add_dos(self):
        '''Acquire the original dos data of each orbital(s, p, d, f).

        Return:
            list_original_add_dos: a list includes the original dos data.
            dict_original_add_dos: a dictionary includes the key(the energy and the orbital)
                                   and the value(the column).
        '''
        (list_original_part_dos,
         dict_original_part_dos) = self.__acquire_original_part_dos()
        list_original_add_dos = []
        dict_original_add_dos = {}

        # Add the data of s, p, d, f orbits
        if len(dict_original_part_dos) == 10:
            dict_original_add_dos = {"energy" : 0, "s" : 1, "p" : 2, "d" : 3}
            num_ions = len(list_original_part_dos)
            num_spins = len(list_original_part_dos[0])
            num_eigens = len(list_original_part_dos[0][0])
            for ni in range(num_ions):
                list_ion_temp = []
                for ns in range(num_spins):
                    list_spin_temp = []
                    for ne in range(num_eigens):
                        dict_temp = {"energy" : 0, "s" : 0, "p" : 0, "d" : 0}
                        dict_temp["energy"] = list_original_part_dos[ni][ns][ne][dict_original_part_dos["energy"]]
                        dict_temp["s"] = list_original_part_dos[ni][ns][ne][dict_original_part_dos["s"]]
                        for orbit in ["px", "py", "pz"]:
                            dict_temp["p"] += list_original_part_dos[ni][ns][ne][dict_original_part_dos[orbit]]
                        for orbit in ["dxy", "dyz", "dz2", "dxz", "x2-y2"]:
                            dict_temp["d"] += list_original_part_dos[ni][ns][ne][dict_original_part_dos[orbit]]
                        list_temp = [dict_temp["energy"],
                                     dict_temp["s"],
                                     dict_temp["p"],
                                     dict_temp["d"]]
                        list_spin_temp.append(list_temp)
                    list_ion_temp.append(list_spin_temp)
                list_original_add_dos.append(list_ion_temp)
        # Finished adding the data of s, p, d, f orbits
        return list_original_add_dos, dict_original_add_dos

    def __acquire_operated_part_dos(self):
        """Acquire the operated dos data of each orbital( which had finished moving the fermi level).

        Return:
            list_original_part_dos: a list includes the original dos data of each orbital.
                                    the layer of data: ion -> spin -> eigen value, dos, integrated
            dict_original_part_dos: a dictory includes the key(the energy or the orbital) 
                                    and the value(the column of each key),such as:
                                    {"energy" : 0, "s" : 1, "py" : 2}
        """
        (list_original_part_dos, 
         dict_original_part_dos) = self.__acquire_original_part_dos()
        revise_data = self.acquire_revise_data()

        num_ions = len(list_original_part_dos)
        num_spins = len(list_original_part_dos[0])
        num_eigens = len(list_original_part_dos[0][0])
        for ni in range(num_ions):
            for ns in range(num_spins):
                for ne in range(num_eigens):
                    list_original_part_dos[ni][ns][ne][dict_original_part_dos["energy"]] -= revise_data

        return list_original_part_dos, dict_original_part_dos

    def __acquire_operated_add_dos(self):
        '''Acquire the operated dos data of each orbital(s, p, d, f).

        Return:
            list_original_add_dos: a list includes the operated dos data.
            dict_original_add_dos: a dictionary includes the key(the energy and the orbital)
                                   and the value(the column).
        '''
        (list_original_add_dos, 
         dict_original_add_dos) = self.__acquire_original_add_dos()
        revise_data = self.acquire_revise_data()

        num_ions = len(list_original_add_dos)
        num_spins = len(list_original_add_dos[0])
        num_eigens = len(list_original_add_dos[0][0])
        for ni in range(num_ions):
            for ns in range(num_spins):
                for ne in range(num_eigens):
                    list_original_add_dos[ni][ns][ne][dict_original_add_dos["energy"]] -= revise_data

        return list_original_add_dos, dict_original_add_dos

    def __create_dos_file(self, list_part_dos, dict_part_dos, file_name_start, folder_name = "dos_file"):
        """Create the file which includes the dos data.

        Args:
            list_part_dos: a list includes the dos data.
            dict_part_dos: a dictory includes the key(the energy and the orbital) and the value(the column of data).
            file_name_start: the start of the file name
            folder_name: the name of folder which can save the file

        Return:
            a list with the name of file.
        """
        # Prepare the folder for saving files
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        list_file_name = []
        num_ions = len(list_part_dos)
        num_spins = len(list_part_dos[0])
        num_eigens = len(list_part_dos[0][0])
        for ni in range(num_ions):
            for ns in range(num_spins):
                my_file = my_folder + "/" + file_name_start + "_ion" + str(ni + 1) + "_spin" + str(ns + 1) + ".dat"
                list_file_name.append(my_file)
                with open(my_file, "w") as f:
                    string = ""
                    for ele in dict_part_dos:
                        string += "%18s  " % ele
                    string += "\n"
                    f.write(string)
                    for ne in range(num_eigens):
                        string = ""
                        for ele in list_part_dos[ni][ns][ne]:
                            string += "%18f  " % ele
                        string += "\n"
                        f.write(string)
        return list_file_name

    def create_original_part_dos_file(self):
        """Create the file includes the original dos data of each orbital.

        Return:
            a list of the file name.
        """
        (list_original_part_dos, 
         dict_original_part_dos) = self.__acquire_original_part_dos()
        list_file_name = self.__create_dos_file(list_original_part_dos,
                                                dict_original_part_dos, 
                                                "partial_original_dos", 
                                                "dos_file")
        return list_file_name

    def create_operated_part_dos_file(self):
        """Create the file includes the operated dos data of each orbital.

        Return:
            a list of the file name.
        """
        (list_operated_part_dos, 
         dict_operated_part_dos) = self.__acquire_operated_part_dos()
        list_file_name = self.__create_dos_file(list_operated_part_dos,
                                                dict_operated_part_dos, 
                                                "partial_operated_dos", 
                                                "dos_file")
        return list_file_name   

    def create_original_add_dos_file(self):
        """Create the file includes the original dos data of each orbital(s, p, d, f).

        Return:
            a list of the file name.
        """
        (list_original_add_dos, 
         dict_original_add_dos) = self.__acquire_original_add_dos()
        list_file_name = self.__create_dos_file(list_original_add_dos,
                                                dict_original_add_dos, 
                                                "add_original_dos", 
                                                "dos_file")
        return list_file_name

    def create_operated_add_dos_file(self):
        """Create the file includes the operated dos data of each orbital(s, p, d, f).

        Return:
            a list of the file name.
        """
        (list_operated_add_dos, 
         dict_operated_add_dos) = self.__acquire_operated_add_dos()
        list_file_name = self.__create_dos_file(list_operated_add_dos,
                                                dict_operated_add_dos, 
                                                "add_operated_dos", 
                                                "dos_file")
        return list_file_name

    def __acquire_define_part_dos(self, list_ions_define, list_part_dos):
        """Acquire the total dos data of several atoms.

        Args:
            list_ion_define: a list includes the tag of list ions
            list_part_dos: a list includes the partial dos data of each ion.

        Return:
            a list includes the total dos data of several atoms.
        """
        list_def_part_dos = []

        num_ions   = len(list_part_dos)
        num_spins  = len(list_part_dos[0])
        num_eigens = len(list_part_dos[0][0])
        num_datas  = len(list_part_dos[0][0][0])

        for ns in range(num_spins):
            list_spin_temp = []
            for ne in range(num_eigens):
                list_eigen_temp = []
                for nd in range(num_datas):
                    temp = 0
                    for ion in list_ions_define:
                        if nd == 0: # "energy"
                            temp = list_part_dos[ion - 1][ns][ne][nd]
                            break
                        else:
                            temp += list_part_dos[ion - 1][ns][ne][nd]
                    list_eigen_temp.append(temp)
                list_spin_temp.append(list_eigen_temp)
            list_def_part_dos.append(list_spin_temp)

        return list_def_part_dos

    def __create_def_dos_file(self, list_part_dos, dict_part_dos, 
                              file_name_start, folder_name = "dos_file"):
        """Create the file for saving the dos data which just includes the information about define atoms list.

        Args:
            list_part_dos: a list which includes the partial dos data.
            dict_part_dos: a dictionary for the list_part_dos, which includes the key(energy and orbit)
                           and the value(the column)
            file_name_start: the start of the name of file
            folder_name: the name of folder for saving files

        Return:
            a list of file name
            Note: create the list for saving file name, cause the dos may has spin un and spin down.
                  or (spin total, spin x, spin y, spin z)
        """
        # Prepare the folder for saving files
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        list_file_name = []

        num_spins = len(list_part_dos)
        num_eigens = len(list_part_dos[0])
        for ns in range(num_spins):
            my_file = my_folder + "/" + file_name_start + "_spin" + str(ns + 1) + ".dat"
            list_file_name.append(my_file)
            with open(my_file, "w") as f:
                string = ""
                for ele in dict_part_dos:
                    string += "%18s  " % ele
                string += "\n"
                f.write(string)
                for ne in range(num_eigens):
                    string = ""
                    for ele in list_part_dos[ns][ne]:
                        string += "%18f  " % ele
                    string += "\n"
                    f.write(string)
        return list_file_name

    def __acquire_def_ori_part_dos(self, list_ions_define):
        """Acquire the original dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            list_def_ori_part_dos: the data of dos.
            dict_original_part_dos: the dictionary of the list which includes
                                    the data of dos.
        """
        (list_original_part_dos, 
         dict_original_part_dos) = self.__acquire_original_part_dos()
        list_def_ori_part_dos = self.__acquire_define_part_dos(list_ions_define, list_original_part_dos)

        return list_def_ori_part_dos, dict_original_part_dos

    def create_def_ori_part_dos(self, list_ions_define):
        """Create the file wichi includes the original dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            the list includes the name of files.
        """
        (list_def_ori_part_dos,
         dict_def_ori_part_dos) = self.__acquire_def_ori_part_dos(list_ions_define)
        list_file_name = self.__create_def_dos_file(list_def_ori_part_dos,
                                                    dict_def_ori_part_dos,
                                                    file_name_start = "def_ori_part_dos",
                                                    folder_name = "def_dos_file")

        return list_file_name

    def __acquire_def_ope_part_dos(self, list_ions_define):
        """Acquire the operated dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            list_def_ope_part_dos: the data of dos.
            dict_original_part_dos: the dictionary of the list which includes
                                    the data of dos.
        """
        (list_operated_part_dos, 
         dict_operated_part_dos) = self.__acquire_operated_part_dos()
        list_def_ope_part_dos = self.__acquire_define_part_dos(list_ions_define, list_operated_part_dos)

        return list_def_ope_part_dos, dict_operated_part_dos

    def create_def_ope_part_dos(self, list_ions_define):
        """Create the file wichi includes the operated dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            the list includes the name of files.
            Note: the orbitals: {s, py, pz, px, ...}
        """
        (list_def_ope_part_dos,
         dict_def_ope_part_dos) = self.__acquire_def_ope_part_dos(list_ions_define)
        list_file_name = self.__create_def_dos_file(list_def_ope_part_dos,
                                                    dict_def_ope_part_dos,
                                                    file_name_start = "def_ope_part_dos",
                                                    folder_name = "def_dos_file")
        return list_file_name

    def __acquire_def_ope_add_dos(self, list_ions_define):
        """Acquire the operated dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            list_def_ope_part_dos: the data of dos.
            dict_original_part_dos: the dictionary of the list which includes
                                    the data of dos.
        """
        (list_operated_add_dos, 
         dict_operated_add_dos) = self.__acquire_operated_add_dos()
        list_def_ope_add_dos = self.__acquire_define_part_dos(list_ions_define, list_operated_add_dos)

        return list_def_ope_add_dos, dict_operated_add_dos

    def create_def_ope_add_dos(self, list_ions_define):
        """Create the file wichi includes the operated dos data for define atoms list.

        Args:
            list_ion_define: a list which includes the tag of define atoms list.

        Return:
            the list includes the name of files.
            Note: the orbitals: s, p, d, f
        """
        (list_def_ope_add_dos,
         dict_def_ope_add_dos) = self.__acquire_def_ope_add_dos(list_ions_define)
        list_file_name = self.__create_def_dos_file(list_def_ope_add_dos,
                                                    dict_def_ope_add_dos,
                                                    file_name_start = "def_ope_add_dos",
                                                    folder_name = "def_dos_file")
        return list_file_name

    def create_part_dos_for_element(self, 
                                   folder_name = "dos_for_element"):
        """Create the file for saving the data of eigen values and dos of each element.

        Args:
            folder_name: the name of folder for saving the file.

        Return:
             a list includes the path of file.
        """
        list_file = []

        list_type_ion = self.__acquire_list_type_ion()

        for str_ele, list_ele_ions in list_type_ion:
            (list_dos, 
             dict_dos) = self.__acquire_def_ope_part_dos(list_ele_ions)
            file_name = "dos_partial_" + str_ele
            list_temp = self.__create_def_dos_file(list_dos, 
                                                 dict_dos, 
                                                 file_name,
                                                 folder_name)
            for f in list_temp:
                list_file.append(f)

        return list_file

    def create_add_dos_for_element(self, 
                                    folder_name = "dos_for_element"):
        """Create the file for saving the data of eigen values and dos of each element.

        Args:
            folder_name: the name of folder for saving the file.

        Return:
             a list includes the path of file.
        """
        list_file = []

        list_type_ion = self.__acquire_list_type_ion()

        for str_ele, list_ele_ions in list_type_ion:
            (list_dos, 
             dict_dos) = self.__acquire_def_ope_add_dos(list_ele_ions)
            file_name = "dos_add_" + str_ele
            list_temp = self.__create_def_dos_file(list_dos, 
                                                 dict_dos, 
                                                 file_name,
                                                 folder_name)
            for f in list_temp:
                list_file.append(f)

        return list_file



    def __acquire_projected_original_eigenvalues(self):
        """Acquire the original eigen values of projected band structure.

        It is the same eigen value with the the band structure.

        Return:
            a list includes the original eigen values of projected band structure.
            the layer of data: spin -> band -> kpoint -> eigen value
        """
        path_eigenvalues = "./calculation/projected/eigenvalues/array/set/set[@comment='spin %d']/set[@comment='kpoint %d']/r"
        list_original_eigens_each_b = []
        num_kpoints_start = self.num_kpoints_start
        num_kpoints_end   = self.num_kpoints_end

        if self.calcu_paras["ISPIN"] == 2:
            list_spins = [1, 2] # spin 1, 2
        else:
            list_spins = [1]
        #num_bands = int(self.calcu_paras["NBANDS"])
        list_kpoints = [i for i in range(num_kpoints_start, num_kpoints_end + 1)]

        # Acquire the data of band structure
        # the layer of data
        # spin -> kpoint -> band
        list_original_eigens_each_k = []
        for ns in list_spins:
            list_spin_temp = []
            for nk in list_kpoints:
                list_kpoint_temp = []
                for r in self.root.findall(path_eigenvalues % (ns, nk)):
                    [energy, occ] = st.get_number(r.text, 2, "float")
                    #print(energy)
                    list_kpoint_temp.append(energy)
                list_spin_temp.append(list_kpoint_temp)
            list_original_eigens_each_k.append(list_spin_temp)

        num_spins   = len(list_original_eigens_each_k)
        num_kpoints = len(list_original_eigens_each_k[0])
        num_bands   = len(list_original_eigens_each_k[0][0])
        # the layer of data
        #spin -> band -> kpoint
        for ns in range(num_spins):
            list_spin_temp = []
            for nb in range(num_bands):
                list_band_temp = []
                for nk in range(num_kpoints):
                    list_band_temp.append(list_original_eigens_each_k[ns][nk][nb])
                list_spin_temp.append(list_band_temp)
            list_original_eigens_each_b.append(list_spin_temp)

        return list_original_eigens_each_b

    def __acquire_projected_operated_eigenvalues(self):
        """Calculate the operated eigen values of projected band structure.

        It is the same eigen value with the the band structure.

        Return:
            a list includes the operated eigen values of projected band structure.
            which has finished moving the fermi level.
            the layer of data: spin -> band -> kpoint -> eigen value
        """
        list_operated_eigens_each_b = []
        # the layer of data
        # spin -> band -> kpoint
        list_original_eigens_each_b = self.__acquire_projected_original_eigenvalues()
        #print(list_original_eigens_each_b)
        revise_data                 = self.acquire_revise_data()

        num_spins = len(list_original_eigens_each_b)
        num_bands = len(list_original_eigens_each_b[0])
        num_kpoints = len(list_original_eigens_each_b[0][0])

        for ns in range(num_spins):
            list_spin_temp = []
            for nb in range(num_bands):
                list_band_temp = []
                for nk in range(num_kpoints):
                    list_band_temp.append(list_original_eigens_each_b[ns][nb][nk] - revise_data)
                list_spin_temp.append(list_band_temp)
            list_operated_eigens_each_b.append(list_spin_temp)

        return list_operated_eigens_each_b

    def __acquire_projected_part_orbits(self):
        """Acquire the weight of each orbital of projected band structure.

        It is the same eigen value with the the band structure.

        Return:
            a list includes the weight of each orbital of projected band structure.(just total spin)
            a dictionary includes the key(the energy and the orbital) and the value(the column)
        """
        path_of_field = "./calculation/projected/array/field"
        path_orbit_weight = "./calculation/projected/array/set/set[@comment='spin%d']/set[@comment='kpoint %d']/set[@comment='band %d']r"
        dict_projected_part_orbits = {}
        list_projected_part_orbits = []
        num_kpoints_start = self.num_kpoints_start
        num_kpoints_end = self.num_kpoints_end

        # Prepare the list of ions and spins
        list_ions = None
        list_spins = None
        # the first element of list_ions and list_spins should be 1.
        list_ions = [i for i in range(1, int(self.calcu_paras["num_atoms"]) + 1)] # here,  the number of atoms should subplus 1
        if self.calcu_paras["LSORBIT"] == "T":
            list_spins = [1, 2, 3, 4] # spin 1, 2, 3, 4
        #else:
        #    if self.calcu_paras["ISPIN"] == 2:
        #        list_spins = [1, 2] # spin 1, 2
        #    else:
        #        list_spins = [1]
        # Finished preparing the list of ions and spins

        # Acquire the meaning of data in each row
        # the element of dict_dos_partial concludes, energy, s, py, pz, px, dxy, dyz, dz2, dxz, x2-y2
        temp_index = 0
        for field in self.root.findall(path_of_field):
            dict_projected_part_orbits[field.text.strip()] = temp_index
            temp_index += 1
        # Finished acquiring the meaning of data in each row

        num_bands = int(self.calcu_paras["NBANDS"])
        list_kpoints = [i for i in range(num_kpoints_start, num_kpoints_end + 1)]
        # Acquire the data of orbit weight
        for nk in list_kpoints:
            list_kpoint_temp = []
            for nb in range(1, num_bands + 1):
                list_band_temp = []
                for r in self.root.findall(path_orbit_weight % (1, nk, nb)): # here, the spin is just 1
                    temp = st.get_number(r.text, len(dict_projected_part_orbits), "float")
                    list_band_temp.append(temp)
                list_kpoint_temp.append(list_band_temp)
            list_projected_part_orbits.append(list_kpoint_temp)
        #print(np.array(list_orbit_data).shape)
        # Finished acquire the data of orbit weight

        return list_projected_part_orbits, dict_projected_part_orbits

    def __acquire_projected_add_orbits(self):
        """Acquire the weight of each orbital of projected band structure.

        It is the same eigen value with the the band structure.

        Return:
            a list includes the weight of each orbital of projected band structure.(just total spin)
            a dictionary includes the key(the energy and the orbital) and the value(the column)
        """
        (list_projected_part_orbits,
         dict_projected_part_orbits) = self.__acquire_projected_part_orbits()
        list_projected_add_orbits = []
        dict_projected_add_orbits = {}

        # Acquire the data of s, p, d, f orbits weight
        if len(dict_projected_part_orbits) == 9:
            dict_projected_add_orbits = {"s" : 0, "p" : 1, "d" : 2}
            num_kpoints = len(list_projected_part_orbits)
            num_bands   = len(list_projected_part_orbits[0])
            num_ions    = len(list_projected_part_orbits[0][0])
            for nk in range(num_kpoints):
                list_kpoint_temp = []
                for nb in range(num_bands):
                    list_band_temp = []
                    for ni in range(num_ions):
                        dict_temp = {"s" : 0, "p" : 0, "d" : 0}
                        n_orbit = dict_projected_part_orbits["s"]
                        dict_temp["s"] = list_projected_part_orbits[nk][nb][ni][n_orbit]
                        for o in ["px", "py", "pz"]:
                            n_orbit = dict_projected_part_orbits[o]
                            dict_temp["p"] += list_projected_part_orbits[nk][nb][ni][n_orbit]
                        for o in ["dxy", "dyz", "dz2", "dxz", "x2-y2"]:
                            n_orbit = dict_projected_part_orbits[o]
                            dict_temp["d"] += list_projected_part_orbits[nk][nb][ni][n_orbit]
                        temp = [dict_temp["s"],
                                dict_temp["p"],
                                dict_temp["d"]]
                        list_band_temp.append(temp)
                    list_kpoint_temp.append(list_band_temp)
                list_projected_add_orbits.append(list_kpoint_temp)
        # Finished acquring the data of s, p, d, f orbits weight

        return list_projected_add_orbits, dict_projected_add_orbits

    def __acquire_define_orbits(self, list_ions_define, list_projected_orbits):
        """Acquire the weight of each orbital of the difine atoms list of projected band structure.

        It is the same eigen value with the the band structure.

        Args:
            list_ions_define: a list with the atoms list.
                              Note: the atoms list should start at 1.
            list_projected_orbits: a list includes the weight of each orbital.

        Return:
            a list includes the weight of each orbital of projected band structure.(just total spin)
            Note: the weight of each orbital of the define atoms list.
        """
        list_define_orbits = []
        num_kpoints = len(list_projected_orbits)
        num_bands   = len(list_projected_orbits[0])
        num_ions    = len(list_projected_orbits[0][0])
        num_orbits  = len(list_projected_orbits[0][0][0])

        for nk in range(num_kpoints):
            list_kpoint_temp = []
            for nb in range(num_bands):
                list_band_temp = []
                for no in range(num_orbits):
                    temp = 0
                    for ion in list_ions_define:
                        temp += list_projected_orbits[nk][nb][ion - 1][no]
                    list_band_temp.append(temp)
                list_kpoint_temp.append(list_band_temp)
            list_define_orbits.append(list_kpoint_temp)

        return list_define_orbits

    def __acquire_define_part_orbits(self, list_ions_define):
        """Acquire the weight of each orbital of the difine atoms list of projected band structure.

        It is the same eigen value with the the band structure.

        Args:
            list_ions_define: a list with the atoms list.
                              Note: the atoms list should start at 1.
            list_projected_orbits: a list includes the weight of each orbital.

        Return:
            a list includes the weight of each orbital of projected band structure.(just total spin)
            Note: the weight of each orbital of the define atoms list.
            the orbital: s, py, pz, px, dxy, ...
           a dictionary includes the key(the energy and the orbital) and the value(the column)
        """
        (list_projected_part_orbits,
         dict_projected_part_orbits) = self.__acquire_projected_part_orbits()
        list_define_part_orbits = self.__acquire_define_orbits(list_ions_define, list_projected_part_orbits)

        return list_define_part_orbits, dict_projected_part_orbits

    def __acquire_define_add_orbits(self, list_ions_define):
        """Acquire the weight of each orbital of the difine atoms list of projected band structure.

        It is the same eigen value with the the band structure.

        Args:
            list_ions_define: a list with the atoms list.
                              Note: the atoms list should start at 1.
            list_projected_orbits: a list includes the weight of each orbital.

        Return:
            a list includes the weight of each orbital of projected band structure.(just total spin)
            Note: the weight of each orbital of the define atoms list.
            the orbital: s, p, d, f
           a dictionary includes the key(the energy and the orbital) and the value(the column)
        """
        (list_projected_add_orbits, 
         dict_projected_add_orbits) = self.__acquire_projected_add_orbits()
        list_define_add_orbits = self.__acquire_define_orbits(list_ions_define, list_projected_add_orbits)

        return list_define_add_orbits, dict_projected_add_orbits

    def __create_define_orbits_file(self, list_define_orbits, dict_define_orbits, file_name, folder_name):
        """Create the file for saving the data of eigen values and the weight of each orbital.

        Args:
            list_define_orbits: a list includes the data of the weight of each orbital.
            dict_define_orbits: a dictionary with the key(the energy and the orbital)
                                and the value(the column).
            file_name: the name of file
            folder_name: the name of folder for saving the file

        Return:
            the path of file
        """
        my_folder = self.folder_save + "/" + folder_name
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        
        list_projected_operated_eigens = self.__acquire_projected_operated_eigenvalues()
        list_kpoints_distance = self.calcu_list_kpoints_distance()

        num_kpoints = len(list_define_orbits)
        num_bands   = len(list_define_orbits[0])
        num_orbits  = len(list_define_orbits[0][0])

        my_file = my_folder + "/" + file_name
        with open(my_file, "w") as f:
            # cue line
            string = "%18s\t" % "kpath"
            string += "%18s\t" % "energy"
            for tag in dict_define_orbits:
                string += "%18s\t" % tag
            string += "\n"
            f.write(string)
            # cue line

            for nb in range(num_bands):
                for nk in range(num_kpoints):
                    string = "%18.6f\t" % list_kpoints_distance[nk] 
                    string += "%18.6f\t" % list_projected_operated_eigens[0][nb][nk]
                    for no in range(num_orbits):
                        string += "%18.6f\t" % list_define_orbits[nk][nb][no]
                    string += "\n"
                    f.write(string)
                f.write("\n")
        return my_file

    def create_define_part_orbits(self, list_ions_define, 
                                  file_name = "def_projected_band_structure_part.dat",
                                  folder_name = "def_projected_band_structure"):
        """Create the file for saving the data of eigen values and the weight of each orbital.

        Args:
            list_ions_define: a list of atoms to recalculate the weight of each orbital.
            file_name: the name of file.
            folder_name: the name of folder for saving the file.

        Return:
            the path of file.
        """
        (list_define_part_orbits, 
         dict_define_part_orbits) = self.__acquire_define_part_orbits(list_ions_define)
        my_file = self.__create_define_orbits_file(list_define_part_orbits, 
                                                   dict_define_part_orbits, 
                                                   file_name,
                                                   folder_name)
        return my_file

    def create_define_add_orbits(self, list_ions_define, 
                                  file_name = "def_projected_band_structure_add.dat",
                                  folder_name = "def_projected_band_structure"):
        """Create the file for saving the data of eigen values and the weight of each orbital.

        Args:
            list_ions_define: a list of atoms to recalculate the weight of each orbital.
            file_name: the name of file.
            folder_name: the name of folder for saving the file.

        Return:
            the path of file.
        """
        (list_define_add_orbits, 
         dict_define_add_orbits) = self.__acquire_define_add_orbits(list_ions_define)
        my_file = self.__create_define_orbits_file(list_define_add_orbits, 
                                                   dict_define_add_orbits, 
                                                   file_name,
                                                   folder_name)
        return my_file

    def create_projected_part_orbits_for_element(self, 
                                                 folder_name = "projected_band_structure_for_element"):
        """Create the file for saving the data of eigen values and the weight of each orbital of each element.

        Args:
            folder_name: the name of folder for saving the file.

        Return:
             a list includes the path of file.
        """
        list_file = []

        list_type_ion = self.__acquire_list_type_ion()

        for str_ele, list_ele_ions in list_type_ion:
            (list_orbits, 
             dict_orbits) = self.__acquire_define_part_orbits(list_ele_ions)
            file_name = "projected_band_structure_partial_" + str_ele + ".dat"
            my_file = self.__create_define_orbits_file(list_orbits, 
                                                       dict_orbits, 
                                                       file_name,
                                                       folder_name)
            list_file.append(my_file)

        return list_file

    def create_projected_add_orbits_for_element(self, 
                                                folder_name = "projected_band_structure_for_element"):
        """Create the file for saving the data of eigen values and the weight of each orbital of each element.

        Args:
            folder_name: the name of folder for saving the file.

        Return:
            a list includes the path of file.
        """
        list_file = []

        list_type_ion = self.__acquire_list_type_ion()

        for str_ele, list_ele_ions in list_type_ion:
            (list_orbits, 
             dict_orbits) = self.__acquire_define_add_orbits(list_ele_ions)
            file_name = "projected_band_structure_add_" + str_ele + ".dat"
            my_file = self.__create_define_orbits_file(list_orbits, 
                                                       dict_orbits, 
                                                       file_name,
                                                       folder_name)
            list_file.append(my_file)
            
        return list_file

















if __name__ == "__main__":
    xml = Vasprunxml(folder_save = "my_try")
    '''
    list_test = xml.get_list_atoms()
    print(list_test)
    list_test = xml.get_list_type_ion()
    print(list_test)
    file_name = xml.create_atomlist_file()
    print(file_name)

    print("reciprocal lattice")
    list_test = xml.get_list_reciprocal_lattice()
    print(list_test)
    print("basis lattice")
    list_test = xml.get_list_basis_lattice()
    print(list_test)
    print("positions")
    list_test = xml.get_list_positions()
    print(list_test)
    print("real positions")
    list_test = xml.get_list_real_positions()
    print(list_test)

    #my_file = xml.create_kpoints_file()

    revise_data = xml.acquire_revise_data()
    print("%s = %f" % ("revise_data", revise_data))
    my_file = xml.create_bandgap_file()
    list_file = xml.create_eigenvalue_file()
    print(my_file)
    print(list_file)


    list_file = xml.create_operated_part_dos_file()
    print(list_file)
    list_file = xml.create_operated_add_dos_file()
    print(list_file)
    list_file = xml.create_original_part_dos_file()
    print(list_file)
    list_file = xml.create_original_add_dos_file()
    print(list_file)

    list_file = xml.create_def_ope_part_dos([6])
    print(list_file)
    list_file = xml.create_def_ope_add_dos([6])
    print(list_file)

    list_file =xml.create_projected_add_orbits_for_element()
    print(list_file)
    list_file = xml.create_projected_part_orbits_for_element()
    print(list_file)
    my_file = xml.create_define_part_orbits([1])
    print(my_file)
    my_file = xml.create_define_add_orbits([1])
    print(my_file)

    list_file = xml.create_part_dos_for_element()
    print(list_file)
    for i in list_file:
        print(i)
    list_file = xml.create_add_dos_for_element()
    for i in list_file:
        print(i)
    '''
