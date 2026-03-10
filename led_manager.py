import board
import neopixel
import time

class LEDManager:
	def __init__(self, pin=board.D21, num_pixels=8):
		#initialise pi5 compatible neopixels
		self.num_pixels = num_pixels
		self.pixels = neopixel.NeoPixel(
		pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
		)
		self.last_count = -1 #optimised to avoid rewriting same data
		
	def update_bar(self, percentage):
		#map 0-100% to 0-8 
		led2light = int((percentage/100) *self.num_pixels)
		#stops the code from trying to light any more than 8 pixels
		led2light = max(0, min(led2light, self.num_pixels)) 
		
		if led2light ==self.last_count:
			return
			
		self.last_count = led2light
		
		#colours
		#full = green
		if led2light == self.num_pixels:
			color = (0,255,0)
		else:
			# blue for regular progress
			color = (0, 0, 255)
		
		for i in range(self.num_pixels):
			if i < led2light:
				self.pixels[i] = color
			else:
				self.pixels[i] = (0,0,0) #turn off remaining pixels
		
		#send to hardware
		self.pixels.show()
		
	def clear(self):
		self.pixels.fill((0,0,0))
		self.pixels.show()
		
