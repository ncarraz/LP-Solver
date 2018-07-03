import unittest
import simplexe
import exceptions


class SimplexeTest(unittest.TestCase):

    def test_get_data(self):
        """
        get_data should parse file correctly
        """
        max_min, signs, table = simplexe.get_data('test_file.txt')
        self.assertEqual(max_min, 'max')
        self.assertEqual(signs, ['<=', '<='])
        self.assertEqual(table, [[1, 3, 1, 0, 0, -1, 0], 
                                 [2, 4, 1, 1, 0, 0, 7],
                                 [3, -1, 2, 0, 1, 0, 3]])
        self.assertRaises(FileNotFoundError, simplexe.get_data, 'no_file.txt')

    def test_to_int(self):
        """
        to_int should return only list of integers or raise an excpetion if provided
        with a list of non digits
        :return:
        """
        self.assertEqual(simplexe.to_int(['1','0','12345','-1234','98172']),[1,0,12345,-1234,98172])
        self.assertRaises(exceptions.NotDigitError, simplexe.to_int, ['123','432','a'])
        self.assertRaises(exceptions.NotDigitError, simplexe.to_int, ['0zas','-12','flac'])

    def test_is_all_negative_but_last(self):
        """
        is_negative_but_last should tell if all numbers in the list but the last are
        positive
        :return:
        """
        self.assertEqual(simplexe.is_all_negative_but_last([6,4,21,3,5]),False)
        self.assertEqual(simplexe.is_all_negative_but_last([6,-4,21,3,5]),False)
        self.assertEqual(simplexe.is_all_negative_but_last([6,-4,-21,-3,5]),False)
        self.assertEqual(simplexe.is_all_negative_but_last([-6,-4,-21,0,-3,5]),True)
        self.assertEqual(simplexe.is_all_negative_but_last([-6,-4,-21,0,-3,-5]),True)

    def test_column_is_all_negative(self):
        """
        check wether table column specified by index is all negative
        :return:
        """

if __name__ == '__main__':
    unittest.main()
