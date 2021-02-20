import mido_tools

class Note:
    def __init__(self, note, time, isNoteOn, velocity):
        self.absoluteTime = time
        self.deltaTime = None
        self.note = note
        self.isNoteOn = isNoteOn
        self.velocity = velocity
        
    def setDeltaTime(self,t):
        self.deltaTime = t
        
        
    
class OneTrackMidi:
    def __init__(self, mido):
        self.tPB = mido.ticks_per_beat
        self.oneTrack = self.restructToOneTrack(mido)
        self.timing = "abs"
        self.key = None
        
    
        
    #notesType1: notes where relative time is measured in terms of track
    #notesType0: notes where relative time measured in terms of all tracks
    def restructToOneTrack(self, mido):
        
        notesType1 = []
        for track in mido.tracks:
            _time = 0
            for msg in track:
                _time+=msg.time
                if(msg.type=="note_on" or msg.type == "note_off"):
                    notesType1.append(Note(msg.note, 
                                           _time, 
                                           msg.type, 
                                           msg.velocity))
                
                if(msg.type=="key_signature"): 
                    self.key= msg.key
                    
        
        notesType1.sort(key = lambda x: x.absoluteTime)
        self.midi = notesType1
        
        
    def absTimeToRel(self):
        assert self.timing == "abs"
        notesType0 = []
        absTime = self.midi.copy()
        firstNote = absTime[0]
        firstNote.setDeltaTime(0)
        notesType0.append(firstNote)
        
        
        for i in range(len(absTime[1:])-1):
            currentNote = absTime[i+1]
            previousNote = absTime[i]
            deltaTime = currentNote.absoluteTime - previousNote.absoluteTime
            currentNote.setDeltaTime(deltaTime)
            notesType0.append(currentNote)
        
        self.midi = notesType0

        
        
        
        
        
        
        
#Takes a reconstructed mido object and encodes it to 
class MidoEncode:
    
    #Takes in mido object then restructures into 1 track without delta time bs
    def encode(self, mf):
        oneTrackMidi = OneTrackMidi(mf)
        oneTrackMidi.absTimeToRel()
        encodedMido = []
        for note in oneTrackMidi.midi:
            encNote = mido_tools.encodeNote(note, oneTrackMidi.tPB)
            encodedMido.extend(encNote)
        return encodedMido
    
    