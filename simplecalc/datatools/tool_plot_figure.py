#!/THFS/home/su-hp/anaconda3/bin/python
#Purpose: Data post-processing and plotting the figure.
#Recode of revisions:
#   Date    Programmer  Description of change   Contact information        Change
#   ====    ==========  =====================   ===================        ------
#0. 20190222    Blackboard  Original code           1125139812@qq.com  

#---------Define packages---------
import numpy as np
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import numpy as np
import smalltool as st
import os
import config_plot as cplot
#---------Finished defining variables----------

#----------Define variables----------
#----------Finished defining variables----------

#----------Define setting----------

#----------Finished defining setting----------

#----------Define functions----------
def initial_setting():
    plt.rcParams["figure.figsize"] = (4.0, 8.0)
    plt.rcParams["savefig.dpi"] = 500
    plt.rcParams["figure.dpi"] = 500
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"

def read_file(file_name):
    dict_of_col = {}
    list_row = []
    list_col = []
    with open(file_name, "r") as f:
        line = f.readline()
        line_split = line.split()
        for n in range(len(line_split)):
            dict_of_col[line_split[n]] = n # the first line is a dictionary
        lines = f.readlines()
        for line in lines:
            list_row.append(line.split())

    for j in range(len(list_row[0])):
        list_temp = []
        for i in range(len(list_row)):
            if st.is_number(list_row[i][j]):
                list_temp.append(float(list_row[i][j]))
            else:
                list_temp.append(list_row[i][j])
        list_col.append(list_temp)

    return dict_of_col, list_col

def read_file_orbits(file_name):
    zoom_factor = [1, 1, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
    list_projected_row = []
    list_projected_col = []
    dict_projected = {}
    with open(file_name, "r") as f:
        line = f.readline()
        list_line = line.split()
        for n in range(len(list_line)):
            dict_projected[list_line[n]] = n

        lines = f.readlines()
        for line in lines:
            list_projected_row.append(line.split())

        list_temp = []
        how_much_col = len(dict_projected)

        # Split the data of each field, each band, each kpoint
        for i in range(how_much_col):
            list_projected_col.append([])
            list_temp.append([])
        for i in range(len(list_projected_row)):
        # Use the vaccum line to split each band in 
        # band structure. If we meet the vaccum line,
        # we can save the data to the list(list_projected_row)
            if len(list_projected_row[i]) == 0:
                for n in range(how_much_col):
                    list_projected_col[n].append(list_temp[n])
                    list_temp[n] = []
            else:
                for n in range(how_much_col):
                    if n <= 1:
                        list_temp[n].append(float(list_projected_row[i][n]))
                    else:
                        list_temp[n].append(float(list_projected_row[i][n]) *
                                            zoom_factor[n])
        # Finished splitting the data of each field, each band, each kpoint
    # Finished reading the data from file
    return dict_projected, list_projected_col

def plot_band_structure(data_in_list = ["my_band.dat"], data_in_kpath = None, 
                        figure_name = "my_band_structure.png", figure_save = "."):
    """Plot the figure of band structure.

    Args:
        data_in_list: a list includes the name of files whih has the eigen values of band structure.
        data_in_kpath: the name of file which includes the high symmetry k path of band structure.
        figure_name: the name of figure
        figure_save: the folder fro saving the figure

    Return:
        the path of figure

    """
    fig_max = cplot.fig_max
    fig_min = cplot.fig_min
    plt.cla()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)

    plt.figure(figsize = (4, 8), dpi = 500)
    if data_in_kpath != None:
        # Read the data of kpath from file my_kpath.dat
        # tags: kpath_tag, kpath_data, energy_min, energy_max
        (dict_kpath, list_k_col) = read_file(data_in_kpath)
        # Finished reading the data of kpath from file my_kpath.dat
        # Plot the high symmetry path
        for d in list_k_col[dict_kpath["kpath_data"]]:
            plt.axvline(d, linestyle = "-", linewidth = 0.5, color = "gray")
        # Finished plotting the high symmetry path

    if 1 == len(data_in_list):
        data_in_file = data_in_list[0]
        # Read the datt of band structure from file my_band.dat
        (dict_band, list_band_col) = read_file(data_in_file)
        # Finished reading the data of band structure from file my_band.dat
        # Plot each band
        for n in range(1, len(list_band_col)):
            plt.plot(list_band_col[0], list_band_col[n], color = "black", linewidth = 0.7)
        # Finished plotting each band
    elif 2 == len(data_in_list):
        data_in_file = data_in_list[0]
        # Read the datt of band structure from file my_band.dat
        (dict_band, list_band_col) = read_file(data_in_file)
        # Finished reading the data of band structure from file my_band.dat
        # Plot each band
        for n in range(1, len(list_band_col)):
            plt.plot(list_band_col[0], list_band_col[n], color = "red", linewidth = 0.7)
        # Finished plotting each band 
        data_in_file = data_in_list[1]
        # Read the datt of band structure from file my_band.dat
        (dict_band, list_band_col) = read_file(data_in_file)
        # Finished reading the data of band structure from file my_band.dat
        # Plot each band
        for n in range(1, len(list_band_col)):
            plt.plot(list_band_col[0], list_band_col[n], color = "blue", linewidth = 0.7)
        # Finished plotting each band 

    # Plot the fermi line
    plt.axhline(0, linestyle = "--", linewidth = 0.5, color = "green")
    # Finshed plotting the fermi line

    # Set the parameters of figure
    plt.xlim(list_band_col[0][0], list_band_col[0][-1])
    plt.ylim(fig_min, fig_max)
    if data_in_kpath != None:
        plt.xticks(list_k_col[dict_kpath["kpath_data"]],
                   list_k_col[dict_kpath["kpath_tag"]])

    my_figure = figure_save + "/" + figure_name
    plt.savefig(my_figure)
    plt.cla()
    # Finished setting the parameters of figure
    return my_figure

def plot_choose_projected_band_structure(list_file_orbit_color_label, 
                                         data_in_kpath = None,
                                         figure_name = "projected_band_structure_by_define.png",
                                         figure_save = "projected_band_structure_choose_by_yourself"):
    fig_max = cplot.fig_max
    fig_min = cplot.fig_min
    plt.cla()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)

    if data_in_kpath != None:
        # tags: kpath_tag, kpath_data, energy_min, energy_max
        (dict_kpath, list_k_col) = read_file(data_in_kpath)
        # Finished reading the data of kpath from file my_kpath.dat

    for n_define in range(len(list_file_orbit_color_label)):
        my_file = list_file_orbit_color_label[n_define][0]
        my_orbit = list_file_orbit_color_label[n_define][1]
        my_color = list_file_orbit_color_label[n_define][2]
        my_label = list_file_orbit_color_label[n_define][3]

        # Read the data from file
        (dict_projected, list_projected_col) = read_file_orbits(my_file)
        # Finished reading the data from file

        # Plot the figure
        plt.figure(figsize = (4, 8), dpi = 500)
        num_bands = len(list_projected_col[0])
        if n_define == 0: # the band structure just plot one time
            # Plot the band structure
            for nb in range(num_bands):
                plt.plot(list_projected_col[dict_projected["kpath"]][nb], 
                         list_projected_col[dict_projected["energy"]][nb],
                         color = "black",
                         linewidth = 0.7)
            # Finished plotting the band structure
            # Plot the fermi line
            plt.axhline(0, linestyle = "-", linewidth = 0.5, color = "green")
            # Finshed plotting the fermi line
            if data_in_kpath != None:
                # Plot the high symmetry path
                for d in list_k_col[dict_kpath["kpath_data"]]:
                    plt.axvline(d, linestyle = "-", linewidth = 0.5, color = "gray")
                # Finished plotting the high symmetry path

        # Plot the orbital weight
        for b in range(num_bands):
            plt.scatter(list_projected_col[dict_projected["kpath"]][b],
                        list_projected_col[dict_projected["energy"]][b],
                        s = list_projected_col[dict_projected[my_orbit]][b],
                        marker = "o",
                        color = my_color,
                        alpha = 0.2)
        # Finished plotting the orbit weight

        label_str = my_label + "  " + my_orbit
        plt.scatter(-10,
                    -10,
                    marker = "o",
                    color = my_color,
                    label = label_str,
                    alpha = 0.2)
        # Finished plotting the figure

    plt.legend(loc = "lower right")
    plt.xlim(list_projected_col[dict_projected["kpath"]][0][0],
            list_projected_col[dict_projected["kpath"]][0][-1])
    plt.ylim(fig_min, fig_max)
    if data_in_kpath != None:
        plt.xticks(list_k_col[dict_kpath["kpath_data"]],
                   list_k_col[dict_kpath["kpath_tag"]])

    my_figure = figure_save + "/" + figure_name
    plt.savefig(my_figure)
    plt.cla()

    return my_figure

def plot_each_orbits_projected_band_structure(file_name, data_in_kpath = None, figure_save = "."):
    set_orbit = cplot.set_orbit
    dict_color = cplot.dict_color
    plt.cla()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)
    list_figure = []

    if data_in_kpath != None:
        # tags: kpath_tag, kpath_data, energy_min, energy_max
        (dict_kpath, list_k_col) = read_file(data_in_kpath)
        # Finished reading the data of kpath from file my_kpath.dat

    # Read the data from file
    (dict_projected, list_projected_col) = read_file_orbits(file_name)
    name_temp = os.path.split(file_name)
    figure_name_start = name_temp[-1].split(".")[0]
    # Finished reading the data from file

    for orbit in dict_projected:
        if orbit in set_orbit:
            list_file_orbit_color_label = [
                                           [file_name,
                                            orbit,
                                            dict_color[orbit],
                                            ""
                                           ]
                                          ]
            figure_name = figure_name_start + "_" + orbit + ".png"
            my_figure = plot_choose_projected_band_structure(list_file_orbit_color_label,
                                                             data_in_kpath = data_in_kpath,
                                                             figure_name = figure_name,
                                                             figure_save = figure_save)
            list_figure.append(my_figure)

    return list_figure

def plot_choose_dos(list_file_orbit_color_label, 
                    figure_name = "dos_by_define.png",
                    figure_save = "."):
    plt.cla()
    initial_setting()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)
    my_figure = figure_save + "/" + figure_name

    plt.figure(figsize = (8, 4), dpi = 500)
    for n_define in range(len(list_file_orbit_color_label)):
        my_file  = list_file_orbit_color_label[n_define][0]
        my_orbit = list_file_orbit_color_label[n_define][1]
        my_color = list_file_orbit_color_label[n_define][2]
        my_label = list_file_orbit_color_label[n_define][3]

        # Read the data from file
        (dict_projected, list_projected_col) = read_file(my_file)
        # Finished reading the data from file

        # Plot the figure
        list_energy = list_projected_col[dict_projected["energy"]]
        list_orbit  = list_projected_col[dict_projected[my_orbit]]
        plt.plot(list_energy, list_orbit, color = my_color, label = my_label)
        # Finished plotting the figure

    plt.axvline(0, linestyle = "--", color = "gray")
    plt.legend(loc = "upper right")
    #plt.xlim(dos_x_min, dos_x_max)
    #plt.ylim(dos_y_min, dos_y_max)
    plt.savefig(my_figure)
    plt.cla()

    return my_figure

def plot_each_orbit_dos(file_name, figure_save="."):
    """Plot the figure with all the dos data in the file. 

    Args:
        file_name: the name of file which includes the data of dos.
        figure_save: the name of folder for saving the figure.

    Return:
        the path of figure.
        Note: All circumstances are taken into account, such as:
        {s, p, d}, {s, p, d, f}, {s, px, py, pz, dxy, ...},
        {s, py, pz, px, dxy, ..., fxyz, ...}
    """
    dict_color = cplot.dict_color
    plt.cla()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)

    name_temp = os.path.split(file_name)
    figure_name_start = name_temp[-1].split(".")[0]
    my_figure = figure_save + "/" + figure_name_start + "_each_orbit.png"

    # Read the data from file
    (dict_dos, list_dos_col) = read_file(file_name)
    new_dict_dos = {v:k for k,v in dict_dos.items()}
    # Finished reading the data from file
    num_add_spd = 3
    num_add_spdf = 4
    num_part_spd = 9
    num_part_spdf = 16
    dict_norbit_nsubplot = { num_add_spd : 310, num_add_spdf : 410, num_part_spd : 330, num_part_spdf : 440}

    fig_split = dict_norbit_nsubplot[len(dict_dos) - 1]
    if num_add_spd == len(dict_dos) - 1:
        plt.figure(figsize = (9, 9), dpi = 500)
    elif num_add_spdf == len(dict_dos) - 1:
        plt.figure(figsize = (9, 12), dpi = 500)
    elif num_part_spd == len(dict_dos) - 1:
        plt.figure(figsize = (18, 9), dpi = 500)
    elif num_part_spdf == len(dict_dos) - 1:
        plt.figure(figsize = (18, 12), dpi = 500)
    for n in range(1, len(dict_dos)):
        list_energy = list_dos_col[dict_dos["energy"]]
        list_orbit = list_dos_col[n]
        ax = plt.subplot(fig_split + n)
        p, = plt.plot(list_energy, list_orbit, color = dict_color[new_dict_dos[n]])
        plt.legend([p], [new_dict_dos[n]], loc = "upper left")
        plt.axvline(0, linestyle = "--", color = "grey")
    plt.savefig(my_figure)
    plt.cla()
    return my_figure

def plot_total_dos(data_in_list, figure_name = "my_total_dos.png", figure_save="."):
    """Create the file includes the data of total dos and plot the figure for dos.

    Args:
        data_in_list: a list includes the name of dos file
        figure_name: the name of dos figure
        figure_save: the folder for savint figure

    Return:
        the path of figure
    """
    plt.cla()
    if not os.path.exists(figure_save):
        os.makedirs(figure_save)
    my_figure = figure_save + "/" + figure_name

    if 1 == len(data_in_list):
        file_dos = data_in_list[0]
        # Read the data from file
        (dict_dos, list_dos_col) = read_file(file_dos)
        # Finished reading the data from file
        # Plot the figure
        plt.figure(figsize = (8, 4), dpi = 500)
        list_energy = list_dos_col[dict_dos["energy"]]
        list_dos    = list_dos_col[dict_dos["total"]]
        plt.plot(list_energy, list_dos, color = "black", label = "total dos")
        plt.axvline(0, linestyle = "--", color = "grey")
        # Finshed plotting the figure
    elif 2 == len(data_in_list):
        file_dos = data_in_list[0]
        # Read the data from file
        (dict_dos, list_dos_col) = read_file(file_dos)
        # Finished reading the data from file
        # Plot the figure
        plt.figure(figsize = (8, 4), dpi = 500)
        list_energy = list_dos_col[dict_dos["energy"]]
        list_dos    = list_dos_col[dict_dos["total"]]
        plt.plot(list_energy, list_dos, color = "red", label = "spin up")
        # Finshed plotting the figure

        file_dos = data_in_list[1]
        # Read the data from file
        (dict_dos, list_dos_col) = read_file(file_dos)
        # Finished reading the data from file
        # Plot the figure
        list_energy = list_dos_col[dict_dos["energy"]]
        list_dos    = np.array(list_dos_col[dict_dos["total"]]) * (-1)
        plt.plot(list_energy, list_dos, color = "blue", label = "spin down")
        plt.axvline(0, linestyle = "--", color = "grey")
        # Finshed plotting the figure
    plt.legend()
    plt.savefig(my_figure)

    return my_figure


        








#----------Finished defining functions----------

if __name__ == "__main__":
    #plt.cla()
    #plot_band_structure(data_in_kpath = "my_kpath.dat")
    #my_file = "band_structure/my_band_spin_up.dat"
    #my_file = "my_band.dat"
    #plot_band_structure(my_file, figure_save = "band_structure")
    #initial_setting()
    file_name = "projected_band_structure_for_element/projected_band_structure_add_Mo.dat"
    plot_each_orbits_projected_band_structure(file_name,
                                              data_in_kpath = "band_structure/my_kpath.dat",
                                              figure_save = "projected_band_structure_for_element")
    '''
    list_file_orbit_color_label = [
                                    ["def_dos_file/def_ope_add_dos_spin1.dat",
                                     "s",
                                     "red",
                                     "ope part s"],
                                    ["def_dos_file/def_ope_add_dos_spin1.dat",
                                     "p",
                                     "green",
                                     "ope part p"]
                                  ]
    plot_choose_dos(list_file_orbit_color_label, figure_save = "def_dos_file")
    plot_each_orbit_dos("def_dos_file/def_ope_part_dos_spin1.dat")
    '''
    #file_name = "def_dos_file/def_ope_part_dos_spin1.dat"
    #(folder_name, f_name) = os.path.split(file_name)
    #my_figure = plot_each_orbit_dos(file_name, folder_name)
    #print(my_figure)
    #file_name = "def_dos_file/def_ope_add_dos_spin1.dat"
    #(folder_name, f_name) = os.path.split(file_name)
    #my_figure = plot_each_orbit_dos(file_name, folder_name)
    #print(my_figure)