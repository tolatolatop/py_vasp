'''Purpose: Get the data from file Vasprun.xml and other files.
            Create the file to save the data.
            Plot the figure.
'''

#----------Import packages----------
import os
import sys
from . import read_xml as rx
from . import tool_plot_figure as tpf
from . import read_kpoints as rk
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
from . import config_plot as cplot
#----------Finished importing packages----------

#----------Define functions----------
def create_plot_band_structure(file_xml = "vasprun.xml", file_k = "KPOINTS", folder_save = None):
    """Create the file includes the data of energy and plot the figure.

    Args:
        file_xml: the file includes the data of energy.
        file_k: the file includes the high symmetry k path.
        folder_save: the name of folder for saving the file and figure

    Return:
        a list includes the path of files and the path of figure.
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)
    kpoints = rk.KPOINTS(file_k, folder_save = folder_save)

    list_reciprocal_lattice = xml.get_list_reciprocal_lattice()
    file_kpath = kpoints.create_file_kpath_dat(list_reciprocal_lattice)

    list_band_file = xml.create_eigenvalue_file()
    for f in list_band_file:
        (fig_folder, file_name) = os.path.split(f)
        fig_name_start = file_name.split(".")[0]
        fig_name = fig_name_start + ".png"
        my_figure = tpf.plot_band_structure(data_in_list = list_band_file,
                                            data_in_kpath = file_kpath,
                                            figure_save = fig_folder,
                                            figure_name = fig_name)
    return [list_band_file, [my_figure]]

def create_plot_total_dos(file_xml="vasprun.xml", folder_save=None):
    '''Create the file for saving the data of total dos and plot the figure of total dos.

    Args:
        file_xml: the name of file which includes the data of total dos.
        folder_save: the name of folder for saving the file and figure.

    Return:
        a list includes the name of file and the name of figure.

    '''
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    list_file_dos = xml.create_total_dos_file()

    file_dos = list_file_dos[0]
    (folder_name, f_name) = os.path.split(file_dos)
    my_figure = tpf.plot_total_dos(list_file_dos, figure_save = folder_name)
    
    return [list_file_dos, [my_figure]]

def create_plot_dos_for_element(file_xml="vasprun.xml", folder_save=None):
    '''Create the file for saving the data of total dos and plot the figure of total dos.

    Args:
        file_xml: the name of file which includes the data of total dos.
        folder_save: the name of folder for saving the file and figure.

    Return:
        a list inclueds the names of file and the name of figures
    '''
    list_figure_dos = []

    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)
    list_file_dos = xml.create_part_dos_for_element()

    for file_dos in list_file_dos:
        (folder_name, f_name) = os.path.split(file_dos)
        my_figure = tpf.plot_each_orbit_dos(file_dos, folder_name)
        list_figure_dos.append(my_figure)

    return [list_file_dos, list_figure_dos]

def create_plot_projected_band_structure_for_element(file_xml = "vasprun.xml", file_k = "KPOINTS", folder_save = None):
    """Create the file includes the data of energy and the weight of each orbital and plot the figure.

    Args:
        file_xml: the file includes the data of energy and the weight of each orbital.
        file_k: the file includes the high symmetry k path.
        folder_save: the name of folder for saving the file and figure

    Return:
        a list includes the path of files and the path of figure.
    """
    list_figure_name = []
    list_file_name = []
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)
    kpoints = rk.KPOINTS(file_k, folder_save = folder_save)

    list_reciprocal_lattice = xml.get_list_reciprocal_lattice()
    file_kpath = kpoints.create_file_kpath_dat(list_reciprocal_lattice)

    list_part_file = xml.create_projected_part_orbits_for_element()
    list_add_file  = xml.create_projected_add_orbits_for_element()
    list_file_name = [i for i in list_part_file] + [i for i in list_add_file]

    for f in list_part_file:
        (f_folder, f_name) = os.path.split(f)
        list_part_fig = tpf.plot_each_orbits_projected_band_structure(f,
                                                                      data_in_kpath = file_kpath,
                                                                      figure_save = f_folder)

    for f in list_add_file:
        (f_folder, f_name) = os.path.split(f)
        list_add_fig = tpf.plot_each_orbits_projected_band_structure(f,
                                                                     data_in_kpath = file_kpath,
                                                                     figure_save = f_folder)
    list_figure_name = [i for i in list_part_fig] + [i for i in list_add_fig]

    return [list_file_name, list_figure_name]
'''
def create_band_structure(file_xml="vasprun.xml", folder_save=None):
    """Create the file to save the data of energy which can use to plot band structure.

    Args:
        file_xml: the file which includes the data ofenergy
        folder_save: the folder for saving file which we had created

    Return:
        a list includes the path of file
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    list_file_band = xml.create_eigenvalue_file()

    return list_file_band
'''
def calcu_distance(file_xml="vasprun.xml", list_ions_define = [1, 2], folder_save=None):
    """Calculate the distance of two positions in the real space.

    Args:
        list_ions_define: a list includes the tag of two atoms.
                          Note: the tag of atoms should start from 1.

    Return:
        the distance of two postions in the real space.
        Default: this function will return the distance of first two atoms.
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    distance = xml.calcu_distance_of_two_positions(list_ions_define)

    return distance

def calcu_angles(file_xml = "vasprun.xml", list_ions_define = [1, 2, 3], folder_save = None):
    """Calculate angles of three positions in the real space.

    Args:
        list_ions_define: a list includes the tag of three atoms.
                          Note: the tag of atoms should start from 1.

    Return:
        a list includes angles of three atoms in the real space.
        Default: this function will return angles of first three atoms
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    list_angles = xml.calcu_angles_of_three_positions(list_ions_define)

    return list_angles

def get_bandgap_file(file_xml = "vasprun.xml", folder_save = None):
    """Create the file includes the data of band gap, vbm and cbm.

    Args:
        file_xml: the name of file to save the data of band gap, vbm and cbm.
        folder_save: the name of folder to save the file.

    Return:
        the path of file.
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    my_file = xml.create_bandgap_file()

    return my_file

def get_kpoints_list_file(file_xml = "vasprun.xml", folder_save = None):
    """Create the file which includes data of k points in the direct axes.

    Args:
        file_xml: the name of file to save the data of k points.
        folder_save: the name of folder to save the file.

    Return:
        a string which includes the path of files.
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    my_file = xml.create_kpoints_file()

    return my_file

def get_ion_dos_file(file_xml = "vasprun.xml", folder_save = None):
    """Create the file which includes partial data of data for each ion.

    Args:
        file_xml: the name of file to save the data of partial dos data.
        folder_save: the name of folder to save the file.

    Return:
        a list includes the name of files.
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    list_file_part = xml.create_operated_part_dos_file()
    list_file_add  = xml.create_operated_add_dos_file()
    list_file = [i for i in list_file_part] + [i for i in list_file_add]

    return list_file

def get_def_dos_file(list_ions_define, file_xml = "vasprun.xml", folder_save = None):
    """Create the file for saving the data of eigen values and the data of dos

    Args:
        list_ions_define: a list includes the tag of ions.
        file_xml: the file includes the data of eigen values and the data of dos
        folder_save: the folder for saving files

    Return:
        a list includes the path of files
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    list_file_part = xml.create_def_ope_part_dos(list_ions_define)
    list_file_add  = xml.create_def_ope_add_dos(list_ions_define)
    list_file = [i for i in list_file_part] + [i for i in list_file_add]

    return list_file

def get_def_projected_band_structure_file(list_ions_define, file_xml = "vasprun.xml", folder_save = None):
    """Create the file for saving the data of eigen values and the weight of each orbital.

    Args:
        list_ions_define: a list includes the tag of ions.
        file_xml: the file includes the data of eigen values and the weight of each orbital
        folder_save: the folder for saving files

    Return:
        a list includes the path of file
    """
    xml = rx.Vasprunxml(file_xml, folder_save = folder_save)

    my_file_part = xml.create_define_part_orbits(list_ions_define)
    my_file_add  = xml.create_define_add_orbits(list_ions_define)
    list_file = [my_file_part, my_file_add]

    return list_file

def get_each_orbits_pbs_fig(file_name, data_in_kpath = None, folder_save = None):
    """Plot the figure which includes the data of projected band structure.

    Args:
        file_name: plot the data in the file
        data_in_kpath: the file includes the data of high symmetry k path
        folder_save: the folder for saving figures

    Return:
        a list includes the path of figure
    """
    (folder_name, f_name) = os.path.split(file_name)
    if "" == folder_name:
        folder_name = "."

    list_fig = tpf.plot_each_orbits_projected_band_structure(file_name = file_name, 
                                                             data_in_kpath = data_in_kpath, 
                                                             figure_save = folder_name)

    return list_fig

def get_each_orbits_dos_fig(file_name, folder_save = None):
    (folder_name, f_name) = os.path.split(file_name)
    if "" == folder_name:
        folder_name = "."

    my_fig = tpf.plot_each_orbit_dos(file_name = file_name, 
                                     figure_save = folder_name)

    return my_fig

#----------Finshed defining functions----------

if __name__ == "__main__":
    print("test")
    #create_plot_band_structure()
    #create_plot_total_dos()
    #create_plot_dos_for_element()
    #list_temp = create_plot_projected_band_structure_for_element()
    distance = calcu_distance(list_ions_define = [1, 2])
    list_angles = calcu_angles(list_ions_define = [1, 2, 3])
    print(distance)
    print(list_angles)
    my_file = get_bandgap_file()
    print(my_file)
    my_file = get_kpoints_list_file()
    print(my_file)
    '''
    list_file = get_def_projected_band_structure_file([1])
    for file_name in list_file:
        list_fig = get_each_orbits_pbs_fig(file_name)
        for i in list_fig:
            print(i)
    '''
    list_file = get_def_dos_file([1])
    for file_name in list_file:
        my_fig = get_each_orbits_dos_fig(file_name)
        print(my_fig)

