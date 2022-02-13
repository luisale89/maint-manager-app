import unittest
from app.utils import (
    validations as val
)

class Email_validation_test(unittest.TestCase):

    def test1_valid_email(self):
        v = val.validate_email('valid@email.com')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), False)

    def test2_invalid_email(self):
        v = val.validate_email('invalid@@email')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), True)

    def test3_invalid_instance(self):
        self.assertRaises(TypeError, val.validate_email, 3)


class Pw_validation_test(unittest.TestCase):
    
    def test1_valid_pw(self):
        v = val.validate_pw("1478520.Lu")
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), False)

    def test2_invalid_pw(self):
        v = val.validate_pw('1')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), True)

    def test3_invalid_instance(self):
        self.assertRaises(TypeError, val.validate_pw, 3)


class Only_letters_validation_test(unittest.TestCase):

    def test1_valid_input_no_spaces(self):
        v = val.only_letters('Abcdefghijklmnopqrstuvwxyz')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), False)

    def test2_valid_input_with_spaces(self):
        v = val.only_letters('abcdefghijklmnopqrs tuvwxyz', spaces=True)
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), False)

    def test3_number_input(self):
        v = val.only_letters('lui28_')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), True)

    def test4_symbol_input(self):
        v = val.only_letters('luis*')
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), True)
    
    def test5_invalid_instance(self):
        self.assertRaises(TypeError, val.only_letters, 3)

    def test6_max_length(self):
        v = val.only_letters('superlong', max_length=2)
        self.assertIsInstance(v, dict)
        self.assertEqual(v.get('error'), True)

    def test7_invalid_spaces_parameter(self):
        with self.assertRaises(TypeError):
            val.only_letters('normal', spaces=5)

    def test8_invalid_length_parameter(self):
        with self.assertRaises(TypeError):
            val.only_letters('normal', max_length='5')

