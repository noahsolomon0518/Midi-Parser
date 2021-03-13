# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:45:41 2021

@author: noahs
"""

import keras
import fluidsynth
import time
from os import path, walk
import numpy as np
import os
import warnings
from mido import MidiFile

sf2 = os.path.abspath(
    "C:/Users/noahs/Local Python Libraries/soundfonts/piano.sf2")

'''
###

--Helper functions--

###
'''


# Takes list of paths (or just one), and parses into mido object
def parseToMidos(paths):
    midos = []

    if(type(paths) != list):
        paths = [paths]

    for _path in paths:
        midos.append(MidiFile(_path, type=0))

    return midos


# Recursively creates list of midi files in directory
def findMidis(folder, r=True):
    paths = []
    if(".mid" in folder):
        paths.append(folder)
        return paths

    for (dirpath, dirnames, filenames) in walk(folder):
        for file in filenames:
            if ".mid" in file:
                paths.append(path.join(dirpath, file))
        if not r:
            return paths
    return paths


# Encompasses entire process of encoding for NN,  from getting midi paths to one hot encoding
def pathsToOneHot(MidiToDecimal, OneHotEncoder):
    sequences = MidiToDecimal.encode()
    OneHotEncoder.encode(sequences)
    return (OneHotEncoder.xEncoded, OneHotEncoder.yEncoded)


'''
###

---Classes---

###
'''


# OneTrack object uses Note to simplify midi representation
class Note:
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







class OneTrack:

    def __init__(self, mido, convertToC = True, scales = "both"):
        self.mido = mido
        self.convertToC = convertToC
        self.scales = scales
        self.key = None
        self.tpb = mido.ticks_per_beat
        self.notesAbs = []
        self.notesRel = []
        self._extractNotesAbs()

    


        #Only does full conversion if valid. Otherwise self.noteRel=[] and is not parsed
        if(self._isValid()):
            self.needKey = (self.convertToC == True or self.scales != "both")
            self.halfStepsAboveC = OneTrack.halfStepsAboveC[self.key.replace("m", "")]
            self.halfStepsBelowC = 14 - OneTrack.halfStepsAboveC[self.key.replace("m", "")]
            self._convertToNotesRel()

    

    def _isValid(self):
        if(self.key==None and (self.convertToC == True or self.scales != "both")):
            return False
        if(self.scales=="major" and "m" in self.key):
            return False
        if(self.scales=="minor" and "m" not in self.key):
            return False
        return True

    halfStepsAboveC = {
        "C":0,
        "B#":0,
        "Db":1,
        "C#":1,
        "D":2,
        "Eb":3,
        "D#":3,
        "Fb":4,
        "E":4,
        "E#":5,
        "F":5,
        "F#":6,
        "Gb":6,
        "G":7,
        "G#":8,
        "Ab":8,
        "A":9,
        "A#":10,
        "Bb":10,
        "B":11
    }



    def _extractNotesAbs(self):

        for track in self.mido.tracks:
            _time = 0
            for msg in track:
                if(msg.type == "key_signature"):
                    self.key = msg.key
                   
                _time += msg.time
                if(msg.type in ["note_on","note_off"]):
                    self.notesAbs.append(Note(msg.note,
                                              _time,
                                              msg.type,
                                              msg.velocity))

        self.notesAbs.sort(key=lambda x: x.time)


    #mode can either be "on-off" or "on".  If "on-off" sees note off as distinct note. Other wise records time relative to how long note played
    def _convertToNotesRel(self):
        notesAbs = self.notesAbs.copy()
        firstNote = notesAbs[0]
        firstNote.time = 0
        self.notesRel.append(firstNote)

        for i in range(len(notesAbs[1:])-1):
            currentNote = notesAbs[i+1]
            previousNote = notesAbs[i]
            deltaTime = currentNote.time - previousNote.time
            
            currentNoteCopy = currentNote.copy()
            if(self.convertToC):
                currentNoteCopy.note = self.convertNoteToC(currentNoteCopy.note) 
            currentNoteCopy.time = deltaTime
            self.notesRel.append(currentNoteCopy)


    def convertNoteToC(self, note):
        newNote = note - self.halfStepsBelowC
        if((note>87 and newNote<88) or newNote<0):
            newNote = note + self.halfStepsAboveC
        return newNote

#Calculates time between each note and encodes it.
class OneTrackOnOnly(OneTrack):

    def __init__(self, mido, convertToC = True, scales = "both"):
        super().__init__(mido, convertToC = True, scales = "both")
        self.notesTimed = []
        self._calculateNoteOns()

    def _calculateNoteOns(self):
        for i, note in enumerate(self.notesRel):
            if(note.time>0):
                self.notesTimed.append(Note(88, note.time, "time_unit", 80))
            if(note.type == "note_on"):
                
                noteNum = note.note
                dt = 0
                for nextNote in self.notesRel[i:]:
                    if(nextNote.type == "note_off" and nextNote.note == noteNum):
                        break
                    dt+=nextNote.time 
                self.notesTimed.append(Note(note.note, dt, "note_on", 80))
                
                

    
"""
##

--MidiToDecimal--

##


--Purpose--
Takes midi file paths and parses them to some type of decimal encoding. After this classes is used, it is assumed that
they encoded sequences will be one hot encoded.

--Parameters--
folder: Folder to get midis
debug: Whether or not all data should be stored in memory to allow easier debugging. DO NOT USE WHEN PARSING A LOT OF MIDIS
r: If true, recursively find all midis in a folder
convertToC: Convert keys of midis to C. As a result midis without keys will not be parsed
scales: Whether to accept major, minor, or both scales. Only used if convertToC is True. Options are "both", "major", "minor"
method: Method of encoding. Three different types

    1. "on_only": Each note on is encoded as its repective note 0-87. 88 represents waittime. After each signal encoding
                  the duration of the note in terms of time units is then recorded. This method worked OK, but it is
                  hard for a LSTM to differentiate between signal notes and durations. 

    2. "on_and_off": Note offs encoded as 0-87 and note ons encodeds as 88-175. Waiting times recorded as 176-<175+maxTimeUnit>
                     The high dimensions make this approach not too effective. 
    
    3. "multi_network": Similar approach of "on_only" but returns 2 lists of notes/waiting time and durations for each midi
                        This method is used with the assumption that a neural network which predicts a time duration,
                        then using that prediction, predicts a note. By far is the most direct, simple and effective
                        method. For one hot encoding use OneHotEncodeMultiNet.

"""

class MidiToDecimal:

    def __init__(self, folder, debug=False, r=True, convertToC = True,  scales = "both", method = "on_and_off"):
        self.convertToC = convertToC
        self.scales = scales
        self.midos = []
        self.method = method
        self.oneTracks = []
        self.encoded = []
        self.paths = []
        self.addFolders(folder, r=True)
        self.debug = debug


    #queues more folders
    def addFolders(self, folder, r=True):
        self.paths.extend(findMidis(folder, r))


    #call when all midi folders added
    def encode(self):
        midos = self._pathsToMidos(self.paths)
        oneTracks = self._midosToOT(midos)
        encoded = self._OTEncode(oneTracks)
        if(len(encoded)==0):
            warnings.warn("No valid midis")
        return encoded
        

    def _pathsToMidos(self, paths):
        if(not self.debug):
            return parseToMidos(paths)
        self.midos = parseToMidos(paths)
        return self.midos

    def _midosToOT(self, midos):
        oneTracks = []
        for mido in midos:
            if(self.method == "on_and_off"):
                ot = OneTrack(mido, convertToC=self.convertToC, scales=self.scales)
            elif(self.method in ["on_only", "multi_network"]):
                ot = OneTrackOnOnly(mido, convertToC=self.convertToC, scales=self.scales)
            if(ot.notesRel != [] and ot != None):
                oneTracks.append(ot)


        if(not self.debug):
            return oneTracks
        self.oneTracks = oneTracks
        return oneTracks



    def _OTEncode(self, oneTracks):
        if(self.method == "on_and_off"):
            OTEncoded = OTEncoderOnOff(oneTracks).encodedOTs
        elif(self.method == "multi_network"):
            OTEncoded = OTEncoderMultiNet(oneTracks).encodedOTs
        elif(self.method == "on_only"):
            OTEncoded = OTEncoderOnOnly(oneTracks).encodedOTs
        if(not self.debug):
            return OTEncoded
        self.encoded = OTEncoded
        return OTEncoded

    




class OTEncoder:

    # list of midos
    def __init__(self, oneTracks):
        self.encodedOTs = []
        self._encodeAll(oneTracks)
    

    def _encodeAll(self, oneTracks):
        for track in oneTracks:
            self.encodedOTs.append(self._encodeOneMido(track))

    def _encodeOneMido(self, track):
        pass

    @staticmethod
    def normalizedTime(time, tpb, normalizationFactor):
        norm = tpb/normalizationFactor
        normalizedT = time/norm
        if(normalizedT >= 0.5):
            normalizedT = round(normalizedT)
        elif(normalizedT > 0):
            normalizedT = 1
        else:
            normalizedT = 0
        return normalizedT



#timeDims are the amount of distinct numbers can represent timing...
class OTEncoderOnOff(OTEncoder):

    def __init__(self, oneTracks, normalizationFactor=16):

        self.normalizationFactor = normalizationFactor
        super().__init__(oneTracks)

    def _encodeOneMido(self, OT):

        encodedOT = []

        for note in OT.notesRel:
            encodedOT.extend(OTEncoderOnOff.encodeOneNote(
                note, OT.tpb, self.normalizationFactor))
        if(len(encodedOT) != 0):
            self.encodedOTs.append(encodedOT)


    #tpb/normFactor is the smallest unit of time. For example if normFact = 16 and tpb=64 aka 1 quarter note = 64 ticks
    #The smallest unit of time is a 1/16 of a quarter note. In this case 4 ticks would equal one of these units or a 64th note
    #Which is veryyyyyyy small
    @staticmethod
    def encodeOneNote(note, tpb, normalizationFactor):
        normalizedDT = OTEncoder.normalizedTime(note.time, tpb, normalizationFactor)
        waitTime = []
        waitTime = [175+normalizedDT] if normalizedDT > 0 else []
        if(note.type == "note_on"):

            if(note.velocity == 0):
                waitTime.append(note.note)
                return waitTime
            else:
                waitTime.append(note.note+88)
                return waitTime
        else:
            waitTime.append(note.note)
            return waitTime



class OTEncoderOnOnly(OTEncoder):
    def __init__(self, oneTracks, normalizationFactor = 16):
        self.normalizationFactor = normalizationFactor
        super().__init__(oneTracks)


    def _encodeOneMido(self, OT):
        encodedOT = []
        for note in OT.notesTimed:
            encodedNote = self.encodeOneNote(note, OT.tpb)
            if(encodedNote!=None):
                encodedOT.extend(encodedNote)
        if(len(encodedOT) != 0):
            self.encodedOTs.append(encodedOT)
        
    def encodeOneNote(self, note, tpb):
        normalizedDT = OTEncoder.normalizedTime(note.time, tpb, self.normalizationFactor)
        if(normalizedDT == 0):
            return [note.note, None]
        elif(note.type == "note_on"):
            return [note.note, normalizedDT]
        else:
  
            return [88, normalizedDT]



#Each piece consist of two list 1.note list 2.time list
class OTEncoderMultiNet(OTEncoderOnOnly):
    def __init__(self, oneTracks, normalizationFactor = 16):
        self.normalizationFactor = normalizationFactor
        super().__init__(oneTracks)

    
    def encodeOneMido(self, OT):
        encodedNotes = []
        encodedTimes = []
        for note in OT.notesTimed:
    
            encodedNote, encodedTime = self.encodeOneNote(note, OT.tpb)
            if(encodedNote!=None and encodedTime!=None):
                encodedNotes.append(encodedNote)
                encodedTimes.append(encodedTime)
            
        if(len(encodedNotes) != 0):
            self.encodedOTs.append([encodedNotes, encodedTimes])
        

