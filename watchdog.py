"""
Excerpt from Rasberry Pi 3 Datasheet
The voltage and frequency are throttled back when the CPU load reduces back to an ’idle’ level OR when the silicon
temperature as mesured by the on-chip temperature sensor exceeds 85C (thermal throttling).

Checks system temperature and alerts via email if the value is nearing the 85C.
"""

import subprocess
import smtplib
import os
import logging
from email.message import EmailMessage

def email_notify(send_from, send_to, passw, subject, html):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = send_from
    msg['To'] = send_to
    msg.set_content(html)
    msg.add_alternative(html, subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        #auth with app password associated with gmail account
        smtp.login(send_from, passw)
        #send email
        smtp.send_message(msg)


def celcius_to_fahrenheit(temp):
    return ((temp * 9) / 5 ) + 32

#returns string in format "temp=63.4'C\n"
def measure_temp():
   return subprocess.check_output("vcgencmd measure_temp", shell=True).decode('utf-8')

#extracts numeric value from temp string and converts to float
def extract_val(st):
    return float(st[5:-3])

#in celcius
def above_ceiling(temp):
    if temp >= 60:
        return True
    else:
        return False

def thermal_warning_str(temp_celcius, temp_fahrenheight):
    return "THERMAL WARNING: Pi-Hole is currently {}C/{}F.".format(temp_celcius,temp_fahrenheight)

def thermal_pass_str(temp_celcius, temp_fahrenheight):
    return "Pi-Hole is currently {}C/{}F.".format(temp_celcius,temp_fahrenheight)

if __name__ == '__main__':
    temp_celcius = extract_val(measure_temp())
    temp_fahrenheight = celcius_to_fahrenheit(temp_celcius)
    #print("Pi-Hole is currently {}F".format(temp_fahrenheight))
    if above_ceiling(temp_celcius):
        html = "<!DOCTYPE html><html><head></head><body><p>Rebooting system now.</p></body></html>"
        thermal_warn = thermal_warning_str(temp_celcius, temp_fahrenheight)
        email_notify(os.environ['SMTP_FROM'], os.environ['SMTP_TO'], os.environ['SMTP_PASS'], thermal_warn, html)
        os.system('sudo systemctl reboot -i')
    else:
       # html = "<!DOCTYPE html><html><head></head><body><p>This temp is below the 85C thermal ceiling.</p><i> Edit /home/pi/watchdog/watchdog.py to alert only if the temp rises above a certain value.</i></body></html>".format(temp_celcius,temp_fahrenheight)
        #thermal_pass = thermal_pass_str(temp_celcius, temp_fahrenheight)
        #email_notify("nicktestnotify@gmail.com", "nick.rabbott@gmail.com", thermal_pass, html)
        pass
