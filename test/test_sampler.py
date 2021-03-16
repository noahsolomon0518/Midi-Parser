# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 18:07:40 2021

@author: noahs
"""
from midi_parser.encoders import MidiToDecimal
from midi_parser.one_hot import OneHotEncodeMultiNet
from midi_parser.sampler import Sampler, loadSmp, saveSmp
import tensorflow as tf
import unittest
from keras.layers import Dense, LSTM
from keras.models import Sequential
from keras.models import load_model








class TestSamplerMultiNet(unittest.TestCase):


    def setUp(self):
        multiGenModel = load_model("models/testing/test_multigen.h5")
        deciData = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/testing", method = "multi_network").encode()
        ohe = OneHotEncodeMultiNet(lookback=50)
        xTrain,_1,_2 = ohe.encode(deciData, 10)
        self.sampler = Sampler(multiGenModel, xTrain)

    def test_generateMusic(self):
        smp = self.sampler.generate(temp = 0.5, nNotes=10)
        self.musicLength(smp.piece)
        self.play(smp)
        self.save(smp)
        self.load()
        self.saveMidi(smp)

    def musicLength(self,piece):
        self.assertGreater(len(piece),0)

    def play(self, smp):
        smp.play()



    def save(self, smp):
        saveSmp(smp, "models/testing/test_piece.smp")

    def load(self):
        smp = loadSmp("models/testing/test_piece.smp")
        smp.play()

    def saveMidi(self, smp):

        smp.saveMidi("models/testing/test_piece.mid")
        newSmp = loadSmp("C:/Users/noahs/Data Science/Music Generation AI/generated/bach/small_epochs/keepers/epoch_1981_p1.smp")
        newSmp.saveMidi("models/testing/test_grakPiece.mid", 32)
    





