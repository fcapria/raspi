#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# A script theat reads temperature from a DS18B20 sensor
# and writes the the result to a Google Sheet.
# It is run every 30 minutes from crontab.

import gspread
from os import path
from datetime import datetime
from w1thermsensor import W1ThermSensor
from oauth2client.service_account import ServiceAccountCredentials
from IoTlib import c2f

# For sending an sms from gmail
import smtplib, ssl
from email.message import EmailMessage

# Path definitions are necessary if script is stored in /bin
# as an executable file. Otherwise, ignore.
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

#read the temperature from the sensor
sensor = W1ThermSensor()
tempC = sensor.get_temperature()
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

# JSON file format  
# The Google Sheet must be shared with your_handle@project_ID.iam.gserviceaccount.com
"""
{
  "type": "service_account",
  "project_id": "your_project_ID",
  "private_key_id": "your_Key_ID ",
  "private_key": "you_full_project_key",
  "client_email": "your_handle@project_ID.iam.gserviceaccount.com",
  "client_id": "your_client_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your_handle%40your_project_ID.iam.gserviceaccount.com"
}
"""

 # use credentials to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
try:
    wb = client.open('wx04849')  #workbook
    ws = wb.worksheet('Sheet5')  #worksheet
except gspread.exceptions.APIError as ex:
    print ("Google sheet error")
    print(ex)

# Read desired scale
row = 1
col = 2
scale = ws.cell(row,col).value

if scale == 'F':
    temperature = c2f(tempC)
elif scale == 'K':
    temperature = round(tempC + 273,1)
else:
    temperature = round(tempC,1)

# Add the degree symbol
entry = str(temperature)

# Write the temperature and timestamp
col = 1
ws.update_cell(row,col,entry)
stamp = str(datetime.now())
col = 3
ws.update_cell(row,col,stamp)

# Send Twilio warning is not within range"
# And note that a warning was sent"
if tempC <= 7.2:
    port = 465  # For SSL
    smtpServer = "smtp.gmail.com"
    senderEmail = "fcapria@gmail.com"  # Enter your address
    # Sending to this address sends emai to Google Voice generating a SMS."
    receiverEmail = "6173203526@vzwpix.com"  # Enter receiver address
    password = "ilhjuftiftqpjufm"
    warningMsg = "Studio temperature out of range: " + temperature

    msg = EmailMessage()
    msg.set_content(warningMsg)
    msg['Subject'] = "Workshop Temperature Notification"
    msg['From'] = senderEmail
    msg['To'] = receiverEmail

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpServer, port, context=context) as server:
        server.login(senderEmail, password)
        server.send_message(msg, from_addr=senderEmail, to_addrs=receiverEmail)
        ws.update_cell(row,col,'Warning sent')
else:
    row = 2
    col = 1
    ws.update_cell(row,col,' ')
    