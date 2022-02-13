import unittest

def add_two_numbers(a, b):
    return a + b


class AddTest(unittest.TestCase):

    def test1(self):
        c = add_two_numbers(1, 5) #6
        self.assertEqual(c, 6)
