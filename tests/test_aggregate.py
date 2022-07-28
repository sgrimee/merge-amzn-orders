import pytest
from aggregate import *
from decimal import Decimal


def test_is_order():
    order_row = ['406-9588407-4699538',
                 '2019-09-22', '1', 'Legrand', 'EUR 9,21']
    header_row = ['order id', 'order date', 'quantity', 'description', 'price']
    footer_row = ['"=SUBTOTAL(103, A2:A11) & "" items"""', '', '', '', '']
    assert is_order(order_row)
    assert not is_order(header_row)
    assert not is_order(footer_row)


def country():
    assert country('de-2018-amazon_order_history.csv') == 'de'


def test_split_currency():
    assert split_currency("EUR 116,08", "de", 'en_US') == ("EUR", "116.08")
    assert split_currency("EUR 1.499,99", "fr", 'en_US') == ("EUR", "1499.99")
    assert split_currency("£23.70", "uk", 'en_US') == ("GBP", "23.7")
    assert split_currency("$16.47", "us", 'en_US') == ("USD", "16.47")
    assert split_currency("0", "us", 'en_US') == ("USD", "0")
