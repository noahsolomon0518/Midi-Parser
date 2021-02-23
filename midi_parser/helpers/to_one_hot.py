# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:42:39 2021

@author: noahs
"""

import numpy as np



class ToOneHot:
    def __init__(self, sampleLength, gap, oneHotDimension):
        self.sampleLength = sampleLength
        self.gap = gap
        self.oneHotDimension = oneHotDimension
        self.xEncoded = []
        self.yEncoded = []
        
    def fit(self, sequences):
        for sequence in sequences:
            self.oneHotEncodeSequence(sequence)
        self.xEncoded = np.array(self.xEncoded)
        self.yEncoded = np.array(self.yEncoded)   
    
    
    def oneHotEncodeSequence(self,sequence):
        nSamples = self.getNSamples(sequence)
        for i in range(nSamples):
            xSample = sequence[i*self.gap:(i)*self.gap + self.sampleLength]
            ySample = sequence[(i)*self.gap + self.sampleLength]
            self.oneHotEncodeSample(xSample, ySample)
            
    
    
    def oneHotEncodeSample(self,x,y):
        xOneHot = np.zeros((self.sampleLength,self.oneHotDimension))
        yOneHot = np.zeros((self.oneHotDimension))
        
        if(y>=self.oneHotDimension):
                yOneHot[self.oneHotDimension-1] = 1
        else:
            yOneHot[y] = 1
        for i,sample in enumerate(x):
            if(sample>=self.oneHotDimension):
                xOneHot[i][self.oneHotDimension-1] = 1
            else:
                xOneHot[i][sample] = 1
        self.xEncoded.append(xOneHot)
        self.yEncoded.append(yOneHot)
            
            
    def getNSamples(self, sequence):
        return (len(sequence)-self.sampleLength)//self.gap
    
