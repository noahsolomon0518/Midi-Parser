# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:35:47 2021

@author: noahs
"""
from mido import MidiFile

class MidiToMido:
    def __init__(self, paths):
        self.midos = []
        self.parseToMidos(paths)
        
    def parseToMidos(self, paths):
        if(type(paths)!=list):
            paths = [paths]
            
        for path in paths:
            self.midos.append(MidiFile(path, type = 0))
            
    
    
    def log(self, ind = 0):
        f = open("mido_log.txt", "w")
        for track in self.midos[ind].tracks:
            for msg in track:
                f.write(str(msg)+"\n")
        f.close()
        
