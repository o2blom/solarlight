import time
import board
import analogio
import neopixel
from analogio import AnalogIn

analog_in = AnalogIn(board.A0)

# Full direct light results in values around 128. Near darkness ~4000
LIGHT_THRESHOLD = 10000 #A higher value means it requires more darkness to turn on
LIGHT_DURATION = 5 #Hours of light after darkness is detected

pixel_pin = board.A1
num_pixels = 8

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

lsense = analogio.AnalogIn(board.A2)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
BLACK = (0, 0, 0)

DAY = 0
NIGHT = 1

state = DAY  # Assume day (Lights off)

i = 0  # Negative -30 means its day time. Plus 30 means night

def get_voltage(pin):  # 2.39 = 4.94V
    return (pin.value * 3.3) / 65536

while True:

    time.sleep(1)

#    print("Value: %d", lsense.value)

#    print("Voltage Reading: %d", get_voltage(analog_in))


    # Read ADC Photoresistor value and run some hysteresis to avoid glitching
    if lsense.value < LIGHT_THRESHOLD:
        if i > -30:
            i = i - 1
    else:
        if i < 30:
            i = i + 1

    if state == DAY and i == 30 and get_voltage(analog_in) > 2.0:
        print("Night Detected - Switching Lights on for 6h")
        state = NIGHT
        pixels.fill(YELLOW)
        pixels.show()
        time.sleep(3600 * LIGHT_DURATION)
        pixels.fill(BLACK)
        pixels.show()

    if state == NIGHT and i == -30:
        print("Day Detected - Switching Lights off")
        state = DAY
        pixels.fill(BLACK)  # Odds are they are already off here
        pixels.show()


