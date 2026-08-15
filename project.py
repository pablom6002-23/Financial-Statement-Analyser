import csv
from fpdf import FPDF
import sys

#Storing each row as a dictionary of data(dict) according to its year(key)
def get_data(file):
    data = {}
    with open(file) as file:
        reader = csv.DictReader(file)
        for row in reader:
            year = int(row["Year"])
            data[year] = row
    return data

class Company:
    def __init__(self, name, csvfile):
        self.name = name
        self.data = get_data(csvfile)
        self.years = sorted(self.data.keys())

        # Identify columns once at initialisation, store for use throughout the class
        self.revenue_col = self.find_column(["revenue", "net sales", "sales", "turnover", "total revenue"])
        self.earnings_col = self.find_column(["net income", "earnings", "net profit", "profit after tax"])
        self.debt_col = self.find_column(["long term debt", "total debt", "long-term debt", "total borrowings"])
        self.assets_col = self.find_column(["total assets"])
        self.net_assets_col = self.find_column(["net assets", "shareholders equity", "stockholders equity", "total equity"])
        self.cash_col = self.find_column(["cash on hand", "cash and cash equivalents", "cash and equivalents"])
        self.liabilities_col = self.find_column(["total liabilities"])
        self.operating_margin_col = self.find_column(["operating margin", "gross margin", "ebit margin"])
        self.market_cap_col = self.find_column(["market cap", "market capitalisation", "market capitalization"])
        self.dividend_col = self.find_column(["dividend (stock split adjusted)", "dividends per share", "dps"])
        self.eps_col = self.find_column(["eps", "earnings per share", "diluted eps"])
        self.pe_col = self.find_column(["p/e ratio", "pe ratio", "price to earnings"])

    # Searches column names for any matching keyword, case-insensitively
    def find_column(self, keywords):
        columns = list(self.data[self.years[0]].keys())
        for col in columns:
            if any(keyword in col.lower() for keyword in keywords):
                return col
        return None

    #Calculates the profit margin of a certain year
    def profit_margin(self, year):
        earnings = float(self.data[year][self.earnings_col])
        revenue = float(self.data[year][self.revenue_col])
        profit_margin = (earnings / revenue) * 100
        return profit_margin

    #Calculates debt-to-assets ratio for a certain year
    def debt_to_assets(self, year):
        total_debt = float(self.data[year][self.debt_col])
        total_assets = float(self.data[year][self.assets_col])
        debt_to_assets = total_debt / total_assets * 100
        return debt_to_assets

    #Calculates Return On Equity for a given year
    def ROE(self, year):
        earnings = float(self.data[year][self.earnings_col])
        net_assets = float(self.data[year][self.net_assets_col])
        roe = (earnings / net_assets) * 100
        return roe

    #Calculates debt-to-equity ratio for a certain year
    def debt_to_equity(self, year):
        debt = float(self.data[year][self.debt_col])
        net_assets = float(self.data[year][self.net_assets_col])
        debt_to_equity = debt / net_assets
        return debt_to_equity

    #Calculates cash ratio for a certain year
    def cash_ratio(self, year):
        cash = float(self.data[year][self.cash_col])
        liabilities = float(self.data[year][self.liabilities_col])
        cash_ratio = cash / liabilities
        return cash_ratio

    #Given a specific metric, it describes the trend of the metric between two given years
    def trend(self, metric, year1=None, year2=None):
        if year1 is None:
            year1 = self.years[0]
        if year2 is None:
            year2 = self.years[-1]
        metric_year1 = float(self.data[year1][metric])
        metric_year2 = float(self.data[year2][metric])
        perc_diff = ((metric_year2 - metric_year1) / metric_year1) * 100
        if metric_year2 > metric_year1 * 1.05:          #1.05 and 0.95 are a 5% buffer for STABLE
            return "IMPROVING", perc_diff
        elif metric_year2 < metric_year1 * 0.95:
            return "DECLINING", perc_diff
        else:
            return "STABLE", 0.0

    #Given a specific metric and year, it calculates its percentage growth/decline from the previous year
    def growth(self, metric, year):
        if year == self.years[0]:
            return None
        metric_current = float(self.data[year][metric])
        prev_year = self.years[self.years.index(year) - 1]
        metric_prev = float(self.data[prev_year][metric])
        metric_perc_diff = ((metric_current - metric_prev) / metric_prev) * 100
        if metric_perc_diff > 0:
            return "IMPROVING", metric_perc_diff
        if metric_perc_diff < 0:
            return "DECLINING", metric_perc_diff
        else:
            return "STABLE", 0.0

    def flags(self):
        warnings = []
        positives = []

        #Profitability
        if self.profit_margin(self.years[-1]) > 20:
            positives.append("Profitability above 20%: STRONG")
        elif 10 <= self.profit_margin(self.years[-1]) <= 20:
            positives.append("Profitability between 10-20%: MODERATE")
        else:
            warnings.append("Profitability below 10%: WEAK")

        #Operating Margin
        if self.operating_margin_col:
            if float(self.data[self.years[-1]][self.operating_margin_col]) < 25:
                warnings.append("Operating margin below 25%: margin compression detected")

        #Revenue trends
        if self.revenue_col:
            revenue_trend, revenue_diff = self.trend(self.revenue_col)
            if revenue_trend == "IMPROVING":
                positives.append(f"Revenue Growing: +{revenue_diff:.2f}%")
            elif revenue_trend == "DECLINING":
                warnings.append(f"Revenue decreasing: {revenue_diff:.2f}%")

        #Earnings trends
        if self.earnings_col:
            earnings_trend, earnings_diff = self.trend(self.earnings_col)
            if earnings_trend == "IMPROVING":
                positives.append(f"Earnings Increasing: +{earnings_diff:.2f}%")
            elif earnings_trend == "DECLINING":
                warnings.append(f"Earnings decreasing: {earnings_diff:.2f}%")

        #Debt
        if self.debt_col and self.assets_col:
            if self.debt_to_assets(self.years[-1]) > 80:
                warnings.append("Debt-to-assets ratio above 80%: highly leveraged")

        #Comparing revenue and debt
        if self.debt_col and self.revenue_col:
            debt_first = float(self.data[self.years[0]][self.debt_col])
            debt_last = float(self.data[self.years[-1]][self.debt_col])
            rev_first = float(self.data[self.years[0]][self.revenue_col])
            rev_last = float(self.data[self.years[-1]][self.revenue_col])
            if debt_first == 0 or rev_first == 0:
                # can't compare growth rates if starting value is zero
                if debt_last > 0:
                    warnings.append("Debt has grown from zero: company has taken on significant debt")
            elif (debt_last / debt_first) > (rev_last / rev_first):
                warnings.append("Debt growing faster than revenue: leverage increasing")
            elif (debt_last / debt_first) < (rev_last / rev_first):
                positives.append("Revenue growing faster than debt: leverage decreasing")

        #ROE and debt-to-equity ratio analysis, only if net assets are positive
        if self.net_assets_col:
            net_assets = float(self.data[self.years[-1]][self.net_assets_col])
            if net_assets < 0:
                warnings.append("Negative net assets: ROE and Debt-to-Equity are not meaningful. Likely driven by aggressive share buybacks")
            else:
                if self.ROE(self.years[-1]) > 20:
                    positives.append(f"Strong ROE: {self.ROE(self.years[-1]):.2f}%")
                elif self.ROE(self.years[-1]) < 10:
                    warnings.append(f"Weak ROE: {self.ROE(self.years[-1]):.2f}%")

                if self.debt_to_equity(self.years[-1]) > 2:
                    warnings.append(f"High debt-to-equity ratio: {self.debt_to_equity(self.years[-1]):.2f}x")
                elif self.debt_to_equity(self.years[-1]) < 1:
                    positives.append(f"Conservative debt-to-equity: {self.debt_to_equity(self.years[-1]):.2f}x")

        #Growth since last year in Revenue, Market Cap and Dividends
        if self.revenue_col:
            revenue_growth = self.growth(self.revenue_col, self.years[-1])
            if revenue_growth[0] == "IMPROVING":
                positives.append(f"Revenue up since last year: +{revenue_growth[1]:.2f}%")
            elif revenue_growth[0] == "DECLINING":
                warnings.append(f"Revenue down since last year: {revenue_growth[1]:.2f}%")

        if self.market_cap_col:
            market_cap_growth = self.growth(self.market_cap_col, self.years[-1])
            if market_cap_growth[0] == "IMPROVING":
                positives.append(f"Market Capitalisation up since last year: +{market_cap_growth[1]:.2f}%")
            elif market_cap_growth[0] == "DECLINING":
                warnings.append(f"Market Capitalisation down since last year: {market_cap_growth[1]:.2f}%")

        if self.dividend_col:
            dividend_growth = self.growth(self.dividend_col, self.years[-1])
            if dividend_growth[0] == "IMPROVING":
                positives.append(f"Dividends up since last year: +{dividend_growth[1]:.2f}%")
            elif dividend_growth[0] == "DECLINING":
                warnings.append(f"Dividends down since last year: {dividend_growth[1]:.2f}%")

        return positives, warnings


class PDF(FPDF):
    def __init__(self, company):
        super().__init__(orientation="portrait", format="A4")
        self.company = company

    def header(self):
        # Only the title here
        self.set_font("Times", style="B", size=20)
        self.cell(0, 10, "", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 10, f"{self.company.name} Financial Report",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)


def main():
    name = sys.argv[1]
    csvpath = sys.argv[2]
    try:
        company = Company(name, csvpath)
    except FileNotFoundError:
        sys.exit(f"Could not read file: {csvpath}")

    pdf = PDF(company)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # FINANCIAL RATIO ANALYSIS SECTION
    pdf.set_font("Times", style="B", size=15)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Financial Ratio Analysis", fill=True,
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Profit Margin: {company.profit_margin(company.years[-1]):.2f}%",
             new_x="LMARGIN", new_y="NEXT")
    if company.debt_col and company.assets_col:
        pdf.cell(0, 8, f"Debt-to-assets: {company.debt_to_assets(company.years[-1]):.2f}%",
                 new_x="LMARGIN", new_y="NEXT")
    if company.cash_col and company.liabilities_col:
        pdf.cell(0, 8, f"Cash ratio: {company.cash_ratio(company.years[-1]):.2f}",
                 new_x="LMARGIN", new_y="NEXT")
    if company.net_assets_col:
        net_assets = float(company.data[company.years[-1]][company.net_assets_col])
        if net_assets < 0:
            pdf.cell(0, 8, "Debt-to-equity: N/A (negative equity)",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, "ROE: N/A (negative equity)",
                     new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 8, f"Debt-to-equity: {company.debt_to_equity(company.years[-1]):.2f}x",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"ROE: {company.ROE(company.years[-1]):.2f}%",
                     new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # POSITIVES SECTION
    positives, warnings = company.flags()
    pdf.set_font("Times", style="B", size=15)
    pdf.set_fill_color(0, 120, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Positives", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    for positive in positives:
        pdf.cell(0, 8, f"[+]  {positive}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # WARNINGS SECTION
    pdf.set_font("Times", style="B", size=15)
    pdf.set_fill_color(180, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Warnings", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    for warning in warnings:
        pdf.cell(0, 8, f"[!] {warning}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # GROWTH SINCE LAST YEAR SECTION
    pdf.set_font("Times", style="B", size=15)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Growth Since Last Year", fill=True,
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    for metric in company.data[company.years[-1]].keys():
        if metric == "Year":
            continue
        growth_result = company.growth(metric, company.years[-1])
        if growth_result:
            direction = "[+]" if growth_result[0] == "IMPROVING" else "[-]" if growth_result[0] == "DECLINING" else "[=]"
            pdf.cell(0, 8, f"{direction}  {metric}: {growth_result[1]:.2f}%",
                     new_x="LMARGIN", new_y="NEXT")

    pdf.output(f"{name}_Financial_Report.pdf")
    print(f"Report saved as {name}_Financial_Report.pdf")


if __name__ == "__main__":
    main()