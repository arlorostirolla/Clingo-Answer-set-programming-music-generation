from ast import arguments
from lib2to3.pygram import Symbols
from multiprocessing import Process, Event
from clingo import Control
import time
import numpy as np
import pygame.midi
import random
import midiutil
from chordAndNoteConverter import ChordAndNoteConverter
from midi_converter import MidiConverter
from midi_playback import MidiPlayer
import random
import mido

##############################
#    Clingo Program          #
##############################

program = r'''
    % Piano notes from 21 to 108 inclusive according to midi format
    note(21..108).

    % mapping root notes to ints to compare
    integer(1, c; 2, cs; 3, d; 4, ds; 5, e; 6, f;7, fs; 8, g; 9, gs; 10, a; 11, as; 12, b).
  
    % mapping fifth intervals
    fifth(c, g; cs, gs; d, a; ds, as; e, b; f, c; fs, cs; g, d; gs, ds; a, e; as, f; b, fs).

    % Database of all chords in a chromatic octave with four different chord types per 
    % root key (12 notes * (maj, min, sus4, dom7)). Notes are in midi number format.
    chord(c,   minor,  48, 51, 55). chord(c,   major,  48, 52, 55).  chord(c,   sus4, 48, 53,  55). chord(c,     dom7, 48, 52,  58).
    chord(cs,  minor,  49, 52, 56). chord(cs,  major,  49, 53, 56).  chord(cs,  sus4, 49, 54,  56). chord(cs,    dom7, 49, 53,  59).
    chord(d,   minor,  50, 53, 57). chord(d,   major,  50, 54, 57). chord(d,   sus4,  50, 55,  57). chord(d,    dom7,  50, 54,  60).
    chord(ds,  minor,  51, 54, 58). chord(ds,  major,  51, 55, 58). chord(ds,  sus4,  51, 56,  58). chord(ds,   dom7,  51, 55,  61).
    chord(e,   minor,  52, 55, 59). chord(e,   major,  52, 56, 59). chord(e,   sus4,  52, 57,  59). chord(e,    dom7,  52, 56,  62).
    chord(f,   minor,  53, 56, 60). chord(f,   major,  53, 57, 60). chord(f,   sus4,  53, 58,  60). chord(f,    dom7,  53, 57,  63).
    chord(fs,  minor,  54, 57, 61). chord(fs,  major,  54, 58, 61). chord(fs,  sus4,  54, 59,  61). chord(fs,   dom7,  54, 58,  64).
    chord(g,   minor,  55, 58, 62). chord(g,   major,  55, 59, 62). chord(g,   sus4,  55, 60,  62). chord(g,    dom7,  55, 59,  65).
    chord(gs,  minor,  56, 59, 63). chord(gs,  major,  56, 60, 63). chord(gs,  sus4,  56, 61,  63).  chord(gs,  dom7,  56, 60,  66).
    chord(a,   minor,  57, 60, 64). chord(a,   major,  57, 61, 64). chord(a,   sus4,  57, 62,  64). chord(a,    dom7,  57, 61,  67).
    chord(as,  minor,  58, 61, 65). chord(as,  major,  58, 62, 65). chord(as,  sus4,  58, 63,  65). chord(as,   dom7,  58, 62,  68).
    chord(b,   minor,  59, 62, 66). chord(b,   major,  59, 63, 66). chord(b,   sus4,  59, 64,  66). chord(b,    dom7,  59, 63,  69).

    % This line allows the chord predicate to consider higher/lower octaves which are available as notes
    % 13 notes up or down means it is the same note just at a different pitch
    % chord(A, B, C, D, E) :- note(F), note(G), note(H), chord(A, B, F, G, H), C = F+13, D = G+13, E = H+13.
    % chord(A, B, C, D, E) :- note(F), note(G), note(H), chord(A, B, F, G, H), C = F-13, D = G-13, E = H-13.

    % scales are all the notes that sound consonant in a certain key. If you compare them to the chords,
    % you will see that every chord is a subset of the scale it shares a name with
    % the chord is the keys root note(1), the third, and the fifth, with an optional 7th
    scale(c,major,  48,  50,  52,  53,  55,  57, 59). scale(c,minor,   48, 50, 51, 53, 55, 56, 58). scale(c,sus4, 48, 50, 52, 54, 55, 58, 59).
    scale(c,dom7,   48,  50,  52,  53,  55,  57, 58). scale(c,dorian,  48, 50, 51, 53, 55, 57, 58).
    scale(cs,major, 49,  51,  53,  54,  56,  58, 60). scale(cs,minor,  49, 51, 52, 54, 56, 57, 59).
    scale(cs,sus4,  49,  51,  53,  55,  56,  59, 60).
    scale(cs,dom7,  49,  51,  53,  54,  56,  58, 59). scale(cs,dorian, 49, 51, 52, 54, 56, 58, 59).
    scale(d,major,  50,  52,  54,  55,  57,  59, 61). scale(d,minor,   50, 52, 53, 55, 57, 58, 60). scale(d,sus4, 50, 52, 54, 56, 57, 60, 61).
    scale(d,dom7,   50,  52,  54,  55,  57,  59, 60). scale(d,dorian,  50, 52, 53, 55, 57, 59, 60).
    scale(ds,major, 51,  53,  55,  56,  58,  60, 62). scale(ds,minor,  51, 53, 54, 56, 58, 59, 61). scale(ds,sus4,51, 53, 55, 57, 58, 61, 62).
    scale(ds,dom7,  51,  53,  55,  56,  58,  60, 61). scale(ds,dorian, 51, 53, 54, 56, 58, 60, 61).
    scale(e,major,  52,  54,  56,  57,  59,  61, 63). scale(e,minor,   52, 54, 55, 57, 59, 60, 62). scale(e,sus4, 52, 54, 56, 58, 59, 62, 63).
    scale(e,dom7,   52,  54,  56,  57,  59,  61, 62). scale(e,dorian,  52, 54, 55, 57, 59, 61, 62).
    scale(f,major,  53,  55,  57,  58,  60,  62, 64). scale(f,minor,   53, 55, 56, 58, 60, 61, 63). scale(f,sus4, 53, 55, 57, 59, 60, 63, 64).
    scale(f,dom7,   53,  55,  57,  58,  60,  62, 63). scale(f,dorian,  53, 55, 56, 58, 60, 62, 63).
    scale(fs,major, 54,  56,  58,  59,  61,  63, 65). scale(fs,minor,  54, 56, 57, 59, 61, 62, 64). scale(fs,sus4,54, 56, 58, 60, 61, 64, 65).
    scale(fs,dom7,  54,  56,  58,  59,  61,  63, 64). scale(fs,dorian, 54, 56, 57, 59, 61, 63, 64).
    scale(g, major, 55,  57,  59,  60,  62,  64, 66). scale(g,minor,   55, 57, 58, 60, 62, 63, 65). scale(g,sus4, 55, 57, 59, 61, 62, 65, 66).
    scale(g,dom7,   55,  57,  59,  60,  62,  64, 65). scale(g,dorian,  55, 57, 58, 60, 62, 64, 65).
    scale(gs,major, 56,  58,  60,  61,  63,  65, 67). scale(gs,minor,  56, 58, 59, 61, 63, 64, 66). scale(gs,sus4,56, 58, 60, 62, 63, 66, 67).
    scale(gs,dom7,  56,  58,  60,  61,  63,  65, 66). scale(gs,dorian, 56, 58, 59, 61, 63, 65, 66).
    scale(a,major,  57,  59,  61,  62,  64,  66, 68). scale(a,minor,   57, 59, 60, 62, 64, 65, 67). scale(a,sus4, 57, 59, 61, 63, 64, 67,68).
    scale(a,dom7,   57,  59,  61,  62,  64,  66, 67). scale(a,dorian,  57, 59, 60, 62, 64, 66, 67).
    scale(as,major, 58,  60,  62,  63,  65,  67, 69). scale(as,minor,  58, 60, 61, 63, 65, 66, 68). scale(as,sus4,58, 60, 62, 64, 65, 68,69).
    scale(as,dom7,  58,  60,  62,  63,  65,  67, 68). scale(as,dorian, 58, 60, 61, 63, 65, 67, 68).
    scale(b,major,  59,  61,  63,  64,  66,  68, 70). scale(b,minor,   59, 61, 62, 64, 66, 67, 69). scale(b,sus4, 59, 61, 63, 65, 66, 69,70).
    scale(b,dom7,   59,  61,  63,  64,  66,  68, 69). scale(b,dorian,  59, 61, 62, 64, 67, 68, 69).
    
    % does the same as before, allows the scale predicate to consider higher/lower octaves
    % scale(A, B, C, D, E, F, G, H, I) :- scale(A, B, L, M, N, O, P, Q, R), note(L), note(M), note(N), note(O), note(P), note(Q), note(R),
    %                                    C = L+13, D = M+13, E = N+13, F = O+13, G=P+13, H=Q+13, I=R+13.
    % scale(A, B, C, D, E, F, G, H, I) :- scale(A, B, L, M, N, O, P, Q, R), note(L), note(M), note(N), note(O), note(P), note(Q), note(R),
    %                                    C = L-13, D = M-13, E = N-13, F = O-13, G=P-13, H=Q-13, I=R-13.

    % A grid of 16 bars as rows and 4 chords as column in each row
    grid(0..15, 0..2).

    % Assign a key in each bar
    {fill(ROW,COL,A,B,C,D,E): chord(A,B,C,D,E),note(C),note(D),note(E)} = 1 :- grid(ROW,COL). % X > 0.

    % Chord should not repeat in the same row
    :- fill(ROW,COL,CHORD,TYPE,A,B,C), scale(_,TYPE,P,_,_,_,_,_,_), TYPE != major, COL==0, A!=P.
    :- fill(ROW,COL0,CHORD,_,A,B,C) ,fill(ROW,COL1,CHORD1,TYPE,D,E,F), 
                                        scale(CHORD,TYPE,A,_,_,Q,_,_,_), TYPE != major, 
                                        COL0==0, COL1==1, D!=Q.
    :- fill(ROW,COL0,CHORD,_,A,B,C) ,fill(ROW,COL2,CHORD2,TYPE,G,H,I), 
                                        scale(CHORD,TYPE,A,_,_,_,R,_,_), TYPE != major, 
                                        COL0==0, COL1==2, G!=R.
    :- fill(ROW,COL,CHORD,TYPE,G,H,I), scale(_,TYPE,_,_,_,_,R,_,_), TYPE != major, COL==2, G!=R.
    :- fill(ROW,COL0,CHORD,TYPE,_,_,_), fill(ROW,COL1,CHORD,TYPE,_,_,_), fill(ROW,COL2,CHORD,TYPE,_,_,_), COL0==0,COL1==1,COL2==2. 
    :- fill(ROW,COL,CHORD,TYPE,A,_,_), fill(ROW+1,COL,CHORD,TYPE,A,_,_).
    :- fill(ROW,COL,CHORD,TYPE,A,_,_), fill(ROW+2,COL,CHORD,TYPE,A,_,_).
    :- fill(ROW,COL,CHORD,TYPE,A,_,_), fill(ROW+3,COL,CHORD,TYPE,A,_,_).

    


    
    #show fill/7.
'''

##########################################
#         Grounding and Solving          #
##########################################
# callback for clingo
def on_model(m):
    symbols = m.symbols(shown=True)

# Ground and solve
ctl = Control()
ctl.configuration.solve.models = "50"
ctl.add("base", [], program)
ctl.ground([("base",[])])
print("Grounding Finished !!")

models = []
with ctl.solve(yield_=True, on_model=on_model) as handle:
    for model in handle:
        models.append(model.symbols(shown=True))

models = [random.choice(models)]
print("Solving Finished")
print("MODELS LENGTH: ", len(models))

##########################################
#       Parsing the model in a list      #
##########################################
grid = [[]]*16
for model in models:
    _FIRST = True
    for symbol in model:
        if symbol.name == 'fill':
            row = int(str(symbol.arguments[0]))
            # print(row)
            col = int(str(symbol.arguments[1]))
            chord = str(symbol.arguments[2])
            chordType = str(symbol.arguments[3])
            note1 = int(str(symbol.arguments[4]))
            note2 = int(str(symbol.arguments[5]))
            note3 = int(str(symbol.arguments[6]))
            if grid[row] == []:
                grid[row] = [(col,chord,chordType,note1,note2,note3)]
                _FIRST = False
            else:
                grid[row] += [(col,chord,chordType,note1,note2,note3)]

# Sort the subgrid and then print it
for subgrid in grid:
    subgrid.sort(key=lambda y: y[0])
    print(subgrid)

##########################################
#           Create a Midi File           #
##########################################
mid_new = mido.MidiFile()
track = mido.MidiTrack()
mid_new.tracks.append(track)
track.append(mido.MetaMessage('set_tempo', tempo = 50000))

_first_chord = True
for row in grid:
    for ind in range(len(row)):
        track.append(mido.Message('note_on', note=row[ind][3]+12, velocity=100, time=1))    
        track.append(mido.Message('note_on', note=row[ind][4]+12, velocity=100, time=0))    
        track.append(mido.Message('note_on', note=row[ind][5]+12, velocity=100, time=0))    
        track.append(mido.Message('note_off', note=row[ind][3]+12, velocity=120, time=4000))
        track.append(mido.Message('note_off', note=row[ind][4]+12, velocity=120, time=0)) 
        track.append(mido.Message('note_off', note=row[ind][5]+12, velocity=120, time=0))    
        track.append(mido.Message('note_on', note=row[ind][3]+12, velocity=100, time=1))    
        track.append(mido.Message('note_on', note=row[ind][4]+12, velocity=100, time=0))    
        track.append(mido.Message('note_on', note=row[ind][5]+12, velocity=100, time=0))    
        track.append(mido.Message('note_off', note=row[ind][3]+12, velocity=120, time=4000))    
        track.append(mido.Message('note_off', note=row[ind][4]+12, velocity=120, time=0))    
        track.append(mido.Message('note_off', note=row[ind][5]+12, velocity=120, time=0))    
        track.append(mido.Message('note_on', note=row[ind][3]+12, velocity=100, time=1))    
        track.append(mido.Message('note_on', note=row[ind][4]+12, velocity=100, time=0))    
        track.append(mido.Message('note_on', note=row[ind][5]+12, velocity=100, time=0))    
        track.append(mido.Message('note_off', note=row[ind][3]+12, velocity=120, time=4000))    
        track.append(mido.Message('note_off', note=row[ind][4]+12, velocity=120, time=0))    
        track.append(mido.Message('note_off', note=row[ind][5]+12, velocity=120, time=0))    
        # track.append(mido.Message('note_on', note=row[ind][3]+12, velocity=100, time=1))    
        # track.append(mido.Message('note_on', note=row[ind][4]+12, velocity=100, time=0))    
        # track.append(mido.Message('note_on', note=row[ind][5]+12, velocity=100, time=0))    
        # track.append(mido.Message('note_off', note=row[ind][3]+12, velocity=120, time=4000))    
        # track.append(mido.Message('note_off', note=row[ind][4]+12, velocity=120, time=0))    
        # track.append(mido.Message('note_off', note=row[ind][5]+12, velocity=120, time=0))    

mid_new.save('convertedMidi\midi_new.mid')

##########################################
#           Play the MIDI File           #
##########################################
player = MidiPlayer(midi_file='convertedMidi\midi_new.mid')
pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(1)