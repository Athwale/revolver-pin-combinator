#!/usr/bin/python3
import functools
import optparse
import os
import sys
from more_itertools import distinct_permutations

import yaml


class Combinator:

    def __init__(self):
        self._pin_database = None
        self._key_pin_list = []
        self._driver_pin_list = []
        self._spring_list = []

        self._parser = optparse.OptionParser('Usage: pin-combinator.py -f PIN_FILE [options]')

        self._parser.add_option('-f', '--file', type='string',
                                action="store", dest="pin_file",
                                help="Select a pin database to use")

        self._parser.add_option('-l', '--lock', type='int',
                                action="store", dest="lock_size",
                                help="Select a lock size 5-7 pins (default 6)")

        self._options, _ = self._parser.parse_args()
        if not self._options.pin_file:
            self._parser.error('Pin file required')
        if not self._options.lock_size:
            self._options.lock_size = 6
        if self._options.lock_size < 5 or self._options.lock_size > 7:
            self._parser.error('Lock size must be 5-7')

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

    def _combine(self):
        """
        Create the pin, spring combinations.
        :return: None
        """
        combinations = {}
        print('\nCombinations:')
        # Fill the list with suitable pins and springs, but only as much as lock size
        for part_list in [self._key_pin_list, self._driver_pin_list, self._spring_list]:
            combinations[part_list[0].get_kind()] = []
            to_combine = []
            for part in part_list:
                amount = self._options.lock_size
                if part.get_count() < self._options.lock_size:
                    amount = part.get_count()
                for _ in range(amount):
                    to_combine.append(part.get_copy())

            print('Calculating ' + str(part_list[0].get_kind()).replace('-', ' ')[:-1] + ' combinations...')
            combinations[part_list[0].get_kind()] = sorted(distinct_permutations(sorted(to_combine),
                                                                                 self._options.lock_size))

        i = 0
        for kind, result in combinations.items():
            print(kind)
            for combination in result:
                print(combination)
                i += 1

            print(i)
            sys.exit(1)



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
            print(kind.replace('-', ' ') + ': ' + str(count))

    def load(self, file):
        """
        Open and validate the pin database.
        :param file: str, database file name.
        :return: None
        """
        self._pin_database = file
        with open(self._pin_database, "r") as yml:
            data = yaml.safe_load(yml)
            self._validate(data)


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
    combinator = Combinator()
