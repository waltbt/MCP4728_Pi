#!/usr/bin/env python3

import MCP4728 as MCP

mcp = MCP.MCP4728(0x61) # Default address is 0x60
mcp.fast_write_DAC_voltages([2.1, 0., 3.5, 4.0]) # Sets all 4 channels of the DAC

mcp.multi_write([0.5, 3.2, 1.8, 2.5]) # Sets all 4 channels of the DAC

print(mcp.get_dac_voltage())
print(mcp.get_eeprom_voltage())
