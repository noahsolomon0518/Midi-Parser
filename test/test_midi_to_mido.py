# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:42:34 2021

@author: noahs
"""

import unittest
from midi_parser.helpers.midi_to_mido import MidiToMido
from midi_parser.helpers.midi_path_extractor import MidiPathExtractor




class TestMidiToMido(unittest.TestCase):
    
    
    def test_oneParsed(self):
        
        mtm = MidiToMido("data/beth.mid")
        assert mtm.midos != []
        
    
    
    def test_manyParsed(self):
        
        paths = MidiPathExtractor("data").midiPaths
        
        mtm = MidiToMido(paths)
        assert mtm.midos != []
        
        
    def test_log(self):
        paths = MidiPathExtractor("data").midiPaths
        MidiToMido(paths).log()