#!/usr/bin/python3
import yaml
import sys
import optparse
from yaml.scanner import ScannerError


class Combinator:

    def __init__(self):
        self._pin_database = None

        self._parser = optparse.OptionParser('Usage: pin-combinator.py -f PIN_FILE -l LOCK_SIZE [options]')

        self._parser.add_option('-f', '--file', default=False,
                                action="store_true", dest="add_record",
                                help="Run the process of adding a record into database")

        self._parser.add_option('-d', '--delete', type='string',
                                action="store", dest="delete_id",
                                help="Delete a database record with the passed ID")

    def load(self, file) -> bool:
        """
        Open and validate the pin database.
        :param file: str, database file name.
        :return: True if opening and validating succeeded.
        """
        with open(file, "r") as yml:
            try:
                data = yaml.safe_load(yml)
                print(data)
            except yaml.scanner.ScannerError as e:
                print('error' + str(e))
            return True


if __name__ == '__main__':
    combinator = Combinator()
