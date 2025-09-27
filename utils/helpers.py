import datetime
import random
import os

#Currency Formatting
def format_currency(amount):
    f_amount = f"${amount}"
    return f_amount

#Date Formatting
def format_date(d):
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    f_date = d[8:10]+" "+months[int(d[5:7])-1]+" "+d[0:4]
    return f_date

#Current date in SQL Format
def today():
    today=datetime.date.today().strftime("%Y-%m-%d")
    return today

def add_days(date_str, n):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    new_date = date_obj + datetime.timedelta(days=n)
    return new_date.strftime("%Y-%m-%d")

#Random Stock Price
def random_stock_price(base_price, volatility=0.05):
    change_percent = random.uniform(-volatility, volatility)
    new_price = base_price * (1 + change_percent)
    return round(new_price, 2)

#Clears Cache
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

#Separator
def separator(length=40):
    print("=" * length)

