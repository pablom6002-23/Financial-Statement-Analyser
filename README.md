# Financial Statement Analyser

A Python program that reads a company's financial data from a CSV file, computes
key financial ratios, identifies long-term trends and year-on-year growth, 
automatically flags financial health indicators, and outputs a structured PDF report.


---

## Demo

The analyser has been tested on two very different companies to demonstrate 
its generality:

**McDonald's (2002-2022)**

**Tesla (2014-2024)** 

**Apple (2009-2024)**

---

## Features

- **Financial Ratio Analysis**: computes profit margin, debt-to-assets ratio, 
return on equity (ROE), debt-to-equity ratio, and cash ratio for the most 
recent year
- **Trend Analysis**: identifies whether any metric has been improving, 
declining, or stable across the full dataset, with a 5% buffer to avoid 
labelling insignificant fluctuations as trends
- **Year-on-Year Growth**: calculates the percentage change in every metric 
from the previous year
- **Automated Flags**: draws plain-English conclusions from the data, 
separating positives (things that look healthy) from warnings (things that 
look concerning), including special handling for edge cases like negative 
equity
- **PDF Report**: outputs a structured, professionally formatted PDF report 
named after the company
- **Generalised Column Matching**: works on any financial CSV, not just a 
specific one, by intelligently identifying relevant columns using keyword 
matching regardless of exact column name formatting

---

## How It Works

The program is structured around two classes:

**`Company`** is the analytical core. It loads the CSV into a dictionary 
keyed by year, identifies relevant columns using keyword matching 
(`find_column`), and exposes methods for computing ratios (`profit_margin`, 
`debt_to_assets`, `ROE`, `debt_to_equity`, `cash_ratio`), analysing trends 
(`trend`), calculating growth (`growth`), and generating flags (`flags`).

**`PDF`** extends fpdf2's `FPDF` class to generate the output report, 
organised into sections: Financial Ratio Analysis, Positives, Warnings, 
and Growth Since Last Year.

**`get_data`** reads the CSV file using Python's `csv.DictReader`, storing 
each row as a dictionary keyed by year.

---

## Installation

Install the required dependency:

```bash
pip install fpdf2
```

No other external libraries are required. The program uses only Python 
built-in modules (`csv`, `sys`) alongside fpdf2.

---

## Usage

```bash
python project.py <company_name> <csvfile>
```

**Examples:**

```bash
python project.py McDonalds McDonalds_Financial_Statements.csv
python project.py Tesla Tesla_Financial_Statements.csv
```

This generates a PDF report named `<company_name>_Financial_Report.pdf` 
in the current directory.

---

## CSV Format

The program expects a CSV with a `Year` column and any combination of 
financial columns. Column names do not need to match exactly since the 
program uses keyword matching to identify relevant columns automatically.

Recognised column types and example names:

| Data | Example column names |
|------|----------------------|
| Revenue | `Revenue ($B)`, `Net Sales`, `Total Revenue` |
| Earnings | `Earnings ($B)`, `Net Income`, `Net Profit` |
| Total Debt | `Total debt ($B)`, `Long-term debt`, `Total Borrowings` |
| Total Assets | `Total assets ($B)`, `Total Assets` |
| Net Assets / Equity | `Net assets ($B)`, `Shareholders Equity`, `Total Equity` |
| Cash | `Cash on Hand ($B)`, `Cash and Equivalents` |
| Total Liabilities | `Total liabilities ($B)`, `Total Liabilities` |
| Operating Margin | `Operating Margin (%)`, `EBIT Margin` |
| Market Cap | `Market cap ($B)`, `Market Capitalisation` |
| Dividends | `Dividend (stock split adjusted) ($)`, `DPS` |
| EPS | `EPS ($)`, `Earnings Per Share` |
| P/E Ratio | `P/E ratio`, `Price to Earnings` |

If a column cannot be identified, that metric is simply skipped rather 
than causing the program to crash.

---

## Output

The PDF report contains four sections:

**Financial Ratio Analysis** — key ratios for the most recent year in the 
dataset, with N/A shown for ratios that are not meaningful (e.g. ROE and 
debt-to-equity when net assets are negative).

**Positives** — plain-English statements about things that look financially 
healthy, for example strong profit margins, growing revenues, or declining 
leverage.

**Warnings** — plain-English statements about things that look concerning, 
for example high leverage, declining earnings, or negative equity, with 
contextual explanations where relevant.

**Growth Since Last Year** — the year-on-year percentage change for every 
metric in the dataset.

---

## Files

| File | Description |
|------|-------------|
| `project.py` | Main program: `Company` class, `PDF` class, `get_data`, `main` |
| `test_project.py` | pytest test suite for core functions and methods |
| `McDonalds_Financial_Statements.csv` | McDonald's annual financial data 2002-2022 |
| `Tesla_Financial_Statements.csv` | Tesla annual financial data 2014-2024 |

---
## Sample Reports

Pre-generated reports for three companies are available in the
`sample_reports/` folder:

- [McDonald's Financial Report](sample_reports/McDonalds_Financial_Report.pdf)
- [Apple Financial Report](sample_reports/Apple_Financial_Report.pdf)  
- [Tesla Financial Report](sample_reports/Tesla_Financial_Report.pdf)

---
## Testing

Tests are implemented using pytest and cover `get_data`, `profit_margin`, 
`debt_to_assets`, `cash_ratio`, `trend`, `growth`, and `flags`.

Run the test suite with:

```bash
pytest test_project.py -v
```

---

## Design Decisions

**Generalised column matching over hardcoded strings.** The initial version 
hardcoded column names like `"Revenue ($B)"`, which meant the program only 
worked with one specific CSV. Replacing these with `find_column`, which 
searches column names case-insensitively for any matching keyword, allows 
the program to work on financial CSVs from any source without modification. 
This was the single most important design improvement.

**Column identification at initialisation.** All column matching is done 
once in `__init__` and stored as attributes (`self.revenue_col`, 
`self.earnings_col` etc.), rather than searching on every method call. 
This avoids repeating the same search dozens of times across a single run.

**Returning raw numbers from calculation methods.** Methods like 
`profit_margin` and `debt_to_assets` return plain floats rather than 
formatted strings. This keeps them flexible: the same method can be used 
in arithmetic, compared in tests, and formatted differently depending on 
context (terminal output vs PDF report).

**Separating trend and growth into two general-purpose methods.** An 
earlier version had separate methods for each metric (`revenue_trend`, 
`earnings_trend`, `revenue_growth` etc.), which led to significant code 
repetition. Replacing these with `trend(metric)` and `growth(metric, year)` 
reduced roughly 60 lines of repetitive code to 2 reusable methods that 
work on any column.

**Handling negative equity explicitly.** McDonald's has had negative 
shareholders equity since around 2016 due to aggressive share buybacks. 
Rather than displaying a meaningless negative ROE of -130%, the program 
detects negative equity and substitutes a plain-English explanation. 
This reflects what a real financial analyst would do rather than blindly 
reporting a number that would mislead any reader without context.



---

## Limitations and Potential Improvements

- The program only analyses the most recent year for ratio calculations. 
A historical ratio table showing how ratios have changed year by year 
would add significant analytical depth.
- Quarterly data is not currently supported. The CSV is assumed to contain 
one row per year.
- Adding chart visualisations (revenue over time, margin trends) to the 
PDF would make the report significantly more compelling.

---

## Source Data

- McDonald's financial data sourced from Kaggle
- Tesla financial data converted from public quarterly reports
- Apple's financial data sourced from Kaggle and formatted to suit the program
