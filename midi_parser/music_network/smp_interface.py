# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 14:41:20 2021

@author: noahs
"""

#ALL PATHS ARE RELATIVE TO MUSICSAMPLER PATH ENIVRONMENT VARIABLE
#This means a paths of "" will be the MusicSampler environment variable directory

from os.path import join
from os import getenv, walk
from .serializer import loadMusicSampler
smpPath = getenv("MUSICSAMPLER")


#Recursively shows all PickledMusicSamplers and descriptions relative to MUSICSAMPLER PATH
#For each PickledMusicSampler shows all pieces
def tree(path=""):
    directory = join(smpPath,path)
    for (dirpath, dirnames, filenames) in walk(directory):
        for file in filenames:
            if ".smp" in file:
                smpInfo(join(dirpath, file))
    
    
 

def smpInfo(path):
    smp = loadMusicSampler(path)
    print("Path: "+ path)
    print("Music Description: " + smp.description)
    print("Piece Titles: ")
    for i,piece in enumerate(smp.music):
        print("   Piece "+ str(i)+": " + piece.title)
        

#Allows you to explore different PickledMusicSamplers that you have created
#And listen to music generated by repective network
def explore(path):
    pass
    