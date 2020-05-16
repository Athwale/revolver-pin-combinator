#!/usr/bin/python3
import optparse
import os
import sys

import yaml
import yamllint
from yaml.scanner import ScannerError


class Combinator:

    def __init__(self):
        self._pin_database = None

        self._parser = optparse.OptionParser('Usage: pin-combinator.py -f PIN_FILE [options]')

        self._parser.add_option('-f', '--file', type='string',
                                action="store", dest="pin_file",
                                help="Select a pin database to use")

        self._parser.add_option('-l', '--lock', type='string',
                                action="store", dest="lock_size",
                                help="Select a lock size 5-7 pins (default 6)")

        self._options, _ = self._parser.parse_args()
        if not self._options.pin_file:
            self._parser.error('Pin file required')
        if not self._options.lock_size:
            self._options.lock_size = 6

        if not self.load(os.path.realpath(self._options.pin_file)):
            print('Combinator error')
            sys.exit(1)

    def _validate(self, yml) -> bool:
        """
        Check the correctness of the pin database
        :param yml: Loaded yaml data
        :return: True if correct.
        """
        print(yml)
        # Check main categories
        for category in ['key-pins', 'driver-pins', 'springs']:
            if category not in yml.keys():
                raise ValueError(str(category) + ' category is required in pin file')

    def load(self, file) -> bool:
        """
        Open and validate the pin database.
        :param file: str, database file name.
        :return: True if opening and validating succeeded.
        """
        self._pin_database = file
        try:
            with open(file, "r") as yml:
                data = yaml.safe_load(yml)
                result = self._validate(data)
        except ValueError as e:
            print(e)
            return False
        return result


if __name__ == '__main__':
    combinator = Combinator()
