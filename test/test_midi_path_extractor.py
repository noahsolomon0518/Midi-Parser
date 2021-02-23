# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:38:42 2021

@author: noahs
"""

import unittest
from midi_parser.helpers.midi_path_extractor import MidiPathExtractor



class TestPathExtract(unittest.TestCase):
    
    
    def test_notEmpty(self):
        mpe = MidiPathExtractor("data")
        assert mpe.midiPaths != []
