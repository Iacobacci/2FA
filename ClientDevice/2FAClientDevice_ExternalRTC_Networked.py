import time, rtc, adafruit_ds3231 #Timing/RTC Libraries
import wifi, socketpool, adafruit_ntp #Networking Libraries
import hmac, base64, struct, adafruit_hashlib as hashlib #2FA Libraries
import sys, board, busio, digitalio, adafruit_rgbled, usb_hid #Board and I/O definitions
from adafruit_hid.keyboard import Keyboard #Keyboard Input Library
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS #Keyboard Input Library

#RGB LED is on GPIO Pins 1, 2, 3 for RGB, respectively
RGBled = adafruit_rgbled.RGBLED(board.GP1, board.GP2, board.GP3)

# Active High 2FA trigger button is on GPIO Pin 10 (Connect Pin 10 to 3.3v to trigger)
twoFactorTrigger = digitalio.DigitalInOut(board.GP10)
twoFactorTrigger.direction = digitalio.Direction.INPUT
twoFactorTrigger.pull = digitalio.Pull.DOWN

#Configure Onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#Configure HID device Keyboard
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

#Configure External RTC. SCLK is on GPIO Pin 15, SDA is on Pin 14
i2c = busio.I2C(board.GP15, board.GP14)
externalRTC = adafruit_ds3231.DS3231(i2c)

# Get wifi and 2FA secret from secrets.py file on the pico
try:
    from secrets import secrets
except ImportError:
    print("WiFi and 2FA secrets are kept in a secrets.py on the Pico, please add them there!")
    raise

def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    #decoding our key
    msg = struct.pack(">Q", intervals_no)
    #conversions between Python values and C structs representation
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    #Generate a hash using both of these. Hashing algorithm is HMAC
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    #unpacking
    return h

def get_totp_token(secret):
    twoFactorCode = str(get_hotp_token(secret,intervals_no=int(time.time())//30))
    while len(twoFactorCode)!=6:
        twoFactorCode = '0' + twoFactorCode
    return twoFactorCode

def main():
    #Set LED to Yellow
    RGBled.color = (255, 100, 0)
    noConnection = False
    
    #Get all currently available networks
    for network in wifi.radio.start_scanning_networks():
        wifi.radio.stop_scanning_networks()

    #Connect to the primary network if it is available
    try:
        #Prints if there is an error
        print(wifi.radio.connect(secrets["primary_ssid"], secrets["primary_password"]))
    except ConnectionError:
        #Connect to the secondary network if it is available
        try:
            print(wifi.radio.connect(secrets["secondary_ssid"], secrets["secondary_password"]))
        except ConnectionError:
            noConnection = True
            #If there are no network connections available, check to see if RTC was set before April 20th, 2023
            #If not, assume it is out of date and/or has never been set
            if (time.mktime(externalRTC.datetime) < 1681948800):
                #Blink the LED red
                while(True):
                    RGBled.color = (255, 0, 0)
                    wait(3)
                    RGBled.color = (0, 0, 0)
                    wait(3)
            #If no network, but RTC has been set, turn the LED on Blue
            RGBled.color = (0, 0, 255)
    
    #If there was a connection        
    if (not noConnection):
        #Set the External RTC to the Datetime returned by the network connection
        externalRTC.datetime = adafruit_ntp.NTP(socketpool.SocketPool(wifi.radio)).datetime;
        #Turn the LED on Green
        RGBled.color = (0, 255, 0)
    
    #Set the internal clock to the external RTC. Happens regardless of if the External RTC was updated
    rtc.RTC().datetime = externalRTC.datetime
        
    led.value = True
    
    while True:
        #Write the 2FA code everytime the button triggers
        if twoFactorTrigger.value:
            layout.write(get_totp_token(secrets["secret"]) + "\n")
        time.sleep(0.2)
    
if __name__ == "__main__":
    main()