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



class MidiToDecimal:
    '''All encoders go through 3 main steps: 
        1. MidiToDecimal._pathsToMido -> converts all queued up paths to mido objects
                                         completely encapsulated

        2. MidiToDecimal._midosToOT -> convert all midos into OneTrack objects 
                                       !must add _convertMidoToOneTrack(mido) to implementation

        3. MidiToDecimal._OTEncode -> encodes all OneTrack objects to decimal encoded list
                                      !must add _OTEncodeOne(oneTrack) to implementation
    '''
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both"):
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
        encoded = self._OTEncodeAll(oneTracks)
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
            ot = self._convertMidoToOneTrack(mido)
            assert type(ot) == OneTrack
            if(ot.notesRel != [] and ot != None):           #Returns None if scales specified and midi does not have key
                oneTracks.append(ot)


        if(not self.debug):
            return oneTracks
        self.oneTracks = oneTracks
        return oneTracks

    def _OTEncodeAll(self, oneTracks):
        allOTEncoded = []
        for oneTrack in oneTracks:
            OTEncoded = self._OTEncodeOne(oneTracks)
        if(not self.debug):
            return allOTEncoded
        self.encoded = allOTEncoded
        return allOTEncoded

    #Interface functions that must be defined
    #Should return some form of a OneTrack
    def _convertMidoToOneTrack(self, mido):
        pass

    #Should return list of decimal encodings for each midi
    def _OTEncodeOne(self, oneTrack):
        pass

    def _dbg(self, msg):
        if(self.debug):
            print(msg)