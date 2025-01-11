# Temperature sensor health check. 
# Run 2x daily from crontab at 06:15 and 18:15. 


from w1thermsensor import W1ThermSensor
from IoTlib import c2f
from mail_config import config


# email libraries
import smtplib, ssl
from email.message import EmailMessage
sensor = W1ThermSensor()
tempC = sensor.get_temperature()
tempF = (tempC*9/5) + 32
# print(tempF)
temperature = "Workshop temperature: " + str(c2f(sensor.get_temperature())) 
print(temperature)


# Assign values to individual variables
port = config["port"]
smtpServer = config["smtpServer"]
senderEmail = config["senderEmail"]
receiverEmail = config["receiverEmail"]
password = config["password"]

"""
port = 465  # For SSL
smtpServer = "smtp.gmail.com"
senderEmail = "fcapria@gmail.com"  # Enter your address
receiverEmail = "6173203526@vzwpix.com"
password = "ilhjuftiftqpjufm"
"""

msg = EmailMessage()
msg.set_content(temperature)
# Do not need subject or priority if going to carriers SMS gateway
# msg['Subject'] = "Workshop Temperature Notification"
msg['From'] = senderEmail
msg['To'] = receiverEmail

'''
if tempF <= 45:
    msg['X-Priority'] = '1'  # Highest priority
else:
    msg['X-Priority'] = '5'  # Lowest priority
'''

try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpServer, port, context=context) as server:
        server.login(senderEmail, password)
        server.send_message(msg, from_addr=senderEmail, to_addrs=receiverEmail)
except:
    print('Failed to send via email.')