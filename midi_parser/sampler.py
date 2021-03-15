# -*- coding: utf-8 -*-

#Pass in a trained neural network along with one hot encoded starting samples
#Uses sampling function to generate new music and plays it

# !!!NOTE: When calling Sampler.saveSampler the path is relative
#          To the environment variable "MUSICSAMPLER"



import os
from os.path import join, relpath
import numpy as np
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





#pickles up a SmpFile
def saveSmp(filename, obj):
    assert ".smp" in filename
    if(os.path.isfile(filename)):
        raise FileExistsError
    if(type(obj)!=SmpFile):
        raise TypeError("object provided is not SmpFile object. It is "+ str(type(obj)))
    outfile = open(filename,'wb')
    pickle.dump(obj, outfile)
    outfile.close()
    
    
    
#returns SmpFile from disk. INCLUDE .smp FILE EXTENTION!!
def loadSmp(filepath):
    samplerFP = os.path.join(smpPath, os.path.join("obj",filepath))
    infile = open(samplerFP,'rb')
    obj = pickle.load(infile)
    infile.close()
    
    if(type(obj)!=SmpFile):
        raise TypeError("filename provided is not SmpFile object")
    return obj

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





#Can't figure out to pickle keras models so just recorded modelpath 
#Description should include what data was used to train, how many epochs, and what the outcome was
class SmpFile:
    def __init__(self, modelPath, generated):
        self.modelPath = modelPath
        self.generated = generated 

        
    @property
    def model(self):
        return load_model(self.modelPath)




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
    def generate(self, temp, nNotes = 500):
        print("---Generating Piece---")
        if(len(self.model.output)==1):
            piece = self._generateReg(temp, nNotes)
        elif(len(self.model.output)==2):
            piece = self._generateMulti(temp, nNotes)

        print("Piece generated...")
        self.generated.append(piece)
    

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

    def _generateMulti(self, temp, nNotes):
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
        return piece

    def _printProgress(self, i, nNotes):
        print("Progress: "+str(i*100/(nNotes))+"%", end = "\r")

    def _getPriorNotes(self, generated):
        return np.expand_dims(generated[-self.maxLen:], axis = 0)

   

        
    
    #Play a decimal encoded piece using roundedEncoding (If I decide to make more encoding methods)
    @staticmethod
    def playEncoded(piece, timeunit = 0.03):

        if(Sampler.isOnOnly(piece)):
            piece = Sampler.onOnlyToOnOff(piece)


        elif(Sampler.isMultiNet(piece)):
            piece = Sampler.onOnlyToOnOff(piece)


        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in piece:
            if(msg>=176):
                time.sleep((msg-175)*timeunit)
            elif(msg>88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)


    @staticmethod
    def isOnOnly(piece):
        return (max([piece[i] for i in range(len(piece)) if i%2==0]) < 176)

    @staticmethod
    def isMultiNet(piece):
        return len(piece[0])==2
    

    @staticmethod
    def multiNetToOnOff(piece):
        pass


    @staticmethod
    def onOnlyToOnOff(piece):

        convertedPiece = []
        #Count total time units
        totalTimeUnits = sum([piece[i+1] for i in range(len(piece)) if i%2 == 0 and piece[i]==88])+100
        notesByTimeUnit = [[] for i in range(totalTimeUnits)]

        currentTimeUnit = 0
        for i,evt in enumerate(piece):

            if(i%2 == 0):
                if(evt==88):
                    currentTimeUnit += piece[i+1]

                else:
                    notesByTimeUnit[currentTimeUnit].append(88+evt)
                    notesByTimeUnit[currentTimeUnit+piece[i+1]].append(evt)    #Signals note off
            
        for timeUnit in notesByTimeUnit:
            if(len(timeUnit)==0 and len(convertedPiece)>0):
                convertedPiece[-1]+=1
            else:
                for note in timeUnit:
                    convertedPiece.append(note)
                convertedPiece.append(176)    #Each timeunit represents 176

        return convertedPiece
        



    
    
    #folder relative to Sampler environment variable path/obj
    def save(self, filepath):
        samplerFP = join(smpPath, relpath("obj/"+filepath+".smp"))
        h5FP = join(smpPath, relpath("h5/"+filepath+".h5"))
        self.model.save(h5FP)
        smp = SmpFile(h5FP, self.generated)
        saveSmp(samplerFP, smp)


        
    
    
    
    
    
        
    





    


    







