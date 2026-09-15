import unittest
from checkout import total


class CheckoutTests(unittest.TestCase):
    def test_small_order(self):
        self.assertEqual(total(1000, 2), 2500)

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            total(1000, 0)


if __name__ == '__main__':
    unittest.main()
