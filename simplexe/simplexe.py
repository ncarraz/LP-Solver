import os
import re
from operator import itemgetter
import exceptions
import tabulate
import numpy as np
import copy


def to_int(list):
    """
    Convert all elements of a list to int
    :param list: list with digits represented as strings
    :return: list which elements are all int
    """
    try:
        return [int(i) for i in list]
    except ValueError:
        raise exceptions.NotDigitError("List should contain digits only")


def get_signs(list, signs):
    """
    store the signs into the sign list and remove them from the prevous list
    :param list: to get the sign from and remove them afterward
    :param signs: to store the signs
    """
    for i in list:
        if not re.match(r'-?\d', i):  # match positive and negative digits
            signs.append(i)
            list.remove(i)
        

def fill_z_column(table):
    """
    Add the z column to the table
    :param table:
    """
    table[0].append(-1)
    table[0].append(0)

    for row in table[1:]:
        row.insert(len(row)-1, 0)  # insert 0 before the last element


def get_data(file='file2.txt'):
    """
    Read a file containing the problem set and return the number of varianles,
    the number of constraints, the matrix of the problem and wether it is max or min
    :param file: file containing the PL
    :return: tuple of wether min or max, the list of signs, the multi dimensional table
    """
    try:
        file = open(file, encoding='utf-8')
    except (IOError, OSError) as e:
        raise FileNotFoundError("The file is not found. Try to check the name you provided.")
    else:
        table = []
        signs = []
        max_min = file.read(3)  # Wether max or min
        for line in file:
            numbers_list = line.split()  # Get a list of string
            get_signs(numbers_list, signs)
            table.append(to_int(numbers_list))
        # Fill the z column of the table
        fill_z_column(table)
        file.close()

        return (max_min, signs, table)


def is_all_negative_but_last(list):
    """
    Check if all elements but the last are negative
    :param list: list of integers
    :return: boolean telling if all elements but last are negative
    """
    is_all_negative = True
    for i in list[:len(list)-1]:  # Do not test for the last element of the list
        if i > 0:
            is_all_negative = False
            break
    return is_all_negative


def column_is_all_negative(col, table):
    """
    Check wether the entire column is negative or equals to zero
    :param col: index of the column to check
    :param table: multidimensional array representing the table
    :return: boolean
    """
    column_is_all_negative = True
    for row in table[1:]:  # Spare the first row since it is the z row
        if row[col] > 0:  # column col in row row
            column_is_all_negative = False
            break
    return column_is_all_negative


def get_pivot_from_column(col, table):
    """
    Return the row number of the pivot at this column
    :param col: index of the column
    :param table: multidimensional array representing the PL table
    :return: int row position of the pivot
    """
    pivot_candidates_over_b = [(row_num, row[col]/row[-1]) for row_num, row in enumerate(table[1:])
                               if row[col] > 0]
    pivot = max(pivot_candidates_over_b, key=itemgetter(1))  # Evaluate the second element of each tuple
    return pivot[0] + 1  # we previously removed the first row so we add it to get the absolute position


def get_pivot(table, stop_function=is_all_negative_but_last):
    """
    Return the coordinate of the pivot if it exists
    :param table: multidimensional array representing the PL table
    :return: tuple of the row and column number of the pivot
    """
    pivot = None
    if isinstance(table, np.matrixlib.defmatrix.matrix):  # Convert to list if matrix
        table = table.tolist()
    while not stop_function(table[0]):  # Until there is no positive digit which
        # column could contain a pivot
        for col, value in enumerate(table[0]):
            if value > 0 and not column_is_all_negative(col, table):  # There is a possible pivot in
                # the column since there is at least one positive number in this column
                pivot = get_pivot_from_column(col, table), col
                break  # pivot found so get out of for loop
        else:
            raise exceptions.SolutionNonBorneeError("Solution non bornee")
        break  # get out of while loop, did not enter else block
    return pivot


def transform(table, pivot):
    """
    Operate the transformation on the table given the pivot
    :param table: multidimensional array representing the PL table
    :param pivot: tuple of the row and column number of the pivot
    :return:
    """
    table = np.matrix(table)
    pivot_row = table[pivot[0]]
    for index, row in enumerate(table):
        if index != pivot[0]:
            table[index] = row*table[pivot] - pivot_row*row[0, pivot[1]]
    return table.tolist()


def last_is_zero(list):
    """
    Check if last element of a list is zero
    :param list: Any list
    :return: boolean wether last element is zero
    """
    return list[-1] == 0


def solve(table, stop_function=is_all_negative_but_last):
    """
    Solve a simple PL with base realisable
    :param signs: list of constraints signs
    :param table: multidimensional array representing the PL table
    :return:
    """
    try:
        pivot = get_pivot(table, stop_function)
    except exceptions.SolutionNonBorneeError:
        print("Solution non bornee")
    else:
        if pivot is not None:
            print_table(table, pivot)
            table = transform(table, pivot)
            # print_table(table)
            solve(table)
        else:
            print_table(table)
            print("Termine\n Valeur optimale = {}".format(table[0][-1]/table[0][-2]))


def phase1(table, var_artif_row):
    """
    Recherche de base realisable a partir de la phase 1
    :param signs: list of constraints signs
    :param table: multidimensional array representing the PL table
    :return: table avec base realisable
    """
    w = [0] * len(table[0])
    for index, value in enumerate(table[0]):
        for row_num in var_artif_row:
            w[index] += table[row_num][index]
    for i in range(len(var_artif_row)):
        w[-3-i] = 0  # We omit the last two columns z zt b columns
    w[-2] = -1  # z column which is now omega column is -1
    table[0] = w
    print_table(table)
    solve(table, stop_function=last_is_zero)


def process(nb_var, table):
    """
    Real process
    :param signs: list of constraints signs
    :param table: multidimensional array representing the PL table
    :return:
    """
    old_dim = len(table[0])
    nb_var_artif = 0
    var_artif_row = []
    for row_num, row in enumerate(table):
        for i in row[nb_var:-2]:  # check only the variable d ecart
            if i == -1:
                var_artif_row.append(row_num)
                nb_var_artif += 1
                for r_num, r in enumerate(table):
                    if r_num == row_num:
                        r.insert(len(r) - 2, 1)
                    else:
                        r.insert(len(r) - 2, 0)
    if old_dim != len(table[0]):
        print("Phase 1")
        print_table(table, nb_var_artif=nb_var_artif)
        table = phase1(table, var_artif_row)
    else:
        # San passer par phase1
        solve(table)


def display_result():
    pass


def standardize(signs, table):
    """
    Put the PL to standard form
    :param signs: list of constraints signs
    :param table: multidimensional array representing the PL table
    :return:
    """
    var_ecart = {"<=": 1, ">=": -1}
    for sign_num, sign in enumerate(signs):
        for row_num, row in enumerate(table):
            if row_num == sign_num+1:  # have to offset since we ignore first column
                row.insert(len(row) - 2, var_ecart[sign])  # insert 0 before the z column
            else:
                row.insert(len(row) - 2, 0)  # insert 0 before the z column


def print_table(table, pivot=None, nb_var_artif=0):
    """
    display the table in a more human readable way
    :param table: multidimensional array representing the table of the PL
    :return:
    """
    printed_table = copy.deepcopy(table)
    if isinstance(printed_table, np.matrixlib.defmatrix.matrix):  # Convert to list if matrix
        printed_table = printed_table.tolist()
    if pivot is not None:
        printed_table[pivot[0]][pivot[1]] = "[{}]".format(printed_table[pivot[0]][pivot[1]])

    lines = ['--' for i in printed_table[0]]
    printed_table.insert(1, lines)  # Insert the lines with -- after the first row

    headers = ['x{}'.format(index+1) for index, item in enumerate(printed_table[0][2:])]  # create headers x
    if nb_var_artif != 0:
        for i in range(nb_var_artif):
            headers[-nb_var_artif+i] = 'y{}'.format(i)
    headers.extend(['z', 'b'])

    print(tabulate.tabulate(printed_table, headers=headers, tablefmt="psql"))


def main():
    max_min, signs, table = get_data()
    print_table(table)
    nb_var = len(table[0][:-2])  # Original number of variables
    standardize(signs, table)
    print_table(table)
    process(nb_var, table)
    # display_result()

if __name__ == "__main__":
    main()
