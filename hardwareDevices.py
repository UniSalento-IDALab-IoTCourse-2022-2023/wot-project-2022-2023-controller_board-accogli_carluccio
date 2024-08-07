import RPi._GPIO as GPIO
from RPLCD.gpio import CharLCD
import time


# GPIO per led 
LED_RED_PIN = 17
LED_GREEN_PIN = 27
LED_BLUE_PIN = 22

# GPIO per led 
BUZZER_PIN = 6

lcd = None


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # SETUP LED RGB
    GPIO.setup(LED_RED_PIN, GPIO.OUT)
    GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
    GPIO.setup(LED_BLUE_PIN, GPIO.OUT)

    # SETUP ACTIVE BUZZER
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    # SETUP display LCD
    init_display()


# Gestione display LCD
################################################
def init_display():
    global lcd
    lcd = CharLCD(pin_rs=25, pin_e=24, pins_data=[23, 18, 15, 14], numbering_mode=GPIO.BCM,
                  cols=16, rows=2, dotsize=8, charmap='A02', auto_linebreaks=True) 

def write_to_display(message):
    lcd.clear()
    lcd.write_string(message)
################################################



# Gestione LED RGB
################################################
def led_off():
    GPIO.output(LED_RED_PIN, GPIO.LOW)
    GPIO.output(LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(LED_BLUE_PIN, GPIO.LOW)


def led_on_red():
    GPIO.output(LED_RED_PIN, GPIO.HIGH)
    GPIO.output(LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(LED_BLUE_PIN, GPIO.LOW)

def led_on_green():
    GPIO.output(LED_RED_PIN, GPIO.LOW)
    GPIO.output(LED_GREEN_PIN, GPIO.HIGH)
    GPIO.output(LED_BLUE_PIN, GPIO.LOW)

def led_on_blue():
    GPIO.output(LED_RED_PIN, GPIO.LOW)
    GPIO.output(LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(LED_BLUE_PIN, GPIO.HIGH)

def led_on_yellow():
    GPIO.output(LED_RED_PIN, GPIO.LOW)
    GPIO.output(LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(LED_BLUE_PIN, GPIO.HIGH)
################################################


# Gestione BUZZER
################################################
def buzzer_on():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_off():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzzer_beep(duration):
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)    
################################################                                                                  



# Spegnimento devices e cleanup pin
def turn_off_all():
    led_off()
    buzzer_off()
    lcd.close(clear=True)
    GPIO.cleanup()