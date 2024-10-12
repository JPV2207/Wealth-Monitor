holdings={}
#input holdings details
while True:
    holdings_list=input("Enter stock symbol:")
    quantity=int(input("Enter Stock Quantity:"))
    avgPrice=float(input("Enter Average Price:"))
    holdings[holdings_list]={}
    holdings[holdings_list]["shares"]=quantity
    holdings[holdings_list]["avgPrice"]=avgPrice
    moreStock=input("Do you want to enter a new Stock Details:(y/n)")
    if moreStock=="n":
        break
    elif moreStock=="y":
        continue
    else:
        print("Invalid input!")
        break
print(holdings)