import unittest
import pandas as pd
import pandabet.pandabet as pb

class TestToImpliedProbability(unittest.TestCase):

    def test_to_implied_probability_invalid_input(self):
        odds = pd.Series([2.0, 1.5, 1.0])
        with self.assertRaises(ValueError):
            odds.to_implied_probability(odds_type="invalid odds type")
        with self.assertRaises(ValueError):
            odds.to_implied_probability(odds_type=5)
    
    def test_decimal_odds_to_implied_probability(self):
        decimal_odds = pd.Series([2.0, 1.5, 1.0])
        true_implied_probabiliy = pd.Series([0.5, 0.6666666666666666, 1.0])
        pd.testing.assert_series_equal(decimal_odds.to_implied_probability(), true_implied_probabiliy)
        decimal_odds = pd.Series([0, 0.5, -3])
        with self.assertRaises(ValueError):
            decimal_odds.to_implied_probability(odds_type="decimal")
        decimal_odds = pd.Series(["ABC", "1.5"])
        with self.assertRaises(ValueError):
            decimal_odds.to_implied_probability(odds_type="decimal")

    def test_fractional_odds_to_implied_probability(self):
        fractional_odds = pd.Series([1/4, 2/1, 10/2])
        true_implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        pd.testing.assert_series_equal(fractional_odds.to_implied_probability(odds_type="fractional"), true_implied_probability)
        fractional_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            fractional_odds.to_implied_probability(odds_type="fractional")

    def test_american_odds_to_implied_probability(self):
        american_odds = pd.Series([100, -150, 200])
        true_implied_probability = pd.Series([0.5, 0.6, 0.333333])
        pd.testing.assert_series_equal(american_odds.to_implied_probability(odds_type="american"), true_implied_probability)
        american_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            american_odds.to_implied_probability(odds_type="american")


class TestToOdds(unittest.TestCase):

    def test_to_odds_invalid_input(self):
        implied_probability = pd.Series(["ABC", "0.8"])
        with self.assertRaises(ValueError):
            implied_probability.to_odds(odds_type="decimal")
        implied_probability = pd.Series([0.8, 0.6])
        with self.assertRaises(ValueError):
            implied_probability.to_odds(odds_type="invalid odds type")

    def test_implied_probability_to_decimal_odds(self):
        implied_probability = pd.Series([0.5, 0.4])
        true_decimal_odds = pd.Series([2, 2.5])
        pd.testing.assert_series_equal(implied_probability.to_odds(odds_type="decimal"), true_decimal_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.to_odds(odds_type="decimal")

    def test_implied_probability_to_fractional_odds(self):
        implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        true_fractional_odds = pd.Series([1/4, 2/1, 10/2])
        pd.testing.assert_series_equal(implied_probability.to_odds(odds_type="fractional"), true_fractional_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.to_odds(odds_type="fractional")

    def test_implied_probability_to_american_odds(self):
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        true_american_odds = pd.Series([100.0, -150.0, 200.0])
        pd.testing.assert_series_equal(implied_probability.to_odds(odds_type="american"), true_american_odds, atol=1e-5)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.to_odds(odds_type="american")

class TestConvert(unittest.TestCase):

    def test_convert_invalid_input(self):
        odds = pd.Series(["ABC", "0.8"])
        with self.assertRaises(ValueError):
            odds.convert(from_type="decimal", to_type="implied_probability")
        odds = pd.Series([0.8, 0.6])
        with self.assertRaises(ValueError):
            odds.convert(from_type="invalid odds type", to_type="implied_probability")

    def test_convert_decimal_to_implied_probability(self):
        decimal_odds = pd.Series([2.0, 1.5, 1.0])
        true_implied_probabilities = pd.Series([0.5, 0.6666666666666666, 1.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="implied_probability"), true_implied_probabilities)
        decimal_odds = pd.Series([0, 0.5, -3])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="implied_probability")
        decimal_odds = pd.Series(["ABC", "1.5"])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="implied_probability")

    def test_convert_fractional_to_implied_probability(self):
        fractional_odds = pd.Series([1/4, 2/1, 10/2])
        true_implied_probabilities = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="implied_probability"), true_implied_probabilities)
        fractional_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="implied_probability")

    def test_convert_american_to_implied_probability(self):
        american_odds = pd.Series([100, -150, 200])
        true_implied_probabilities = pd.Series([0.5, 0.6, 0.333333])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="implied_probability"), true_implied_probabilities)
        american_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="implied_probability")

    def test_convert_implied_probability_to_decimal(self):
        implied_probability = pd.Series([0.5, 0.4])
        true_decimal_odds = pd.Series([2, 2.5])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="decimal"), true_decimal_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="decimal")

    def test_convert_implied_probability_to_fractional(self):
        implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        true_fractional_odds = pd.Series([1/4, 2/1, 10/2])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="fractional"), true_fractional_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="fractional")

    def test_convert_implied_probability_to_american(self):
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        true_american_odds = pd.Series([100.0, -150.0, 200.0])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="american"), true_american_odds, atol=1e-5)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="american")

    def test_convert_decimal_to_american(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        true_american_odds = pd.Series([100.0, -200.0, 200.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="american"), true_american_odds, atol=1e-5)
        decimal_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="american")

    def test_convert_decimal_to_fractional(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        true_fractional_odds = pd.Series([1.0, 0.5, 2.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="fractional"), true_fractional_odds)
        decimal_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="fractional")

    def test_convert_american_to_fractional(self):
        american_odds = pd.Series([100.0, -200.0, 300.0])
        true_fractional_odds = pd.Series([1.0, 0.5, 3.0])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="fractional"), true_fractional_odds)
        american_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="fractional")

    def test_convert_american_to_decimal(self):
        american_odds = pd.Series([100, -200, 300])
        true_decimal_odds = pd.Series([2.0, 1.5, 4.0])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="decimal"), true_decimal_odds)
        american_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="decimal")

    def test_convert_fractional_to_decimal(self):
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        true_decimal_odds = pd.Series([2.0, 1.5, 3.0])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="decimal"), true_decimal_odds)
        fractional_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="decimal")

    def test_convert_fractional_to_american(self):
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        true_american_odds = pd.Series([100.0, -200.0, 200.0])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="american"), true_american_odds, atol=1e-5)
        fractional_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="american")


class TestAsFloat(unittest.TestCase):

    def test_as_float(self):
        fractional_odds = pd.Series(["1/4", "1/2", "2/1"])
        true_fractional_odds = pd.Series([0.25, 0.5, 2.0])
        pd.testing.assert_series_equal(fractional_odds.as_float(), true_fractional_odds)
        fractional_odds = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            fractional_odds.as_float()

class TestAsFraction(unittest.TestCase):

    def test_as_fraction(self):
        fractional_odds = pd.Series([0.25, 0.5, 2.0, 1.0])
        true_fractional_odds = pd.Series(["1/4", "1/2", "2/1", "1/1"])
        pd.testing.assert_series_equal(fractional_odds.as_fraction(), true_fractional_odds)
        fractional_odds = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            fractional_odds.as_fraction()

class TestOverround(unittest.TestCase):

    def test_overround_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([2.0, 1.5, 3.0]).overround(odds_type="invalid")
        with self.assertRaises(ValueError):
            pd.Series([1.2, -0.5, 0.8]).overround(odds_type="implied_probability")
        with self.assertRaises(ValueError):
            pd.Series([0, -1, 1/3]).overround(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.Series([0, -1, 1/3]).overround(odds_type="american")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).overround(odds_type="decimal")

    def test_overround(self):
        implied_odds = pd.Series([0.8, 0.5, 0.3])
        self.assertAlmostEqual(implied_odds.overround(), 1.6, places=2)
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        self.assertAlmostEqual(fractional_odds.overround(odds_type="fractional"), 1.5, places=2)
        american_odds = pd.Series([100.0, -200.0, 300.0])
        self.assertAlmostEqual(american_odds.overround(odds_type="american"), 1.41666, places=2)
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        self.assertAlmostEqual(decimal_odds.overround(odds_type="decimal"), 1.4999, places=2)

class TestVig(unittest.TestCase):

    def test_vig_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([0.8, 0.4, 0.6]).vig(odds_type="invalid_input")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="decimal")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="american")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="implied_probability")

    def test_vig(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        self.assertAlmostEqual(decimal_odds.vig(odds_type="decimal"), 0.3333, places=2)
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        self.assertAlmostEqual(fractional_odds.vig(odds_type="fractional"), 0.3333, places=2)
        american_odds = pd.Series([100.0, -200.0, 300.0])
        self.assertAlmostEqual(american_odds.vig(odds_type="american"), 0.294, places=2)
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        self.assertAlmostEqual(implied_probability.vig(odds_type="implied_probability"), 0.302, places=2)

class TestDevig(unittest.TestCase):

    def test_devig_implied_probabilities(self):
        implied_probabilities = pd.Series([0.8, 0.5, 0.3])
        self.assertAlmostEqual(implied_probabilities.devig().sum(), 1.0, places=2)
        self.assertAlmostEqual(implied_probabilities.devig(type="equal").sum(), 1.0, places=2)

    def test_devig_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([0.8, 0.4, 0.6]).devig(type="invalid_input")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).devig(type="decimal")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).devig(type="fractional")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).devig(type="american")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).devig(type="implied_probability")

class TestPayoutAndProfit(unittest.TestCase):

    def test_payout(self):
        self.assertAlmostEqual(pb.payout(100, 2.0, 'decimal'), 200.0, places=2)
        self.assertAlmostEqual(pb.payout(100, 1.5, 'fractional'), 250.0, places=2)
        self.assertAlmostEqual(pb.payout(100, 200.0, 'american'), 300.0, places=2)

    def test_profit(self):
        self.assertAlmostEqual(pb.profit(100, 2.0, 'decimal'), 100.0, places=2)
        self.assertAlmostEqual(pb.profit(100, 1.5, 'fractional'), 150, places=2)
        self.assertAlmostEqual(pb.profit(100, 200.0, 'american'), 200.0, places=2)

    def test_invalid_odds_type(self):
        with self.assertRaises(ValueError):
            pb.payout(100, 2.0, 'invalid_odds_type')

    def test_invalid_odds(self):
        with self.assertRaises(ValueError):
            pb.payout(100, -1.0, 'decimal')
        with self.assertRaises(ValueError):
            pb.payout(100, 0.0, 'fractional')
        with self.assertRaises(ValueError):
            pb.payout(100, 90, 'american')

class TestKellyCriterion(unittest.TestCase):

    def test_kelly_criterion(self):
        bankroll = 1
        odds = 100
        probability = 0.6
        kelly_fraction = pb.kelly_criterion(odds, 'american', probability, bankroll)
        self.assertAlmostEqual(kelly_fraction, 0.2, places=2)

    def test_kelly_criterion_no_bet(self):
        bankroll = 1
        odds = 100
        probability = 0.4
        kelly_fraction = pb.kelly_criterion(odds, 'american', probability, bankroll)
        self.assertAlmostEqual(kelly_fraction, 0.0, places=2)
