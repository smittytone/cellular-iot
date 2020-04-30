from cellulariot import *
import time
import sys

# Set up the modem
modem = CellularIoT()
modem.boot()

# Loop to issue entered AT commands
while True:
    cmd = input("AT Command: ")
    cmd = cmd.upper()
    
    if cmd == "EXIT":
        sys.exit()

    if cmd[:5] == "DEBUG":
        state = True
        if cmd[-2:] == "FF":
            state = False
        modem.set_debug(state)
        continue
        
    if cmd[:2] != "AT":
        cmd = "AT" + cmd
        resp = modem.send_command(cmd)
        print("Response state:", resp[0])
        print("Response:      ", resp[1])
