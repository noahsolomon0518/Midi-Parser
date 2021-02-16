# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 15:30:16 2021

@author: noahs
"""


f = open('fullpiece.txt', 'w')


tracks = Midi2Matrix.parseTrack('data/bwv806a.mid')
for track in tracks:
    track.parse()
    
    for note in track:
        
        f.write(str(note)+": HEADER:"+str(note.header))
        if(note.header!=255):
            f.write(" CHANNEL:"+str(note.channel))
            f.write(" DATA:"+str(note.data))
        f.write("\n")
        print(note)
f.close()
 


#Testing
def MIDITest():
    piece = Mfile("data/bwv772.mid")
    piece.parse()
    print(piece)
    for track in piece:
        track.parse()
        print(track)
        
file = open("data/bwv806a.mid", "rb")

byte = file.read(1)
while byte:

    print(byte.hex())
    byte = file.read(1)
  
