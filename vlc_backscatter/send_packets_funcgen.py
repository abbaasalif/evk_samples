import pyvisa as visa
import time
import binascii
# resource of Device
device_resource = 'USB0::0xF4ED::0xEE3A::SDG10GAD1R1965::INSTR'
d7 = '000011110000' # Data stream of ch7 in digital
d6 = '101010101010' # Data stream of ch6 in digital
d5 = '010101010101' # Data stream of ch5 in digital
d4 = '110011001100' # Data stream of ch4 in digital
d3 = '000000111111' # Data stream of ch3 in digital
d2 = '111000111000' # Data stream of ch2 in digital
d1 = '001100110011' # Data stream of ch1 in digital
d0 = '110011001100' # Data stream of ch0 in digital
other = '00000000' # The last 8ch data is 0
wave_points = []
for i7, i6, i5, i4, i3, i2, i1, i0 in zip(d7, d6, d5, d4, d3, d2, d1, d0):
    a = i7 + i6 + i5 + i4 + i3 + i2 + i1 + i0 + other
    wave_points.append(int(a, 2))
def create_wave_file():
    f = open("wave1.bin", "wb")
    for a in wave_points:
        b = hex(a)
        b = b[2:]
        len_b = len(b)
        if 0==len_b:
            b = '0000'
        elif 1==len_b:
            b = '000' + b
        elif 2==len_b:
            b = '00' + b
        elif 3==len_b:
            b = '0' + b
        c = binascii.unhexlify(b)
        f.write(c)
    f.close()

def send_wave_data(dev):
    """send wave1.bin to the device"""
    f = open("wave1.bin", "rb") # open the wave file
    data = f.read()
    print('write bytes:%s'%len(data))
    dev.write("C1:WVDTWVNM,wave1,FREQ,2000.0,AMPL,5.001,OFST,2.5,PHASE,0.0,WAVEDATA,%s" % (data))
    dev.write("C1:ARWV NAME,wave1")
    f.close()

def get_wave_data(dev):
    """get wave from the device"""
    f = open("wave2.bin", "wb")
    dev.write("WVDT? user,wave1")
    time.sleep(1)
    data = dev.read()
    data_pos = data.find("WAVEDATA,") + len("WAVEDATA,")
    print(data[0:data_pos])
    wave_data = data[data_pos:]
    print('read bytes:%s'%len(wave_data))
    f.write(wave_data)
    f.close()

if __name__ == '__main__':
    rm = visa.ResourceManager()
    device = rm.open_resource(device_resource, timeout=50000, chunk_size=24*1024*1024)
    create_wave_file()
    send_wave_data(device)
    #get_wave_data(device)
    device.close()
    rm.close()