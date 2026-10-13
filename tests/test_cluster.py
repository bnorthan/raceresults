"""Run from the repo root:  python -m unittest discover -s tests"""
import datetime as dt
import unittest

import pandas as pd

from scoreware.runner.cluster import cluster_runners


def results(*rows):
    """rows of (year, first, last, gender, age); every race on Nov 10."""
    df = pd.DataFrame(rows, columns=['year', 'first_name', 'last_name', 'gender', 'age'])
    df['race_date'] = [dt.date(y, 11, 10) for y in df.year]
    df['city'] = None
    return df


class ClusterTest(unittest.TestCase):

    def test_same_year_is_two_people(self):
        c = cluster_runners(results((2000, 'John', 'Smith', 'M', 40),
                                    (2000, 'John', 'Smith', 'M', 40)))
        self.assertEqual(c.person_id.nunique(), 2)

    def test_father_and_son_stay_apart(self):
        c = cluster_runners(results((2000, 'John', 'Smith', 'M', 60), (2001, 'John', 'Smith', 'M', 61),
                                    (2002, 'John', 'Smith', 'M', 32), (2003, 'John', 'Smith', 'M', 33)))
        self.assertEqual(c.person_id.nunique(), 2)

    def test_one_bad_age_stays_with_its_runner(self):
        # Mark Mindel's 1986 result says 38; every other year puts him at 34
        c = cluster_runners(results((1984, 'Mark', 'Mindel', 'M', 32), (1985, 'MARK', 'MINDEL', 'M', 33),
                                    (1986, 'MARK', 'MINDEL', 'M', 38), (1987, 'Mark', 'Mindel', 'M', 35),
                                    (1988, 'Mark', 'Mindel', 'M', 36)))
        self.assertEqual(c.person_id.nunique(), 1)
        self.assertEqual(c.set_index('year').link[1986], 'age outlier')


if __name__ == '__main__':
    unittest.main()
