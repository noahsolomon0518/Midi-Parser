from midi_parser.one_hot_encoder import DataGen
from midi_parser.on_off import MidiToDecimalOnOff
from keras.models import Sequential
from keras.layers import LSTM, Dense



import unittest



encoderOnOff = MidiToDecimalOnOff("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, nOctaves=8, smallestTimeUnit=  1/32, nClassesTimes = 20)
encoderOnOff.encode()
encodedOTs = encoderOnOff.encoded
lookback = 50
model = Sequential()
model.add(LSTM(64, input_shape = (lookback,12*8+20)))
model.add(Dense(12*8+20, activation = "softmax"))
model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

class TestDatagen(unittest.TestCase):

    def test_encoded(self):
        print(encodedOTs)
        datagen = DataGen(encodedOTs, nClasses=8*12+20)
        model.fit(datagen, epochs = 10)
    