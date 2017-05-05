#!/usr/bin/env python

# ReEnviDa - Record Environmental Data
# Get Temperature, Humidity by SHT31, and Particulates Matter by SDS011
# SHT31 is connected via TWI2
# SDS011 is connected via USB
# C.H.I.P. is used as controller running Linux chip 4.4.13-ntc-mlc
# based on # SDS011_Feinstaub_Sensor.py
# Copyright 2017 by luetzel <webmaster_at_raspberryblog.de>
# The SHT31 part based on 
# https://www.controleverything.com/content/Humidity?sku=SHT31_I2CS#tabs-0-product_tabset-2
# Enhancements to a complete station for recording environmental data by
# 2017-04-07 Claus Kuehnel <info@ckuehnel.ch>

import smbus, serial, time, struct, os

from axp209 import AXP209
axp = AXP209()

import thingspeak
channel_id = '<your channel id>' # change this
write_key  = '<your write key>'  # change this

# Switch off C.H.I.P.'s heartbeat LED
os.system('sudo echo none > /sys/class/leds/chip\:white\:status/trigger')

# Initialize I2C Bus
bus = smbus.SMBus(2) # SHT31 connected to TWI2

# Initialize Serial Interface to SDS011
ser = serial.Serial()
ser.port = "/dev/ttyUSB0" # Set this to your serial port 
ser.baudrate = 9600 
ser.open() 
ser.flushInput()

CYCLE = 600 # Cycle Time in sec 

print "Measuring Environmental Data..."
print "Cycle Time is %d sec" % (CYCLE)

def read_SHT31():
    global cTemp, humidity
    # Send measurement command, 0x2C 0x06	High repeatability measurement
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.5)
    # Read data back from 0x00(00), 6 bytes
    # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
    data = bus.read_i2c_block_data(0x44, 0x00, 6)
    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = round((-45 + (175 * temp / 65535.0)),1)
    humidity = round((100 * (data[3] * 256 + data[4]) / 65535.0),1)
    
    # Terminal output
    print "Temperature in Celsius: %.2f C" %cTemp
    print "Relative Humidity: %.2f %%RH" %humidity
	
def process_frame(d):
    global pm25, pm10
    r = struct.unpack('<HHxxBBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(ord(v) for v in d[2:8])%256
    print "Particulate Matter"
    if (checksum==r[2] and r[3]==0xab):
        print("PM 2.5: {} g/m^3  PM 10: {} g/m^3".format(pm25, pm10))
        f = open("/home/chip/PM10","w")
        f.write(str(pm10))
        f.close()
    else:
        print("CRC Error")

def read_SDS011():
    byte = 0
    while byte != "\xaa":
        byte = ser.read(size=1)
    d = ser.read(size=10)
    if d[0] == "\xc0":
        process_frame(byte + d)
		
def doit(channel):
    try:
        response = channel.update({1:cTemp, 2:humidity, 3:pm25, 4:pm10})
        #print response
    except:
        print "connection failed"

#sleep for CYCLE seconds (api limit of 15 secs)
if __name__ == "__main__":
    channel = thingspeak.Channel(id=channel_id,write_key=write_key)
    while True:
        axp.gpio2_output = True
        print(time.strftime("\nCurrent Time: %d.%m.%Y %H:%M:%S"))
        read_SHT31()
        read_SDS011()
        doit(channel)
	axp.gpio2_output = False
        time.sleep(CYCLE)
