# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:29:18 2021

@author: noahs
"""

from os import path, walk

class MidiPathExtractor:
    def __init__(self, folder, r=True):
        self.midiPaths = []
        self.addMidis(folder, r)
        
    
    def addMidis(self, folder, r=True):
        if(".mid" in folder):
            self.midiPaths.append(folder)
            return
        
        for (dirpath, dirnames, filenames) in walk(folder):
            for file in filenames:
                if ".mid" in file:
                    self.midiPaths.append(path.join(dirpath,file))
            if not r:
                break
