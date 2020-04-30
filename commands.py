from cellulariot import *
import time
import sys

# Set up the modem
modem = CellularIoT()
modem.boot()
mode.set_debug(False)

while True:
    try:
        # Is there a message?
        msg = modem.send_command("AT+CMGR=0")
        if len(msg) > 0:
            # Extract the command from the message
            parts = msg.split("\r\n")
            command = parts[2]
            if len(command) > 0:
                # Delete the message (all messages, in fact)
                modem.send_command("AT+CMGD=0,4")

                # Process the command
                if command.upper() == "EXIT":
                    print("Quitting...")
                    sys.exit()

                if command.upper() == "INFO":
                    # Display modem info
                    result = modem.send_command("AT+QNWINFO")
                    print(result[1])

                if command.upper()[:2] == "AT":
                    # Run supplied AT command
                    print("AT Command Received:", command[2:])
                    result = modem.send_command(command)
                    print("Response:           ", result[1])

        # Wait 15 seconds before checking again
        time.sleep(15)
    except KeyboardInterrupt:
        print("Ctrl-c hit... quitting...")
        sys.exit()
