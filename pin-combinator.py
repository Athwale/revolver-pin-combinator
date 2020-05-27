#!/usr/bin/python3
import functools
import locale
import optparse
import os
import sys
from itertools import product

import yaml
from more_itertools import distinct_permutations
from yaml.parser import ParserError


class Combinator:
    LOCK_MIN_LIMIT = 1
    LOCK_MAX_LIMIT = 20
    FILE_LIMIT = 5000000

    def __init__(self):
        self._pin_database = None
        self._key_pin_list = []
        self._driver_pin_list = []
        self._spring_list = []
        self._combinations = {}
        self._locks = None
        self._counts = {}
        self._output_file = None

        # Set large numbers to display comma separators
        locale.setlocale(locale.LC_ALL, 'cs_CZ')
        self._parser = optparse.OptionParser('Usage: pin-combinator.py -f PIN_FILE [options]')

        self._parser.add_option('-f', '--file', type='string',
                                action="store", dest="pin_file",
                                help="Select a pin database to use")

        self._parser.add_option('-l', '--lock', type='int',
                                action="store", dest="lock_size",
                                help="Select a lock size " + str(self.LOCK_MIN_LIMIT) + "-" +
                                     str(self.LOCK_MAX_LIMIT) + " pins (default 6)")

        self._parser.add_option('-q', '--quiet', default=False,
                                action="store_true", dest="quiet",
                                help="Do not print lock combinations on screen, just save into file")

        self._options, _ = self._parser.parse_args()
        if not self._options.pin_file:
            self._parser.error('Pin file required')
        if self._options.lock_size is None:
            self._options.lock_size = 6
        if self._options.lock_size < self.LOCK_MIN_LIMIT or self._options.lock_size > self.LOCK_MAX_LIMIT:
            self._parser.error('Lock size must be ' + str(self.LOCK_MIN_LIMIT) + '-' + str(self.LOCK_MAX_LIMIT))

        try:
            self.load(os.path.realpath(self._options.pin_file))
        except ValueError as e:
            print(e)
            print('Load error')
            sys.exit(1)

        try:
            self._combine()
        except ValueError as e:
            print(e)
            print('Combinator error')
            sys.exit(2)

    def _combine(self) -> None:
        """
        Create the key pin, driver pin, spring combinations and print counts.
        :return: None
        """
        print('\nCalculating combinations:')
        print('Depending on computer speed, number of pins in pin file and lock size, this can take a long time.\n')
        # Fill the list with suitable pins and springs, but only as much as lock size
        for part_list in [self._key_pin_list, self._driver_pin_list, self._spring_list]:
            self._combinations[part_list[0].get_kind()] = []
            to_combine = []
            for part in part_list:
                amount = self._options.lock_size
                if part.get_count() < self._options.lock_size:
                    amount = part.get_count()
                for _ in range(amount):
                    to_combine.append(part.get_copy())

            part_type = str(part_list[0].get_kind())
            self._counts[part_type] = 0
            print(('Calculating ' + part_type.replace('-', ' ')[:-1] + ' combinations:').ljust(36), end=' ')
            # Create combination iterators
            self._combinations[part_type] = sorted(distinct_permutations(sorted(to_combine), self._options.lock_size))
            # Print how many combinations we have
            for _ in self._combinations[part_type]:
                self._counts[part_type] += 1
            print(str(locale.format_string("%d", self._counts[part_type], grouping=True)))

        self._locks = product(self._combinations['key-pins'], self._combinations['driver-pins'],
                              self._combinations['springs'])
        lock_total = self._counts['key-pins'] * self._counts['driver-pins'] * self._counts['springs']
        print(
            'Total lock configurations: '.ljust(37) + str(locale.format_string("%d", lock_total, grouping=True)) + '\n')
        self._save_combinations()

    def _save_combinations(self) -> None:
        """
        Print the finished lock combinations on screen and save then into a set of files.
        :return: None
        """
        i = 1
        file_counter = 1
        try:
            for lock in self._locks:
                lock_string = self._format_lock(lock, i)
                if not self._options.quiet:
                    print(lock_string)
                else:
                    print('Saving lock: ' + str(locale.format_string("%d", i, grouping=True)), end='\r')
                    if not self._output_file:
                        output_file_name = os.path.basename(self._options.pin_file).replace('.yml', '') + '_locks_' + \
                                           str(file_counter) + '.txt'
                        self._output_file = open(output_file_name, 'w')

                    # Write the lock into the file
                    self._output_file.write(lock_string)

                    if (i % self.FILE_LIMIT) == 0:
                        self._output_file.close()
                        file_counter += 1
                        self._output_file = None
                i += 1
        except KeyboardInterrupt as _:
            self._output_file.close()
            raise KeyboardInterrupt('Stopped by user')

    @staticmethod
    def _format_lock(lock, number: int) -> str:
        """
        Get a string representation of a fully assembled lock
        :param lock: Tuple of 3 combinations
        :param number: Index of this lock.
        :return: string lock representation
        """
        key_pins = lock[0]
        driver_pins = lock[1]
        springs = lock[2]
        assembled = ''

        assembled += 'Lock: ' + str(locale.format_string("%d", number, grouping=True)) + ':\n'
        for part_type in [springs, driver_pins, key_pins]:
            assembled += str(part_type[0].get_kind().replace('-', ' ') + ': ').ljust(13)
            for part in part_type:
                assembled += '|' + part.get_name() + str(part.get_size())
            assembled += '|\n'
        assembled += '\n'

        return assembled

    def _validate(self, yml):
        """
        Check the correctness of the pin database
        :param yml: Loaded yaml data
        :return: None
        """
        # Check main categories
        for category in ['key-pins', 'driver-pins', 'springs']:
            if category not in yml.keys():
                raise ValueError(str(category) + ' category is required in pin file')

        pin_list = []
        for category in yml.keys():
            # Check at least one record in each category
            if not yml[category]:
                raise ValueError('Category: ' + str(category) + ' has not records')

            # Check for duplicate pins
            pin_list.extend(yml[category])
            for item in pin_list:
                if pin_list.count(item) > 1:
                    raise ValueError('Duplicate record: ' + str(item) + ' in pin file: ' + str(self._pin_database))

            # Check pin format
            for part in yml[category]:
                elements = part.split('-')
                # Check pin name
                # Check the name is a string
                try:
                    err = int(elements[0])
                    if err:
                        raise AttributeError(str(part) + ' has incorrect format, name must not be a number')
                except ValueError as _:
                    pass
                except AttributeError as e:
                    raise ValueError(str(e))
                # Check the pin has a two letter name
                if len(elements[0]) != 2:
                    raise ValueError(str(part) + ' must have a two letter name')
                # Check pin size and count
                try:
                    int(elements[1])
                    int(elements[2])
                except ValueError as _:
                    raise ValueError(str(part) + ' has incorrect format, size and count must be a number')

                # Validation passed, create part instance
                if category == 'key-pins':
                    target_list = self._key_pin_list
                elif category == 'driver-pins':
                    target_list = self._driver_pin_list
                else:
                    target_list = self._spring_list

                target_list.append(Part(category, elements[0], int(elements[1]), int(elements[2])))

        # Check that we have enough parts for the selected lock size
        for kind, count in Part.count_dict.items():
            if count < self._options.lock_size:
                raise ValueError('Not enough ' + kind.replace('-', ' ').upper() + ' (' + str(count) + ')'
                                 + ' for a ' + str(self._options.lock_size) + ' pin lock')

        self._print_database()

    def _print_database(self) -> None:
        """
        Nicely print the database and useful data.
        :return: None
        """
        print('Key pins:')
        print(self._key_pin_list)
        print('Driver pins:')
        print(self._driver_pin_list)
        print('Springs:')
        print(self._spring_list)
        print('\nSummary:')
        for kind, count in Part.count_dict.items():
            print((kind.replace('-', ' ') + ': ').ljust(13) + str(locale.format_string("%d", count, grouping=True)))
        print('Lock size: '.ljust(13) + str(self._options.lock_size))

    def load(self, file):
        """
        Open and validate the pin database.
        :param file: str, database file name.
        :return: None
        """
        self._pin_database = file
        if not os.path.splitext(file)[1] == '.yml':
            raise ValueError('File ' + str(os.path.basename(file)) + ' must end with .yml')
        try:
            with open(self._pin_database, "r") as yml:
                data = yaml.safe_load(yml)
                self._validate(data)
        except FileNotFoundError as _:
            raise ValueError('File ' + str(os.path.basename(file)) + ' does not exist')
        except ParserError as _:
            raise ValueError('File ' + str(os.path.basename(file)) + ' is not valid yaml')


@functools.total_ordering
class Part:
    # Static variable counting how many of each part type we have.
    count_dict = {'key-pins': 0, 'driver-pins': 0, 'springs': 0}

    def __init__(self, kind: str, name: str, size: int, count: int):
        """
        Constructor for a lock part class. This may represent a pin or a spring.
        :param kind: key-pin, driver-pin, spring
        :param name: The user defined name of the pin or spring
        :param size: The size (strength) of the pin or spring.
        :param count: How many of these are in the database.
        """
        self._kind = kind
        self._name = name
        self._size = size
        self._count = count

        Part.count_dict[kind] += self._count

    def get_kind(self) -> str:
        """
        Return what part this is.
        :return: Either key-pin, driver-pin or a spring
        """
        return self._kind

    def get_name(self) -> str:
        """
        Return type this part is.
        :return: A two letter description of this part (ST, MU, SP,...)
        """
        return self._name

    def get_size(self) -> int:
        """
        Return the size or strength of this part.
        :return: The size or strength of this part.
        """
        return self._size

    def get_count(self) -> int:
        """
        Return how many of these parts the database has.
        :return: How many of these parts the database has.
        """
        return self._count

    def get_copy(self):
        """
        Return a new instance of it self.
        :return: Return a new instance of it self.
        """
        return Part(self.get_kind(), self._name, self.get_size(), self._count)

    def __str__(self):
        return '(' + self._kind + '-' + self._name + '-' + str(self._size) + '-' + str(self._count) + ')'

    def __repr__(self):
        return self._name + '-' + str(self._size) + '-' + str(self._count)

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()


if __name__ == '__main__':
    try:
        combinator = Combinator()
    except KeyboardInterrupt as s:
        print(s)
        sys.exit(2)
