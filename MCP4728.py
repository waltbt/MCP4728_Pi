#!/usr/bin/env python3

"""
MCP4728.py
Function: A simple class to operate an MCP4728 DAC on an RPi with Python
Author: Benjamin Walt
Date: 10/29/2022
Version: 0.1
Copyright (c) Benjamin Thomas Walt
Licensed under the MIT license.
"""


import smbus
import time

class MCP4728:

	def __init__(self, address=0x60):
		self._bus = smbus.SMBus(1) # Channel = 1
		self._address = address
		self.sequential_write_EEPROM([0.0, 0.0, 0.0, 0.0])
		self.set_x2_gain(True) # This code assumes x2 gain
		self.set_internal_voltage_reference(True) # This code assumes the internal reference voltage is used

	def _write_reg(self, value):
		"""Write a block of data, no registers are used"""
		self._bus.write_i2c_block_data(self._address, value[0], value[1:]) # First entry takes place of register
	
	def _read_reg(self, length):
		"""Read a block of data, no registers are used"""
		return self._bus.read_i2c_block_data(self._address, 0, length) #No registers, so 0 is offset

	def fast_write_DAC_voltages(self, voltages):
		"""Alternate write command that does not write to EEPROM. Gain and internal reference voltage must be set beforehand"""
		msg = []
		for value in voltages:
			digital_val = int((value/4.095*4095)) # Create a value between 0 and 4095
			digital_val = max(0, min(4095, digital_val))
			# Shift everything left by 8 bits and separate bytes
			upper = (digital_val & 0x0f00) >> 8 # Upper data bits (C2|C1|PD1|PD0|D11|D10|D9|D8)
			# C2|C1|PD1|PD0 Are all zero here, which is what we want
			lower = (digital_val & 0xff) # Lower data bits (D7|D6|D5|D4|D3|D2|D1|D0)
			msg.append(upper)
			msg.append(lower)
		self._write_reg(msg)

	def sequential_write_EEPROM(self, voltages):
		"""This changes the output voltages of the DAC.  It also writes to the
		registers and is persistant over power downs. There is a limited number
		of times to write to the registers, so it is better to use
		fast_write_DAC_voltages"""
		msg = [0x50] # 0b01010000 Start at Channel A
		for value in voltages:
			digital_val = int((value/4.095*4095)) # Create a value between 0 and 4095
			digital_val = max(0, min(4095, digital_val))
			# Shift everything left by 8 bits and separate bytes
			upper = (digital_val & 0x0f00) >> 8 # Upper data bits (Vref|PD1|PD0|Gx|D11|D10|D9|D8)
			# Set Vref|PD1|PD0|Gx
			upper |= 0x90 # 1|0|0|1|D11|D10|D9|D8 VRef: Internal, Gain: x2
			lower = (digital_val & 0xff) # Lower data bits (D7|D6|D5|D4|D3|D2|D1|D0)
			msg.append(upper)
			msg.append(lower)
		self._write_reg(msg)
		time.sleep(0.1) #Need time for the previous command to write to the EEPROM
	
	def multi_write(self, voltages):
		"""This changes the output voltages of the DAC.  It does not change the EEPROM"""
		msg_hdr = [0x40,2,4,6] # 0b01000000 Start at Channel A
		msg = []
		itr = 0
		for value in voltages:
			digital_val = int((value/4.095*4095)) # Create a value btween 0 and 4095
			digital_val = max(0, min(4095, digital_val))
			# Shift everything left by 8 bits and separate bytes
			upper = (digital_val & 0x0f00) >> 8 # Upper data bits (Vref|PD1|PD0|Gx|D11|D10|D9|D8)
			# Set Vref|PD1|PD0|Gx
			upper |= 0x90 # 1|0|0|1|D11|D10|D9|D8 VRef: Internal, Gain: x2
			lower = (digital_val & 0xff) # Lower data bits (D7|D6|D5|D4|D3|D2|D1|D0)
			msg.append(msg_hdr[itr])
			msg.append(upper)
			msg.append(lower)
			itr += 1
		self._write_reg(msg)

	"""
	Aborts current conversion
	Internal reset
	After reset, EEPROM values loaded into DAC
	"""
	def general_call_reset(self):
		"""General Call Reset"""
		self._bus.write_byte(0x00, 0x06)
	
	"""
	Resets power down bits to Normal Mode 0,0 in the DAC
	"""
	def general_call_wake_up(self):
		"""General Call Wake-Up"""
		self._bus.write_byte(0, 0x09)


	def get_dac_voltage(self):
		"""Returns an array of the current voltage settings"""
		voltage = []
		data = self._read_reg(24)
		for itr in [0,6,12,18]:
			top = (data[1+itr]& 0x0f) << 8
			bottom = data[2+itr]
			voltage.append(4.095*(top+bottom)/4095)
		return voltage
	
	def get_eeprom_voltage(self):
		"""Returns an array of the current voltage settings"""
		voltage = []
		data = self._read_reg(24)
		for itr in [0,6,12,18]:
			top = (data[4+itr]& 0x0f) << 8
			bottom = data[5+itr]
			voltage.append(4.095*(top+bottom)/4095)
		return voltage
	
	def get_dac_gain(self):
		"""Gets x2 gain (1) or x1 gain (0)"""
		gain = []
		data = self._read_reg(24)
		for itr in [0,6,12,18]:
			Gx = (data[1+itr] >> 4) & 0x01
			gain.append(Gx)
		return gain
	
	def get_dac_internal_voltage_reference(self):
		"""Gets internal reference voltage 2.048V (1) or VCC (0)"""
		ref_voltage = []
		data = self._read_reg(24)
		for itr in [0,6,12,18]:
			Vref = (data[1+itr] >> 7) & 0x01
			ref_voltage.append(Vref)
		return ref_voltage
		
	def set_x2_gain(self, status):
		"""Sets x2 gain (True) or x1 gain (False) for all channels"""
		_SET_GAIN_X2 = 0xcf #0b11001111
		_CLEAR_GAIN_X2 = 0xc0 #0b11000000
		if status:
			self._write_reg([_SET_GAIN_X2])
		elif not status:
			self._write_reg([_CLEAR_GAIN_X2])
		else:
			print("Error setting gain")

	def set_internal_voltage_reference(self, status):
		"""Sets internal reference voltage 2.048V (True) or VCC (False) for all channels"""
		_SET_INT_REF = 0x8f #0b10001111
		_CLEAR_INT_REF = 0x80 #0b10000000
		if status:
			self._write_reg([_SET_INT_REF])
		elif not status:
			self._write_reg([_CLEAR_INT_REF])
		else:
			print("Error setting reference voltage")
	

