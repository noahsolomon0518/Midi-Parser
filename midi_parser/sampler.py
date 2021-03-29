# -*- coding: utf-8 -*-

#Pass in a trained neural network along with one hot encoded starting samples
#Uses sampling function to generate new music and plays it

# !!!NOTE: When calling Sampler.saveSampler the path is relative
#          To the environment variable "MUSICSAMPLER"



import os
from os.path import join, relpath
import numpy as np
import tensorflow as tf
from mido import Message, MidiFile, MidiTrack
from random import choice
import fluidsynth
import time
import pickle
from keras.models import load_model
sf2 = os.path.abspath("C:/Users/noahs/Local Python Libraries/soundfonts/piano.sf2")
smpPath = os.getenv("MUSICSAMPLER")
fs = fluidsynth.Synth()
fs.start()
sfid = fs.sfload(sf2)
fs.program_select(0, sfid, 0, 0)


'''
###

--- Utility functions ---

###
'''




#Saves smpfiles as well as regular pieces
def saveSmp(piece, filepath):
    if ".smp" not in filepath:
        filepath += ".smp"
    outfile = open(filepath,'wb')
    if(type(piece)==SmpFile):
        piece = piece.piece
        
    pickle.dump(piece, outfile)
    outfile.close()
    
def loadSmp(filepath):
    
    infile = open(filepath,'rb')
    piece = SmpFile(pickle.load(infile))
    infile.close()
    return piece

#Mixes up probabilities of multinomial distribution (prediction of music neural network)
def sample(preds, temperature = 0.5):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    expPreds = np.exp(preds)
    preds = expPreds/np.sum(expPreds)
    probs = np.random.multinomial(1,preds,1)
    return np.argmax(probs)

    

#Takes one hot encoded vectors and converts them to their respective integers
def encodeFromOneHot(generated):
    piece = []
    for note in generated:
        piece.append(np.argmax(note))
    return piece




'''
###

--- Classes ---

###
'''






class Player:
    @staticmethod
    def play(piece, smallestTimeUnit = 1/32, tempo = 120):
        timeUnitSeconds =  (smallestTimeUnit/(1/4))*(60/tempo)     #How many beats in smallest time unit
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in piece:
            print(msg)
            if(msg>=176):
                time.sleep((msg-175)*timeUnitSeconds)
            elif(msg>88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)





    
#Takes in any form of decimal encoded midi and converts in to standard form. Can save and play as midis
class SmpFile:
    def __init__(self, piece):
        if(self._isMultiNet(piece)):
            print("Converting piece from MultiNet to OnOff")
            piece = self._multiNetToOnOff(piece)
        elif(self._isOnOnly(piece)):
            print("Converting piece from OnOnly to OnOff")
            piece = self._onOnlyToOnOff(piece)

        self.piece = piece
        

    def _isOnOnly(self, piece):
        return (max([piece[i] for i in range(len(piece)) if i%2==0]) < 176)

    def _onOnlyToOnOff(self, piece):
        totalTimeUnits = sum([piece[i+1] for i in range(len(piece)) if i%2 == 0 and piece[i]==88])+100
        notesByTimeUnit = self._calcNoteOnNoteOffs(piece, totalTimeUnits)
        convertedPiece = self._collapseTimeUnits(notesByTimeUnit)
        return convertedPiece

    def _calcNoteOnNoteOffs(self, piece, totalTimeUnits):
        notesByTimeUnit = [[] for i in range(totalTimeUnits)]
        currentTimeUnit = 0
        for i,evt in enumerate(piece):
            if(i%2 == 0):
                if(evt==88):
                    currentTimeUnit += piece[i+1]
                else:
                    notesByTimeUnit[currentTimeUnit].append(88+evt)
                    notesByTimeUnit[currentTimeUnit+piece[i+1]].append(evt)    #Signals note off
        return notesByTimeUnit

    def _isMultiNet(self, piece):
        return (len(piece)==2)

    def _multiNetToOnOff(self, piece):
        onOnlyConverted = []
        for note,time in zip(piece[0], piece[1]):
            onOnlyConverted.extend([note,time])
        return self._onOnlyToOnOff(onOnlyConverted)



    #If there are many 176's right next to each other they can be combined
    def _collapseTimeUnits(self, notesByTimeUnit):
        convertedPiece = []
        for timeUnit in notesByTimeUnit:
            if(len(timeUnit)==0 and len(convertedPiece)>0):
                convertedPiece[-1]+=1
            else:
                for note in timeUnit:
                    convertedPiece.append(note)
                convertedPiece.append(176)    #Each timeunit represents 176
        return convertedPiece
    

    def play(self):
        Player.play(self.piece)


    def saveMidi(self, path, ticksPerTimeUnit = 16):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        for i, message in enumerate(self.piece):
            if(i>0 and self.piece[i-1]>175):
                dt = (self.piece[i-1] - 175) * ticksPerTimeUnit
            else:
                dt = 0
            self._addMessage(dt, message, track)
        mid.save(path)

    def _addMessage(self, dt, message, track):
        #If note off
        if(message<88):
            track.append(Message('note_off', note=message, velocity=127, time=dt))
        elif(message<176):
            track.append(Message('note_on', note=message-88, velocity=127, time=dt))



    




    

    




#Used for testing music generation capabilities of networks
#Also can save as SmpFile (MusicSampler without some atrributes)

class Sampler:
    
    def __init__(self, model, xTrain):
        self.model = model
        self.maxLen = len(xTrain[0])
        self.xTrain = xTrain
        self.generated = []
    
        
        
    
    
    
    
    
    #Generates in the form of one hot encoded vectors then converted to decimal
    #to be stored and played easily. 
    def generate(self, temp, nNotes = 500, save = False, fp = None):
        if(save):
            assert fp != None
        print("---Generating Piece---")
        if(len(self.model.output)==1):
            piece = self._generateReg(temp, nNotes)
        elif(len(self.model.output)==2):
            piece = self._generateMulti(temp, nNotes)
        print("Piece generated...")
        self.generated.append(SmpFile(piece))           
        if(save):
            saveSmp(piece, fp)
        return SmpFile(piece)
    

    def _generateReg(self, temp, nNotes):
        piece = []
        generated = choice(self.xTrain)
        
        for i in range(nNotes):
            priorNotes = self._getPriorNotes(generated)
            preds = self.model.predict(priorNotes)
            argMax = sample(preds, temp)
            piece.append(argMax)
            generated = np.concatenate([generated,preds])
            self._printProgress(i, nNotes)
        return piece


    #Does not work with gpu :(
    def _generateMulti(self, temp, nNotes):
        with tf.device('/cpu:0'):
            piece = []
            generated = choice(self.xTrain)

            for i in range(nNotes):
                priorNotes = self._getPriorNotes(generated)
                predNotes, predTimes = self.model.predict(priorNotes)
                argmaxNotes = sample(predNotes[0], temp)
                argmaxTimes = sample(predTimes[0], temp)
                piece.extend([argmaxNotes,argmaxTimes])
                preds = np.concatenate([predNotes, predTimes], axis = 1)
                generated = np.concatenate([generated,preds])
                self._printProgress(i, nNotes)
            return piece

    def _printProgress(self, i, nNotes):
        print("Progress: "+str(i*100/(nNotes))+"%", end = "\r")

    def _getPriorNotes(self, generated):
        return np.expand_dims(generated[-self.maxLen:], axis = 0)

   