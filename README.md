# MCP4728 12-bit Four Channel DAC
The MCP4728 is a 12-bit, four channel Digital-to-Analog (DAC) converter.  It runs on I2C and can be reprogramed with 8 different addresses.  It has an accurate internal reference voltage and programable gain.  

## Python code for the Raspberry Pi
This is a very basic program to allow you to use the MCP4728 with a Raspberry Pi. It does not have any special features, but can easily be modified to include them.  It was tested on Python 3.10, but should easily work with later versions of Python.  It is coded assuming that the internal reference voltage and x2 gain are used to give a range of 0-4.096V.

## SMBus
This program uses smbus.  Any recent version is likely to work as only basic functions are used.  

## Changing the Address
Changing the I2C address is not a simple exercise.  It requires requires carefully timed writes while manipulating the LDAC pin value.  

This project is licensed under the terms of the MIT license.
