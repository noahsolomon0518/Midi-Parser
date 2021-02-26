# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.parser import Parser


import unittest

p = Parser("data")
p.parse(10, 3, 500)


class TestParser(unittest.TestCase):
    
    
    def test_encoded_exist(self):
        assert len(p.encoded)!=0
        
        
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
        
        
        
        