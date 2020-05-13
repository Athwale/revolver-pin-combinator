#!/usr/bin/python3

import yaml
from yaml.scanner import ScannerError


def load(file) -> bool:
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
    load('./pins.yml')
