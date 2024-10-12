from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import math
from flask_cors import CORS
import csv
from flask_mail import Mail
from dotenv import load_dotenv
import os
#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
#from cryptography.hazmat.backends import default_backend

# Load environment variables from the .env file
load_dotenv()

def is_valid_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")  # Append ".NS" for Indian stock market
        info = ticker.info
        if info['country'] == 'India':
            return True
        else:
            return False
    except:
        return False

def is_unique(symbol, username):
    details = Holdings.query.all()
    for stock_symbol in details:
        if stock_symbol.holding_list == symbol and stock_symbol.userid == username:
            return False
    return True

def fetch_stock_details(symbol):
    try:
        # Fetching stock data
        stock = yf.Ticker(symbol + ".NS")  # Appending ".NS" for NSE stocks
        #stock = yf.Ticker(symbol + ".BO")  # Appending ".BO" for BSE stocks
        
        # Fetching company name
        company_name = stock.info.get('longName', "Not Available")

        # Fetching live price
        live_price = stock.info.get('currentPrice', "Not Available")

        # Fetching previous close price
        previous_close = stock.info.get('previousClose', "Not Available")
        
        # Fetching market capitalization
        market_cap = stock.info.get('marketCap', "Not Available")
        
        # Fetching fundamental ratios
        '''fundamental_ratios = {
            'PE Ratio (TTM)': stock.info.get('forwardPE', "Not Available"),
            'EPS (TTM)': stock.info.get('trailingEps', "Not Available"),
            'Dividend Yield': stock.info.get('dividendYield', "Not Available"),
            '52 Weeks Low' : stock.info.get('fiftyTwoWeekLow', "Not Available"),
            '52 Weeks High' : stock.info.get('fiftyTwoWeekHigh', "Not Available")
        }

        #Fetching recommendation
        recommendation = stock.info.get('recommendationKey', "Not Available")
        no_of_analyst = stock.info.get('numberOfAnalystOpinions', "Not Available")
        '''
        # Returning all details
        return {
            'Symbol': symbol,
            'Company Name' : company_name,
            'Live Price': round(live_price,2),
            'Previous Close' : round(previous_close,2),
            'Market Capitalization': str(math.ceil(market_cap/10000000)),
            #'Fundamental Ratios': fundamental_ratios,
            #'Expert Recommendation' : recommendation,
            #'No. of Analyst Opinions' : no_of_analyst
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
        print(f"Error fetching sector information for {symbol}: {e}")
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
        print(f"Error fetching industry information for {symbol}: {e}")
        return None

def get_stock_symbols_from_csv(csv_file):
    stock_symbols = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the stock symbols are in the first column of the CSV file
            stock_symbols.append(row[0])
    return stock_symbols


# Example SMTP settings for Gmail
# EMAIL_HOST = ''
# EMAIL_PORT = 587
# EMAIL_USERNAME = ''
# EMAIL_PASSWORD = ''

'''
# Encryption Key
key = b'mysupersecretkeysecret9981133601'
# Initialize the AES cipher with ECB mode
backend = default_backend()
cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
'''

# Creating Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app) 
app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST')
app.config['MAIL_PORT'] = int(os.getenv('EMAIL_PORT', 587))  # Default port for SMTP is 587
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


# Define a custom filter function for sorting numbers
def custom_sort_numbers(lst):
    return sorted(lst, key=lambda x: float(x[1]))

# Add the custom filter to the Jinja2 environment
app.jinja_env.filters['custom_sort_numbers'] = custom_sort_numbers


# Creating SQLAlchemy instance
db = SQLAlchemy()

user = os.getenv('DB_USER')
pin = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Configuring database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{pin}@{host}/{db_name}?charset=utf8"
 
# Disable modification tracking
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing Flask app with SQLAlchemy
db.init_app(app)

# Creating Report
class Report():
    def __init__(self):
        self._1dreturn = ""
        self.total_profit = ""
        self. profit = {}
        self.sector = {}
        self.industry = {}
        self.company_size = {}
        self.large_cap = ""
        self.mid_cap = ""
        self.small_cap = ""
        self.count = 0
        self.current = ""
        self.invested = ""
        
# Creating Portfolio
class Portfolio():
    def __init__(self):
        self. _1dreturn = ""
        self.total_profit = ""
        self. profit = {}
        self._1dprofit = {}
        self._1dcurrent = {}
        self.count = 0
        self.current = ""
        self.invested = ""

def create_db():
    with app.app_context():
        db.create_all()


class Holdings(db.Model):
    __tablename__ = 'Holdings'
    sr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(256), primary_key=True)
    holding_list = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    avgPrice = db.Column(db.Float, nullable=False)


username = None
encrypted_username = "default"
decrypted_username = None
@app.route('/receive_email', methods=['POST'])
def receive_email():
    try:
        email_data = request.get_json()
        email = email_data.get('email')
        global username, encrypted_username, decrypted_username
        username = email
        
        encrypted_username = username
        '''
        encryptor = cipher.encryptor()
        padded_username = username.ljust(32)  # Pad username to 32 bytes (AES block size)
        encrypted_username = str(encryptor.update(padded_username.encode()) + encryptor.finalize())
        '''
        '''
        decryptor = cipher.decryptor()
        decrypted_username = decryptor.update(encrypted_username) + decryptor.finalize()
        decrypted_username = str(decrypted_username.decode().rstrip())  # Remove padding and decode to string
        '''
        return jsonify({"message": "Email received successfully"}), 200
    except Exception as e:
        encrypted_username = "default"
        return jsonify({"error": str(e)}), 500
        

# Home route
@app.route("/", methods=['GET', 'POST'])
def home():
    details = Holdings.query.filter_by(userid=encrypted_username).all()
    return render_template("home.html", details=details)
 

# Add data route
@app.route("/add", methods=['GET', 'POST'])
def add_holdings():
    if request.method == 'POST':
        
        holding_list = request.form.get('holding_list')
        quantity = request.form.get('quantity')
        avgPrice = request.form.get('avgPrice')

        holding_list = holding_list.upper()
        if is_valid_symbol(holding_list):
            if is_unique(holding_list, encrypted_username):
                add_detail = Holdings(
                    userid=encrypted_username,
                    holding_list = holding_list,
                    quantity = quantity,
                    avgPrice = avgPrice
                )
                db.session.add(add_detail)
                db.session.commit()
            else:
                flash("Duplicate Stock Symbol!")
        else:
            flash("Entered Stock Symbol is not valid!")

        return redirect(url_for('add_holdings'))
    details = Holdings.query.filter_by(userid=encrypted_username).all()
    return render_template("holdings.html", details=details)

# Delete data route
@app.route("/delete/<int:sr>")
def delete(sr):
    #username = getattr(g, 'email', None)
    delete_data = Holdings.query.filter_by(sr=sr, userid=encrypted_username).first()
    db.session.delete(delete_data)
    db.session.commit()
    return redirect(url_for('add_holdings'))

# Analysis
@app.route("/analysis", methods=['GET', 'POST'])
def analysis():
        
    my_report = Report()
    global my_cap
    my_cap = {}    
    #storing holdings details
    holdings = {}
    #input holdings details

    with app.app_context():
        details = Holdings.query.all()
        for data in details:
            holdings_list = data.holding_list #Stock Symbol should be an valid symbol
            quantity = data.quantity #Quantity ebtered should be integer
            avgPrice = data.avgPrice #avgPrice entered should be float
            holdings[holdings_list] = {}
            holdings[holdings_list]["shares"] = quantity
            holdings[holdings_list]["avgPrice"] = avgPrice

    #Profit Calculations
    profit_division = {}
    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        profit = (holdings[keys]["shares"]*float(stock_details["Live Price"] - holdings[keys]["avgPrice"]))
        profit_percentage = profit / ( holdings[keys]["shares"] * holdings[keys]["avgPrice"]) * 100
        profit_division[keys] = round(profit_percentage,2)

    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
    #print(stock_details["Company Name"] + " : " + str(profit_division[keys]) + " % ")
        my_report.count = my_report.count + 1
        my_report.profit[str(stock_details["Company Name"])] = str(profit_division[keys]) + " % "

    # Total Profit
    total_profit = 0
    total_invested = 0
    total_current = 0
    total_1dreturn = 0
    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        previous_close = stock_details["Previous Close"]
        current = stock_details["Live Price"]
        total_current = total_current + current * holdings[keys]["shares"]
        invested = holdings[keys]["avgPrice"]
        total_invested = total_invested + invested * holdings[keys]["shares"]
        total_profit = total_profit + holdings[keys]["shares"]*float(current-invested)
        total_1dreturn = total_1dreturn + holdings[keys]["shares"]*float(current-previous_close)
    total_profit_precentage = (total_profit / total_invested) * 100
    total_profit_precentage = round(total_profit_precentage,2)
    total_profit = round(total_profit,2)
    total_1dreturn_percentage = (total_1dreturn / total_current) * 100
    total_1dreturn_percentage = round(total_1dreturn_percentage,2)
    total_1dreturn = round(total_1dreturn,2)
    my_report._1dreturn = "₹" + str(total_1dreturn) + "(" + str(total_1dreturn_percentage) +"% )"
    my_report.total_profit = "₹" + str(total_profit) + "( " + str(total_profit_precentage) + " % )"
    my_report.current = "₹" + str(round(total_current,2))
    my_report.invested = "₹" + str(round(total_invested,2))
    
    # Market Cap Diverification

    market_cap = {} #dictionary <stock symbol, market capitalization>
    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        market_cap[keys] = stock_details["Market Capitalization"]

    cap={} #dictionary <stock symbol, largecap/ mid cap/ small cap>
    for keys in market_cap:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        if float(market_cap[keys]) >= 20000:
            cap[keys] = "Large Cap"
            my_report.company_size[str(stock_details["Company Name"])] = "LargeCap"
        elif float(market_cap[keys]) >=5000:
            cap[keys] = "Mid Cap"
            my_report.company_size[str(stock_details["Company Name"])] = "MidCap"
        elif float(market_cap[keys]) <5000:
            cap[keys] = "Small Cap"
            my_report.company_size[str(stock_details["Company Name"])] = "SmallCap"

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

    #print("\nMarket Capatilization : ")
    large_cap_percentage = l/(l+m+s)*100
    mid_cap_percentage = m/(l+m+s)*100
    small_cap_percentage = s/(l+m+s)*100
    large_cap_percentage = round(large_cap_percentage,2)
    mid_cap_percentage = round(mid_cap_percentage,2)
    small_cap_percentage = round(small_cap_percentage,2)
    my_cap["large_cap"] = large_cap_percentage
    my_cap["mid_cap"] = mid_cap_percentage
    my_cap["small_cap"] = small_cap_percentage
    my_report.large_cap = str(large_cap_percentage) + " % " 
    my_report.mid_cap = str(mid_cap_percentage) + " % " 
    my_report.small_cap = str(small_cap_percentage) + " % " 


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

    #print("\nSector Wise Diversification : ")
    for keys in sector_percentage:
        sectorPer = round((sector_percentage[keys] / total_current)*100,2) #sector percentage
        #print(keys + " : " + str(sectorPer) + " % ")
        my_report.sector[keys] = sectorPer


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

    #print("\nIndustry Wise Diversification : ")
    for keys in industry_percentage:
        industryPer = round((industry_percentage[keys] / total_current)*100,2) #industry percentage
        #print(keys + " : " + str(industryPer) + " % ")
        my_report.industry[keys] = industryPer



    report = my_report
    
    return render_template("analysis.html", report = report)

# Market Cap route
@app.route("/market_cap_data", methods=['GET', 'POST'])
def capitalization():
    return jsonify(my_cap)

# Portfolio route 
@app.route("/portfolio", methods=['GET', 'POST'])
def portfolio():
    return render_template("portfolio.html")


@app.route("/portfolio_data", methods=['GET', 'POST'])
def portfolio_data():

    my_portfolio = Portfolio()

    #storing holdings details
    holdings = {}

    with app.app_context():
        details = Holdings.query.filter_by(userid=encrypted_username).all()
        for data in details:
            holdings_list = data.holding_list #Stock Symbol should be an valid symbol
            quantity = data.quantity #Quantity ebtered should be integer
            avgPrice = data.avgPrice #avgPrice entered should be float
            holdings[holdings_list] = {}
            holdings[holdings_list]["shares"] = quantity
            holdings[holdings_list]["avgPrice"] = avgPrice

    #Profit Calculations
    profit_division = {}
    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        profit = (holdings[keys]["shares"]*float(stock_details["Live Price"] - holdings[keys]["avgPrice"]))
        profit_percentage = profit / ( holdings[keys]["shares"] * holdings[keys]["avgPrice"]) * 100
        profit_division[keys] = round(profit_percentage,2)

    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
    #print(stock_details["Company Name"] + " : " + str(profit_division[keys]) + " % ")
        my_portfolio.count = my_portfolio.count + 1
        my_portfolio.profit[str(stock_details["Company Name"])] = str(profit_division[keys]) + " % "

    # Total Profit
    total_profit = 0
    total_invested = 0
    total_current = 0
    total_1dreturn = 0
    for keys in holdings:
        stock_symbol = keys
        stock_details = fetch_stock_details(stock_symbol)
        previous_close = stock_details["Previous Close"]
        current = stock_details["Live Price"]
        total_current = total_current + current * holdings[keys]["shares"]
        invested = holdings[keys]["avgPrice"]
        total_invested = total_invested + invested * holdings[keys]["shares"]
        total_profit = total_profit + holdings[keys]["shares"]*float(current-invested)
        total_1dreturn = total_1dreturn + holdings[keys]["shares"]*float(current-previous_close)

        _1dreturn = round((current-previous_close)/previous_close*100,2)
        my_portfolio._1dprofit[str(stock_details["Company Name"])] = "₹" + str(round(current - previous_close, 2)) + "( " + str(_1dreturn) + " %)"

        my_portfolio._1dcurrent[str(stock_details["Company Name"])] = "₹" + str(current)

    total_profit_precentage = (total_profit / total_invested) * 100
    total_profit_precentage = round(total_profit_precentage,2)
    total_profit = round(total_profit,2)
    total_1dreturn_percentage = (total_1dreturn / total_invested) * 100
    total_1dreturn_percentage = round(total_1dreturn_percentage,2)
    total_1dreturn = round(total_1dreturn,2)
    my_portfolio._1dreturn = str(total_1dreturn) + "(" + str(total_1dreturn_percentage) +"% )"
    my_portfolio.total_profit = str(total_profit) + "( " + str(total_profit_precentage) + " % )"
    my_portfolio.current = str(round(total_current,2))
    my_portfolio.invested = str(round(total_invested,2))


    portfolio_dict = {
        'total_profit': my_portfolio.total_profit,
        '_1dreturn': my_portfolio._1dreturn,
        'current': my_portfolio.current,
        'invested': my_portfolio.invested,
        'profit': my_portfolio.profit,
        '_1dprofit' : my_portfolio._1dprofit,
        '_1dcurrent' : my_portfolio._1dcurrent
    }


    return jsonify(portfolio_dict)

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '')

    # Load stock symbols from CSV file
    csv_file = 'list_of_symbols.csv'
    stock_symbols = get_stock_symbols_from_csv(csv_file)

    # Filter stock symbols based on query
    suggestions = [symbol for symbol in stock_symbols if query.lower() in symbol.lower()]

    return jsonify({'suggestions': suggestions})

if __name__ == "__main__":
    create_db()

    app.run(debug=True)
    