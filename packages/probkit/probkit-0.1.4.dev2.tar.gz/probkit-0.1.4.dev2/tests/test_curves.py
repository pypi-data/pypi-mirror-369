import unittest
from probkit.curves import ntsig, nthsig, biased_curve

class TestCurves(unittest.TestCase):
    def test_ntsig(self):
        # Test edge cases for k
        self.assertEqual(ntsig(-1, 0), 0)
        self.assertEqual(ntsig(-1, 0.5), 0.5)
        self.assertEqual(ntsig(-1, 1), 1)
        self.assertEqual(ntsig(0, 0), 0)
        self.assertEqual(ntsig(0, 0.5), 0.5)
        self.assertEqual(ntsig(0, 1), 1)
        self.assertEqual(ntsig(1, 0), 0)
        self.assertEqual(ntsig(1, 0.5), 0.5)
        self.assertEqual(ntsig(1, 1), 1)
        # Test behavior for a sample of x values with specific k values
        for x in [0.1, 0.25, 0.75, 0.9]:
            self.assertTrue(0 <= ntsig(-0.5, x) <= 1)
            self.assertTrue(0 <= ntsig(0.5, x) <= 1)
        # Test invalid inputs
        with self.assertRaises(ValueError): ntsig(-1.1, 0.5)
        with self.assertRaises(ValueError): ntsig(1.1, 0.5)
        with self.assertRaises(ValueError): ntsig(0, -0.1)
        with self.assertRaises(ValueError): ntsig(0, 1.1)

    def test_nthsig(self):
        # Test behavior at key points for various k values
        self.assertEqual(nthsig(-1, 0), 0)
        self.assertEqual(nthsig(-1, 1), 1)
        self.assertEqual(nthsig(0, 0), 0)
        self.assertEqual(nthsig(0, 1), 1)
        self.assertEqual(nthsig(1, 0), 0)
        self.assertEqual(nthsig(1, 1), 1)
        # Test for different k values across the x range
        for x in [0.1, 0.25, 0.75, 0.9]:
            self.assertTrue(0 <= nthsig(-0.5, x) <= 1)
            self.assertTrue(0 <= nthsig(0.5, x) <= 1)
        # Test handling of invalid inputs
        with self.assertRaises(ValueError): nthsig(-1.1, 0.5)
        with self.assertRaises(ValueError): nthsig(1.1, 0.5)
        with self.assertRaises(ValueError): nthsig(0, -0.1)
        with self.assertRaises(ValueError): nthsig(0, 1.1)

    def test_biased_curve(self):
        # Test linear behavior
        self.assertEqual(biased_curve(0, 0, 1, 0), 0)
        self.assertEqual(biased_curve(0, 0, 1, 1), 1)
        self.assertEqual(biased_curve(0, 0, 1, 0.5), 0.5)
        # Test bias influence
        self.assertLess(biased_curve(-1, 0, 1, 0.5), 0.5)
        self.assertGreater(biased_curve(1, 0, 1, 0.5), 0.5)
        # Test a and b inversion
        self.assertEqual(biased_curve(0, 1, 0, 0), 1)
        self.assertEqual(biased_curve(0, 1, 0, 1), 0)
        self.assertEqual(biased_curve(0, 1, 0, 0.5), 0.5)
        # Test extreme biases
        self.assertLess(biased_curve(-1, 0, 1, 0.25), biased_curve(0, 0, 1, 0.25))
        self.assertGreater(biased_curve(1, 0, 1, 0.75), biased_curve(0, 0, 1, 0.75))
        # Test invalid inputs
        with self.assertRaises(ValueError): biased_curve(0, 0, 1, -0.1)
        with self.assertRaises(ValueError): biased_curve(0, 0, 1, 1.1)

if __name__ == '__main__':
    unittest.main()
