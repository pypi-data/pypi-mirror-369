import pandas as pd
from pandas.core.base import PandasObject
from math import gcd
from typing import Union

"""
Private helper functions for pybet
"""

def _american_odds_check(odds: float) -> bool:
    """
    Check if the odds are in American format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in American format, False otherwise.
    """
    return isinstance(float(odds), (int, float)) and (float(odds) >= 100 or float(odds) < -100)

def _decimal_odds_check(odds: float) -> bool:
    """
    Check if the odds are in decimal format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in decimal format, False otherwise.
    """
    return isinstance(float(odds), (int, float)) and float(odds) >= 1

def _fractional_odds_check(odds: float) -> bool:
    """
    Check if the odds are in fractional format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in fractional format, False otherwise.
    """
    return isinstance(odds, (int, float)) and odds > 0

def _payout_american(odds: Union[float, int], stake: Union[float, int]) -> float:
    """
    Calculate the payout based on American odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The American odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _american_odds_check(odds):
        if float(odds) >= 100:
            return stake * (odds / 100) + stake
        elif float(odds) < -100:
            return stake * (100 / -odds) + stake
    raise ValueError("Invalid American odds.")

def _payout_decimal(odds: float, stake: float) -> float:
    """
    Calculate the payout based on decimal odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The decimal odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _decimal_odds_check(odds):
        return stake * odds
    raise ValueError("Invalid decimal odds.")

def _payout_fractional(odds: float, stake: float) -> float:
    """
    Calculate the payout based on fractional odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The fractional odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _fractional_odds_check(odds):
        return stake * (odds + 1)
    raise ValueError("Invalid fractional odds.")

def _payout(odds: float, stake: float, odds_type: str) -> float:
    """
    Calculate the payout based on the odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The odds.
        stake (float): The stake.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').
    
    Returns:
        float: The payout.
    """
    if odds_type == 'decimal':
        return _payout_decimal(odds, stake)
    elif odds_type == 'fractional':
        return _payout_fractional(odds, stake)
    elif odds_type == 'american':
        return _payout_american(odds, stake)
    raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")

def _implied_probability_check(probability: float) -> bool:
    """
    Check if the probability is a valid implied probability. For Internal Use Only.
    
    Args:
        probability (float): The probability to check.
    
    Returns:
        bool: True if the probability is valid, False otherwise.
    """
    return isinstance(probability, (int, float)) and 0 < probability < 1

def _series_odds_check(odds: pd.Series, odds_type: str) -> bool:
    """
    Check if the Series contains valid odds. For Internal Use Only.
    
    Args:
        odds (Series): The Series to check.
        odds_type (str): The type of odds to check ('decimal', 'fractional', 'american', or 'implied_probability').
    
    Returns:
        bool: True if the Series contains valid odds, False otherwise.
    """
    if odds_type == 'decimal':
        return all(_decimal_odds_check(odd) for odd in odds)
    elif odds_type == 'fractional':
        return all(_fractional_odds_check(odd) for odd in odds)
    elif odds_type == 'american':
        return all(_american_odds_check(odd) for odd in odds)
    elif odds_type == 'implied_probability':
        return all(_implied_probability_check(prob) for prob in odds)
    else:
        raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")

def _american_odds_to_implied_probability(odds: float) -> float:
    """
    Convert American odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The American odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds >= 100:
            return 100 / (odds + 100)
        elif odds <= -100:
            return -odds / (-odds + 100)
        else:
            raise ValueError("American odds must be greater than or equal to 100 or less than or equal to -100.")
    except Exception:
        raise ValueError("Invalid American odds.")

    
def _decimal_odds_to_implied_probability(odds: float) -> float:
    """
    Convert decimal odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The decimal odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds >= 1:
            return 1 / odds
        else:
            raise ValueError("Decimal odds must be greater than or equal to 1.0")
    except Exception:
        raise ValueError("Invalid decimal odds.")

def _fractional_odds_to_implied_probability(odds: float) -> float:
    """
    Convert fractional odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The fractional odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds > 0:
            return 1 / (odds + 1)
        else:
            raise ValueError("Fractional odds must be greater than 0.")
    except Exception:
        raise ValueError("Invalid fractional odds.")
    
def _implied_probability_to_decimal_odds(probability: float) -> float:
    """
    Convert implied probability to decimal odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The decimal odds.
    """
    try:
        if probability > 0 and probability < 1:
            return 1 / probability
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")

def _implied_probability_to_fractional_odds(probability: float) -> float:
    """
    Convert implied probability to fractional odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The fractional odds.
    """
    try:
        if probability > 0 and probability < 1:
            return (1 / probability) - 1
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")
    
    
def _implied_probability_to_american_odds(probability: float) -> float:
    """
    Convert implied probability to American odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The American odds.
    """
    try:
        if probability > 0 and probability < 1:
            if probability <= 0.5:
                return (100 / probability) - 100
            else:
                return (probability * 100) / (1 - probability) * -1
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")
    
def _as_fraction(fractional_odds: float) -> str:
    """
    Convert a float representing fractional odds to a string representation. Private Function

    Args:
        odds (float): The fractional odds as a float.

    Returns:
        str: The fractional odds as a string.
    """
    if not _fractional_odds_check(fractional_odds):
        raise ValueError("Invalid fractional odds.")
    numerator = int(fractional_odds * 100)
    denominator = 100
    common_divisor = gcd(numerator, denominator)
    numerator //= common_divisor
    denominator //= common_divisor
    return f"{numerator}/{denominator}"

def _as_float(fraction: str) -> float:
    """
    Convert a string representing fractional odds to a float. Private Function

    Args:
        fraction (str): The fractional odds as a string (e.g., "3/2").

    Returns:
        float: The fractional odds as a float.
    """
    try:
        numerator, denominator = map(int, fraction.split('/'))
        return numerator / denominator
    except Exception:
        raise ValueError("Invalid fractional odds string format.")
    
 
"""
Public interface functions for pybet. Not converted to pandas function
"""

def to_implied_probability(odds: pd.Series, odds_type: str = 'decimal') -> pd.Series:
        """
        Calculate the implied probability from the odds.
        
        Returns:
            Series: A series of implied probabilities.
        """
        if odds_type == 'decimal':
            return odds.apply(lambda odd: _decimal_odds_to_implied_probability(odd))
        elif odds_type == 'fractional':
            return odds.apply(lambda odd: _fractional_odds_to_implied_probability(odd))
        elif odds_type == 'american':
            return odds.apply(lambda odd: _american_odds_to_implied_probability(odd))
        else:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")

def to_odds(odds: pd.Series, odds_type: str) -> pd.Series:
    """
    Convert implied probability to the specified odds type.
    
    Args:
        odds_type (str): The type of odds to convert to ('decimal', 'fractional', 'american').
    
    Returns:
        Series: A series of odds.
    """
    if odds_type not in ['decimal', 'fractional', 'american']:
        raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")
    elif odds_type == 'decimal':
        return odds.apply(lambda prob: _implied_probability_to_decimal_odds(prob))
    elif odds_type == 'fractional':
        return odds.apply(lambda prob: _implied_probability_to_fractional_odds(prob))
    elif odds_type == 'american':
        return odds.apply(lambda prob: _implied_probability_to_american_odds(prob))
    
def convert(input: pd.Series, from_type: str, to_type: str) -> pd.Series:
    """
    Convert odds or implied probability from one type to another.
    
    Args:
        input (pd.Series): A series of odds or implied probabilities.
        from_type (str): The current type of odds ('decimal', 'fractional', 'american', 'implied_probability').
        to_type (str): The type of odds to convert to ('decimal', 'fractional', 'american', 'implied_probability').
    
    Returns:
        Series: A series of converted odds.
    """
    if _series_odds_check(input, from_type) is False:
        raise ValueError(f"Invalid odds in Series for type '{from_type}'.")
    if from_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
        raise ValueError("Invalid from_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
    if to_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
        raise ValueError("Invalid to_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
    if from_type == to_type:
        return input
    if from_type == 'implied_probability':
        implied_prob = input
    elif from_type in ['decimal', 'fractional', 'american']:
        implied_prob = input.to_implied_probability(from_type)
    if to_type == 'implied_probability':
        return implied_prob
    return implied_prob.to_odds(to_type)

def as_fraction(fractional_odds: pd.Series) -> pd.Series:
    """
    Convert a series of fractional odds from float to string representation.

    Args:
        fractional_odds (pd.Series): A series of fractional odds as floats.

    Returns:
        pd.Series: A series of fractional odds as strings.
    """
    return fractional_odds.apply(lambda x: _as_fraction(x))

def as_float(fraction: pd.Series) -> pd.Series:
    """
    Convert a series of fractional odds from string representation to float.

    Args:
        fraction (pd.Series): A series of fractional odds as strings.

    Returns:
        pd.Series: A series of fractional odds as floats.
    """
    return fraction.apply(lambda x: _as_float(x))

def overround(odds: pd.Series, odds_type: str = 'implied_probability') -> float:
    """
    Calculate the overround from the odds.
    
    Args:
        odds (Series): A series of odds.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american', or 'implied_probability').

    Returns:
        float: The overround.
    """
    if not isinstance(odds, pd.Series):
        raise TypeError("Odds must be a pandas Series.")
    if not _series_odds_check(odds, odds_type):
        raise ValueError(f"Invalid odds in Series for type '{odds_type}'.")
    if odds_type == 'implied_probability':
        implied_probs = odds
    else:
        implied_probs = odds.to_implied_probability(odds_type)
    total_implied_prob = implied_probs.sum()
    return total_implied_prob

def vig(odds: pd.Series, odds_type: str = 'implied_probability') -> float:
    """
    Calculate the vig (vigorish) from the odds.
    
    Args:
        odds (Series): A series of odds.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american', 'implied_probability').

    Returns:
        float: The vig.
    """
    if not isinstance(odds, pd.Series):
        raise TypeError("Odds must be a pandas Series.")
    if not _series_odds_check(odds, odds_type):
        raise ValueError(f"Invalid odds in Series for type '{odds_type}'.")
    overround_value = overround(odds, odds_type)
    if overround_value <= 1:
        return 0.0
    return (overround_value - 1.0)/overround_value

def devig(implied_probabilities: pd.Series, type: str = 'equal') -> pd.Series:
    """
    Calculate the equal de-vigged odds from the implied probabilities.
    
    Args:
        implied_probabilities (Series): A series of implied probabilities.
    
    Returns:
        Series: A series of de-vigged .
    """
    if not isinstance(implied_probabilities, pd.Series):
        raise TypeError("Implied probabilities must be a pandas Series.")
    if not _series_odds_check(implied_probabilities, 'implied_probability'):
        raise ValueError("Invalid implied probabilities in Series.")
    if type not in ['equal']:
        raise ValueError(f"Invalid devig type: {type}")

    overround_value = implied_probabilities.sum()
    equal_devigged_probs = implied_probabilities / overround_value
    return equal_devigged_probs

def payout(stake: float, odds: float, odds_type: str) -> float:
    """
    Calculate the potential payout for a given stake and odds.

    Args:
        stake (float): The amount of the stake.
        odds (float): The odds of the bet.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').

    Returns:
        float: The potential payout.
    """
    if not _series_odds_check(pd.Series([odds]), odds_type):
        raise ValueError(f"Invalid odds for type '{odds_type}'.")
    return _payout(odds, stake, odds_type)

def profit(stake: float, odds: float, odds_type: str) -> float:
    """
    Calculate the potential profit for a given stake and odds.

    Args:
        stake (float): The amount of the stake.
        odds (float): The odds of the bet.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').

    Returns:
        float: The potential profit.
    """
    payout_amount = payout(stake, odds, odds_type)
    return payout_amount - stake

def kelly_criterion(odds: float, odds_type: str, true_probability: float,  bank_roll: float = 100.0, kelly_percentage: float = 1.0) -> float:
    """
    Calculate the Kelly Criterion for a given bet.
    
    Args:
        odds (float): The odds of the bet.
        bank_roll (float): The current bankroll.
        true_probability (float): The true probability of winning the bet.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').
    
    Returns:
        float: The optimal stake according to the Kelly Criterion.
    """
    if not _implied_probability_check(true_probability):
        raise ValueError("Invalid true probability. Must be between 0 and 1.")
    
    if not _series_odds_check(pd.Series([odds]), odds_type):
        raise ValueError(f"Invalid odds for type '{odds_type}'.")
    
    if pd.Series(odds).to_implied_probability(odds_type)[0] > true_probability:
        return 0.0

    b = profit(1, odds, odds_type=odds_type)
    
    kelly_fraction = (b*(true_probability) - (1 - true_probability)) / b

    return kelly_percentage * bank_roll * kelly_fraction

"""
Converting interface functions to Pandas functions
"""

PandasObject.to_implied_probability = to_implied_probability
PandasObject.to_odds = to_odds
PandasObject.convert = convert
PandasObject.as_fraction = as_fraction
PandasObject.as_float = as_float
PandasObject.overround = overround
PandasObject.vig = vig
PandasObject.devig = devig
