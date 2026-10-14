import pytest

from app.services.pricing import money, quantity_to_milli, line_total_cents, milli_to_quantity


def test_unit_pricing():
    assert quantity_to_milli('2','unit')==2000
    assert line_total_cents(750,2000,'unit')==1500


def test_weight_pricing():
    assert quantity_to_milli('1.58','kg')==1580
    assert line_total_cents(340,1580,'kg')==537


def test_fractional_unit_rejected():
    with pytest.raises(ValueError): quantity_to_milli('1.5','unit')


def test_display_quantity():
    assert milli_to_quantity(250,'kg')=='0.25'
    assert milli_to_quantity(2000,'unit')=='2'


def test_non_positive_and_blank_quantities_become_zero():
    for raw in ('0', '-3', '', '   ', None):
        assert quantity_to_milli(raw, 'kg') == 0
        assert quantity_to_milli(raw, 'unit') == 0


def test_non_numeric_quantity_is_a_clean_value_error():
    for raw in ('abc', '1,5', 'NaN'):
        with pytest.raises(ValueError):
            quantity_to_milli(raw, 'kg')


def test_weight_quantity_rounds_half_up_to_milli():
    assert quantity_to_milli('1.2345', 'kg') == 1235
    assert quantity_to_milli('0.4995', 'kg') == 500


def test_weight_total_rounds_half_up_to_cents():
    # 100 cents per kg x 1.555 kg = 155.5 cents -> 156
    assert line_total_cents(100, 1555, 'kg') == 156
    # 340 cents per kg x 1.58 kg = 537.2 cents -> 537
    assert line_total_cents(340, 1580, 'kg') == 537


def test_unit_total_requires_a_whole_number_of_items():
    with pytest.raises(ValueError):
        line_total_cents(750, 1500, 'unit')
    assert line_total_cents(750, 3000, 'unit') == 2250


def test_display_quantity_edge_cases():
    assert milli_to_quantity(None, 'kg') == ''
    assert milli_to_quantity(0, 'unit') == '0'
    assert milli_to_quantity(500, 'kg') == '0.5'
    assert milli_to_quantity(1000, 'unit') == '1'


def test_money_formats_cents_for_display():
    assert money(0) == '$0.00'
    assert money(None) == '$0.00'
    assert money(1500) == '$15.00'
    assert money(123456) == '$1,234.56'
