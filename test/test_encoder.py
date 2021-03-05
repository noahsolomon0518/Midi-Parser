# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.encoders import MidiToDecimal
from midi_parser.one_hot import OneHotEncodeGen, OneHotInfo
from midi_parser.sampler import Sampler
from midi_parser import encoders
from keras.layers import Dense, LSTM
from keras.models import Sequential
maxLen, maxDim = 20, 300
import tensorflow as tf
import unittest



p = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/AMERICANA_FOLK_www.pdmusic.org_MIDIRip/1800s/subset", scales="major")
data = p.encode()




class TestOTEncoder(unittest.TestCase):
    
       
    '''               
    def test_datagen(self):
        datagen = DataGen(p.encode())

        with tf.device("cpu:0"):
            mod = Sequential()
            mod.add(LSTM(64,  input_shape=(maxLen, maxDim), return_sequences = True))
            mod.add(LSTM(128, return_sequences = False))
            mod.add(Dense(maxDim, activation = 'softmax'))
            mod.compile(optimizer = 'rmsprop', loss = 'categorical_crossentropy', metrics = ['accuracy'])
            mod.fit(datagen, epochs = 1, use_multiprocessing=True, workers=-1)
    '''

     
    def test_onehotgen(self):
        p.encode()
        
    def test_paths_exist(self):
        assert len(p.paths)!=0
        
        
    def test_on_only(self):
        #ohe = OneHotEncodeGen(nClasses=89)

        onOnly = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/Classical Archives - The Greats (MIDI)/Bach/Bwv001- 400 Chorales", method = "on_only", debug = True)
        encoded = onOnly.encode()
        #(x,y) = ohe.encode(encoded, 100)
        Sampler.playEncoded(encoded[0], 0.03)


        
