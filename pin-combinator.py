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
        self._count_dict = None

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

        for category in yml.keys():
            # Check at least one record in each category
            if not yml[category]:
                raise ValueError('Category: ' + str(category) + ' has not records')

            # Check pin format
            for part in yml[category]:
                elements = part.split('-')
                print(elements)
                # Check pin name
                try:
                    err = int(elements[0])
                    if err:
                        raise AttributeError(str(part) + ' has incorrect format, name must not be a number')
                except ValueError as _:
                    pass
                except AttributeError as e:
                    raise ValueError(str(e))
                # Check pin size and count
                try:
                    int(elements[1])
                    int(elements[2])
                except ValueError as _:
                    raise ValueError(str(part) + ' has incorrect format, size and count must be a number')

        # Check that we have enough parts for the selected lock size
        chamber_count = self._options.lock_size
        self._count_dict = {}
        for category in yml.keys():
            self._count_dict[category] = 0
            for part in yml[category]:
                pin_count = int(part.split('-')[2])
                self._count_dict[category] += pin_count


    def _print_database(self):
        """

        :return:
        """
        pass

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
