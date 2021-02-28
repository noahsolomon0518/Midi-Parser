# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.parsers.midi_encoder import MidiToDecimal, OneHotEncoder
from midi_parser.parsers import midi_encoder

import unittest

p = MidiToDecimal("data")
p.encode()


oneHotEnc = OneHotEncoder(5, 2, 10)

class TestOTEncoder(unittest.TestCase):
    
    
    def test_encoded_exist(self):
        
        for encMidi in p.encoded:
            assert len(encMidi)>0
        
        
    def test_encoded_less_than_500(self):
        for encMidi in p.encoded:
            
            for msg in encMidi:
                assert msg<500          
                    
                
    def test_oneTracks_exist(self):
        assert len(p.oneTracks)!=0
     
        
        
    def test_midos_exist(self):
        assert len(p.midos)!=0
        
        
    def test_paths_exist(self):
        assert len(p.paths)!=0
        
        
        
        
    def test_dminor(self):
        mtd = MidiToDecimal("dminor")
        mtd.encode()
        print(mtd.encoded)
        
        
        
class TestOneHot(unittest.TestCase):
    
    
    
    def test_one_hot_encode(self):
        data = [[1,2,3,4,2,3,4,5,3,2,3,4,7,5,3,2,1,2,3],[0,3,3,4,2]]
        
        oneHotEnc.encode(data)  
        
        assert len(oneHotEnc.xEncoded) != 0
        
        assert len(oneHotEnc.yEncoded) != 0
        
        
        for sample in oneHotEnc.xEncoded:
            assert sample.shape == (5,10)
            
        for target in oneHotEnc.yEncoded:
            assert len(target) == 10
            
            
        
class TestPathsToOneHot(unittest.TestCase):
    parsedData = midi_encoder.pathsToOneHot(p, oneHotEnc)
    assert len(parsedData)>0
    
    
    
        
        
        
        
        