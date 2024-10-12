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
            'Live Price': round(live_price,2),
            'Market Capitalization': str(math.ceil(market_cap/10000000))+" Cr ",
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
