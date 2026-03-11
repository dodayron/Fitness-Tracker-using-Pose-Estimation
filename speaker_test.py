import pygame
import time

pygame.mixer.init() ##starts audio engine and connecs to speaker

sound = pygame.mixer.Sound("wind-chimes-2014.wav") #load audio to memory as a Sound

sound.set_volume(1.0)

sound.play()

time.sleep(2) #stop script from ending before sound finishes

pygame.quit() #turns off engine and audio system
