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

    for (dirpath, _, filenames) in walk(folder):
        for file in filenames:
            if ".mid" in file:
                paths.append(path.join(dirpath, file))
        if not r:
            return paths
    return paths




'''
###

---Classes---

###
'''


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

    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4):
        assert maxOctaves in [2,4,6]
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

    @staticmethod
    def calcMinMaxNote(maxOctaves):
        maxNote = OneTrack.MIDDLE_C + (maxOctaves/2) * OneTrack.NOTES_PER_OCTAVE
        minNote = OneTrack.MIDDLE_C - (maxOctaves/2) * OneTrack.NOTES_PER_OCTAVE
        return int(minNote), int(maxNote)


    def _extractNotesAbs(self):

        for track in self.mido.tracks:
            _time = 0
            for msg in track:
            
                if(msg.type == "key_signature"):
                    self.key = msg.key
                
                _time += msg.time
                if(msg.type in ["note_on","note_off"]):
                    self.notesAbs.append(Note(msg.note,
                                              self._convertTicksToMSTimeUnits(_time),
                                              msg.type,
                                              msg.velocity))

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
                currentNoteCopy.note = self.convertNoteToC(currentNoteCopy.note) 
            currentNoteCopy.time = deltaTime
            self.notesRel.append(currentNoteCopy)


    def convertNoteToC(self, note):
        newNote = note - self.halfStepsBelowC
        if((note>87 and newNote<88) or newNote<0):
            newNote = note + self.halfStepsAboveC
        return newNote

    def _convertTicksToMSTimeUnits(self, ticks):
        msTimeUnits = (ticks*(1/self.tpb)*self.microSecsPerBeat)//1000
        return int(max([msTimeUnits, 1]))   #Ensures atleast 1 timeunit


'''
##
--OneTrackOnOnly--
##


--Purpose--
Same as OneTrack but calculates how long notes are held for. Used for MidiToDecimal with method = "on_only" or "multi_network"

--Parameters--
Same as OneTrack

'''
class OneTrackOnOnly(OneTrack):

    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4):
        super().__init__(mido, convertToC = True, scales = "both", maxOctaves = maxOctaves)
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
                        dt+=nextNote.time 
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

maxOctaves: how many different octaves that can be encoded. Options are [2,4,6,8]

"""

class MidiToDecimal:

    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", method = "on_and_off"):
        self.convertToC = convertToC
        self.maxOctaves = maxOctaves
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
                ot = OneTrack(mido, convertToC=self.convertToC, scales=self.scales, maxOctaves = self.maxOctaves)
            elif(self.method in ["on_only", "multi_network", "encapsul_net"]):
                ot = OneTrackOnOnly(mido, convertToC=self.convertToC, scales=self.scales, maxOctaves = self.maxOctaves)
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

    


"""
##

--OTEncoder--

##


--Purpose--
Psuedo interface to make incorporating new encoders more of an easy process. Subclasses must include _encodeOneMido function
to work with OTEncoder

--Parameters--
oneTracks: List of oneTrack objects
"""

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






"""
##

--OTEncoderOnOff--

##


--Purpose--
Encodes note ons and note offs as well as waiting times

--Parameters--
oneTracks: List of oneTrack objects
normalizationFactor: Smallest unit of time is quarter note / <normalizationFactor>. Larger it is the smaller and more accurate
                     units of times are. But more dimensions
"""

class OTEncoderOnOff(OTEncoder):

    def __init__(self, oneTracks):
        super().__init__(oneTracks)

    def _encodeOneMido(self, OT):

        encodedOT = []

        for note in OT.notesRel:
            encodedOT.extend(self.encodeOneNote(
                note, OT.tpb))
        if(len(encodedOT) != 0):
            return encodedOT

   
    def encodeOneNote(self, note, tpb):
        
        waitTime = []
        waitTime = [175+note.time] if note.time > 0 else []
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



"""
##

--OTEncoderOnOnly--

##


--Purpose--
Only encodes note ons/waiting time as signal events and durations following each signal event

--Parameters--
oneTracks: List of oneTrack objects
normalizationFactor: Smallest unit of time is quarter note / <normalizationFactor>. Larger it is the smaller and more accurate
                     units of times are. But more dimensions
"""

class OTEncoderOnOnly(OTEncoder):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)


    def _encodeOneMido(self, OT):
        encodedOT = []
        for note in OT.notesTimed:
            encodedNote = self._encodeOneNote(note, OT.tpb)
            if(None not in encodedNote):
                encodedOT.extend(encodedNote)
        if(len(encodedOT) != 0):
            return encodedOT
        
        
    def _encodeOneNote(self, note, tpb):
        if(note.time == 0):
            return [note.note, None]
        elif(note.type == "note_on"):
            return [note.note, note.time]
        else:
            return [88, note.time]




"""
##

--OTEncoderOnOff--

##


--Purpose--
For each midi returns two list. One for the notes/waiting time and one for the durations of each note. 

--Parameters--
oneTracks: List of oneTrack objects
normalizationFactor: Smallest unit of time is quarter note / <normalizationFactor>. Larger it is the smaller and more accurate
                     units of times are. But more dimensions
"""

class OTEncoderMultiNet(OTEncoderOnOnly):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)

  
    def _encodeOneMido(self, OT):
        encodedNotes = []
        encodedTimes = []
        for note in OT.notesTimed:
    
            encodedNote, encodedTime = self._encodeOneNote(note, OT.tpb)
            if(encodedNote!=None and encodedTime!=None):

                if(len(encodedNotes)>0 and encodedNotes[-1]==encodedNote):
                    encodedTimes[-1]+=encodedTime
                else:
                    encodedNotes.append(encodedNote)
                    encodedTimes.append(encodedTime)
            
        if(len(encodedNotes) != 0):
            return [encodedNotes, encodedTimes]


class OTEncoderEncapsulNet()
            
        

