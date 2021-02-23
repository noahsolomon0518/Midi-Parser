# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:32:25 2021

@author: noahs
"""


def encodeOneTrackMidi(self, oneTrackMidi):
    oneTrackMidi.absTimeToRel()
    encodedMido = []
    for note in oneTrackMidi.midi:
        encNote = encodeNote(note, oneTrackMidi.tPB)
        encodedMido.extend(encNote)
    return encodedMido




def encodeNote(note, tpb):
    norm = tpb/64
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

    