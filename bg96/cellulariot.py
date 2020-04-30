'''
  Simplified Library for the Sixfab RPi Cellular IoT Hat.
  ---
  Derived from Sixfab's Cellular IoT Shield library:
      https://github.com/sixfab/Sixfab_RPi_CellularIoT_App_Shield)
      MIT Licence
'''


import time
import serial
import RPi.GPIO as GPIO


# Global variables
TIMEOUT = 3 # seconds
debug = True
ser = serial.Serial()

# Function for printing debug message
def debug_print(message):
    if debug:
        print(message)

# Function for getting time in miliseconds
def millis():
    return int(time.time())

# Function for delay in miliseconds
def delay(ms):
    time.sleep(float(ms / 1000.0))


class CellularIoT:

    ip_address = "" # ip address
    domain_name = "" # domain name
    port_number = "" # port number
    timeout = TIMEOUT

    response = "" # variable for modem responses
    compose = "" # variable for command strings

    # Pins
    BG96_ENABLE = 17
    BG96_POWERKEY = 24
    STATUS = 23

    # Cellular Modes
    AUTO_MODE = 0
    GSM_MODE = 1
    CATM1_MODE = 2
    CATNB1_MODE = 3

    # LTE Bands
    LTE_B1 = "1"
    LTE_B2 = "2"
    LTE_B3 = "4"
    LTE_B4 = "8"
    LTE_B5 = "10"
    LTE_B8 = "80"
    LTE_B12 = "800"
    LTE_B13 = "1000"
    LTE_B18 = "20000"
    LTE_B19 = "40000"
    LTE_B20 = "80000"
    LTE_B26 = "2000000"
    LTE_B28 = "8000000"
    LTE_B39 = "4000000000" # catm1 only
    LTE_CATM1_ANY = "400A0E189F"
    LTE_CATNB1_ANY = "A0E189F"
    LTE_NO_CHANGE = "0"

    # GSM Bands
    GSM_NO_CHANGE = "0"
    GSM_900 = "1"
    GSM_1800 = "2"
    GSM_850 = "4"
    GSM_1900 = "8"
    GSM_ANY = "F"

    # Special Characters
    CTRL_Z = '\x1A'

    # Initializer function
    def __init__(self, serial_port="/dev/ttyS0", serial_baudrate=115200, rtscts=False, dsrdtr=False):
        ser.port = serial_port
        ser.baudrate = serial_baudrate
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.bytesize = serial.EIGHTBITS
        ser.rtscts = rtscts
        ser.dsrdtr = dsrdtr
        debug_print("CellularIoT class instantiated")

    def __del__(self):
        GPIO.cleanup()

    def boot(self):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BG96_ENABLE, GPIO.OUT)
        GPIO.setup(self.BG96_POWERKEY, GPIO.OUT)
        GPIO.setup(self.STATUS, GPIO.IN)

        # Enable board and power up
        self.enable()
        self.power_up()

    # Function to enable BG96 module
    def enable(self):
        GPIO.output(self.BG96_ENABLE, 0)
        debug_print("Modem enabled")

    # Function for powering down BG96 module and all peripherals from voltage regulator
    def disable(self):
        GPIO.output(self.BG96_ENABLE, 1)
        debug_print("Modem disabled")

    # Function for powering BG96 module
    def power_up(self):
        GPIO.output(self.BG96_POWERKEY, 1)
        while GPIO.input(self.STATUS):
            pass
        GPIO.output(self.BG96_POWERKEY, 0)
        debug_print("Modem powered")

    # Function for saving conf. and reset BG96_AT module
    def reset(self):
        self.save_config()
        delay(200)
        self.disable()
        delay(200)
        self.enable()
        self.power_up()

    # Function for sending a comamand or data to module
    def send(self, command, is_command=True):
        if ser.isOpen() is False:
            ser.open()
        self.compose = str(command)
        if is_command:
            self.compose += "\r"
        ser.reset_input_buffer()
        ser.write(self.compose.encode())

    # Function for sending at command to BG96_AT.
    def send_command(self, command, desired_response="OK\r\n", timeout=None):
        if timeout is None:
            timeout = self.timeout
        self.response = ""
        self.send(command)
        timer = millis()
        while True:
            if millis() - timer > timeout:
                # Re-issue command on timeout
                # TODO or return an error?
                self.response = ""
                self.send(command)
                timer = millis()
            while ser.in_waiting > 0:
                try:
                    self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    delay(100)
                except Exception as exp:
                    debug_print(exp.Message)
            if self.response.find(desired_response) != -1:
                debug_print(self.response)
                return ("OK", self.response)
            if self.response.find("ERROR") != -1:
                debug_print(self.response)
                return ("ERROR", self.response)
                break

    # Function for sending data to BG96_AT.
    def send_data(self, data, desired_response="OK\r\n", timeout=None):
        if timeout is None:
            timeout = self.timeout
        self.response = ""
        self.send(data, False)
        timer = millis()
        while True:
            if millis() - timer > timeout:
                self.response = ""
                self.send(data, False)
                timer = millis()
                self.response = ""
            while ser.in_waiting > 0:
                self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if self.response.find(desired_response) != -1 or self.response.find("ERROR") != -1:
                debug_print(self.response)
                break

    # Function for save configurations that be done in current session.
    def save_config(self):
        self.send_command("AT&W")

    # Function for setting GSM Band
    def set_gsm_band(self, gsm_band):
        self.compose = "AT+QCFG=\"band\","
        self.compose += str(gsm_band)
        self.compose += ","
        self.compose += str(self.LTE_NO_CHANGE)
        self.compose += ","
        self.compose += str(self.LTE_NO_CHANGE)
        self.send_command(self.compose)
        self.compose = ""

    # Function for setting Cat.M1 Band
    def set_catm1_band(self, catm1_band):
        self.compose = "AT+QCFG=\"band\","
        self.compose += str(self.GSM_NO_CHANGE)
        self.compose += ","
        self.compose += str(catm1_band)
        self.compose += ","
        self.compose += str(self.LTE_NO_CHANGE)
        self.send_command(self.compose)
        self.compose = ""

    # Function for setting NB-IoT Band
    def set_nbiot_band(self, nbiot_band):
        self.compose = "AT+QCFG=\"band\","
        self.compose += str(self.GSM_NO_CHANGE)
        self.compose += ","
        self.compose += str(self.LTE_NO_CHANGE)
        self.compose += ","
        self.compose += str(nbiot_band)
        self.send_command(self.compose)
        self.compose = ""

    # Function for getting current band settings
    def get_band_config(self):
        return self.send_command("AT+QCFG=\"band\"")

    # Function for setting running mode.
    def set_mode(self, mode):
        if mode == self.AUTO_MODE:
            self.send_command("AT+QCFG=\"nwscanseq\",00,1")
            self.send_command("AT+QCFG=\"nwscanmode\",0,1")
            self.send_command("AT+QCFG=\"iotopmode\",2,1")
            debug_print("Modem configuration : AUTO_MODE")
            debug_print("*Priority Table (Cat.M1 -> Cat.NB1 -> GSM)")
        elif mode == self.GSM_MODE:
            self.send_command("AT+QCFG=\"nwscanseq\",01,1")
            self.send_command("AT+QCFG=\"nwscanmode\",1,1")
            self.send_command("AT+QCFG=\"iotopmode\",2,1")
            debug_print("Modem configuration : GSM_MODE")
        elif mode == self.CATM1_MODE:
            self.send_command("AT+QCFG=\"nwscanseq\",02,1")
            self.send_command("AT+QCFG=\"nwscanmode\",3,1")
            self.send_command("AT+QCFG=\"iotopmode\",0,1")
            debug_print("Modem configuration : CATM1_MODE")
        elif mode == self.CATNB1_MODE:
            self.send_command("AT+QCFG=\"nwscanseq\",03,1")
            self.send_command("AT+QCFG=\"nwscanmode\",3,1")
            self.send_command("AT+QCFG=\"iotopmode\",1,1")
            debug_print("Modem configuration : CATNB1_MODE ( NB-IoT )")

    # Function for getting self.ip_address
    def get_ip_address(self):
        return self.ip_address

    # Function for setting self.ip_address
    def set_ip_address(self, ip):
        self.ip_address = ip

    # Function for getting self.domain_name
    def get_domain_name(self):
        return self.domain_name

    # Function for setting domain name
    def set_domain_name(self, domain):
        self.domain_name = domain

    # Function for getting port
    def get_port(self):
        return self.port_number

    # Function for setting port
    def set_port(self, port):
        self.port_number = port

    # Function for getting timout in ms
    def get_timeout(self):
        return self.timeout

    # Function for setting timeout in ms
    def set_timeout(self, new_timeout):
        self.timeout = new_timeout

    # Function to set debug state
    def set_debug(self, state=True):
        global debug
        debug = state

    #******************************************************************************************
    #*** SMS Functions ************************************************************************
    #******************************************************************************************

    # Function for sending SMS
    def send_sms(self, number, text):
        self.send_command("AT+CMGF=1") # text mode
        delay(500)

        self.compose = "AT+CMGS=\""
        self.compose += str(number)
        self.compose += "\""

        self.send_command(self.compose, ">")
        delay(1000)
        self.compose = ""
        delay(1000)
        self.send(text)
        self.send_command(self.CTRL_Z, "OK", 8) # with 8 seconds timeout

    #******************************************************************************************
    #*** TCP & UDP Protocols Functions ********************************************************
    #******************************************************************************************

    # Function for configurating and activating TCP context
    def activate_context(self):
        self.send_command("AT+QICSGP=1")
        delay(1000)
        self.send_command("AT+QIACT=1", "\r\n")

    # Function for deactivating TCP context
    def deactivate_context(self):
        self.send_command("AT+QIDEACT=1", "\r\n")

    # Function for connecting to server via TCP
    # just buffer access mode is supported for now.
    def connect_to_server_tcp(self):
        self.compose = "AT+QIOPEN=1,1"
        self.compose += ",\"TCP\",\""
        self.compose += str(self.ip_address)
        self.compose += "\","
        self.compose += str(self.port_number)
        self.compose += ",0,0"
        self.send_command(self.compose)
        self.compose = ""
        self.send_command("AT+QISTATE=0,1")

    # Fuction for sending data via TCP.
    # just buffer access mode is supported for now.
    def send_data_tcp(self, data):
        self.compose = "AT+QISEND=1,"
        self.compose += str(len(data))
        self.send_command(self.compose, ">")
        self.send_command(data, "SEND OK")
        self.compose = ""

    # Function for connecting to server via UDP
    def connect_to_server_udp(self):
        port = "3005"
        self.compose = "AT+QIOPEN=1,1,\"UDP SERVICE\",\""
        self.compose += str(self.ip_address)
        self.compose += "\",0,"
        self.compose += str(port)
        self.compose += ",0"
        self.send_command(self.compose)
        self.compose = ""
        self.send_command("AT+QISTATE=0,1", "\r\n")

    # Fuction for sending data via udp.
    def send_data_udp(self, data):
        self.compose = "AT+QISEND=1,"
        self.compose += str(len(data))
        self.compose += ",\""
        self.compose += str(self.ip_address)
        self.compose += "\","
        self.compose += str(self.port_number)
        self.send_command(self.compose, ">")
        self.compose = ""
        self.send_command(data, "SEND OK")

    # Function for closing server connection
    def close_connection(self):
        self.send_command("AT+QICLOSE=1", "\r\n")
