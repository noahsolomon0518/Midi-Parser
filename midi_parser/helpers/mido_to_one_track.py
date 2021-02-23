# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 12:21:38 2021

@author: noahs
"""


class OneTrack:
    def __init__(self, notes, tpb):
        self.notes = notes
        self.tpb = tpb



class OTMidoAbsolute:
    def __init__(self, mido):
        self.notes = []
        self.ticks_per_beat = mido.ticks_per_beat
        self.oneTrack = self.toOneTrack(mido)
    
        
    #notesType1: notes where relative time is measured in terms of track
    #notesType0: notes where relative time measured in terms of all tracks
    def toOneTrack(self, mido):
        
        
        for track in mido.tracks:
            _time = 0
            for msg in track:
                _time+=msg.time
                if(msg.type=="note_on" or msg.type == "note_off"):
                    self.notes.append({"note": msg.note, 
                                  "time": _time,
                                  "type": msg.type,
                                  "velocity": msg.velocity})
                
        
        self.notes.sort(key = lambda x: x['time'])
        
        
        
class OTMidoRelative:
    def __init__(self, oneTrackAbsolute):
        self.notes = []
        self.absTimeToRel(oneTrackAbsolute)
        
        
    def absTimeToRel(self, oneTrackAbsolute):
        absTime = oneTrackAbsolute.notes
        firstNote = absTime[0]
        firstNote['time'] = 0
        self.notes.append(firstNote)
        
        
        for i in range(len(absTime[1:])-1):
            currentNote = absTime[i+1]
            previousNote = absTime[i]
            deltaTime = currentNote['time'] - previousNote['time']
            currentNoteCopy = currentNote.copy()
            currentNoteCopy['time'] = deltaTime
            self.notes.append(currentNoteCopy)
        
        
        
        
        
        
        
class MidoToOT:
    def __init__(self, midos):
        self.oneTracks = []
        self.allToOneTracks(midos)
        
    def allToOneTracks(self, midos):
        if(type(midos)!= list):
            midos = [midos]
        for mido in midos:
            self.oneToOneTrack(mido)
            
            
    def oneToOneTrack(self, mido):
        otAbs = OTMidoAbsolute(mido)
        otRel = OTMidoRelative(otAbs)
        self.oneTracks.append(OneTrack(otRel.notes, mido.ticks_per_beat))
    