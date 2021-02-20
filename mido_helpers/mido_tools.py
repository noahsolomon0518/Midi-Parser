# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 11:43:08 2021

@author: noahs
"""

import fluidsynth 
import time         


def playEncodedMido(encMido):
    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload("soundfonts/piano.sf2")
    fs.program_select(0, sfid, 0, 0)
    for msg in encMido:
        if(msg>=176):
            time.sleep((msg-175)*0.05)
        elif(msg>88):
            fs.noteon(0, msg-88, 100)
        else:
            fs.noteoff(0, msg)


 


#ticks per beat/8 = 32nd notes

def encodeNote(note, tpb):
    norm = tpb/8
    normalizedDT = round(note.deltaTime/norm)
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

    


