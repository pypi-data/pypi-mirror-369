import unittest

from pandas import Series

from pyholos import utils


class TestConvertCamelCaseToSpaceDelimited(unittest.TestCase):
    def test_expected_values(self):
        for input_str, expected_str in [
            ("CamelCase", "Camel Case"),
            ("camelCase", "camel Case"),
            ("Notcamelcase", "Notcamelcase"),
            ("snake_case", "snake_case"),
        ]:
            self.assertEqual(
                expected_str,
                utils.convert_camel_case_to_space_delimited(s=input_str)
            )


class TestCalcAverage(unittest.TestCase):
    def test_values(self):
        for values, expected_result in [
            ([1, 2, 3], 2),
            (range(10), 4.5),
            ((v for v in range(10)), 4.5),
            ((3, 3, 3), 3),
            ((-1, 1), 0)
        ]:
            self.assertEqual(
                expected_result,
                utils.calc_average(values=values))


class TestCleanString(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_input = "This is a sentence. (once a day) [twice a day]"

    def test_values(self):
        self.assertEqual(
            "Thisisasentence.",
            utils.clean_string(input_string=self.raw_input))

        self.assertEqual(
            "This is a sentence.  ",
            utils.clean_string(
                input_string=self.raw_input,
                characters_to_remove=''))

        self.assertEqual(
            "This is a sentence.  [twice a day]",
            utils.clean_string(
                input_string=self.raw_input,
                characters_to_remove='',
                is_remove_text_between_brackets=False))

        self.assertEqual(
            "This is a sentence. (once a day) ",
            utils.clean_string(
                input_string=self.raw_input,
                characters_to_remove='',
                is_remove_text_between_parentheses=False))


class TestCalcVectorPercentage(unittest.TestCase):
    def test_values_using_list(self):
        self.assertEqual(
            [10, 20, 30, 40],
            utils.calc_vector_percentage(vector=[1, 2, 3, 4])
        )

    def test_values_using_tuple(self):
        self.assertEqual(
            [10, 20, 30, 40],
            utils.calc_vector_percentage(vector=(1, 2, 3, 4))
        )

    def test_values_using_series(self):
        self.assertEqual(
            [10, 20, 30, 40],
            utils.calc_vector_percentage(vector=Series((1, 2, 3, 4)))
        )

    def test_one_value(self):
        self.assertEqual(
            [100],
            utils.calc_vector_percentage(vector=3.5)
        )
        self.assertEqual(
            [100],
            utils.calc_vector_percentage(vector=Series(3.5))
        )

    def test_function_raises_error_for_negative_values(self):
        try:
            utils.calc_vector_percentage(vector=[-3.5, 1])
        except AssertionError:
            pass

    def test_function_raises_error_for_all_zero_values(self):
        try:
            utils.calc_vector_percentage(vector=[0, 0])
        except AssertionError:
            pass


if __name__ == '__main__':
    unittest.main()
