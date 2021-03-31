from midi_parser.multi_net import MidiToDecimalMultiNet
from midi_parser import Player
from midi_parser.sampler import SmpFile



import unittest



encoderMultiNet = MidiToDecimalMultiNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderMultiNet.encode()
encodedOTs = encoderMultiNet.encoded



class TestOTEncoderOnOnly(unittest.TestCase):
    

    def test_lengths(self):
        for piece in encodedOTs:
            print(len(piece[0]))


  
        
        



