# 2FA Pico

This project was designed as a way to simplify the user interface/experience for low-security applications of two-factor authentication. This project uses one or more Raspberry Pi Pico W's due to their relatively low cost and wifi capabilities.

This system consists of one Raspberry Pi Pico W as a Client Device and may include one or more Pico W's as Emitter Devices.

## Client Device

The Client device is a Raspberry Pi Pico running CircuitPython that takes the current time, converts it to a 2FA code, and sends it to a connected USB device via USB_HID. This time could be fetched either from a personal hotspot (via NTP), or from the broadcast of the Emitter Device. This device is only capable of exporting one 2FA token -- selecting being multiple 2FA tokens is not supported to minimize security risks if this device is compromised.

### Setup

#### Hardware

The client device will need a button between GPIO 10 (Pin 14) on the Raspberry Pi Pico W and 3.3v (Pin 36) to trigger the write of the 2FA token to the connected computer.

#### Software

The client device needs to be formatted by first entering bootloader mode (holding the bootsel button while plugging the pico into your computer), before uploading the most recent [Circuit Python Binaries](https://circuitpython.org/board/raspberry_pi_pico/) to the device. Once installed, the device will disconnect and remount as "CIRCUITPY." This device uses CircuitPython due to MicroPython not supporting USB_HID at the time of this project being completed. Adafruit Blinka and Platform Detect *should* be able to be used as a compatibility layer between CircuitPython and MicroPythion allowing the USB_HID libraries to function properly, however, upon testing it caused significant syntax errors and appears to not yet be fully supported.

Now the appropriate libraries could be installed on the device:

- [Adafruit HashLib Library](https://github.com/adafruit/Adafruit_CircuitPython_hashlib): Required for key generation
- [Base 64 Library](https://github.com/python/cpython/blob/3.11/Lib/base64.py): Required for key generation
- [HMAC Library](https://github.com/micropython/micropython-lib/blob/master/python-stdlib/hmac/hmac.py): Required for key generation
- [USB_HID Library](https://github.com/adafruit/Adafruit_CircuitPython_HID): Required to send 2FA as a keyboard input
- [Adafruit NTP](https://github.com/adafruit/Adafruit_CircuitPython_NTP): (Optional) Required for syncing time with wifi

A secrets.py file (see example) must be on the device and contain the secret used for 2FA generation. Optionally, this file will have the SSID username and password for NTP based time configuration methods.

### Time Synchronization Methods

- [Network Time Protocol (NTP)](Client%Device/NTP_2FA.py): This method of time syncronization connects the client device to a wifi network (home, office, mobile hotspot, etc) and fetches the time from the NTP server.
  - If using with a mobile hotspot, ensure the hotspot is enabled prior to powering the device or it will fail to connect.
  - The LED will blink green indefinitely once the client device successfully connected to a wifi network and synchronized the time.
  - [NTP background](https://en.wikipedia.org/wiki/Network_Time_Protocol)

- [Emitter Device](Client%Device/parseWifi_2FA.py): This method of synchronization takes a wifi broadcast of the current UTC time as seconds in the current Epoch (Time: "XXXXXXXXX"), removes the "Time:" pre-fix, and converts the remaining wifi name to an integer to use for 2FA generation.
  - As multiple wifi signals may be present at the same, the device keeps the greatest number of seconds of any of the broadcasts.
  - The client device will check for a wifi network on each button press, to ensure the time is within the current 30 second interval

Either of these programs will need to be renamed to "main.py" on the device to have it automatically run on program launch.
