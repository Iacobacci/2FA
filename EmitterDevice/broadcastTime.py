try:
 import usocket as socket      
except:
 import socket
import network
import machine
import time
from machine import Pin, PWM
from configureTime import set_time

password = '12345678'	#Set your access point password arbitrarily
set_time() #Run the configure time program to get the time from the display

while True:

    now = time.time() + 14400 #Adding 14400 seconds to account for the 4 hour time difference between EDT and UTC

    #Network credentials
    ssid = ("Time:" + str(now))	#Set access point name to the time in seconds in the current epoch

    #Soft access point generator
    ap = network.WLAN(network.AP_IF) #Broadcast the Wifi Network
    ap.config(essid=ssid, password=password)
    ap.active(True) #Activate the network
    time.sleep(30)
    ap.active(False) #Deactivate the netwrok after 30 seconds
