import Levenshtein
import math
import pandas as pd

# A missing gender, city or age is no evidence either way, so it scores the
# neutral 0.5 rather than counting as a mismatch.
NEUTRAL = 0.5

def _missing(value):
    return value is None or (not isinstance(value, str) and pd.isna(value)) \
        or str(value).strip().lower() in ('', 'nan', 'none', 'u')

def matchRunner(first1, last1, gender1, age1, city1, first2, last2, gender2, age2, city2):
    """Similarity of two runners, 0 to 6: first name + 2 x last name + gender
    + city + age.  Ages only need to be comparable, so birth years work too."""
    fscore=matchFirstName(first1, first2)
    lscore=2*matchLastName(last1, last2)
    cscore=matchCity(city1, city2)
    ascore=matchAge(age1, age2)
    gscore=matchGender(gender1, gender2)
    return fscore+lscore+gscore+cscore+ascore

def matchGender(gender1, gender2):
    if _missing(gender1) or _missing(gender2):
        return NEUTRAL
    if (gender1.lower()[0]==gender2.lower()[0]):
        return 1
    else:
        return 0


def matchFirstName(first1, first2):
    return Levenshtein.ratio(first1, first2)

def matchLastName(last1, last2):
    return Levenshtein.ratio(last1, last2)

def matchCity(city1, city2):
    if _missing(city1) or _missing(city2):
        return NEUTRAL
    return Levenshtein.ratio(city1,city2)

def matchAge(age1, age2):
    try:
        if _missing(age1) or _missing(age2):
            return NEUTRAL
        exponent=0.5*float(abs(age1-age2))
        # a wildly wrong age (bad birthdate) would overflow exp(); the score is ~0 anyway
        return 2/(1+math.exp(exponent)) if exponent < 700 else 0.0
    except (TypeError, ValueError):
        return NEUTRAL
