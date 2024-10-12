import yfinance as yf
import datetime as dt
import math

def is_market_open():
    current_datetime = dt.datetime.now()
    current_time = current_datetime.time()
    current_day = current_datetime.strftime('%A')
    open_time=dt.time(9,15)
    close_time=dt.time(15,30)
    if(current_day=="Monday" or current_day=="Tuesday" or current_day=="Wednesday" 
       or current_day=="Thrusday" or current_day=="Friday"):
        if(current_time>=open_time and current_time<=close_time):
            return True
        else:
            return False
    else:
        return False

def fetch_stock_details(symbol):
    try:
        # Fetching stock data
        stock = yf.Ticker(symbol + ".NS")  # Appending ".NS" for NSE stocks
        #stock = yf.Ticker(symbol + ".BO")  # Appending ".BO" for BSE stocks
        
        # Fetching company name
        company_name = stock.info.get('longName', "Not Available")

        # Fetching live price
        live_price = stock.info.get('currentPrice', "Not Available")
        
        # Fetching market capitalization
        market_cap = stock.info.get('marketCap', "Not Available")
        
        # Fetching fundamental ratios
        fundamental_ratios = {
            'PE Ratio (TTM)': stock.info.get('forwardPE', "Not Available"),
            'EPS (TTM)': stock.info.get('trailingEps', "Not Available"),
            'Dividend Yield': stock.info.get('dividendYield', "Not Available"),
            '52 Weeks Low' : stock.info.get('fiftyTwoWeekLow', "Not Available"),
            '52 Weeks High' : stock.info.get('fiftyTwoWeekHigh', "Not Available")
        }

        #Fetching recommendation
        recommendation = stock.info.get('recommendationKey', "Not Available")
        no_of_analyst = stock.info.get('numberOfAnalystOpinions', "Not Available")
        # Returning all details
        return {
            'Symbol': symbol,
            'Company Name' : company_name,
            'Live Price': round(live_price,2),
            'Market Capitalization': str(math.ceil(market_cap/10000000)),
            'Fundamental Ratios': fundamental_ratios,
            'Expert Recommendation' : recommendation,
            'No. of Analyst Opinions' : no_of_analyst
        }
    except Exception as e:
        return {'error': str(e)}

def get_sector(symbol):
    try:
        # Create a Ticker object for the stock
        ticker = yf.Ticker(symbol + ".NS")
        
        # Get information about the stock
        stock_info = ticker.info
        
        # Extract the sector information
        sector = stock_info['sector']
        
        return sector
    except Exception as e:
        print(f"Error fetching sector information for {stock_symbol}: {e}")
        return None
    
def get_industry(symbol):
    try:
        # Create a Ticker object for the stock
        ticker = yf.Ticker(symbol + ".NS")
        
        # Get information about the stock
        stock_info = ticker.info
        
        # Extract the sector information
        sector = stock_info['industry']
        
        return sector
    except Exception as e:
        print(f"Error fetching industry information for {stock_symbol}: {e}")
        return None


# Providing Stocks Data
'''
stock_symbol = input("Enter Stock Symbol:")  
stock_details = fetch_stock_details(stock_symbol)
sector = get_sector(stock_symbol)
industry = get_industry(stock_symbol)
if 'error' in stock_details:
    print("Error:", stock_details['error'])
else:
    print("Stock Details:")
    for key, value in stock_details.items():
        print(f"{key}: {value}")
    if sector:
        print(f"The sector of {stock_symbol} is: {sector}")
    if industry:
        print(f"The industry of {stock_symbol} is: {industry}")
'''

#storing holdings details
holdings={}
#input holdings details
while True:
    holdings_list = input("Enter stock symbol:") #Stock Symbol should be an valid symbol
    quantity = int(input("Enter Stock Quantity:")) #Quantity ebtered should be integer
    avgPrice = float(input("Enter Average Price:")) #avgPrice entered should be float
    holdings[holdings_list] = {}
    holdings[holdings_list]["shares"] = quantity
    holdings[holdings_list]["avgPrice"] = avgPrice
    moreStock = input("Do you want to enter a new Stock Details:(y/n)")
    if moreStock == "n":
        break
    elif moreStock == "y":
        continue
    else:
        print("Invalid input!")
        break
        
#Profit Calculations
profit_division = {}
for keys in holdings:
    stock_symbol = keys
    stock_details = fetch_stock_details(stock_symbol)
    profit = (holdings[keys]["shares"]*float(stock_details["Live Price"] - holdings[keys]["avgPrice"]))
    profit_percentage = profit / ( holdings[keys]["shares"] * holdings[keys]["avgPrice"]) * 100
    profit_division[keys] = round(profit_percentage,2)
print("\nProfit")
for keys in holdings:
    stock_symbol = keys
    stock_details = fetch_stock_details(stock_symbol)
    print(stock_details["Company Name"] + " : " + str(profit_division[keys]) + " % ")

# Total Profit
total_profit = 0
total_invested = 0
total_current = 0
for keys in holdings:
    stock_symbol = keys
    stock_details = fetch_stock_details(stock_symbol)
    current = stock_details["Live Price"]
    total_current = total_current + current * holdings[keys]["shares"]
    invested = holdings[keys]["avgPrice"]
    total_invested = total_invested + invested * holdings[keys]["shares"]
    total_profit = total_profit + holdings[keys]["shares"]*float(current-invested)
total_profit_precentage = (total_profit / total_invested) * 100
total_profit_precentage = round(total_profit_precentage,2)
total_profit = round(total_profit,2)
print("\nTotal Profit : "+ str(total_profit) + "( " + str(total_profit_precentage) + " % )" )


# Market Cap Diverification

market_cap = {} #dictionary <stock symbol, market capitalization>
for keys in holdings:
    stock_symbol = keys
    stock_details = fetch_stock_details(stock_symbol)
    market_cap[keys] = stock_details["Market Capitalization"]

cap={} #dictionary <stock symbol, largecap/ mid cap/ small cap>
for keys in market_cap:
    if float(market_cap[keys]) >= 20000:
        cap[keys] = "Large Cap"
    elif float(market_cap[keys]) >=5000:
        cap[keys] = "Mid Cap"
    elif float(market_cap[keys]) <5000:
        cap[keys] = "Small Cap"

large = [] #large cap company list
mid = [] #mid cap company list
small = [] #small cap company list
for keys in cap:
    if cap[keys] == "Large Cap" :
        large.append(keys)
    elif cap[keys] == "Mid Cap" :
        mid.append(keys)
    elif cap[keys] == "Small Cap" :
        small.append(keys)

l=0
for i in large:
    stock_details = fetch_stock_details(i)
    current = stock_details["Live Price"] * holdings[i]["shares"]
    l = l + current

m=0
for i in mid:
    stock_details = fetch_stock_details(i)
    current = stock_details["Live Price"] * holdings[i]["shares"]
    m = m + current

s=0
for i in small:
    stock_details = fetch_stock_details(i)
    current = stock_details["Live Price"] * holdings[i]["shares"]
    s = s + current

print("\nMarket Capatilization : ")
large_cap_percentage = l/(l+m+s)*100
mid_cap_percentage = m/(l+m+s)*100
small_cap_percentage = s/(l+m+s)*100
large_cap_percentage = round(large_cap_percentage,2)
mid_cap_percentage = round(mid_cap_percentage,2)
small_cap_percentage = round(small_cap_percentage,2)
print("Large Cap : " + str(large_cap_percentage) + " % ")
print("Mid Cap : " + str(mid_cap_percentage) + " % ")
print("Small Cap : " + str(small_cap_percentage) + " % ")

# Sector Wise Categorization

sector_category = {} #dictionary <stock symbol, sector>
for keys in holdings:
    stock_symbol = keys
    sector = get_sector(stock_symbol)
    if sector:
        sector_category[keys] = sector

sector_category_diversification = {} #dictionary < sector, list of stock symbol>
for keys in sector_category:
    sector_category_diversification[sector_category[keys]] = []

for keys in sector_category:
    sector_category_diversification[sector_category[keys]].append(keys)

# Sector Wise Categorization Percentage

sector_percentage = {} #dictionary <sector, invested amount in a perticular sector>
for keys in sector_category_diversification:
    sector_percentage[keys] = 0

for keys in sector_category_diversification:
    for symbol in sector_category_diversification[keys]:
        stock_symbol = symbol
        stock_details = fetch_stock_details(stock_symbol)
        sector_percentage[keys] = sector_percentage[keys] + stock_details["Live Price"] * holdings[stock_symbol]["shares"]

print("\nSector Wise Diversification : ")
for keys in sector_percentage:
    sectorPer = round((sector_percentage[keys] / total_current)*100,2) #sector percentage
    print(keys + " : " + str(sectorPer) + " % ")


# Industry Wise Categorization

industry_category = {} #dictionary <stock symbol, industry>
for keys in holdings:
    stock_symbol = keys
    industry = get_industry(stock_symbol)
    if industry:
        industry_category[keys] = industry

industry_category_diversification = {} #dictionary < industry, list of stock symbol>
for keys in industry_category:
    industry_category_diversification[industry_category[keys]] = []

for keys in industry_category:
    industry_category_diversification[industry_category[keys]].append(keys)

# Industry Wise Categorization Percentage

industry_percentage = {} #dictionary <industry, invested amount in a perticular sector>
for keys in industry_category_diversification:
    industry_percentage[keys] = 0

for keys in industry_category_diversification:
    for symbol in industry_category_diversification[keys]:
        stock_symbol = symbol
        stock_details = fetch_stock_details(stock_symbol)
        industry_percentage[keys] = industry_percentage[keys] + stock_details["Live Price"] * holdings[stock_symbol]["shares"]

print("\nIndustry Wise Diversification : ")
for keys in industry_percentage:
    industryPer = round((industry_percentage[keys] / total_current)*100,2) #industry percentage
    print(keys + " : " + str(industryPer) + " % ")

