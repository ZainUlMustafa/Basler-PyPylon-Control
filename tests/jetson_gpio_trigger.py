import Jetson.GPIO as GPIO

# Handles time
import time 
 
# Pin Definition
led_pin = 11
 
# Set up the GPIO channel
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.HIGH)

 
# # Blink the LED
# while True: 
#     time.sleep(0.5) 
#     GPIO.output(led_pin, GPIO.HIGH) 
#     print("LED is ON")
#     time.sleep(0.5) 
#     GPIO.output(led_pin, GPIO.LOW)
#     print("LED is OFF")
# #endwhile

# BEEP BEEP BEEP BEEEEEEP
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.1)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.1)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.1)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.5)
GPIO.output(led_pin, GPIO.LOW)

time.sleep(1)

# BEEEEEP BEEP BEEP
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.5)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.1)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.1)
GPIO.output(led_pin, GPIO.LOW)

time.sleep(1)

GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.09)
GPIO.output(led_pin, GPIO.LOW)
time.sleep(0.05)
GPIO.output(led_pin, GPIO.HIGH) 
time.sleep(0.13)
GPIO.output(led_pin, GPIO.LOW)