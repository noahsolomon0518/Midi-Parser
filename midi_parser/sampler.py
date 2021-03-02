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

def sample2(preds):
    return choice(range(len(preds)))
    

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



#Data structure stored in MusicSampler and SmpFile 
class GeneratedPiece:
    def __init__(self, piece, title):
        self.piece = piece
        self.title = title




#Can't figure out to pickle keras models so just recorded modelpath 
#Description should include what data was used to train, how many epochs, and what the outcome was
class SmpFile:
    def __init__(self, modelPath, generated, description, title):
        self.title = title
        self.modelPath = modelPath
        self.generated = generated 
        self.description = description
        
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
        self.cached = None
    
        
        
    
    
    
    
    
    #Generates in the form of one hot encoded vectors then converted to decimal
    #to be stored and played easily. 
    def generate(self, temp, shouldSample = True, roundPredictions = True,nNotes = 500):
        start = choice(self.xTrain)
        piece = []
        generated = start
        print("---Generating Piece---")
        for i in range(nNotes):
            priorNotes = np.expand_dims(generated[-self.maxLen:], axis = 0)
            preds = self.model.predict(priorNotes)
            if(shouldSample):    
                argmax = sample(preds[0], temp)
            else:
                argmax = np.argmax(preds[0])
            piece.append(argmax)
            if(roundPredictions):
                preds = preds.astype('int')
            generated = np.concatenate([generated,preds])
            print("Progress: "+str(i*100/(nNotes))+"%", end = "\r")
        
        
        Sampler.playEncoded(piece)
        self.cached = piece
        print('1:SAVE PIECE \n2:GENERATE NEW PIECE \n3:ABORT\n')
        shouldSave = input("")
        if(shouldSave == "1"):
            print("---Saving Piece---")
            title = input("Piece title: ")
            self._savePiece(piece, title)
            print("Piece saved... \n1:GENERATE NEW PIECE \n2:ABORT \n")
            generateNew = input("")
            if(generateNew == "1"):
                self.generate(temp, roundPredictions, nNotes)
        elif(shouldSave == "2"):
            self.generate(temp, roundPredictions, nNotes)
    



    #Used to save most recently generated piece. Useful for testing
    def saveCached(self, title):
        self._savePiece(self.cached, title)

        
    #Appends GeneratedPiece to self which will eventually be passed to SmpFile
    def _savePiece(self, piece, title):
        
        self.generated.append(GeneratedPiece(piece, title))
        
        
        
        
        
    
    #Play a decimal encoded piece using roundedEncoding (If I decide to make more encoding methods)
    @staticmethod
    def playEncoded(piece):
        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        for msg in piece:
            if(msg>=176):
                time.sleep((msg-175)*0.03)
            elif(msg>88):
                fs.noteon(0, msg-88, 100)
            else:
                fs.noteoff(0, msg)
    
    
    #folder relative to Sampler environment variable path/obj
    def save(self, filepath):
        samplerFP = join(smpPath, relpath("obj/"+filepath+".smp"))
        h5FP = join(smpPath, relpath("h5/"+filepath+".h5"))
        print("---Saving generated music as SmpFile---")
        self.model.save(h5FP)
        title = input("Title of AI: ")
        description = input("Description of Music: ")
        smp = SmpFile(h5FP, self.generated, description, title)
        saveSmp(samplerFP, smp)
        
    
    
    
    
    
        
    





    


    







