# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 11:43:08 2021

@author: noahs
"""

import fluidsynth 
import time         
import os



sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/midi_parser/soundfonts/piano.sf2")

def playEncodedMido(encMido):
    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload(sf2)
    fs.program_select(0, sfid, 0, 0)
    for msg in encMido:
        if(msg>=176):
            time.sleep((msg-175)*0.005)
        elif(msg>88):
            fs.noteon(0, msg-88, 100)
        else:
            fs.noteoff(0, msg)


 


#ticks per beat/8 = 32nd notes

def encodeNote(note, tpb):
    norm = tpb/64
    print("ISTHISWORKING")
    normalizedDT = note.deltaTime/norm
    if(normalizedDT>=0.5):
        normalizedDT = round(normalizedDT)
    elif(normalizedDT>0):
        normalizedDT = 1
    else:
        normalizedDT = 0
        
    waitTime = []
    waitTime = [175+normalizedDT] if normalizedDT>0 else []
    if(note.isNoteOn):
        
        if(note.velocity==0):
            waitTime.append(note.note)
            return waitTime
        else:
            waitTime.append(note.note+88)
            return waitTime
    else:
        waitTime.append(note.note)
        return waitTime

    


