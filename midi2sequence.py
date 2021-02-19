# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:37:57 2021

@author: noahs
"""
import numpy as np
from mido import MidiFile

import fluidsynth 
import time
from os import listdir,path, walk
from mido_tools import MidoEncode, MidoUtils

#Parses a folder full of midi files
class Midi2Sequence:
    

    
    
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
        if(log):
            Midi2Sequence._logParsedMidi(mf)
        sequentializedMidi = self.midoEncode.encode(mf)
        return sequentializedMidi
    
    
    
   
    @staticmethod   
    def logParsedMido(mf):
        f = open('log.txt', 'w')
        for i, track in enumerate(mf.tracks):
            for msg in track:
                f.write(str(msg)+"\n")
        f.close()
                
                
                
    @staticmethod
    def _playParsedMido(mf):
        for i, track in enumerate(mf.tracks):
            for msg in track:
                if(msg.type == "note_on"):
                    if(msg.velocity != 0):
                        print(msg.note,msg.time)
                        fs.noteon(0, msg.note, 30)
                        time.sleep(msg.time/(96*8))
                    else:
                        fs.noteoff(0, msg.note)
                        time.sleep(msg.time/(96*8))
                if(msg.type == "note_off"):
                    fs.noteoff(0, msg.note)
                    time.sleep(msg.time/(96*8))



    
    




fs = fluidsynth.Synth()
fs.start()
sfid = fs.sfload("piano.sf2")
fs.program_select(0, sfid, 0, 0)




    
def testM2M():
    mf = MidiFile("data/someothermidis/bachmusic1.mid")
    Midi2Sequence.logParsedMido(mf)

testM2M()
    
    
    
def testParseFold():
    mf = Midi2Sequence("data")
    mf.parseMidis()
    MidoUtils.playEncodedMido(mf.sequentializedMidis[0])
    
testParseFold()
    

    



    
    
