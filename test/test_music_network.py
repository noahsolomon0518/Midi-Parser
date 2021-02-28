# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 18:07:40 2021

@author: noahs
"""
from midi_parser.parsers.midi_encoder import MidiToDecimal, OneHotEncoder,pathsToOneHot
from midi_parser.parsers import midi_encoder
from midi_parser.music_network.serializer import MusicSampler, loadMusicSampler, dumpMusicSampler


import unittest
from keras.layers import Dense, LSTM
from keras.models import Sequential
import tensorflow as tf


maxLen, maxDim = 20, 200


mtd = MidiToDecimal("dminor")
ohe = OneHotEncoder(maxLen,3,maxDim)


(x, y) = pathsToOneHot(mtd,ohe)




class TestMusicNetwork(unittest.TestCase):
    
    def setUp(self):
        do = input("build NN? 1:Yes 0:No\n")
        if(do=="1"):
            mod = None
            with tf.device("cpu:0"):
                mod = Sequential()
                mod.add(LSTM(64, dropout=0.3,  input_shape=(maxLen, maxDim), return_sequences = True))
                mod.add(LSTM(128,  return_sequences = False))
                mod.add(Dense(maxDim, activation = 'softmax'))
                mod.compile(optimizer = 'rmsprop', loss = 'categorical_crossentropy', metrics = ['accuracy'])
                mod.fit(x,y, epochs = 1)
                
                
                
            self.ms = MusicSampler(mod, x)
            do = input("Generate music test? 1:Yes 0:No\n")
            if(do=="1"):
                ms = self.ms
                ms.generate(temp = 0.4)
                ms.saveSampler("testing2")
            

    
    def test_load_sampler(self):
        do = input("Load Sampler? 1:Yes 0:No\n")
        if(do=="1"):    
            ms = loadMusicSampler("testing2.smp")
            ms.playPiece(0)
            ms.getModel().summary()
    
    

