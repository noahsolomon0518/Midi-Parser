# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.parser import Parser


import unittest



class TestParser(unittest.TestCase):
    
    
    def test_parser(self):
        p = Parser("data")
        p.parse(10, 3, 500)
        assert p.getData() != None

        