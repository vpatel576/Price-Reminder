import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import pandas_datareader.data as web

from datetime import datetime
from datetime import date
from datetime import time, timedelta

# me == my email address
# you == recipient's email address
sender = #Sender's Email
receiver =  #Receiver's email
date_today = date.today()


# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] =  str(date_today.month)+ '/' + str(date_today.day) + '/' +str(date_today.year)+" || Price Alert"
msg['From'] = sender
msg['To'] = ", ".join(receiver)

tickers = #list of tickers
target = #list of target prices

start = date.today()-timedelta(days = 2)
end = date.today()

def func(ticker, target):
    i = 0
    dict_ini = {}
    
    for i in range (len(ticker)):
        price_data = web.DataReader(ticker[i], 'yahoo', start, end)['Adj Close']
        price = round(price_data[-1],2)
        from_target = (target[i]-price)/price
        
        dict_ini[ticker[i]]={}
        dict_ini[ticker[i]]['Price']= price
        dict_ini[ticker[i]]['Target']= target[i]
        dict_ini[ticker[i]]['Move Today'] = str(round(((price_data[-1]-price_data[-2])/price_data[-2])*100,2))+'%'
        dict_ini[ticker[i]]['% From Target']= round(from_target*100,2)

    return dict_ini

info = func(tickers, targets)

df = pd.DataFrame.from_dict(info)
df = df.transpose()

indexNames = df[(df['% From Target'] > 3)].index
df.drop(indexNames , inplace=True)

for i in range(len(df)):
    if df['% From Target'][i]<=0:
        df.replace(df['% From Target'][i],'Target Hit',inplace = True)

html = df.to_html()

if len(df) >= 0:
    p2 = MIMEText(html, 'html')

    msg.attach(p2)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender,'IMAQuantOps3$')

    server.sendmail(sender, receiver, msg.as_string())
    server.quit()