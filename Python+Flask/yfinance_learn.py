import yfinance as yf
stock = yf.Ticker("HDFCGOLD" + ".NS")
stock_info=stock.info
for keys in stock_info:
    print(str(keys) +" : "+str(stock_info[keys]))
#print(type(stock_info))