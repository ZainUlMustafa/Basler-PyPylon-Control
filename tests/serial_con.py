import time
import serial
from datetime import datetime
import struct

serialPort = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=9600,
)

def main():
    serialPort.close()
    serialPort.open()

    line = serialPort.readline()
    print(line)

    data = "1000\r\n".encode()
    print(data)
    serialPort.write(data)
    line = serialPort.readline()
    print(line)
    serialPort.close()
#enddef

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        serialPort.close()
    #endtry
#endif