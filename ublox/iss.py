from ublox_lara_r2 import *
import time
import sys
import json

# Set up the modem
modem = UbloxLaraR2()
modem.boot()
modem.set_debug(False)

# URL of the data source
base_url = "http://api.open-notify.org"
conn_open = False

while True:
    try:
        # Open a data connection
        modem.activate_context()
        conn_open = True

        # Reset the HTTP profile
        modem.send_command("AT+UHTTP=0")

        # Set the URL parameters: length and timeout
        modem.send_command("AT+UHTTP=0,1,\"" + base_url + "\"")

        # Make the GET request
        result = modem.send_command("AT+UHTTPC=0,1,\"/iss-now.json\",\"data.json\"", "+UUHTTPCR")

        if result[0] == "OK":
            # Check for HTTP error code
            result = result[1].split(": ")
            result = result[1].split(",")
            if result[2] == "1":
                response = modem.send_command("AT+URDFILE=\"data.json\"", "+URDFILE:")
                response = response[1].split(": ")
                response = response[1].split(",")
                response = response[2]
                data = json.loads(response)

                if data["message"] == "success":
                    print("ISS is at",data["iss_position"]["longitude"],",",data["iss_position"]["latitude"])
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

