# 2FA Pico

This project was designed as a way to simplify the user interface/experience for low-security applications of two-factor authentication. This project uses one (or more) Raspberry Pi Pico W('s) due to their relatively low cost and wifi capabilities.

This system consists of one Raspberry Pi Pico W as a Client Device and may include one or more Pico W's as Emitter Devices.

---

## Client Devices

All of the client devices use USB HID to output the 6-digit 2FA code to the connected computer. This setup does not require any configuration on the destination computer, and is therefore platform agnostic. This setup does not work for mobile device applications, so it is recommended that any secrets used with this device to generate the codes are also added to a 2FA generation app, such as Microsoft Authy, Google Authenticator, or another similar platform.

## Internal RTC (Real Time Clock) Only

The Client device is a Raspberry Pi Pico running CircuitPython that takes the current time, converts it to a 2FA code, and sends it to a connected USB device via USB_HID. This time could be fetched either from a connected network (via NTP), or from the broadcast of the Emitter Device. This device is only capable of exporting one 2FA token -- selecting being multiple 2FA tokens is not supported to minimize security risks if this device is compromised.

### Hardware

The client device requires a button between GPIO 10 (Pin 14) on the Raspberry Pi Pico W and 3.3v (Pin 36) to trigger the write of the 2FA token to the connected computer. [A Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

### Software

The client device needs to be formatted by first entering bootloader mode (holding the bootsel button while plugging the pico into your computer), before uploading the most recent [Circuit Python Binaries](https://circuitpython.org/board/raspberry_pi_pico/) to the device. Once installed, the device will disconnect and remount as "CIRCUITPY." This device uses CircuitPython due to MicroPython not supporting USB_HID at the time of this project being completed. Adafruit Blinka and Platform Detect *should* be able to be used as a compatibility layer between CircuitPython and MicroPythion allowing the USB_HID libraries to function properly, however, upon testing it caused significant syntax errors and appears to not yet be fully supported.

Now the appropriate libraries could be installed on the device:

- [Adafruit HashLib Library](https://github.com/adafruit/Adafruit_CircuitPython_hashlib): Required for key generation
- [Base 64 Library](https://github.com/python/cpython/blob/3.11/Lib/base64.py): Required for key generation
- [HMAC Library](https://github.com/micropython/micropython-lib/blob/master/python-stdlib/hmac/hmac.py): Required for key generation
- [USB_HID Library](https://github.com/adafruit/Adafruit_CircuitPython_HID): Required to send 2FA as a keyboard input
- [Adafruit NTP](https://github.com/adafruit/Adafruit_CircuitPython_NTP): (Optional) Required for syncing time with wifi

A secrets.py file (see example) must be on the device and contain the secret used for 2FA generation, and one or more sets of SSID/password combinations to allow for Wifi Connectivity.

### Time Synchronization Methods

- [Get Time from Network Time Protocol (NTP)](ClientDevice/2FAClientDevice_InternalRTCOnly_Networked.py): This method of time syncronization connects the client device to a wifi network (home, office, mobile hotspot, etc) and fetches the time from the NTP server -- requires network connectivity.
  - If using with a mobile hotspot, ensure the hotspot is enabled prior to powering the device or it will fail to connect.
  - The onboard LED will blink green slowly (every 0.3 seconds) once the client device successfully connected to a wifi network and synchronized the time.
  - The onboard LED will blink green rapidly (every 0.1 seconds) if the device is not connected to any wifi network
  - [NTP background](https://en.wikipedia.org/wiki/Network_Time_Protocol)

- [Get Time from Emitter Device](ClientDevice/2FAClientDevice_InternalRTCOnly_NotNetworked.py): This method of synchronization takes a wifi broadcast of the current UTC time as seconds in the current Epoch (Time: "XXXXXXXXX"), removes the "Time:" pre-fix, and converts the remaining wifi name to an integer to use for 2FA generation. **This requires an Emitter Pico that has been configured with the current time to be in range**
  - As multiple wifi signals may be present at the same, the device keeps the greatest number of seconds of any of the broadcasts.
  - The client device will check for a wifi network on each button press, to ensure the time is within the current 30 second interval

- EXPERIMENTAL: [Get Time from local file](ClientDevice/2FAClientDevice_InternalRTCOnly_CreateFileWithTime.py): This program is configured to run on macOS and will automatically open a Terminal File, navigate to the Pico directory, and make a file with the time. The idea was to then sync time with the time located in the file on the device, or the modification time of the file. **This does not currently work due to issues in the Pico recongizing files created after the program ran.**

Either of these programs will need to be renamed to "main.py" on the device to have it automatically run on device connection.

## External RTC (Real Time Clock)

The Client device is a Raspberry Pi Pico running CircuitPython that takes the current time, converts it to a 2FA code, and sends it to a connected USB device via USB_HID. This time is fetched from a connected network (via NTP) and is stored on an external real time clock which updates the onboard clock at each button press. This device is only capable of exporting one 2FA token -- selecting being multiple 2FA tokens is not supported to minimize security risks if this device is compromised.

### Hardware

- The client device will need:
  - [A Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
  - A button between GP10 (Pin 14) on the Raspberry Pi Pico W and 3.3v (Pin 36) to trigger the write of the 2FA token to the connected computer.
  - An [DS3231 external RTC](https://www.amazon.com/DS3231-AT24C32-Module-Memory-Replace/dp/B09LLMYBM1/ref=cm_cr_arp_d_product_top?ie=UTF8) connected with SCLK is on GP15, SDA is on GP14, GND (Pin 3), and 3.3v (Pin 36)
  - An RGB LED with 100 ohn resistors between each of the R (GP1), G (GP2), and B pins (GP3).

### Software

The client device needs to be formatted by first entering bootloader mode (holding the bootsel button while plugging the pico into your computer), before uploading the most recent [Circuit Python Binaries](https://circuitpython.org/board/raspberry_pi_pico/) to the device. Once installed, the device will disconnect and remount as "CIRCUITPY." This device uses CircuitPython due to MicroPython not supporting USB_HID at the time of this project being completed. Adafruit Blinka and Platform Detect *should* be able to be used as a compatibility layer between CircuitPython and MicroPythion allowing the USB_HID libraries to function properly, however, upon testing it caused significant syntax errors and appears to not yet be fully supported.

Now the appropriate libraries could be installed on the device:

- [Adafruit HashLib Library](https://github.com/adafruit/Adafruit_CircuitPython_hashlib): Required for key generation
- [Base 64 Library](https://github.com/python/cpython/blob/3.11/Lib/base64.py): Required for key generation
- [HMAC Library](https://github.com/micropython/micropython-lib/blob/master/python-stdlib/hmac/hmac.py): Required for key generation
- [USB_HID Library](https://github.com/adafruit/Adafruit_CircuitPython_HID): Required to send 2FA as a keyboard input
- [Adafruit NTP](https://github.com/adafruit/Adafruit_CircuitPython_NTP): Required for syncing time with wifi
- [Adafruit DS3231](https://github.com/adafruit/Adafruit_CircuitPython_DS3231/releases/tag/2.4.17): Required for using the external RTC
- [Adafruit Register](https://github.com/adafruit/Adafruit_CircuitPython_Register/releases/tag/1.9.15): Required for the external RTC to talk to the Pico
- [Adafruit Bus Device](https://github.com/adafruit/Adafruit_CircuitPython_BusDevice/releases/tag/5.2.4): Required for the external RTC to talk to the Pico
- [Adafruit RGB LED](https://github.com/adafruit/Adafruit_CircuitPython_RGBLED): Not required, but makes controlling the LEDs easier

A [secrets.py](ClientDevice/secrets.py) file (see example) must be on the device and contain the secret used for 2FA generation, and one or more sets of SSID/password combinations to allow for Wifi Connectivity.

### Time Synchronization Methods

- [Get Time from Network Time Protocol (NTP)](ClientDevice/2FAClientDevice_ExternalRTC_Networked.py): This method of time syncronization connects the client device to a wifi network (home, office, mobile hotspot, etc) and fetches the time from the NTP server -- requires network connectivity.
  - If using with a mobile hotspot, ensure the hotspot is enabled prior to powering the device or it will fail to connect.
  - The external LED will be yellow until networks are checked. If there is a network available, the LED will turn Green. If not network is available, but the external RTC is synced, the LED will turn blue. Otherwise it turns red.
  - [NTP background](https://en.wikipedia.org/wiki/Network_Time_Protocol)

---

## Emitter Device

The emitter device is a Raspberry Pi Pico W Configured with a Pimoroni displaypack. A user configures the time via the display pack, and then the time is broadcase via a soft access point to allow multiple client devices to sync time from that device.

### Hardware

- The emitter device will need:
  - [A Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
  - [A Pimoroni Pico Display Pack PIM543](https://shop.pimoroni.com/en-us/products/pico-display-pack) connected to the header pins of the Pico W

### Software

The emitter device needs to be formatted by first entering bootloader mode (holding the bootsel button while plugging the pico into your computer), before uploading the most recent [Pimoroni Micropython Pico Binary](https://github.com/pimoroni/pimoroni-pico/releases) to the device. Once installed, the device will disconnect and remount as "CIRCUITPY." This device uses the Pimoroni flavor of Micropython due to ease in connecting the Display Pack.

All required libraries should be installed by the Pimoroni Micropython binary listed above.

The [configureTime.py](EmitterDevice/configureTime.py) file configures the time using the PIM543 displaypack, and the [broadcastTime.py](EmitterDevice/broadcastTime.py) file uses that time to broadcast the accurate time as a soft access point. The [2FAClientDevice_InternalRTCOnly_NotNetworked](ClientDevice/2FAClientDevice_InternalRTCOnly_NotNetworked.py) file pulls that time on each button press to resync the time. Inaccuracies in timing may occur based on how recently the time was configured, and if there were significant delays in getting the time.

---

## References

The code/implementation for this project was inspired by and derived from:

- [DIY Macro Keyboard Using a Raspberry PI Pico](https://www.instructables.com/DIY-Macro-Keyboard-Using-a-Raspberry-PI-Pico/)
- [Building a 2FA TOTP generator using a Raspberry Pi Pico and MicroPython](https://eddmann.com/posts/building-a-2fa-totp-generator-using-a-raspberry-pi-pico-and-micropython/)
- [Picoth - 2FA Auth with Pi Pico](https://hackaday.io/project/177593-picoth-2fa-auth-with-pi-pico)
