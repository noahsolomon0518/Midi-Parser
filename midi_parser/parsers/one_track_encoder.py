# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 22:52:51 2021

@author: noahs
"""

class OTEncoder:

    #list of midos
    def __init__(self):
        self.encodedOTs = []

    #func is a function that encodes for one OT
    def encodeAllOT(self, OTs, func):
        if(type(OTs)!=list):
            OTs = [OTs]
        for OT in OTs:
            func(OT)






class RoundedOTEncoder(OTEncoder):

    def __init__(self, oneTracks, normalizationFactor = 16):

        self.normalizationFactor = normalizationFactor
        super().__init__()
        super().encodeAllOT(oneTracks, self.encodeOneMido)

    def encodeOneMido(self, OT):
        encodedOT = []
        
        for note in OT.notesRel:
            encodedOT.extend(RoundedOTEncoder.encodeOneNote(note, OT.tpb, self.normalizationFactor))
        
        self.encodedOTs.append(encodedOT)
        


    @staticmethod
    def encodeOneNote(note, tpb, normalizationFactor):
        
        norm = tpb/normalizationFactor
        normalizedDT = note.time/norm
        if(normalizedDT>=0.5):
            normalizedDT = round(normalizedDT)
        elif(normalizedDT>0):
            normalizedDT = 1
        else:
            normalizedDT = 0

        waitTime = []
        waitTime = [175+normalizedDT] if normalizedDT>0 else []
        if(note.type == "note_on"):

            if(note.velocity==0):
                waitTime.append(note.note)
                return waitTime
            else:
                waitTime.append(note.note+88)
                return waitTime
        else:
            waitTime.append(note.note)
            return waitTime