#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
import visa
import time

# USB resource of Device
device_resource = 'USB0::0xF4ED::0xEE3A::SDG10GAD1R1965::INSTR'

# Waveform data: Little endian, 16-bit 2's complement
wave_points = [0x0080, 0x0070, 0x0060, 0x0040, 0x0050, 0x0060, 0x0070, 0xff7f, 0x0050]

def create_wave_file():
    """Create a file with waveform data."""
    with open("wave1.bin", "wb") as f:
        for point in wave_points:
            # Ensure the value is treated as a signed 16-bit integer
            if point > 0x7FFF:
                # Convert to a signed integer
                point -= 0x10000
            # Convert each point to bytes and write to the file
            f.write(point.to_bytes(2, byteorder='little', signed=True))

def send_wave_data(device):
    """Send wave1.bin to the device."""
    with open("wave1.bin", "rb") as f:
        data = f.read()
        print('write bytes:', len(data))
        # Use write_binary_values for binary data. Adjust command as needed.
        device.write_binary_values("C1:WVDT WVNM,wave1,FREQ,5000,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,", data, datatype='B')
        device.write("C1:ARWV NAME,wave1")

# Main execution
if __name__ == '__main__':
    rm = visa.ResourceManager()
    device = rm.open_resource(device_resource, timeout=50000, chunk_size=24*1024*1024)
    create_wave_file()
    send_wave_data(device)
    # Optionally, enable get_wave_data(device) if needed
    device.close()
