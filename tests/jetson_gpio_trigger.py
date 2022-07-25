import Jetson.GPIO as GPIO

# Handles time
import time 
 
# Pin Definition
led_pin = 7
 
# Set up the GPIO channel
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.HIGH)

 
# Blink the LED
while True: 
    time.sleep(0.5) 
    GPIO.output(led_pin, GPIO.HIGH) 
    print("LED is ON")
    time.sleep(0.5) 
    GPIO.output(led_pin, GPIO.LOW)
    print("LED is OFF")
#endwhile