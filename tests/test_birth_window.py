"""Run from the repo root:  python -m unittest discover -s tests"""
import datetime as dt
import unittest

from scoreware.race.utils import birth_window, windows_overlap


class BirthWindowTest(unittest.TestCase):

    def test_november_birthday_between_race_dates(self):
        # born 1950-11-10: races fall either side of the birthday, so the age
        # repeats one year and jumps by two the other way round
        born = dt.date(1950, 11, 10)
        same_age_twice = (birth_window(35, dt.date(1985, 11, 15)), birth_window(35, dt.date(1986, 11, 8)))
        jump_by_two    = (birth_window(34, dt.date(1985, 11, 8)),  birth_window(36, dt.date(1986, 11, 15)))
        for w1, w2 in (same_age_twice, jump_by_two):
            self.assertTrue(windows_overlap(w1, w2, slack_years=0))
            self.assertTrue(w1[0] <= born <= w1[1] and w2[0] <= born <= w2[1])

    def test_ages_years_apart(self):
        joe_1985 = birth_window(25, dt.date(1985, 11, 10))
        self.assertTrue(windows_overlap(joe_1985, birth_window(39, dt.date(1999, 11, 10))))
        self.assertFalse(windows_overlap(joe_1985, birth_window(45, dt.date(1999, 11, 10))))
        # a year off is a typo we tolerate only through the slack
        off_by_one = birth_window(40, dt.date(1999, 11, 10))
        self.assertTrue(windows_overlap(joe_1985, off_by_one, slack_years=1))
        self.assertFalse(windows_overlap(joe_1985, off_by_one, slack_years=0))

    def test_unknown_age_matches_anything(self):
        self.assertIsNone(birth_window(None, dt.date(1976, 11, 21)))
        self.assertTrue(windows_overlap(None, birth_window(30, dt.date(2000, 11, 12))))


if __name__ == '__main__':
    unittest.main()
