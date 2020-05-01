 #!/usr/bin/python

'''
  Simplified Library for the Seeed LTA Hat.
  ---
  Derived from Sixfab's Cellular IoT Shield library:
      https://github.com/Seeed-Studio/ublox_lara_r2_pi_hat
      MIT Licence
'''

import serial
import time
import os
import RPi.GPIO as GPIO


class UbloxLaraR2():

    response = ""
    debug = True
    timeout = 3 # seconds

    def __init__(self, port="/dev/ttyAMA0", baudrate=115200):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.bytesize = serial.EIGHTBITS
        self.debug_print("CellularIoT class instantiated")

    def initialize(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(6, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)

    # Start up the modem
    def boot(self):
        #self.initialize()
        while True:
            result = self.send_command("AT")
            if result[0] == "OK": return
            time.sleep(1)

    # Send a command or date out via serial
    def send(self, command):
        if self.ser.isOpen() is False:
            self.ser.open()
        command = str(command) + "\r"
        self.ser.reset_input_buffer()
        self.ser.write(command.encode())

    # Sending a specific AT command to the modem
    def send_command(self, command, desired_response="OK\r\n", timeout=None):
        if timeout is None:
            timeout = self.timeout
        self.response = ""
        self.send(command)
        timer = self.millis()
        while True:
            if self.millis() - timer > timeout:
                # Re-issue command on timeout
                # TODO or return an error?
                self.response = ""
                self.send(command)
                timer = self.millis()
            while self.ser.in_waiting > 0:
                try:
                    self.response += self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    self.delay(100)
                except Exception as exp:
                    self.debug_print(exp.Message)
            if self.response.find(desired_response) != -1:
                self.debug_print(self.response)
                return ("OK", self.response)
            if self.response.find("ERROR") != -1:
                self.debug_print(self.response)
                return ("ERROR", self.response)
                break

    # Activate a PDP context
    def activate_context(self):
        self.send_command("AT+CGACT=1,1")

    # Deactivate a PDP context
    def deactivate_context(self):
        self.send_command("AT+CGACT=0,1")

    # Output debug messages if the debug flag is set
    def debug_print(self, message):
        if self.debug:
            print(message)

    # Set the debug flag
    def set_debug(self, state=True):
        self.debug = state

    # Getting a time in miliseconds
    def millis(self):
        return int(time.time())

    # Delay in miliseconds
    def delay(self, ms):
        time.sleep(float(ms / 1000.0))
