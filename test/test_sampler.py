# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 18:07:40 2021

@author: noahs
"""
from midi_parser.encoders import MidiToDecimal, OneHotEncoder, pathsToOneHot
from midi_parser.sampler import Sampler, loadSmp
import tensorflow as tf
import unittest
from keras.layers import Dense, LSTM
from keras.models import Sequential


maxLen, maxDim = 20, 200


mtd = MidiToDecimal("dminor")
ohe = OneHotEncoder(maxLen,3,maxDim)


(x, y) = pathsToOneHot(mtd,ohe)




class TestMusicNetwork(unittest.TestCase):
    
    def setUp(self):
        self.name = ""
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
                
                
                
            self.ms = Sampler(mod, x)
            do = input("Generate music test? 1:Yes 0:No\n")
            if(do=="1"):
                ms = self.ms
                ms.generate(temp = 0.4, nNotes = 100)
                
                name = input("Name: ")
                self.name = name
                ms.save(name)
            

    
    def test_load_sampler(self):
        do = input("Load Sampler? 1:Yes 0:No\n")
        if(do=="1"):    
            name = input("which model"+"last model was "+ self.name)
            ms = loadSmp(name)
            ms.model.summary()
    
    

