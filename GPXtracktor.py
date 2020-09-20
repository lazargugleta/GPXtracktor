try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import * 
    from tkinter.ttk import *
    from tkinter import Label
#!/usr/bin/python
#Extract GPS data from video file of DOD car dashcam to GPX file.
#all the libraries used for the project
import os
import mmap
import struct
import binascii
from time import sleep
from termcolor import colored
from functools import partial

master = Tk()
master.geometry("350x150")

master.title("GPXtractor".center(10))

#progress bar
progress = Progressbar(master, orient = HORIZONTAL, 
              length = 100, mode = 'determinate')

#give starting value
progress['value'] = 0

def pronadji(finalLabel):
    n_chunk = 400 # each GPS data item is 32 bytes
    from tkinter.filedialog import askopenfilenames
    filenames = askopenfilenames()
    filename = list(filenames)
    #print(filename)
    #The GPS data segment start with freeGPS('\x66\x72\x65\x65\x47\x50\x53')
    data_prefix=b'freeGPS'
    item_prefix=b'$S'   #'\x24\x53'
    

    version =    '<?xml version="1.0" encoding="UTF-8"?>\n'
    version+=    '<gpx version="1.0" creator="DOD video to GPX - by lazar.gugleta@gmail.com" '
    version+=   'xmlns="http://www.topografix.com/GPX/1/0">\n'
    track_start='  <trk>\n    <name>{}</name>\n    <trkseg>\n'
    track_point ='      <trkpt lat="{}" lon="{}">\n'
    track_point+='        <time>{}-{:02}-{:02}T{}Z</time>\n'
    track_point+='        <speed>{}</speed>\n'
    track_point+='      </trkpt>\n'
    track_desc ='    <desc>Max Speed:{:.2f}km/h at time:{}</desc>\n'
    track_end=  '    </trkseg>\n  </trk>\n</gpx>\n'

    progress['value'] = 0
    sleep(0.5)

    nr_files = len(filenames)

    if (nr_files >= 1):
        finalLabel.pack_forget()
    

    for filename in filenames:
        
        with open(filename, "r+b") as f:
            try:
                mm = mmap.mmap(f.fileno(), 0)
            except OSError as e:
                print("OSError({0}): {1}".format(e.errno, e.strerror))
                print("The 32bit Python cannot handle huge .mov file")
                print("Please install the 64bit Python")
            else:
                start=0;
                maxSpeed=-1
                maxTime=""
                file_name, file_extension = os.path.splitext(filename)
                gpx_filename=file_name+'.gpx'
                gpx_file = open(gpx_filename, 'w')
                gpx_file.write(version+track_start.format(filename))
                master.update_idletasks()
                while True:
                    freegps=mm.find(data_prefix,start)
                    if freegps==-1: break
                    mm.seek(freegps)
                    start=freegps+6
                    #print(freegps)
                    buf=mm.read(n_chunk)
                    dataItem=0
                    while True:
                        dataItem=buf.find(item_prefix,dataItem)
                        if dataItem==-1: break
                        #24 53 00 00 10 8B year month day hour minute second latitude longtidue 10 00 00 00
                        gpsData=buf[dataItem+2:dataItem+25]
                        unknownData=buf[dataItem+4:dataItem+6]
                        #print(binascii.hexlify(bytearray(gpsData)))
                        dataItem=dataItem+2
                        speed,unknown1,year,month,day,hour,minute,second,unknown2,latitude,longitude,last=struct.unpack('!HhH4BHB2iH',gpsData)

                        if last!=4096: break
                        latitude=latitude/10000000.0
                        longitude=longitude/10000000.0
                        speed_mps=speed/100.0     #Meters per second
                        speed_kph=speed/100.0*3.6 #Kilometers per hour
                        strTime ='{:02}:{:02}:{:04.1f}'.format(hour,minute,second/10.0)
                        strSpeed='{:6.2f}km/h'.format(speed_kph)
                        #print(strTime+' '+strSpeed+' '+'{:<11}'.format(latitude)+' {:<11}'.format(longitude)+"   "+" ".join("{:02x}".format(c) for c in unknownData))
                        track_point_data =track_point.format(latitude,longitude,year,month,day,strTime,speed_mps)
                        gpx_file.write(track_point_data)
                        if speed_kph>maxSpeed:
                            maxSpeed=speed_kph
                            maxTime=strTime
                            #print(" ".join("{:02x}".format(c) for c in unknown)+' ' +s+' '+'{0:.2f}km/h'.format(speed))
                        break
                mm.close()
                gpx_file.write(track_desc.format(maxSpeed,maxTime))
                gpx_file.write(track_end)
                gpx_file.close()
                progress['value'] += 100/nr_files
                sleep(0.25)
                print("Max Speed:{:.2f}km/h".format(maxSpeed))
                print("Time:"+str(maxTime))
                print(colored("Video complete!", "green"))

    if (nr_files >= 1):
        finalLabel.pack()

                
#visual defines

a = Label(master, text="Obrada zavrsena!", bg="red")

progress.pack(pady = 10)

w = Label(master, text="Odaberi jedan ili vise videa da extract-ujes GPX file",width = 120)
w.pack()

b = Button(master, text="Izaberi", command=partial(pronadji, a),width = 10)
b.pack()

a = Label(master, text="Autor: Lazar Gugleta")
a.pack()

mainloop()
