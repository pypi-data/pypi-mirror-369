#!/usr/bin/env python

import argparse
import unittest

from waflibs import log


class TestLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v_parser = argparse.ArgumentParser(description="test verbose logger")
        v_parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
        cls.v_args = v_parser.parse_args(["-v"])

        parser = argparse.ArgumentParser(description="test logger")
        cls.args = parser.parse_args({})


class TestLogger(TestLog):
    def tearDownModule(self):
        self.logging.shutdown()

    def test_create_verbose_logger(self):
        logger = log.create_logger(self.v_args)
        logger.handlers.clear()

    def test_create_logger(self):
        logger = log.create_logger(self.args)
        logger.handlers.clear()

    def test_one_logger(self):
        logger = log.create_logger(self.v_args)

        with self.assertLogs(logger, level="DEBUG") as cm:
            logger.debug("test")
        self.assertNotRegex(str(cm.output), r".*test.*test")

        logger.handlers.clear()


if __name__ == "__main__":
    unittest.main()
