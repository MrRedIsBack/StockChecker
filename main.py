import requests
from bs4 import BeautifulSoup
import os

URL = "https://finance.yahoo.com/quote/MBG.DE/?"
#URL = "https://finance.yahoo.com/quote/TSLA/?"
#URL = "https://finance.yahoo.com/quote/NVDA/?"
#URL = "https://uk.finance.yahoo.com/quote/UK/?"
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0"}
r = requests.get(URL, headers=header)
r.raise_for_status()
soup = BeautifulSoup(r.text, 'html.parser')

def find_substring(variable):

    variable = str(variable)

    start_index = variable.find("data-value")
    end_index = start_index+12
    for i in variable[start_index+12:]:
        if i == '"':
            break
        else:
            end_index += 1
            continue

    return variable[start_index+12:end_index]

def find_beta(variable):

    variable = str(variable)

    start_index = variable.find(">")
    end_index = start_index+1
    for i in variable[start_index+1:]:
        if i == "<":
            break
        else:
            end_index += 1
            continue

    return variable[start_index+1:end_index]

def find_value():

    points = 0
    max_points = 12

    #scrape relevant data
    stock_name = soup.select("h1.yf-xxbei9")[0].text.strip()
    price = soup.select_one('[data-testid="qsp-price"]').text
    previous_close = find_substring(soup.select('[class="value yf-dudngy"]')[0])
    open_price = find_substring(soup.select('[class="value yf-dudngy"]')[1])
    week_range_52 = find_substring(soup.select('[class="value yf-dudngy"]')[5])
    market_cap = find_substring(soup.select('[class="value yf-dudngy"]')[8]) #Convert market cap into an actual number
    beta = find_beta(soup.select('[class="value yf-dudngy"]')[9])
    EPS = find_substring(soup.select('[class="value yf-dudngy"]')[11])
    target_estimate = find_substring(soup.select('[class="value yf-dudngy"]')[15])

    #Create File
    if os.path.exists(stock_name):
        os.remove(stock_name)
    file = open(stock_name, "a")

    #Test 1
    end_index = 0
    for i in week_range_52[0:]:
        if i == "-":
            break
        else:
            end_index += 1
            continue

    bottom_range = float(week_range_52[0:end_index-1])
    top_range = float(week_range_52[end_index+1:])
    midpoint = (top_range+bottom_range)/2

    #Test 1
    try:
        if float(price) < midpoint:
            points += 1
            file.write(f"The price is less than the midpoint of the 52 week range, so +1 point. Midpoint: {midpoint}\n")
            
    except ValueError:
        max_points -= 1
        file.write("There is no stock price available.\n")

    #Test 2
    try:
        if float(beta) <= 1:
            file.write("The Beta value is less than or equal to 1 so +2 points.\n")
            points += 2
    except ValueError:
        max_points -= 2
        file.write("No Beta value available.\n")

    try:
        if float(EPS) > 2:
            points += 1
            file.write("The EPS value is more than 2 so +1 point.\n")
    except ValueError:
        max_points -= 1
        file.write("No EPS value available.\n")

    #Test 3
    try:
        if float(target_estimate) > top_range:
            points += 3
            file.write("Since the 1Y Target Estimate is larger than the the top of the 52 week range, we suspect the stock is going to grow, so +3 points.\n")
    except ValueError:
        max_points -= 3
        file.write("No 1Y Target Estimate available.\n")

    #Test 4
    try:
        if float(open_price) >= float(previous_close):
            points += 1
            file.write("Open price is greater than or equal to the previous close so there is interest in the stock, so +1 points.\n")
    except ValueError:
        max_points -= 1
        file.write("No open price and/or previous close available.\n")

    #Test 5
    try:
        market_cap = str(market_cap)

        if "T" in market_cap:
            points += 4
            file.write(f"The Market Cap is in the trillions, so +4 points, market cap: {market_cap}\n")

        elif "B" in market_cap:
            market_cap = float(market_cap[:-1])

            if market_cap >= 10:
                points += 3
                file.write(f"The market Cap is more than or equal to 10B so +3 points, market cap: {market_cap}B\n")
            else:
                file.write(f"Market Cap is less than 10B so no points. Market Cap: {market_cap}\n")
    
        else:
            file.write(f"Market Cap is less than 10B so no points. Market Cap: {market_cap}\n")

    except Exception as e:
        max_points -= 4
        file.write(f"Error with the market cap: {e}\n")

    #Final Output
    if points < (5*max_points)/8:
        file.write(f"The stock scored {points} points, which is less than 5/8 of the max points, so it is a bad stock!\n")
        file.write(f"Max Points available: {max_points}")
        file.close()

    else:
        file.write(f"The stock scored {points} points, which is more than or equal 5/8 of the max points, so it is a good stock!\n")
        file.write(f"Max Points available: {max_points}")
        file.close()

def print_info():

    stock_name = soup.select("h1.yf-xxbei9")[0].text.strip()
    price = soup.select_one('[data-testid="qsp-price"]').text
    previous_close = find_substring(soup.select('[class="value yf-dudngy"]')[0])
    change_from_previous_close = soup.select_one('[data-testid="qsp-price-change"]').text
    change_from_previous_close_percentage = soup.select_one('[data-testid="qsp-price-change-percent"]').text
    open_price = find_substring(soup.select('[class="value yf-dudngy"]')[1])
    days_range = find_substring(soup.select('[class="value yf-dudngy"]')[4])
    week_range_52 = find_substring(soup.select('[class="value yf-dudngy"]')[5])
    volume = find_substring(soup.select('[class="value yf-dudngy"]')[6])
    avg_volume = find_substring(soup.select('[class="value yf-dudngy"]')[7])
    market_cap = find_substring(soup.select('[class="value yf-dudngy"]')[8])
    beta = find_beta(soup.select('[class="value yf-dudngy"]')[9])
    pe_ratio = find_substring(soup.select('[class="value yf-dudngy"]')[10])
    EPS = find_substring(soup.select('[class="value yf-dudngy"]')[11])
    target_estimate = find_substring(soup.select('[class="value yf-dudngy"]')[15])

    try:
        print(f"Stock Name: {stock_name}")
        print(f"Current stock price: {price}")
        print(f"Previous close: {previous_close}")
        print(f"Change from previous close: {change_from_previous_close} {change_from_previous_close_percentage}") #change code to get exact value of change
        print(f"Open Price: {open_price}")
        print(f"Days Range: {days_range}")
        print(f"52 Week Range: {week_range_52}")
        print(f"Volume: {volume}")
        print(f"Average Volume: {avg_volume}")
        print(f"Market Cap (Intraday): {market_cap}")
        print(f"Beta: {beta}")
        print(f"PE Ratio (TTM): {pe_ratio}")
        print(f"EPS (TTM): {EPS}")
        print(f"1 Year Target Estimate: {target_estimate}")

    except Exception as exception:
        print(exception)

print_info()
find_value()
