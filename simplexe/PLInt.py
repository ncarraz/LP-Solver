import PL
import tabulate
import math
import copy


class PLInt(PL.PL):
    """
    A PL which solutions and optimal values are integers only
    It does not work when solving a PL solution non bornee
    Attributes:
        pseudo_pivot: position of the pseudo pivot
    """

    def __init__(self, file):
        """
        Add the new attribute pseudo_pivot for this class
        :param file:
        """
        super().__init__(file)
        self.pseudo_pivot = None

    def fill_additional_column(self):
        """
        Add the b column to the table and set the number of additional column
        Do not add a z column
        """
        self.nb_additional_col = 1
        self.table[0].append(0)  # Fill the b column

    def __str__(self):
        """
        display the table in a more human readable way
        """
        printed_table = copy.deepcopy(self.table)
        nb_iteration = ""

        if self.pivot is not None:  # Add the pivot [] recognizer
            printed_table[self.pivot[0]][self.pivot[1]] = "({})".format(
                printed_table[self.pivot[0]][self.pivot[1]])

        if self.pseudo_pivot is not None:  # Add the pseudo-pivot recognizer
            printed_table[self.pseudo_pivot[0]][self.pseudo_pivot[1]] = "[{}]".format(
                printed_table[self.pseudo_pivot[0]][self.pseudo_pivot[1]])
            self.pseudo_pivot = None

        lines = ['--' for i in printed_table[0]]
        printed_table.insert(1, lines)  # Insert the lines with -- after the first row

        headers = ['x{}'.format(index + 1) for index, item in enumerate(printed_table[0][1:])]  # create headers x
        if self.has_base_real():
            for i in range(self.nb_var_artif):
                headers[-self.nb_var_artif + i] = 'y{}'.format(i)
        headers.extend(['b'])

        if self.nb_iteration != 0:
            nb_iteration = "Tableau {}\n".format(self.nb_iteration)

        return nb_iteration + tabulate.tabulate(printed_table, headers=headers, tablefmt="psql")

    def set_pivot_from_column(self, col):
        """
        Override the parent method replacing the chosen pivot if not 1
        :param col:
        """
        super().set_pivot_from_column(col)

        pivot_value = self.table[self.pivot[0]][self.pivot[1]]
        self.pseudo_pivot = (self.pivot[0], self.pivot[1])
        if pivot_value != 1:
            for row in self.table:
                row.insert(-1, 0)  # Append 0 before the b column
            new_constraint = [math.floor(i/pivot_value) for i in self.table[self.pivot[0]]]
            self.table.append(new_constraint)
            self.table[-1][-2] = 1
            self.pivot = len(self.table) - 1, col  # we change the pivot row by the last row

    def set_optimal_val(self):
        """
        Set the optimal value depending on the PL
        :return:
        """
        self.optimal_val = -self.table[0][-1]


if __name__ == "__main__":
    my_PL = PLInt('file_integer.txt')
    print(my_PL)
    my_PL.standardize()
    print("Forme standard")
    print(my_PL)
    my_PL.solve()
    my_PL.display_result()
