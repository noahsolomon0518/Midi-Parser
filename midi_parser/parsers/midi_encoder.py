# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:45:41 2021

@author: noahs
"""

import fluidsynth
import time
from os import path, walk
import numpy as np
from ..helpers.one_track_encoder import NormalizedOTEncoder
import os
import warnings
from mido import MidiFile

sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/midi_parser/soundfonts/piano.sf2")

'''
###

--Helper functions--

###
'''



#Takes list of paths (or just one), and parses into mido object
def parseToMidos(paths):
    midos = []
    
    if(type(paths)!=list):
        paths = [paths]
        
    for _path in paths:
        midos.append(MidiFile(_path, type = 0))
        
    return midos





#Recursively creates list of midi files in directory
def findMidis(folder, r = True):
        paths = []
        if(".mid" in folder):
            paths.append(folder)
            return paths
            
        for (dirpath, dirnames, filenames) in walk(folder):
            for file in filenames:
                if ".mid" in file:
                    paths.append(path.join(dirpath,file))
            if not r:
                return paths
        return paths
            

#Encompasses entire process of encoding for NN,  from getting midi paths to one hot encoding
def pathsToOneHot(OTEncoder, OneHotEncoder):
    OTEncoder.encode()
    sequences = OTEncoder.encoded
    OneHotEncoder.encode(sequences)
    return (OneHotEncoder.xEncoded, OneHotEncoder.yEncoded)


'''
###

---Classes---

###
'''



#OneTrack object uses Note to simplify midi representation
class Note():
    def __init__(self, note, time, type, velocity):
        self.note = note
        self.time = time
        self.velocity = velocity
        if(velocity == 0):
            self.type = "note_off"
        else:
            self.type = type
    
    
    def copy(self):
        return Note(self.note, self.time, self.type, self.velocity)
        
    


# Dumbed down mido object with one track
class OneTrack:
    def __init__(self, mido):
        self.mido = mido
        self.notes = []
        self.notesAbs = [] 
        self.notesRel = [] 
        self._extractNotesAbs()
        self._convertToNotesRel()
        self.tpb = mido.ticks_per_beat
        
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




#Main class to be used. Takes in directory and parses all midis to encoded sequences
class OTEncoder:
    
    
    def __init__(self, folder, r = True, encodingMethod = 'normalizedOT'):
        self.midos = []
        self.oneTracks = []
        self.encoded = []
        self.paths = []
        self.addFolders(folder, r = True)
        self.encodingMethod = encodingMethod
        
        
    def addFolders(self, folder , r =True):
        self.paths.extend(findMidis(folder, r))
        
    def encode(self):
        self._pathsToMidos()
        self._midosToOT()
        self._OTEncode()
        
       
        
       
    def _pathsToMidos(self):
        self.midos = parseToMidos(self.paths)
        
    def _OTEncode(self):
        self.encoded = NormalizedOTEncoder(self.oneTracks).encodedOTs
        
    def _midosToOT(self):
        for mido in self.midos:
            self.oneTracks.append(OneTrack(mido))
            

    
    
    
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
                
                
                






#One hot encoder for recurrent neural networks
class OneHotEncoder:
    def __init__(self, sampleLength, gap, oneHotDimension):
        self.sampleLength = sampleLength
        self.gap = gap
        self.oneHotDimension = oneHotDimension
        self.xEncoded = []
        self.yEncoded = []
        
    def encode(self, sequences):
        for sequence in sequences:
            self.oneHotEncodeSequence(sequence)
        self.xEncoded = np.array(self.xEncoded)
        self.yEncoded = np.array(self.yEncoded)   
    
    
    def oneHotEncodeSequence(self,sequence):
        nSamples = self.getNSamples(sequence)
        for i in range(nSamples):
            xSample = sequence[i*self.gap:(i)*self.gap + self.sampleLength]
            ySample = sequence[(i)*self.gap + self.sampleLength]
            self.oneHotEncodeSample(xSample, ySample)
            
    
    
    def oneHotEncodeSample(self,x,y):
        xOneHot = np.zeros((self.sampleLength,self.oneHotDimension))
        yOneHot = np.zeros((self.oneHotDimension))
        
        if(y>=self.oneHotDimension):
                yOneHot[self.oneHotDimension-1] = 1
        else:
            yOneHot[y] = 1
        for i,sample in enumerate(x):
            if(sample>=self.oneHotDimension):
                warnings.warn("Encoded number > one hot vectors dimension")
                xOneHot[i][self.oneHotDimension-1] = 1
            else:
                xOneHot[i][sample] = 1
        self.xEncoded.append(xOneHot)
        self.yEncoded.append(yOneHot)
            
            
    def getNSamples(self, sequence):
        return (len(sequence)-self.sampleLength)//self.gap
    

    

            
    

        
        