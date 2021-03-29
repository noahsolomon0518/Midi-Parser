from midi_parser.on_only import MidiToDecimalOnOnly
from midi_parser import Player
from midi_parser.sampler import SmpFile



import unittest



encoderOnOnly = MidiToDecimalOnOnly("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderOnOnly.encode()
encodedOTs = encoderOnOnly.encoded



class TestOTEncoderOnOnly(unittest.TestCase):
    

    def test_lengths(self):
        

        self.assertGreater(len(encodedOTs), 0)
        for OT in encodedOTs:
            self.assertGreater(len(OT), 0)
            for note in OT:
                self.assertGreater(note, 0)
    
    def test_play(self):
        piece = SmpFile(encodedOTs[0])
        piece.play()
        
        



