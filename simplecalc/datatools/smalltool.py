#!/THFS/home/su-hp/anaconda3/bin/python
#Purpose: Some small tools for mathmatic calculation.
#Recode of revisions:
#   Date        Programmer  Description of change   Contact information        Change
#   ========    ==========  =====================   ===================        ------
#0. 20190223    Blackboard  Original code           1125139812@qq.com  

#---------Import packages---------
import numpy as np
import re
import math
#---------Finished importing variables----------

#----------Define functions----------
def is_number(str):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    resule = pattern.match(str)
    if resule:
        return True
    else:
        return False

def get_number(tstr, number = 1, dtype = "float"):
    '''
    This function was copied from zhou's code.
    '''
    if dtype == "float":
        re_test = re.compile("[0-9.\+\-E]+")
        convert = float
    elif dtype == "int":
        re_test = re.compile("[0-9]+")
        convert = int
    r = re_test.findall(tstr)[0:number]
    # if you didn't set number, the function will convert every string in variable tstr.
    if number == None: 
        number = len(r)
    if len(r) != number:
        raise ValueError("Error in %s" % (tstr))
    else:
        result = [convert(i) for i in r]
    return result

def get_max_tag_data(list_x):  
    for n in range(len(list_x)):
        if n == 0:
            max_tag = n
            max_data = list_x[n]
        elif max_data < list_x[n]:
            max_tag = n
            max_data = list_x[n]
    
    return [max_tag, max_data]

def get_min_tag_data(list_x):
    for n in range(len(list_x)):
        if n == 0:
            min_tag = n
            min_data = list_x[n]
        elif min_data > list_x[n]:
            min_tag = n
            min_data = list_x[n]

    return [min_tag, min_data]


def calcu_distance_of_two_points(point1, point2):
    '''
    calculate the distance of two points
    point1: [x, y, z]
    point2: [x, y, z]
    '''
    # Transvert the type of data
    direction = {"x" : 0, "y" : 1, "z" : 2}
    for element in [point1, point2]:
        for i in ["x", "y", "z"]:
            element[direction[i]] = float(element[direction[i]])

    multiply_result = math.sqrt(
                 (point1[direction["x"]] - point2[direction["x"]]) ** 2 +
                 (point1[direction["y"]] - point2[direction["y"]]) ** 2 +
                 (point1[direction["z"]] - point2[direction["z"]]) ** 2
                 )
    return multiply_result

def calcu_angle_of_three_lengths(length_a, length_b, length_c):
    """
    Calculate the angle which was facing the final length "length_c"
    """
    angle_c = math.degrees(math.acos((length_c * length_c - 
                                      length_a * length_a - 
                                      length_b * length_b) /
                                      (-2 * length_a * length_b)))
    return angle_c

def calcu_angles_of_three_points(point1, point2, point3):
    """
    Calculating the three angles of one triangle which formed by three points.

    The triangle just like this: 
                                  point1
                            a      *            b
                                *      *
                         point3********** point2 
                                      c
    """
    d12 = calcu_distance_of_two_points(point1, point2) # length b
    d23 = calcu_distance_of_two_points(point2, point3) # length c
    d31 = calcu_distance_of_two_points(point3, point1) # length a

    angle123 = calcu_angle_of_three_lengths(d12, d23, d31) # angle a
    angle231 = calcu_angle_of_three_lengths(d23, d31, d12) # angle b
    angle312 = calcu_angle_of_three_lengths(d31, d12, d23) # angle c

    list_angle = [angle312, angle123, angle231]
    return list_angle

#----------Finished defining functions----------

if __name__ == "__main__":
    length_a = 14
    length_b = 17
    length_c = 20
    angle_c = calcu_angle_of_three_lengths(length_a, length_b, length_c)
    print(angle_c)

    point1 = [0, 4, 0]
    point2 = [3, 0, 0]
    point3 = [0, 0, 0]
    list_a = calcu_angles_of_three_points(point1, point2, point3)
    for i in list_a:
        print(i)