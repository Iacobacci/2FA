import time, rtc #Timing Libraries
import wifi, socketpool, adafruit_ntp #Wifi Libraries
import hmac, base64, struct #2FA Libraries
import adafruit_hashlib as hashlib #2FA Library
import board, digitalio, usb_hid #Keyboard Input Library
from adafruit_hid.keyboard import Keyboard #Keyboard Input Library
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS #Keyboard Input Library

#Configure the onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#Configure the HID Keyboard
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

#Configure 2FA Trigger Button
twoFactorTrigger_pin = board.GP10
twoFactorTrigger = digitalio.DigitalInOut(twoFactorTrigger_pin)
twoFactorTrigger.direction = digitalio.Direction.INPUT
twoFactorTrigger.pull = digitalio.Pull.DOWN

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
    #conversions between Python values and C structs represente
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    #Generate a hash using both of these. Hashing algorithm is HMAC
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    #unpacking
    return h

def get_totp_token(secret):
    #Gets the two factor code by generating the HOTP token with the current 30 second block
    twoFactorCode = str(get_hotp_token(secret,intervals_no=int(time.time())//30))
    
    #Adds leading zeros if the code is less than 6 digits
    while len(twoFactorCode)!=6:
        twoFactorCode = '0' + twoFactorCode
    return twoFactorCode

networkTime = 0

while True:
    led.value = not led.value
    if twoFactorTrigger.value:
        #Get all currently available networks
        for network in wifi.radio.start_scanning_networks():
            currentNetwork = network.ssid
            #Check to see if any available networks are in the "Time: <Seconds in current Epoch> formatting"
            if currentNetwork[0:5] == 'Time:' and int(currentNetwork[5:]) > int(networkTime) :
                print(currentNetwork[5:])
                networkTime = currentNetwork[5:]
            wifi.radio.stop_scanning_networks()
        #Set RTC to NTP
        rtc.RTC().datetime = time.localtime(int(networkTime))
        
        #Send the 2FA code to the connected device
        layout.write(get_totp_token(secrets["secret"]) + "\n")
    time.sleep(0.3)