# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:45:41 2021

@author: noahs
"""

import fluidsynth
import time
from os import path, walk

from .helpers.midi_path_extractor import MidiPathExtractor
from .helpers.midi_to_mido import MidiToMido
from .helpers.mido_to_one_track import MidoToOT
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








'''
###

--Parser Class--

###
'''


class Parser:
    
    
    def __init__(self, folder, r = True, encodingMethod = 'normalizedOT'):
        self.midos = None
        self.oneTracks = None
        self.encoded = None
        self.x = None
        self.y = None
        self.paths = []
        self.addFolders(folder, r = True)
        self.encodingMethod = encodingMethod
        
        
    def addFolders(self, folder , r =True):
        self.paths.extend(Parser.findMidis(folder, r))
        
    def parse(self, maxLen, gap, maxDim):
        self.midos = parseToMidos(self.paths)
        
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
                
                
                





    

            
    

        
        