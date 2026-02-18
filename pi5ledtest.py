import board #converts GPIO to a python format
import neopixel # controls led timing and colours
import time

# Configuration
pixel_pin = board.D18        # GPIO 18 (Pin 12)
num_pixels = 8               # Your 8-led stick
ORDER = neopixel.GRB         # Most sticks are Green-Red-Blue

pixels = neopixel.NeoPixel( #init and call class
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

def color_wipe(color, wait): #
    for i in range(num_pixels):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

try:
    print("Running Pi 5 NeoPixel Test... Press Ctrl+C to stop.")
    while True:
        # Red
        color_wipe((255, 0, 0), 0.1)
        time.sleep(0.5)
        # Green
        color_wipe((0, 255, 0), 0.1)
        time.sleep(0.5)
        # Blue
        color_wipe((0, 0, 255), 0.1)
        time.sleep(0.5)
        # Clear
        #pixels.fill((0, 0, 0))
        color_wipe((0, 0, 0), 0.1)
        pixels.show()
        time.sleep(0.5)

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
