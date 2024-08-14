import serial
import datetime
import sys

device = sys.argv[1]

# Open serial port
ser = serial.Serial(device, 9600)  # Update '/dev/ttyUSB0' with your serial port

log_file = 'log_computer.txt'
is_robot = False

if device == '/dev/tty.usbserial-1120':
    log_file = 'log_robot.txt'
    is_robot = True

with open('log_all.txt', 'a') as all_f:
    with open(log_file, 'w') as f:
        try:
            buffer = b''  # Initialize a buffer to hold incoming data as bytes
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)  # Read data as bytes
                    buffer += data  # Append new data to the buffer

                    # Split commands within buffer
                    while b'\x02' in buffer and b'\x03' in buffer:
                        start_index = buffer.find(b'\x02')
                        end_index = buffer.find(b'\x03', start_index)
                        command = buffer[start_index:end_index+1]  # Extract command as bytes
                        
                        # Get current time in milliseconds
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"
                        print(f"{timestamp} - {command}") # Print command
                        f.write(f"{timestamp} - {command}\n")

                        all_f.write(f"{'-' if is_robot else '>'} {command}\n")
                        
                        buffer = buffer[end_index+1:]  # Remove printed command from buffer
        except KeyboardInterrupt:
            ser.close()  # Close serial port when done