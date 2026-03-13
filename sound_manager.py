#sound manager 
#prob dont really need but ill include it for better structure

import pygame
import time

# Initialize audio engine
pygame.mixer.init()

# Load audio to memory as a Sound
chimes = pygame.mixer.Sound("wind-chimes-2014.wav") 
rep_beep = pygame.mixer.Sound("success-alert-2039.wav")

def sound_quit():
    #Safely shuts down the audio engine
    pygame.mixer.quit()
