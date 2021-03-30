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

sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/soundfonts/piano.sf2")

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

    for (dirpath, _, filenames) in walk(folder):
        for file in filenames:
            if ".mid" in file:
                paths.append(path.join(dirpath, file))
        if not r:
            return paths
    return paths



class MidiToDecimal:
    '''All encoders go through 3 main steps: 
        1. MidiToDecimal._pathsToMido -> converts all queued up paths to mido objects
                                         completely encapsulated

        2. MidiToDecimal._midosToOT -> convert all midos into OneTrack objects 
                                       !must add _convertMidoToOneTrack(mido) to implementation

        3. MidiToDecimal._OTEncode -> encodes all OneTrack objects to decimal encoded list
                                      !must add _OTEncodeOne(oneTrack) to implementation
    '''
    def __init__(self, folder,  maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both"):
        self.convertToC = convertToC
        self.maxOctaves = maxOctaves
        self.scales = scales
        self.midos = []
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
        self._dbg("---Decimal Encoding Started---")
        self._dbg("Converting queued paths to mido")
        midos = self._pathsToMidos(self.paths)
        self._dbg("Converting midos to OneTracks")
        oneTracks = self._midosToOT(midos)
        self._dbg("OTEncoding OneTracks")
        encoded = self._OTEncode(oneTracks)
        self._dbg("Encoded "+ str(len(encoded))+ " tracks")
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
            ot = self._initOneTrack(mido)
            assert isinstance(ot, OneTrack)
            if(ot.notesRel != [] and ot != None):           #Returns None if scales specified and midi does not have key
                oneTracks.append(ot)
        if(not self.debug):
            return oneTracks
        self.oneTracks = oneTracks
        return oneTracks

    def _OTEncode(self, oneTracks):
        oTEncoder = self._initOTEncoder(oneTracks)
        assert isinstance(oTEncoder, OTEncoder)
        OTEncoded = oTEncoder.encodedOTs
        if(not self.debug):
            return OTEncoded
        self.encoded = OTEncoded
        return OTEncoded

    #Should return the OTEncoder
    def _initOTEncoder(self, OTs):
        raise NotImplementedError("Must define OTEncoder that will be used")
    
    def _initOneTrack(self, mido):
        raise NotImplementedError("Must define OneTrack that will be used")
    

    def _dbg(self, msg):
        if(self.debug):
            print(msg)







'''
##
--Note--
##


--Purpose--
Used for recording meaningful data for each note attained from mido object. OneTrack class is meant to be filled with
many Notes

--Parameters--
note: respective note ranging from 0-87
time: delta time relative to previous notes. In terms of ticks.
type: can be "note_on", "note_off", or "time_unit"
velocity: soley used to determine if "note_on" is actually "note_off" (note on with 0 velocity which is common in midi files)
'''


class Note:
    def __init__(self, note, time, type, velocity, instrument):
        self.note = note
        self.time = time
        self.instrument = instrument
        self.velocity = velocity
        if(velocity == 0):
            self.type = "note_off"
        else:
            self.type = type

    def copy(self):
        return Note(self.note, self.time, self.type, self.velocity, self.instrument)





'''
##
--OneTrack
##

--Purpose--
Since midis have multiple tracks, one for each channel, in order to get all notes at played correctly synchronously,
the track must be converted to absolutes time, then back to relative time. OneTrack records does this, in addition to 
keeping track of important information such as ticks per beat and key. 

--Parameters--
mido: mido object to construct OneTrack
convertToC: whether or not to convert midi to C. If no key then will not be valid
scales: if want major/minor or both scales. If no key, then will not be valid
'''



class OneTrack:

    MIDDLE_C = 60
    NOTES_PER_OCTAVE = 12
    DEFAULT_MICRO_SECS_PER_BEAT = 50000
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

    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4):
        assert maxOctaves in [2,4,6,8]
        self.mido = mido
        self.maxOctaves = maxOctaves
        self.minNote, self.maxNote = OneTrack.calcMinMaxNote(maxOctaves)
        self.convertToC = convertToC
        self.scales = scales
        self.microSecsPerBeat = OneTrack.DEFAULT_MICRO_SECS_PER_BEAT
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
            self._applyMinMaxOctave()

    
    #Checks if midi file has key information which is needed for key change
    def _isValid(self):
        if(self.key==None and (self.convertToC == True or self.scales != "both")):
            return False
        if(self.scales=="major" and "m" in self.key):
            return False
        if(self.scales=="minor" and "m" not in self.key):
            return False
        return True


    @staticmethod
    def calcMinMaxNote(maxOctaves):
        maxNote = OneTrack.MIDDLE_C + (maxOctaves/2) * OneTrack.NOTES_PER_OCTAVE
        minNote = OneTrack.MIDDLE_C - (maxOctaves/2) * OneTrack.NOTES_PER_OCTAVE
        return int(minNote), int(maxNote)


    def _extractNotesAbs(self):

        for track in self.mido.tracks:
            _time = 0
            instrument = 0
            for msg in track:
                if(msg.type == "program_change"):
                    instrument = msg.program

                if(msg.type == "key_signature"):
                    self.key = msg.key

                _time += msg.time
                
                if(msg.type in ["note_on","note_off"]):
                    self.notesAbs.append(Note(msg.note,
                                              _time,
                                              msg.type,
                                              msg.velocity, 
                                              instrument))


        self.notesAbs.sort(key=lambda x: x.time)

    #Input notesrel and changes note take in account of min max octave
    def _minMaxOctaveConvert(self, note):
        if(note.note>self.maxNote):
            octavesToShift = (((note.note-self.maxNote)//OneTrack.NOTES_PER_OCTAVE) + 1)
            note.note = int(note.note - 12 * octavesToShift)
        elif(note.note<self.minNote):
            octavesToShift = (((self.minNote - note.note)//OneTrack.NOTES_PER_OCTAVE) + 1)
            note.note = int(note.note + 12 * octavesToShift)

    #After notes converted to relative function is used to make sure every note is inside min-max note range
    def _applyMinMaxOctave(self):
        for note in self.notesRel:
            self._minMaxOctaveConvert(note)
            


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
                currentNoteCopy.note = self._convertNoteToC(currentNoteCopy.note) 
            currentNoteCopy.time = self._timeConversion(deltaTime)
            self.notesRel.append(currentNoteCopy)


    def _convertNoteToC(self, note):
        newNote = note - self.halfStepsBelowC
        if((note>87 and newNote<88) or newNote<0):
            newNote = note + self.halfStepsAboveC
        return newNote


    #Can define custom time conversions in different implementations
    def _timeConversion(self, _time):
        return _time
    '''
    def _convertTicksToMSTimeUnits(self, ticks):
        msTimeUnits = (ticks*(1/self.tpb)*self.microSecsPerBeat)//1000
        return int(max([msTimeUnits, 1]))   #Ensures atleast 1 timeunit
    '''




class OTEncoder:
    def __init__(self, oneTracks):
        self.encodedOTs = []
        self._encodeAll(oneTracks)
    

    def _encodeAll(self, oneTracks):
        for track in oneTracks:
            encodedOT = self._encodeOneMido(track)
            if (encodedOT != None):
                self.encodedOTs.append(encodedOT)
            

    def _encodeOneMido(self, track):
        pass
