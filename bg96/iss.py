from cellulariot import *
import time
import sys
import json

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

        # Make the GET request
        result = modem.send_command("AT+QHTTPGET", "+QHTTPGET", 120)
        if result[0] == "OK":
            # Check for HTTP error code, eg. x in "+QHTTPGET: x,200,22323" not zero
            response = result[1].split(": ")
            response = response[1].split(",")
            if response[0] == "0":
                result = modem.send_command("AT+QHTTPREAD", "OK")
                if result[0] == "OK":
                    response = result[1].split("\r\n")[2]
                    data = json.loads(response)
                    if data["message"] == "success":
                        print("ISS is at",data["iss_position"]["longitude"],",",data["iss_position"]["latitude"])
                else:
                    print("ISS location not retrieved")
            else:
                print("ISS location not retrieved")
        else:
            print("ISS location not retrieved")

        # Close the data connection
        modem.deactivate_context()
        conn_open = False

        # Pause 1 minute
        time.sleep(60)
    except KeyboardInterrupt:
        if conn_open:
            modem.deactivate_context()
        sys.exit()
