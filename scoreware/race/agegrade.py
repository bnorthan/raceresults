"""Age grading: a time as a percentage of the best possible time for the runner's
age and sex, using the 2025 road standards (agegrade_tables/README.md)."""
import functools
import os

import pandas as pd

TABLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agegrade_tables')


@functools.lru_cache()
def _standards(gender):
    return pd.read_csv(os.path.join(TABLES, f'road_standards_2025_{gender}.csv'), index_col='Age')


def age_standard(age, gender, distance='15 km'):
    """Age-standard time in seconds, or None if age/gender is unknown or off the table."""
    if gender not in ('M', 'F') or age is None or pd.isna(age):
        return None
    table = _standards(gender)
    age = int(age)
    return float(table.at[age, distance]) if age in table.index else None


def age_grade(seconds, age, gender, distance='15 km'):
    """Age grade in percent (100 = the age standard), or None if it can't be graded."""
    standard = age_standard(age, gender, distance)
    if standard is None or not seconds or seconds <= 0:
        return None
    return 100 * standard / seconds
