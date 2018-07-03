import re
from operator import itemgetter
import exceptions
import tabulate
import numpy as np
import copy
from functools import reduce
import math


class PL:
    """
    Class to represent a PL Programme Lineaire
    Attributes:
        table : Multidimensional table(list of list of numbers) representing the PL table
        signs : list of signs of constraints
        max_min : string telling wether the problem is max or min
        pivot
        nb_var_artif : Number of artifivial variables
        optimal_val : Valeur optimale si elle existe
        with_base_real: boolean telling if the PL has a base realisable
        var_artif_row_numbers: list of the var artificial row numbers
        nb_var : int Original number of variables
        nb_additional_col: int Number of additionnal column other than x or y, so b or z
        nb_iteration = compte le nombre d iteration
    """

    def __init__(self, file='file4.txt'):
        """
        Create the PL from a file
        set the the matrix of the problem, the signs and wether it is max or min
        :param file: file containing the PL
        """
        self.file = file
        self.table = []
        self.signs = []
        self.max_min = ""
        self.pivot = None
        self.nb_var_artif = 0
        self.optimal_val = None
        self.with_base_real = False
        self.var_artif_row_numbers = []
        self.nb_var = 0
        self.nb_additional_col = 0
        self.nb_iteration = 0

        try:
            my_file = open(self.file, encoding='utf-8')
        except (IOError, OSError) as e:
            raise FileNotFoundError("File not found. Try to check the name you provided.")
        else:
            self.max_min = my_file.read(3)  # Wether max or min

            for line in my_file:
                numbers_list = line.split()  # Get a list of string
                self.set_signs(numbers_list)
                self.table.append(self.to_int(numbers_list))

            self.fill_additional_column()  # Fill the z column of the table

            self.nb_var = len(self.table[0][:-2])  # Original number of variables

            my_file.close()

    def has_base_real(self):
        """
        Wether it has a base realisable or not
        :return: boolean telling whether it has a base realisable or not
        """
        return self.with_base_real

    @staticmethod
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

    def set_signs(self, numbers_list):
        """
        store the signs into the sign list and remove them from the prevous list
        :param numbers_list: to get the sign from and remove them afterward
        """
        for i in numbers_list:
            if not re.match(r'-?\d', i):  # match positive and negative digits
                self.signs.append(i)
                numbers_list.remove(i)

    def fill_additional_column(self):
        """
        Add the z and bcolumn to the table
        """
        self.nb_additional_col = 2

        self.table[0].append(-1)
        self.table[0].append(0)

        for row in self.table[1:]:
            row.insert(len(row) - 1, 0)  # insert 0 for the z column

    def __str__(self):
        """
        display the table in a more human readable way
        :param table: multidimensional array representing the table of the PL
        :return:
        """
        printed_table = copy.deepcopy(self.table)

        if self.pivot is not None:
            printed_table[self.pivot[0]][self.pivot[1]] = "[{}]".format(printed_table[self.pivot[0]][self.pivot[1]])

        lines = ['--' for i in printed_table[0]]
        printed_table.insert(1, lines)  # Insert the lines with -- after the first row

        headers = ['x{}'.format(index + 1) for index, item in enumerate(printed_table[0][2:])]  # create headers x
        if self.has_base_real():
            for i in range(self.nb_var_artif):
                headers[-self.nb_var_artif + i] = 'y{}'.format(i)
        headers.extend(['z', 'b'])

        return tabulate.tabulate(printed_table, headers=headers, tablefmt="psql")

    def standardize(self):
        """
        Put the PL to standard form
        :param signs: list of constraints signs
        :param table: multidimensional array representing the PL table
        """
        var_ecart = {"<=": 1, ">=": -1}
        for sign_num, sign in enumerate(self.signs):
            for row_num, row in enumerate(self.table):
                if row_num == sign_num + 1:  # have to offset since we ignore first column
                    row.insert(len(row) - self.nb_additional_col, var_ecart[sign])  # insert 0 before the z column
                else:
                    row.insert(len(row) - self.nb_additional_col, 0)  # insert 0 before the z column

    def solve(self):
        """
        Solve a simple PL with base realisable
        """
        try:
            self.set_pivot()
        except exceptions.SolutionNonBorneeError:
            print("Solution non bornee")
        else:
            if self.pivot is not None:
                self.nb_iteration += 1
                print(self)
                self.transform()
                self.solve()
            else:
                print("Dernier tableau:")
                self.nb_iteration += 1
                print(self)
                # self.simplify()
                self.set_optimal_val()

    def set_pivot(self):
        """
        Return the coordinate of the pivot if it exists
        """
        self.pivot = None
        while not self.is_all_negative_but_last(self.table[0]):  # Until there is no positive digit which
            # column could contain a pivot
            for col, value in enumerate(self.table[0]):
                if value > 0 and not self.column_is_all_negative(col):  # There is a possible pivot in
                    # the column since there is at least one positive number in this column
                    self.set_pivot_from_column(col)
                    break  # pivot found so get out of for loop
            else:
                raise exceptions.SolutionNonBorneeError("Solution non bornee")
            break  # get out of while loop, did not enter else block

    @staticmethod
    def is_all_negative_but_last(list):
        """
        Check if all elements but the last are negative
        :param list: list of integers
        :return: boolean telling if all elements but last are negative
        """
        is_all_negative = True
        for i in list[:len(list) - 1]:  # Do not test for the last element of the list
            if i > 0:
                is_all_negative = False
                break
        return is_all_negative

    def column_is_all_negative(self, col):
        """
        Check wether the entire column is negative or equals to zero
        :param col: index of the column to check
        :return: boolean
        """
        column_is_all_negative = True
        for row in self.table[1:]:  # Spare the first row since it is the z row
            if row[col] > 0:  # column col in row row
                column_is_all_negative = False
                break
        return column_is_all_negative

    def set_pivot_from_column(self, col):
        """
        Return the row number of the pivot at this column
        :param col: index of the column
        """
        pivot_candidates_over_b = [(row_num, row[-1] / row[col]) for row_num, row in enumerate(self.table[1:])
                                   if row[col] > 0]
        pivot = min(pivot_candidates_over_b, key=itemgetter(1))  # Evaluate the second element of each tuple
        self.pivot = (pivot[0] + 1, col)  # we previously removed the first row so we add it to get
        # the absolute position

    def transform(self):
        """
        Operate the transformation on the table given the pivot
        :param table: multidimensional array representing the PL table
        :param pivot: tuple of the row and column number of the pivot
        """
        self.table = np.matrix(self.table)
        pivot_row = self.table[self.pivot[0]]
        for index, row in enumerate(self.table):
            if index != self.pivot[0]:
                self.table[index] = row * self.table[self.pivot] - pivot_row * row[0, self.pivot[1]]
        self.pivot = None
        self.table = self.table.tolist()

    def check_base_real(self):
        """
        Verify if the base is realisable
        """
        old_dim = len(self.table[0])
        for row_num, row in enumerate(self.table):
            for i in row[self.nb_var:-2]:  # check only the variable d ecart
                if i == -1:
                    self.var_artif_row_numbers.append(row_num)
                    self.nb_var_artif += 1
                    for r_num, r in enumerate(self.table):
                        if r_num == row_num:
                            r.insert(len(r) - 2, 1)
                        else:
                            r.insert(len(r) - 2, 0)
        if old_dim != len(self.table[0]):
            self.with_base_real = True
            print("Phase 1 \nRecherche d'une base realisable")
            print("Introduction de {} variables artificielles".format(self.nb_var_artif))
            print(self)
            # table = phase1(table, var_artif_row)

    def simplify(self):
        """
        Simplifie chaque ligne du tableau si possible
        """
        original_table = copy.deepcopy(self.table)
        for index, row in enumerate(self.table):
            self.table[index] = [int(i / reduce(math.gcd, row)) for i in row]
        if not original_table == self.table:
            print("Simplified")
            print(self)

    def set_optimal_val(self):
        """
        Set the optimal value depending on the PL
        """
        self.optimal_val = self.table[0][-1] / self.table[0][-2]

    def display_result(self):
        """
        Display the optimal value of the PL
        :return:
        """
        print("Valeur optimale = {}".format(self.optimal_val))


if __name__ == "__main__":
    my_PL = PL('file2.txt')
    print(my_PL)
    my_PL.standardize()
    print(my_PL)
    # my_PL.check_base_real()
    my_PL.solve()
    my_PL.display_result()
