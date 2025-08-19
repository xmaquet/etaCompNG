import serial

def connect(port: str, baudrate=1200, parity='E', bytesize=7):
    return serial.Serial(port=port, baudrate=baudrate, parity=parity, bytesize=bytesize, timeout=1)

def read_value(ser):
    if ser.in_waiting:
        line = ser.readline().decode('ascii').strip()
        return line
    return None