from midi_parser.encapsul_net import MidiToDecimalEncapsulNet
from midi_parser import Player
from midi_parser.sampler import SmpFile



import unittest



encoderEncapsulNet = MidiToDecimalEncapsulNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=8, smallestTimeUnit=  1/32)
encoderEncapsulNet.encode()
encodedOTs = encoderEncapsulNet.encoded



class TestOTEncoderOnOnly(unittest.TestCase):
    

    def test_lengths(self):
        
        print(encodedOTs)

  
        
        



