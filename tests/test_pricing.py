import pytest
from app.services.pricing import quantity_to_milli,line_total_cents,milli_to_quantity

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
