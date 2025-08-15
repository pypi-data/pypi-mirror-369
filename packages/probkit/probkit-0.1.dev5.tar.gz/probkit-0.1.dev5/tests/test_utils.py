import unittest
from probkit.utils import clamp, transform_range, effective_ratio

class TestUtils(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 1, 10), 5)
        self.assertEqual(clamp(-1, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
        self.assertEqual(clamp(0, 0, 0), 0)

    def test_transform_range(self):
        self.assertAlmostEqual(transform_range(0.5, (0, 1), (0, 10)), 5)
        self.assertAlmostEqual(transform_range(0, (0, 1), (10, 20)), 10)
        self.assertAlmostEqual(transform_range(1, (0, 1), (10, 20)), 20)
        self.assertAlmostEqual(transform_range(0.5, (0, 1)), 0.5)
        self.assertAlmostEqual(transform_range(5, (0, 10), (0, 1)), 0.5)

    def test_effective_ratio(self):
        self.assertEqual(effective_ratio(0, 5), 0)
        self.assertEqual(effective_ratio(5, 0), float('inf'))
        self.assertEqual(effective_ratio(-5, 0), float('-inf'))
        self.assertEqual(effective_ratio(10, 2), 5)
        self.assertEqual(effective_ratio(-10, 2), -5)

if __name__ == '__main__':
    unittest.main()
