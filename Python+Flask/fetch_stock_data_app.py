from flask import Flask, render_template, request
import yfinance as yf
import datetime as dt
import math

#global stock_symbol

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
        #print(f"Error fetching sector information for {stock_symbol}: {e}")
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
        #print(f"Error fetching industry information for {stock_symbol}: {e}")
        return None


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    #stock_symbol = input("Enter Stock Symbol:") 

    if request.method == 'POST':
        # Check if the 'stock_symbol' field exists in the form data
        if 'stock_symbol' in request.form:
            stock_symbol = request.form['stock_symbol']
            # Process the input (e.g., print it)
            
            stock_details = fetch_stock_details(stock_symbol)
            sector = get_sector(stock_symbol)
            industry = get_industry(stock_symbol)
            if 'error' in stock_details:
                print("Error:", stock_details['error'])
            else:

                _symbol = stock_details['Symbol']
                live_price = stock_details['Live Price']
                market_cap = stock_details['Market Capitalization']
                PE = stock_details['Fundamental Ratios']['PE Ratio (TTM)']
                EPS = stock_details['Fundamental Ratios']['EPS (TTM)']
                Dividend_Yield = stock_details['Fundamental Ratios']['Dividend Yield']
                _52_Weeks_Low = stock_details['Fundamental Ratios']['52 Weeks Low']
                _52_Weeks_High = stock_details['Fundamental Ratios']['52 Weeks High']
                Expert_Recommendation = stock_details['Expert Recommendation']
                No_of_Analyst_Opinions = stock_details['No. of Analyst Opinions']
                
                if sector:
                    #print(f"The sector of {stock_symbol} is: {sector}")
                    _sector=sector
                if industry:
                    #print(f"The industry of {stock_symbol} is: {industry}")
                    _industry=industry

            # Render the template with the stock details
            return render_template('stock_data_index.html', _symbol=_symbol, live_price=live_price, market_cap=market_cap, PE=PE, EPS=EPS, 
            Dividend_Yield=Dividend_Yield, _52_Weeks_Low=_52_Weeks_Low, _52_Weeks_High=_52_Weeks_High, Expert_Recommendation=Expert_Recommendation,
            No_of_Analyst_Opinions=No_of_Analyst_Opinions, _sector=_sector , _industry=_industry)

            
        else:
            return "Error: Stock symbol not provided"
    else:
        return render_template('stock_data_index.html')

    

if __name__ == '__main__':
    app.run(debug=True)
