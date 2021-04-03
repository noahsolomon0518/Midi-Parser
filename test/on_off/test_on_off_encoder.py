from midi_parser.on_off import MidiToDecimalOnOff, OnOffPiece



import unittest



encoderOnOff = MidiToDecimalOnOff("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, nOctaves=8, smallestTimeUnit=  1/32)
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
        piece = OnOffPiece(encodedOTs[0], nOctaves = 8, smallestTimeUnit = 1/32)
        piece.play(tempo = 150)




        



