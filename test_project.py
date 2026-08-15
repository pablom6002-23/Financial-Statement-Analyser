import pytest
from project import Company, get_data

CSVFILE = "McDonalds_Financial_Statements.csv"

def test_get_data_returns_dict():
    data = get_data(CSVFILE)
    assert isinstance(data, dict)

def test_get_data_invalid_file():
    with pytest.raises(FileNotFoundError):
        get_data("nonexistent.csv")

def test_profit_margin_range():
    company = Company("McDonald's", CSVFILE)
    assert 0 < company.profit_margin(2022) < 100

def test_cash_ratio_positive():
    company = Company("McDonald's", CSVFILE)
    assert company.cash_ratio(2022) > 0

def test_trend_improving():
    company = Company("McDonald's", CSVFILE)
    trend, metric_diff = company.trend("Revenue ($B)")
    assert trend == "IMPROVING"
    assert metric_diff > 0

def test_growth_first_year_returns_none():
    company = Company("McDonald's", CSVFILE)
    assert company.growth("Revenue ($B)", 2002) == None

def test_growth_declining():
    company = Company("McDonald's", CSVFILE)
    trend, metric_diff = company.growth("Revenue ($B)", 2020)
    assert trend == "DECLINING"
    assert metric_diff < 0
