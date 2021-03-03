# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:26:27 2021

@author: noahs
"""

from midi_parser.encoders import MidiToDecimal, OneHotEncodeAll, OneHotEncodeGen, DataGen, OneHotInfo 
from midi_parser import encoders
from keras.layers import Dense, LSTM
from keras.models import Sequential
maxLen, maxDim = 20, 300
import tensorflow as tf
import unittest

p = MidiToDecimal("data")



oneHotEnc = OneHotEncodeAll()
encodeGen = OneHotEncodeGen()

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
        res = oneHotEnc.encode(p.encode())
        res2 = encodeGen.encode(p.encode(), 6000)
        print("Number of samples that can be generated: " + str(OneHotInfo.nSamples(p.encode(), 30, 3)))
        
    def test_paths_exist(self):
        assert len(p.paths)!=0
        
        
        
        
    def test_dminor(self):
        mtd = MidiToDecimal("data")
      
        
        
        

    
        
        
        
        
        