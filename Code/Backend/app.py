import time
from RPi import GPIO
import threading
from helpers.mcp3008 import Mcp3008
from helpers.lcd import LCD
from pad4pi import rpi_gpio
import socket
import subprocess
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request, url_for, json
from repositories.DataRepository import DataRepository


# Code voor Hardware
# GPIO.setwarnings(False)

# variabelen
waarde_ldr = 0
waarde_rain = 0
laser = 27
pir = 22
led = 17
servo = 1

# LCD

pins = [16, 12, 25, 24, 23, 26, 19, 13]
clock = 20
rs = 21

KEYPAD = [
    [1, 2, 3, "A"],
    [4, 5, 6, "B"],
    [7, 8, 9, "C"],
    ["*", 0, "#", "D"]
]

typed_code = []
rfid_code = ['10']
status_door = False
ROW_PINS = [0, 5, 6, 14]  # BCM numbering
COL_PINS = [15, 18, 2, 3]  # BCM numbering
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(
    keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo, GPIO.OUT)
    GPIO.setup(laser, GPIO.OUT)
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(laser, GPIO.HIGH)
    GPIO.setup(pir, GPIO.IN)


def check_code(key):
    global lcd
    global status_door
    print(rfid_code)
    print(key)
    typed_code.append(key)
    if key == 'D':
        typed_code.clear()
    if key == 'A':
        lcd.reset()
    if key == 'B':
        lcd.send_string(f"Temp: {read_temp()} C", False)
        lcd.send_string(f"Rain: {read_rain()} %", True)
    if key == 'C':
        lcd.send_string("Smart Mailbox", False)
        lcd.send_string(get_ip(), True)
    if typed_code == rfid_code and status_door == False:
        open_door()
        typed_code.clear()
        status_door = True
    elif typed_code == rfid_code and status_door == True:
        close_door()
        typed_code.clear()
        status_door = False


def code_run():
    print("Checking codes")
    keypad.registerKeyPressHandler(check_code)


thread = threading.Timer(2, code_run)
thread.start()


def update_history(id):
    if id == 0:
        DataRepository.update_history(2, 6, read_temp())
        DataRepository.update_history(3, 9, read_ldr())
        DataRepository.update_history(4, 8, read_rain())
    else:
        DataRepository.update_history(2, id, read_temp())
        DataRepository.update_history(3, id, read_ldr())
        DataRepository.update_history(4, id, read_rain())


def update_timestamp():
    while True:
        update_history(10)
        time.sleep(300)


thread = threading.Timer(2, update_timestamp)
thread.start()


def read_history():
    return DataRepository.read_history()


def send_history():
    socketio.emit('B2F_history', {'history': read_history()})


def check_rfid():
    pass


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipa = s.getsockname()[0]
    s.close()
    return ipa


def SetDuty(dutycycle):
    p = GPIO.PWM(servo, 50)
    p.start(2.5)
    p.ChangeDutyCycle(dutycycle)
    time.sleep(0.5)
    p.stop()


def open_door():
    SetDuty(10)
    print("Door open")
    socketio.emit("B2F_door_opened")


def close_door():
    SetDuty(2)
    print("Door closed")


def read_rain():
    mcp = Mcp3008()
    waarde_rain = mcp.read_channel(1)
    omgezette_waarde = round((((waarde_rain/1023)*100)-100), 2)
    return str(omgezette_waarde)[1:]


def read_ldr():
    mcp = Mcp3008()
    waarde_ldr = mcp.read_channel(0)
    omgezette_waarde = round((((waarde_ldr/1023)*100)-100), 2)
    final_ldr = str(omgezette_waarde)[1:]
    return final_ldr


def read_temp():
    sensor_file_name = '/sys/bus/w1/devices/28-011452f117aa/w1_slave'
    sensorfile = open(sensor_file_name, 'r')
    sensorfile = open(sensor_file_name, 'r')
    for i, line in enumerate(sensorfile):
        if i == 1:
            temp = int(line.strip('\n')[line.find('t=')+2:])/1000.0

    final_temp = round(temp, 2)
    return final_temp


def mail_cleared():
    socketio.emit('B2F_mail_delivered', {'isMail': False})


def read_pir():
    DataRepository.update_history(9, 7, 1.0)
    if GPIO.input(pir):
        print('Motion Detected')
    else:
        print("No Motion Detected")


# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'W8w00rd'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


@ socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


print("**** Program started ****")

# API ENDPOINTS


@ app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@app.route('/temperature', methods=["GET"])
def showTemperatuur():
    if request.method == "GET":
        return jsonify(DataRepository.read_temp_hist()), 200


@app.route('/rain', methods=["GET"])
def showRain():
    if request.method == "GET":
        return jsonify(DataRepository.read_rain_hist()), 200


@ socketio.on('connect')
def initial_connection():
    print('A new client connect')
    status_rain = read_rain()
    status_temp = read_temp()
    socketio.emit('B2F_status_temp', {
        'currentTemp': status_temp})
    socketio.emit('B2F_status_rain', {
        'currentRain': status_rain})


@ socketio.on('F2B_deur_open')
def init():
    open_door()


@ socketio.on('F2B_deur_toe')
def init():
    close_door()
# ANDERE FUNCTIES


@ socketio.on('F2B_new_code')
def init(new_code):
    rfid_code.clear()
    for x in new_code:
        rfid_code.append(int(x))
    socketio.emit("B2F_new_code", {'newRfidCode': new_code})


def main():
    global lcd
    lcd = LCD(pins, clock, rs)
    lcd.init_lcd()
    lcd.display_on()
    lcd.reset()
    DataRepository.project_on()
    DataRepository.component_off(7)
    print("main wordt uigevoerd")
    time.sleep(3)
    lcd.reset()
    lcd.send_string("Smart Mailbox", False)
    lcd.send_string(get_ip(), True)
    while True:
        status_rain = read_rain()
        status_temp = read_temp()
        waarde_ldr = read_ldr()
        socketio.emit('B2F_status_rain', {
            'currentRain': status_rain})
        socketio.emit('B2F_status_temp', {
            'currentTemp': status_temp})
        if float(waarde_ldr) < 70.0:
            print("Mail Delivered")
            lcd.reset()
            lcd.send_string("Mail delivered", False)
            update_history(0)
            socketio.emit('B2F_mail_delivered', {'isMail': True})
            time.sleep(3)
            lcd.reset()
            lcd.send_string("Smart Mailbox", False)
            lcd.send_string(get_ip(), True)


thread = threading.Timer(2, main)
thread.start()

if __name__ == '__main__':
    setup()
    try:
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as ex:
        print(ex)
    finally:
        DataRepository.project_off()
        close_door()
        GPIO.cleanup()
