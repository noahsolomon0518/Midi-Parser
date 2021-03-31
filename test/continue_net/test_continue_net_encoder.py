from midi_parser.continue_net import MidiToDecimalContinueNet




import unittest



encoderContinueNet = MidiToDecimalContinueNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderContinueNet.encode()
encodedOTs = encoderContinueNet.encoded



class TestOTEncoderOnOnly(unittest.TestCase):
    

    def test_lengths(self):
        for piece in encodedOTs:
            print(len(piece))
  
        
        



