from cellulariot import *
import time
import sys
import json


# Process the ISS data: lat and long
def process_iss_data(modem_response):
    # 'modem_response' is a string, eg. "+QHTTPGET: 0,200,22323"
    # Check for HTTP error code, the
    response = modem_response[1].split(": ")
    response = response[1].split(",")

    if response[0] == "0":
        # Got a good response from the server,
        # so read it back from the modem
        result = modem.send_command("AT+QHTTPREAD", "OK")
        if result[0] == "OK":
            received_data = result[1].split("\r\n")[2]
            iss_data = json.loads(received_data)
            if iss_data["message"] == "success":
                print("ISS is at",iss_data["iss_position"]["longitude"],",",iss_data["iss_position"]["latitude"])
                return

    # Display error message
    print("ISS location not retrieved")


# Set up the modem
modem = CellularIoT()
modem.boot()
modem.set_debug(False)
# Turn off echoing (easier to parse responses)
modem.send_command("ATE0")

# URL of the data source
source_url = "http://api.open-notify.org/iss-now.json"
conn_open = False

while True:
    try:
        # Open a data connection
        modem.activate_context()
        conn_open = True

        # Assemble the HTTP request
        # 1. Set the PDP Context ID
        modem.send_command("AT+QHTTPCFG=\"contextid\",1")

        # 2. Choose no custom headers
        modem.send_command("AT+QHTTPCFG=\"requestheader\",0")

        # 3. Set the URL parameters: length and timeout
        modem.send_command("AT+QHTTPURL=" + str(len(source_url)) + ",80", "CONNECT", 30)

        # 4. Set the URL as data
        modem.send_data(source_url)

        # Make the GET request and parse the result
        result = modem.send_command("AT+QHTTPGET", "+QHTTPGET", 120)
        if result[0] == "OK":
            process_iss_data(result[1])

        # Close the data connection
        modem.deactivate_context()
        conn_open = False

        # Pause 1 minute
        time.sleep(60)
    except KeyboardInterrupt:
        if conn_open:
            modem.deactivate_context()
        sys.exit()
