from midi_parser.on_off import OneHotEncoderOnOff, MidiToDecimalOnOff, OnOffGenerator
from keras.models import load_model




import unittest



encoderOnOff = MidiToDecimalOnOff("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, nOctaves=4, smallestTimeUnit=  1/32)
encoderOnOff.encode()
encodedOTs = encoderOnOff.encoded
ohe = None


class TestOneHotEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        global ohe 
        ohe = OneHotEncoderOnOff(lookback=100,nClasses=100)
        (x,y) = ohe.encode(encodedOTs, 500)
        self.assertEqual(len(x), 500)
        self.assertEqual(len(y), 500)
        print(len(x))
        print(len(y))


    def test_sampler(self):
        model = load_model("models/testing/on_off_net_test.h5")
        (x, _) = ohe.encode(encodedOTs, 10)
        gen = OnOffGenerator(model, x, 1/32, 4)
        piece = gen.generate(1,100) 
        print(piece.piece)
        piece.play(tempo = 120)
        


    
        
    




