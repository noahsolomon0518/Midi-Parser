# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:37:57 2021

@author: noahs
"""
from mido import MidiFile
from . import mido_tools
from os import path, walk
from .mido_encode import MidoEncode

#Parses a folder full of midi files
class MidiToSequence:
    

    
    
    def __init__(self,folder, r = True ):
        self.folder = folder
        self.midoEncode = MidoEncode()
        self.midiPaths = []
        self.sequentializedMidis = []
        self.addMidis(self.folder, r = r)
        
        
        
    #Function that parses all queued midis
    def parseMidis(self):
        for midi in self.midiPaths:
            self.sequentializedMidis.append(self.parseTrack(midi))
            
        
        
   
               

    def addMidis(self, folder, r):
        for (dirpath, dirnames, filenames) in walk(folder):
            print("Midis to be parsed from directory \""+dirpath+"\":")
            for file in filenames:
                if ".mid" in file:
                    print(path.join(dirpath, file))
                    self.midiPaths.append(path.join(dirpath,file))
            if not r:
                break
            print("\n")
             
    
        
    #Parses one midi file. Takes argument as file path
    def parseTrack(self,file, log = False):
        assert ".mid" in file
        print("Parsing", file)
        mf = MidiFile(file)
        sequentializedMidi = self.midoEncode.encode(mf)
        return sequentializedMidi
    @staticmethod
    def logParsing(file):
        mf = MidiFile(file)
        
        f = open("log.txt", "w")
        for track in mf.tracks:
            for msg in track:
                f.write(str(msg)+"\n")
                
                
                
def testParseFold():
    mf = MidiToSequence("data")
    mf.parseMidis()
    mido_tools.playEncodedMido(mf.sequentializedMidis[0])
    
#testParseFold()
    

    



    
    
