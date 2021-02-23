# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 12:34:01 2021

@author: noahs
"""


import unittest
from midi_parser.helpers.mido_to_one_track import *
from mido import MidiFile


class TestMidoEncoder(unittest.TestCase):
    
    
    def test_allOneTracks(self):
        otAbsolute = OTMidoAbsolute(MidiFile("data/beth.mid", type = 0))
        otRelative = OTMidoRelative(otAbsolute)
        
    def test_oneTrack(self):
        oneTrack = MidoToOT(MidiFile("data/beth.mid", type = 0))
        print(oneTrack.oneTracks)
        