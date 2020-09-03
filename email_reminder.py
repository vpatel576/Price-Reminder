import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import pandas_datareader.data as web

from datetime import datetime
from datetime import date
from datetime import time, timedelta
from ima_info import ima_emails, info_dict

sender = ##
receiver =  #ima_emails
password = ##
date_today = date.today()

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] =  str(date_today.month)+ '/' + str(date_today.day) + '/' +str(date_today.year)+" || Price Alert"
msg['From'] = sender
msg['To'] = ", ".join(receiver)

# Getting all the Data
start = date.today()-timedelta(days = 4)
end = date.today()

def func(dict_info):
    ticker = list(dict_info.keys())
    
    for i in range(len(dict_info)):
        
        price_data = web.DataReader(ticker[i], 'yahoo', start, end)['Adj Close']
        curr_price = round(price_data[-1],2)
        of_target = curr_price/(dict_info[ticker[i]]['Target'])
        
        dict_info[ticker[i]]['Price']= curr_price
        dict_info[ticker[i]]['Move Today'] = round(((price_data[-1]-price_data[-2])/price_data[-2])*100,2)
        dict_info[ticker[i]]['% of Target']= round(of_target*100,2)

    return dict_info

info = func(info_dict)

# Preparing and cleaning data
df = pd.DataFrame.from_dict(info)
df = df.transpose()

df = df[(df['% of Target'] > 97)]

for i in range(len(df)):
    df.replace(df['% of Target'][i],str(df['% of Target'][i])+'%',inplace = True)
    df.replace(df['Move Today'][i],str(df['Move Today'][i])+'%',inplace = True)
    df.replace(df['Price'][i],'$'+str(df['Price'][i]),inplace = True)
    df.replace(df['Target'][i],'$'+str(df['Target'][i]),inplace = True)

html = df.to_html()

#Sending the emmail

def email_send():
    if len(df) >= 0:
        p1 = MIMEText(html, 'html')

        msg.attach(p1)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender,password)

        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

##Only sends email on the weekdays
day = date_today.isoweekday()
if day != 7 and day != 6:
    email_send()
