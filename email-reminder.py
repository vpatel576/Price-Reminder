import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import pandas_datareader.data as web

from datetime import datetime
from datetime import date
from datetime import time, timedelta
from ima_info import targets, tickers, ima_emails

#import alpaca_trade_api as tradeapi

sender = #Sender's email
receiver =  #Receiver's email
password = #Password
date_today = date.today()

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] =  'New Format, Who Dis || '+str(date_today.month)+ '/' + str(date_today.day) + '/' +str(date_today.year)+" || Price Alert"
msg['From'] = sender
msg['To'] = ", ".join(receiver)

# Getting all the Data
start = date.today()-timedelta(days = 4)
end = date.today()
def func(ticker, target):
    i = 0
    dict_ini = {}
    
    for i in range (len(ticker)):
        price_data = web.DataReader(ticker[i], 'yahoo', start, end)['Adj Close']
        price = round(price_data[-1],2)
        of_target = price/(target[i])
        
        dict_ini[ticker[i]]={}
        dict_ini[ticker[i]]['Price']= price
        dict_ini[ticker[i]]['Target']= target[i]
        dict_ini[ticker[i]]['Move Today'] = str(round(((price_data[-1]-price_data[-2])/price_data[-2])*100,2))+'%'
        dict_ini[ticker[i]]['% of Target']= round(of_target*100,2)

    return dict_ini

info = func(tickers, targets)

# Preparing and cleaning data
df = pd.DataFrame.from_dict(info)
df = df.transpose()

indexNames = df[(df['% of Target'] < 97)].index
df.drop(indexNames , inplace=True)

for i in range(len(df)):
    df.replace(df['% of Target'][i],str(df['% of Target'][i])+'%',inplace = True)
    df.replace(df['Price'][i],'$'+str(df['Price'][i]),inplace = True)
    df.replace(df['Target'][i],'$'+str(df['Target'][i]),inplace = True)

html = df.to_html()

def email_send():
    if len(df) >= 0:
        p1 = MIMEText(html, 'html')

        msg.attach(p1)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender,password)

        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

#Only sends email on the weekdays
day = date_today.isoweekday()
if day != 7 and day != 6:
    email_send()
