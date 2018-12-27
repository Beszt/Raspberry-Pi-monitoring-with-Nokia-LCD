'''
	Original codes:
	Nokia 5110 LCD setup: http://www.electronicwings.com
	Raspberry monitoring https://www.raspberrypi.org/forums/viewtopic.php?t=22180
'''
import os, time
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list                                        
# Index 0: total RAM                                                                
# Index 1: used RAM                                                                 
# Index 2: free RAM                                                                 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string                                
def getCPUuse():
    cpuStats = open("/proc/stat", "r").readline()
    columns = cpuStats.replace("cpu", "").split(" ")
    cpulist1 = map(int, filter(None, columns))
    time.sleep(0.5)
    cpuStats = open("/proc/stat", "r").readline()
    columns = cpuStats.replace("cpu", "").split(" ")
    cpulist2 = map(int, filter(None, columns))
    dt = list((t2-t1) for t1, t2 in zip(cpulist1, cpulist2))
    idle_time = float(dt[3])
    total_time = sum(dt)
    cpu_percent = round((((total_time-idle_time)/total_time)*100)/1)
    return cpu_percent

# Return information about disk space as a list (unit included)                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0


# Hardware SPI usage:
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

# Initialize library.
disp.begin(contrast=30)

# Clear display.
disp.clear()
disp.display()

font = ImageFont.load_default()

# Load image and convert to 1 bit color.
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

while True:
    # CPU informatiom
    CPU_temp = int(float(getCPUtemperature()))
    CPU_usage = getCPUuse()

    # RAM information
    # Output is in kb, here I convert it in Mb for readability
    RAM_stats = getRAMinfo()
    RAM_total = round(int(RAM_stats[0]) / 1000,1)
    RAM_used = round(int(RAM_stats[1]) / 1000,1)
    RAM_free = round(int(RAM_stats[2]) / 1000,1)
    RAM_percent = int((RAM_used / 945.5) * 100)

    # Disk information
    DISK_stats = getDiskSpace()
    DISK_total = DISK_stats[0]
    DISK_free = DISK_stats[1]
    DISK_percent = DISK_stats[3]
    
    #Draw informations
    draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
    draw.text((1,7), 'CPU: ' + str(CPU_usage) + '%, ' + str(CPU_temp) + 'C', font=font)
    draw.text((1,18), 'RAM: ' + str(RAM_percent) + '%', font=font)
    draw.text((1,30), 'HDD: ' + str(DISK_percent), font=font)

    #Display Image
    disp.image(image)
    disp.display()
    time.sleep(1)
