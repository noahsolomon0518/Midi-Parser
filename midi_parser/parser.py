# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:45:41 2021

@author: noahs
"""

import fluidsynth
import time
from .helpers.midi_path_extractor import MidiPathExtractor
from .helpers.midi_to_mido import MidiToMido
from .helpers.mido_to_one_track import MidoToOT
from .helpers.one_track_encoder import NormalizedOTEncoder
from .helpers.to_one_hot import ToOneHot
import os



sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/midi_parser/soundfonts/piano.sf2")

class Parser:
    
    
    def __init__(self, folder, encodingMethod = 'normalizedOT'):
        self.midos = None
        self.oneTracks = None
        self.encoded = None
        self.x = None
        self.y = None
        self.pathExtractor = MidiPathExtractor(folder)
        self.encodingMethod = encodingMethod
        
        
    def addFolders(self, folder , r =True):
        self.pathExtractor.addMidis(folder, r)
        
    def parse(self, maxLen, gap, maxDim):
        self.midos = MidiToMido(self.pathExtractor.midiPaths).midos
        
        self.oneTracks = MidoToOT(self.midos).oneTracks
        self.encoded = NormalizedOTEncoder(self.oneTracks).encodedOTs
        oneHot = ToOneHot(maxLen, gap, maxDim)
        oneHot.fit(self.encoded)
        self.x = oneHot.xEncoded
        self.y = oneHot.yEncoded
        
        
        
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
            
        
            
            
        
        
        