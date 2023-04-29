import time
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from machine import RTC
    
def set_time():
    # We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM!
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)

    display.set_backlight(0.5)
    display.set_font("bitmap8")
    WIDTH, HEIGHT = display.get_bounds()

    button_a = Button(12)
    button_b = Button(13)
    button_x = Button(14)
    button_y = Button(15)

    WHITE = display.create_pen(255, 255, 255)
    BLACK = display.create_pen(0, 0, 0)
    CYAN = display.create_pen(0, 255, 255)
    MAGENTA = display.create_pen(255, 0, 255)
    YELLOW = display.create_pen(255, 255, 0)
    GREEN = display.create_pen(0, 255, 0)

    # sets up a handy function we can call to clear the screen
    def clear():
        display.set_pen(BLACK)
        display.clear()
        display.update()

    # set up
    clear()

    #Configure the default time for when the device screen boots up
    datetime = [2023, 3, 5, 0, 0, 0]
    selected_idx = 0
        
    while True:
        if button_a.read():
            selected_idx = (selected_idx + 1) % len(datetime)
        if button_x.read():
            datetime[selected_idx] += 1
        if button_y.read():
            datetime[selected_idx] = max(datetime[selected_idx] - 1, 1)
        if button_b.read():
            break
        
        clear()                                           # clear to black
        display.set_pen(WHITE)
        
        display.text("Next", 10, 10, 30, 2)
        display.text("Inc", WIDTH - 40, 10, 30, 2)
        display.text("Dec", WIDTH - 40, HEIGHT - 20, 30, 2)
        display.text("Confirm", 10, HEIGHT - 20, 30, 2)
        
        display.text("YYYY MM DD HH MM SS", 30,
                         HEIGHT // 2 - 10, WIDTH - 30, 2)
        display.text(
                " ".join("%s%02d" % (">" if idx == selected_idx else "", sep)
                         for idx, sep in enumerate(datetime)),
                30, HEIGHT // 2 + 10, WIDTH - 30, 2)
        
        display.update()
        time.sleep(0.1)

    rtc = RTC() # initialize the RTC
    #Configure the RTC based on the input from the user
    rtc.datetime((datetime[0], datetime[1], datetime[2], 0, datetime[3], datetime[4], datetime[5], 0))
    return(rtc.datetime())

