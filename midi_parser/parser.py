# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:45:41 2021

@author: noahs
"""

import fluidsynth
import time
from os import path, walk


from .helpers.one_track_encoder import NormalizedOTEncoder
from .helpers.to_one_hot import ToOneHot
import os

from mido import MidiFile

sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/midi_parser/soundfonts/piano.sf2")

'''
###

--Helper functions--

###
'''




def parseToMidos(paths):
    midos = []
    
    if(type(paths)!=list):
        paths = [paths]
        
    for _path in paths:
        midos.append(MidiFile(_path, type = 0))
        
    return midos



def findMidis(folder, r = True):
        paths = []
        if(".mid" in folder):
            paths.append(folder)
            return
            
        for (dirpath, dirnames, filenames) in walk(folder):
            for file in filenames:
                if ".mid" in file:
                    paths.append(path.join(dirpath,file))
            if not r:
                break





class Note:
    def __init__(self, note, time, type, velocity):
        self.note = note
        self.time = time
        self.velocity = velocity
        if(velocity == 0):
            self.type = "note_off"
        else:
            self.type = type
        
    


### Dumbed down mido object with one track

class OneTrack:
    def __init__(self, mido):
        self.mido = mido
        self.notes = []
        self.notesAbs = self._extractNotesAbs()
        self.notesRel = self._convertToNotesRel()
        self.tpb = self.ticks_per_beat
        
    def _extractNotesAbs(self):
        
        
        for track in self.mido.tracks:
            _time = 0
            for msg in track:
                _time+=msg.time
                if(msg.type=="note_on" or msg.type == "note_off"):
                    self.notesAbs.append(Note(msg.note, 
                                           _time,
                                           msg.type,
                                           msg.velocity))
                
        
        self.notesAbs.sort(key = lambda x: x.time)
        
    
    def _convertToNotesRel(self):
        notesAbs = self.notesAbs
        firstNote = notesAbs[0]
        firstNote.time = 0
        self.notesRel.append(firstNote)
        
        
        for i in range(len(notesAbs[1:])-1):
            currentNote = notesAbs[i+1]
            previousNote = notesAbs[i]
            deltaTime = currentNote.time - previousNote.time
            currentNoteCopy = currentNote.copy()
            currentNoteCopy.time = deltaTime
            self.notesRel.append(currentNoteCopy)







'''
###

--Parser Class--

###
'''


class Parser:
    
    
    def __init__(self, folder, r = True, encodingMethod = 'normalizedOT'):
        self.midos = []
        self.oneTracks = []
        self.encoded = []
        self.x = None
        self.y = None
        self.paths = []
        self.addFolders(folder, r = True)
        self.encodingMethod = encodingMethod
        
        
    def addFolders(self, folder , r =True):
        self.paths.extend(Parser.findMidis(folder, r))
        
    def parse(self, maxLen, gap, maxDim):
        self.midos = parseToMidos(self.paths)
        
        self._midosToOT(self.midos)
        
        
        self.encoded = NormalizedOTEncoder(self.oneTracks).encodedOTs
        
        
        
        oneHot = ToOneHot(maxLen, gap, maxDim)
        oneHot.fit(self.encoded)
        
        
        
        
        self.x = oneHot.xEncoded
        self.y = oneHot.yEncoded
        
        
    def _midosToOT(self):
        for mido in self.midos:
            self.oneTracks.append(OneTrack(mido))
            
            
            
            
            
            
            
        
    def getData(self):
        return (self.x,self.y)
    
    
    
    def playEncoded(self, ind):
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in self.encoded[ind]:
            if(msg>=176):
                time.sleep((msg-175)*0.03)
            elif(msg>88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)
                
                
                





    

            
    

        
        