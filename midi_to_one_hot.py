# -*- coding: utf-8 -*-

from midi_to_sequence import MidiToSequence
from sequence_to_one_hot import SequenceToOneHot


def encode(folder,sampleLength, gap, maxLength = 300, additionalDirs = []):
    midiToSeq = MidiToSequence(folder)
    for directory in additionalDirs:
        midiToSeq.addMidis(directory)
    toOneHot = SequenceToOneHot(sampleLength, gap, maxLength)


    midiToSeq.parseMidis()
    midis = midiToSeq.sequentializedMidis
    toOneHot.fit(midis)
    return (toOneHot.xEncoded, toOneHot.yEncoded)