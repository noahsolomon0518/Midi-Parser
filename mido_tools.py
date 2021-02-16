# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 11:43:08 2021

@author: noahs
"""
from mido import MidiFile
import numpy as np
import fluidsynth 


    
    
class NoahsOneTrackMidi:
    def __init__(self, mido):
        self.tPB = mido.ticks_per_beat
        self.oneTrack = self.restructToOneTrack(mido)
        self.timing = "abs"
        
    
    def findTempo(self, mido):
        for track in mido.tracks:
            for msg in track:
                if(msg.type=="tempo"):
                    return msg.tempo
            return 500000
        
    
    
    def restructToOneTrack(self, mido):
        
        absoluteTiming = []
        for track in mido.tracks:
            _time = 0
            for msg in track:
                _time+=msg.time
                if(msg.type=="note_on" or msg.type == "note_off"):
                    absoluteTiming.append([msg, _time])
                    
        absoluteTiming.sort(key = lambda x: x[1])
        self.midi = absoluteTiming
        
        
    def absTimeToRel(self):
        assert self.timing == "abs"
        relTime = []
        absTime = self.midi.copy()
        relTime.append(absTime[0])
        for i, value in enumerate(absTime[1:]):
            newDeltaTime = absTime[i+1][1] - absTime[i][1]
            relTime.append([absTime[i+1][0], newDeltaTime])
        
        self.midi = relTime
        print(relTime[20], self.midi[20])
        self.timing = "rel"
        
    def relTimeToAbs(self):
        assert self.timing == "rel"
        
#Takes a reconstructed mido object and encodes it to 
class MidoEncode:
    
    #Takes in mido object then restructures into 1 track without delta time bs
    def encode(self, mf):
        oneTrackMidi = NoahsOneTrackMidi(mf)
        oneTrackMidi.absTimeToRel()
        encodedMido = []
        for msg in oneTrackMidi.midi:
            encNote = MidoUtils.encodeNote(msg, oneTrackMidi.tPB)
            encodedMido.extend(encNote)
        return encodedMido
    
    

        
import time         
class MidoUtils:
    
    @staticmethod
    def playEncodedMido(encMido):
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload("piano.sf2")
        fs.program_select(0, sfid, 0, 0)
        for msg in encMido:
            if(msg>=176):
                time.sleep((msg-175)*0.05)
            elif(msg>88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)
    
    
     
    


    @staticmethod
    def encodeNote(msg, tpb):
        norm = tpb/8
        waitTime = []
        msgObj = msg[0]
        msgDeltaTime = msg[1]
        normalizedDT = round(msgDeltaTime/norm)
        waitTime = [175+normalizedDT] if normalizedDT>0 else []
        if(msgObj.type=="note_on"):
            
            if(msgObj.velocity==0):
                waitTime.append(msgObj.note)
                return waitTime
            else:
                waitTime.append(msgObj.note+88)
                return waitTime
        else:
            waitTime.append(msgObj.note)
            return waitTime
    
        

        
        
    
    
    
    
    
import inspect
   
class MidoRestructTest:
    @staticmethod   
    def testPassed():
        print(str(inspect.stack()[1][3])+": " + "PASSED")
        
        
    @staticmethod
    def getTestMido():
        return MidiFile('data/someothermidis/bachmusic2.mid')
    
    
    @staticmethod
    def encodeTest():
        testMido = MidoRestructTest.getTestMido()
        mr = MidoEncode(True, 8)
        enc = mr.encode(testMido)
        MidoUtils.playEncodedMido(enc)
        

    
        MidoRestructTest.testPassed()
        
       
        

        
        
 
        
        
    
    
    
    
#MidoRestructTest.encodeTest()
#MidoRestructTest.restructLengthOfTrackTest()
