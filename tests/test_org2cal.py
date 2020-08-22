"""Tests org2cal.py."""
import unittest
import datetime
from time import time
import os
import filecmp
import org2cal  # pylint: disable=import-error


class TestOrg2Cal(unittest.TestCase):
    """Tests org2cal.py."""

    def test_single_day(self):
        """Tests getting single day's clock events."""
        log_file = org2cal.OrgFile("tests/log.org")
        target_file = "tests/target.ics"
        date = [datetime.date(2020, 8, 17)]
        out_file = "tests/out-{}.ics".format(time())
        log_file.export_clock(date, out_file)
        self.assertTrue(filecmp.cmp(target_file, out_file))
        os.remove(out_file)
