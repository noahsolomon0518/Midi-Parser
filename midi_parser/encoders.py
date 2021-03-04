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
            print(file)
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


    def __init__(self, mido, convertToC = True, scales = "both"):
        self.mido = mido
        self.convertToC = convertToC
        self.scales = scales
        self.key = None
        self.notesAbs = []
        self.notesRel = []
        self._extractNotesAbs()

        #Only does full conversion if valid. Otherwise self.noteRel=[] and is not parsed
        if(self._isValid()):
            self.needKey = (self.convertToC == True or self.scales != "both")
            self.halfStepsAboveC = OneTrack.halfStepsAboveC[self.key.replace("m", "")]
            self.halfStepsBelowC = 14 - OneTrack.halfStepsAboveC[self.key.replace("m", "")]
            self._convertToNotesRel()
            self.tpb = mido.ticks_per_beat


    def _isValid(self):
        if(self.key==None and (self.convertToC == True or self.scales != "both")):
            return False
        if(self.scales=="major" and "m" in self.key):
            return False
        if(self.scales=="minor" and "m" not in self.key):
            return False
        return True




    



    def _extractNotesAbs(self):

        for track in self.mido.tracks:
            _time = 0
            for msg in track:
                _time += msg.time
                
                if(msg.type == "key_signature"):
                    self.key = msg.key
                   
                if(msg.type == "note_on" or msg.type == "note_off"):
                    self.notesAbs.append(Note(msg.note,
                                              _time,
                                              msg.type,
                                              msg.velocity))

        self.notesAbs.sort(key=lambda x: x.time)

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
"""
--Parameters--
folder: Folder to get midis
debug: Whether or not all data should be stored in memory to allow easier debugging. DO NOT USE WHEN PARSING A LOT OF MIDIS
r: If true, recursively find all midis in a folder
convertToC: Convert keys of midis to C. As a result midis without keys will not be parsed
scales: Whether to accept major, minor, or both scales. Only used if convertToC is True. Options are "both", "major", "minor"


"""
# Main class to be used. Takes in directory and parses all midis to encoded sequences
class MidiToDecimal:

    def __init__(self, folder, debug=False, r=True, convertToC = True,  scales = "both"):
        self.convertToC = convertToC
        self.scales = scales
        self.midos = []
        self.oneTracks = []
        self.encoded = []
        self.paths = []
        self.addFolders(folder, r=True)
        self.debug = debug

    def addFolders(self, folder, r=True):
        self.paths.extend(findMidis(folder, r))

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
            ot = OneTrack(mido, convertToC=self.convertToC, scales=self.scales)
            if(ot.notesRel != []):
                oneTracks.append(ot)
        if(not self.debug):
            return oneTracks
        self.oneTracks = oneTracks

    def _OTEncode(self, oneTracks):
        if(not self.debug):
            return RoundedOTEncoder(oneTracks).encodedOTs
        self.encoded = RoundedOTEncoder(oneTracks).encodedOTs
        return self.encoded

    @staticmethod
    def play(piece):
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in piece:
            if(msg >= 176):
                time.sleep((msg-175)*0.03)
            elif(msg > 88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)


  
class OTEncoder:

    # list of midos
    def __init__(self):
        self.encodedOTs = []

    # func is a function that encodes for one OT
    def encodeAllOT(self, OTs, func):
        if(type(OTs) != list):
            OTs = [OTs]
        for OT in OTs:
            func(OT)


class RoundedOTEncoder(OTEncoder):

    def __init__(self, oneTracks, normalizationFactor=16):

        self.normalizationFactor = normalizationFactor
        super().__init__()
        super().encodeAllOT(oneTracks, self.encodeOneMido)

    def encodeOneMido(self, OT):
        encodedOT = []

        for note in OT.notesRel:
            encodedOT.extend(RoundedOTEncoder.encodeOneNote(
                note, OT.tpb, self.normalizationFactor))
        if(len(encodedOT) != 0):
            self.encodedOTs.append(encodedOT)

    @staticmethod
    def encodeOneNote(note, tpb, normalizationFactor):

        norm = tpb/normalizationFactor
        normalizedDT = note.time/norm
        if(normalizedDT >= 0.5):
            normalizedDT = round(normalizedDT)
        elif(normalizedDT > 0):
            normalizedDT = 1
        else:
            normalizedDT = 0

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


