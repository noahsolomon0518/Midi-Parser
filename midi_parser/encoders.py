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
    "C:/Users/noahs/Local Python Libraries/midi_parser/soundfonts/piano.sf2")

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
                _time += msg.time

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
            currentNoteCopy.time = deltaTime
            self.notesRel.append(currentNoteCopy)


# Main class to be used. Takes in directory and parses all midis to encoded sequences
class MidiToDecimal:

    def __init__(self, folder, debug=False, r=True, encodingMethod='normalizedOT'):
        self.midos = []
        self.oneTracks = []
        self.encoded = []
        self.paths = []
        self.addFolders(folder, r=True)
        self.encodingMethod = encodingMethod
        self.debug = debug

    def addFolders(self, folder, r=True):
        self.paths.extend(findMidis(folder, r))

    def encode(self):
        midos = self._pathsToMidos(self.paths)
        oneTracks = self._midosToOT(midos)
        return self._OTEncode(oneTracks)

    def _pathsToMidos(self, paths):
        if(not self.debug):
            return parseToMidos(paths)
        self.midos = parseToMidos(paths)
        return self.midos

    def _midosToOT(self, midos):
        oneTracks = []
        for mido in midos:
            ot = OneTrack(mido)
            if(ot.notesRel != []):
                oneTracks.append(OneTrack(mido))
        if(not self.debug):
            return oneTracks
        self.oneTracks = oneTracks

    def _OTEncode(self, oneTracks):
        if(not self.debug):
            return RoundedOTEncoder(oneTracks).encodedOTs
        self.encoded = RoundedOTEncoder(oneTracks).encodedOTs
        return self.encoded

    def playEncoded(self, ind):
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in self.encoded[ind]:
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


class DataGen(keras.utils.Sequence):

    # samplersPerEpoch is multiplied against nNotes. Smaller fractions will result in less samplers per epoch
    def __init__(self, xEncoded, batchSize=32, sequenceSize=20, nClasses=300, samplesPerEpoch=1/3):

        self.xEncoded = xEncoded
        self.batchSize = batchSize
        self.nClasses = nClasses
        self.sequenceSize = sequenceSize
        self.samplesPerEpoch = samplesPerEpoch
        self.length = int(
            np.sum([len(piece)-(self.sequenceSize+1) for piece in self.xEncoded]))

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        # If batchsize<nPieces => choose batchsize pieces and sample from them
        # If batchsize>nPieces => sample from each piece batchsize//nPieces times then choose remainder peices to sample from
        batchEncoded = []
        nPieces = len(self.xEncoded)
        for i in range(self.batchSize//nPieces):
            for piece in self.xEncoded:
                batchEncoded.append(self._randSequence(piece))

        r = self.batchSize % nPieces
        pieceInds = np.random.choice(range(nPieces), replace=False, size=r)
        for ind in pieceInds:
            batchEncoded.append(self._randSequence(self.xEncoded[ind]))

        batchEncoded = np.array(batchEncoded)
        X, y = self.__data_generation(batchEncoded)

        return X, y

    def _randSequence(self, piece):
        start = np.random.randint(len(piece)-(self.sequenceSize+1))

        return piece[start:start+self.sequenceSize]

    def __data_generation(self, xEncoded):
        # one hot encode sequences
        x = np.zeros((self.batchSize, self.sequenceSize, self.nClasses))
        y = np.zeros((self.batchSize, self.nClasses))
        for i, sequence in enumerate(xEncoded):
            for n, val in enumerate(sequence[:-1]):
                if(val > (self.nClasses-1)):
                    x[i][n][self.nClasses-1] = 1
                else:
                    x[i][n][val] = 1

            yVal = sequence[-1]
            if(yVal > (self.nClasses-1)):
                y[i][self.nClasses-1] = 1
            else:
                y[i][yVal] = 1

        return (x, y)
