# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.encoders import MidiToDecimal, OTEncoderMultiNet, OTEncoderOnOff, OTEncoderOnOnly
from midi_parser.sampler import Player, SmpFile



import unittest



encoderOnOff = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/testing", method = "on_and_off", debug = True)
encoderOn = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/testing", method = "on_only", debug = True, maxOctaves=6)
encoderMultiNet = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/testing", method = "multi_network", debug = True, maxOctaves=6)


encoderOnOff.encode()
encoderOn.encode()
encoderMultiNet.encode()




class TestOTEncoderOnOff(unittest.TestCase):
    

    def test_lengths(self):
        encodedOTs = encoderOnOff.encoded
        
        self.assertGreater(len(encodedOTs), 0)
        for OT in encodedOTs:
            self.assertGreater(len(OT), 0)
            for note in OT:
                self.assertGreater(note, 0)



class TestOTEncoderOnOnly(unittest.TestCase):
    def test_lengths(self):
        encodedOTs = encoderOn.encoded

        self.assertGreater(len(encodedOTs), 0)
        for OT in encodedOTs:
            self.assertGreater(len(OT), 0)
            for note in OT:
                self.assertGreater(note, 0)


class TestOTEncoderMultiNet(unittest.TestCase):
    def test_lengths(self):
        encodedOTs = encoderMultiNet.encoded
        smp = SmpFile(encodedOTs[0])
        smp.play()
        self.assertGreater(len(encodedOTs), 0)
        for OT in encodedOTs:
            self.assertEqual(len(OT), 2)           #One list with notes one with times durations
            notes, times = OT
     
            self.assertGreater(len(notes), 0)
            self.assertGreater(len(times), 0)
            for note in notes:
                self.assertTrue(note>=0 and note<=88)
            for time in times:
                self.assertGreater(time, 0)
        

        

     

        
    


        
