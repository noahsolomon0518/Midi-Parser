from midi_parser.on_off import MidiToDecimalOnOff
from midi_parser import Player



import unittest



encoderOnOff = MidiToDecimalOnOff("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderOnOff.encode()
encodedOTs = encoderOnOff.encoded



class TestOTEncoderOnOff(unittest.TestCase):
    

    def test_lengths(self):
        

        self.assertGreater(len(encodedOTs), 0)
        for OT in encodedOTs:
            self.assertGreater(len(OT), 0)
            for note in OT:
                self.assertGreater(note, 0)
    
    def test_play(self):
        Player.play(encodedOTs[0], smallestTimeUnit = 1/32, tempo = 150)
        



