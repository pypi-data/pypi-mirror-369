import unittest
from probkit.probability import modified_probability

class TestProbability(unittest.TestCase):
    def test_modified_probability_basic(self):
        self.assertEqual(modified_probability(1, 1), 1)
        self.assertEqual(modified_probability(1, 0), 0)
        self.assertEqual(modified_probability(0, 1), 0)
        self.assertEqual(modified_probability(0, 0), 0)
        self.assertEqual(modified_probability(0.5, float('inf')), 1)

    def test_modified_probability_direct_ratio(self):
        self.assertLess(modified_probability(0.42, 0.9), 0.42)
        self.assertEqual(modified_probability(0.42, 1), 0.42)
        self.assertGreater(modified_probability(0.42, 1.1), 0.42)

    def test_modified_probability_fraction(self):
        self.assertLess(modified_probability(0.42, 2, 3), 0.42)
        self.assertEqual(modified_probability(0.42, 2, 2), 0.42)
        self.assertGreater(modified_probability(0.42, 3, 2), 0.42)

    def test_modified_probability_edge(self):
        self.assertEqual(modified_probability(0.42, 1, 0), 1)
        self.assertEqual(modified_probability(0.42, 1000, 0), 1)
        self.assertEqual(modified_probability(0.42, 0.0001, 0), 1)

    def test_modified_probability_errors(self):
        with self.assertRaises(ValueError): modified_probability(-0.5, 1)
        with self.assertRaises(ValueError): modified_probability(1.5, 1)
        with self.assertRaises(ValueError): modified_probability(0.5, -1)

if __name__ == '__main__':
    unittest.main()
