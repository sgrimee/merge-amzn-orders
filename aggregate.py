# Aggregate all amazon orders csv files in current directory
# Remove title line and total line, concatenate and save a single output.csv file.
# Add title line to the output
# Add column with country, taken from filename. Convention CC-YYYY-(.*).csv where CC is country code and YYYY is year
# Reports obtained with chrome extension: https://chrome.google.com/webstore/detail/amazon-order-history-repo/mgkilgclilajckgnedgjgnfdokkgnibi

from email.policy import strict
from babel.numbers import format_decimal, parse_decimal
from babel import Locale
from decimal import Decimal
import csv
import glob
import os
import re
import sys


def is_order(row):
    """ Whether row is a data row with an order id (neither a header nor a footer). """
    pattern = re.compile(r"\d+-\d+-\d+")
    return pattern.match(row[0]) is not None


def get_country(filename):
    """ Return the given the country code extracted from the filename. """
    pattern = re.compile(r"^([a-z]{2,3})-\d{4}-\w+")
    country = pattern.match(filename).group(1)
    return country


def split_currency(numstring, country, output_locale):
    """ split numstring into a currency and value, adjusting locale for the country """
    pattern = re.compile(r"\D*([\d\.\,]+)")
    m = pattern.match(numstring)
    locales = {
        "us": Locale("en", "US"),
        # french locale does not support thousand separators, but amazon.fr uses them
        "fr": Locale("de"),
        "de": Locale("de"),
        "uk": Locale("en", "GB")
    }
    currencies = {
        "us": "USD",
        "fr": "EUR",
        "de": "EUR",
        "uk": "GBP"
    }
    value = parse_decimal(m.group(1), locale=locales[country],
                          strict=True).quantize(Decimal('1.00'))
    return (currencies[country], format_decimal(value, locale=output_locale, group_separator=False))


def iter_merged_item_rows(path, output_locale):
    """ Iterate over rows merged from all csv files in 'path', that contain an order item.
        The country is extracted from the file name and added as last column. """
    for relative_file in glob.iglob('??-????-*.csv', root_dir=path):
        with open(os.path.join(path, relative_file), 'r') as file:
            country = get_country(relative_file)
            for row in filter(is_order, csv.reader(file)):
                (currency, value) = split_currency(
                    row[-1], country, output_locale)
                row[-1] = currency
                row.append(value)
                row.append(country)
                yield(row)


def main():
    path = sys.argv[1]
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["order id", "order date", "quantity",
                        "description", "currency", "price", "country"])
        writer.writerows(iter_merged_item_rows(path, output_locale='en_US'))


if __name__ == "__main__":
    main()
