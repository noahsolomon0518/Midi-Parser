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


#Abstract class for piece
#Piece only records timing and notes
#2 purposes include storing piece and converting to standard format
class Piece:
    def __init__(self, piece, smallestTimeUnit):
        self.smallestTimeUnit = smallestTimeUnit
        piece = self.convertToOnOff(piece)
        self.piece = self._removeDup(piece)


    #If piece generates multiple note of the same pitch played at same time
    #This function removes them
    def _removeDup(self, piece):
        for i, note in enumerate(piece):
            if(note<176):
                back = 1
                while(i-back>=0 and piece[i-back]<176):
                    if(note == piece[i-back]):
                        del piece[i]
                        break
                    back+=1
        return piece

    #Must define convertToOnOff in child classes
    def convertToOnOff(self, piece):
        raise NotImplementedError("Must define convertToOnOff function.")

    def play(self, tempo = 120):
        """
        Plays piece after converted to OnOff form

        Parameters
        ----------
        tempo: int
            Tempo in beats per minute
        """
        Player.play(self.piece, self.smallestTimeUnit, tempo)

    def save(self, path, tempo = 120):
        """
        Saves piece as midi

        Parameters
        ----------
        path: str
            Path at which midi will be saved in. Add extension .mid
        tempo: int
            Tempo in beats per minute
        """
        timeUnitSeconds =  (self.smallestTimeUnit/(1/4))*(60/tempo)
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        for i, message in enumerate(self.piece):
            if(i>0 and self.piece[i-1]>175):
                dt = (self.piece[i-1] - 175) * timeUnitSeconds
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



class OnOffPiece(Piece):
    ##Standard format for pieces

    #NoteOns -> 88 + <pitch>
    #NoteOffs -> 0 + <pitch>
    #Wait Time -> 175 + <number of time units>
    

    def __init__(self, piece, smallestTimeUnit):
        super().__init__(piece, smallestTimeUnit)

    #Already in standard form
    def convertToOnOff(self, piece):
        return piece



class OnOnlyPiece(Piece):

    #Each note broken down into:
    # <pitch number> <time units player for>
    # 88 is waiting time unit

    def __init__(self, piece, smallestTimeUnit):
        super().__init__(piece, smallestTimeUnit)

    
    def convertToOnOff(self, piece):
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

class MultiNetPiece(OnOnlyPiece):
    def __init__(self, piece, smallestTimeUnit):
        super().__init__(piece, smallestTimeUnit)

    def convertToOnOff(self, piece):
        onOnlyConverted = []
        for note,time in zip(piece[0], piece[1]):
            onOnlyConverted.extend([note,time])
        return OnOnlyPiece.convertToOnOff(self, onOnlyConverted)



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




'''

    def _isEncapsulNet(self, piece):
        return (len(piece)==3)
    
    def _encapsulNetToOnOff(self, piece):
        timeUnit = max(piece[0])
        onOnlyConverted = []
        for note,time,octave in zip(piece[0], piece[1], piece[2]):
            if(note == timeUnit):
                onOnlyConverted.extend([88,time])
            else:
                onOnlyConverted.extend([12*octave + note,time])
        return self._onOnlyToOnOff(onOnlyConverted)

'''

    
    


    

    






class Generator:
    
    def __init__(self, model, xTrain, smallestTimeUnit):
        self.smallestTimeUnit = smallestTimeUnit
        self.model = model
        self.maxLen = len(xTrain[0])
        self.xTrain = xTrain
        self.generated = []

    def generate(self, temp, nNotes):
        generated = self._generate(temp, nNotes)
        self.generated.append(generated)
        return generated

    def _generate(self, temp, nNotes):
        raise NotImplementedError("_generate function must be implemented")
    

    def _getPriorNotes(self, generated):
        return np.expand_dims(generated[-self.maxLen:], axis = 0)
        
    
        
        

class OnOffGenerator(Generator):
    def __init__(self, model, xTrain, smallestTimeUnit):
        super().__init__(model,xTrain, smallestTimeUnit)
    
    def _generate(self, temp, nNotes = 500):
        piece = []
        generated = choice(self.xTrain)
        
        for i in range(nNotes):
            priorNotes = self._getPriorNotes(generated)
            preds = self.model.predict(priorNotes)
            argMax = sample(preds, temp)
            piece.append(argMax)
            generated = np.concatenate([generated,preds])
        piece = self._convertToPieceObj(piece)
        return piece
    
    def _convertToPieceObj(self, piece):
        return OnOffPiece(piece, self.smallestTimeUnit)
    



#Same exact process as OnOffGenerator except for the type of the piece
class OnOnlyGenerator(OnOffGenerator):
    def __init__(self, model, xTrain, smallestTimeUnit):
        super().__init__(model,xTrain, smallestTimeUnit)
    

    def _convertToPieceObj(self, piece):
        return OnOnlyPiece(piece, self.smallestTimeUnit)
    
    


class MultiNetGenerator(Generator):
    def __init__(self, model, xTrain, smallestTimeUnit):
        super().__init__(model,xTrain, smallestTimeUnit)

    def _generate(self, temp, nNotes):
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
        return MultiNetPiece(piece, self.smallestTimeUnit)




   