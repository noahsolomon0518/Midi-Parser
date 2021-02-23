# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 11:38:16 2021

@author: noahs
"""

import unittest
from midi_parser.helpers.one_track_encoder import NormalizedOTEncoder
from midi_parser.helpers.mido_to_one_track import MidoToOT
from mido import MidiFile


class TestMidoEncoder(unittest.TestCase):
    
    
    def test_normalizationEncoder(self):
        ot = MidoToOT(MidiFile("data/beth.mid", type = 0))
        nme = NormalizedOTEncoder(ot.oneTracks)
        print(nme.encodedOTs)
        assert nme.encodedOTs != []
        
