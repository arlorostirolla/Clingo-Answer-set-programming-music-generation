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

midifile = midiutil.MIDIFile(11)
##############################
#    Clingo Program          #
##############################

program = r'''
  % from c3 to b5
  % note(int midi note)
  note(48;49;50;51;52;53;54;55;56;57;58;59;60;61;62;63;64;65;66;67).
  note(68;69;70;71;72;73;74;75;76;77;78;79;80;81;82;83).
  
  % mapping root notes to ints to compare
  integer(1, c; 2, cs; 3, d; 4, ds; 5, e; 6, f;7, fs; 8, g; 9, gs; 10, a; 11, as; 12, b).
  
  % mapping fifth intervals
  fifth(c, g; cs, gs; d, a; ds, as; e, b; f, c; fs, cs; g, d; gs, ds; a, e; as, f; b, fs).
  
  % Database of all chords in a chromatic octave with four different chord types per 
  % root key (12 notes * (maj, min, sus4, dom7)). Notes are in midi number format.
  chord(c,   minor,  48, 51, 55).  chord(c,   major, 48, 52, 55).  chord(c,   sus4, 48, 53,  55). chord(c,     dom7, 48, 52,  58).
  chord(cs,  minor,  49, 52, 56).  chord(cs,  major, 49, 53, 56).  chord(cs,  sus4, 49, 54,  56). chord(cs,    dom7, 49, 53,  59).
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

  chord(c,   dorian,  48, 51, 58).  chord(cs,  dorian,  49, 52, 59). chord(d,   dorian,  50, 53, 60).chord(ds,  dorian,  51, 54, 61).
  chord(e,   dorian,  52, 55, 62).  chord(f,   dorian,  53, 56, 63). chord(fs,  dorian,  54, 57, 64).chord(g,   dorian,  55, 58, 65).
  chord(gs,  dorian,  56, 59, 66). chord(a,   dorian,  57, 60, 67). chord(as,  dorian,  58, 61, 67). chord(b,   dorian,  59, 62, 69).
  
  % This line allows the chord predicate to consider higher/lower octaves which are available as notes
  % 13 notes up or down means it is the same note just at a different pitch
  chord(A, B, C, D, E) :- note(F), note(G), note(H), chord(A, B, F, G, H), C = F+13, D = G+13, E = H+13.
  chord(A, B, C, D, E) :- note(F), note(G), note(H), chord(A, B, F, G, H), C = F-13, D = G-13, E = H-13.

  % scales are all the notes that sound consonant in a certain key. If you compare them to the chords,
  % you will see that every chord is a subset of the scale it shares a name with
  % the chord is the keys root note(1), the third, and the fifth, with an optional 7th
  scale(c,major,  48,  50,  52,  53,  55,  57, 59). scale(c,minor,   48, 50, 51, 53, 55, 56, 58). scale(c,sus4, 48, 50, 52, 54, 55, 58, 59).
  scale(c,dom7,   48,  50,  52,  53,  55,  57, 58). scale(c,dorian,  48, 50, 51, 53, 55, 57, 58).
  scale(cs,major, 49,  51,  53,  54,  56,  58, 60). scale(cs,minor,  49, 51, 52, 54, 56, 57, 59).
  scale(cs,sus4,49, 51, 53, 55, 56, 59, 60).
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
  scale(A, B, C, D, E, F, G, H, I) :- scale(A, B, L, M, N, O, P, Q, R), note(L), note(M), note(N), note(O), note(P), note(Q), note(R),
                                    C = L+13, D = M+13, E = N+13, F = O+13, G=P+13, H=Q+13, I=R+13.
  scale(A, B, C, D, E, F, G, H, I) :- scale(A, B, L, M, N, O, P, Q, R), note(L), note(M), note(N), note(O), note(P), note(Q), note(R),
                                    C = L-13, D = M-13, E = N-13, F = O-13, G=P-13, H=Q-13, I=R-13.
  
  % 16 bars * 16 notes per bar
  grid(0..15, 0..15).

  % assigns 1 chord to every bar
  {assign(A, B, C, D, E, F): chord(B, C, D, E, F), note(D), note(E), note(F)} = 1 :-  grid(A, _).

  % fill 16 note positions every bar
  {fill(S, X, Z): note(Z)} = 1 :- grid(S, X).
  
  % constraints to stop clingo from cheating and playing the same note over and over
  :- fill(S, X, Z), fill(S, X+1, Z).
  :- fill(S, X, Z), fill(S, X+2, Z).
  :- fill(S, X, Z), fill(S, X+3, Z).

  % dont assign the same chord to two bars in a row
  :- assign(A, B, C, D, E, F), assign(A+1, B, C, D, E, F).

  % if you assign a dom7 chord, make sure the next one is the root
  :- assign(A, B, dom7, D, E, F), fifth(X, B), assign(A+1, L, G, H, I, J), X != L.
  
  % dont do massive hops between notes
  :- fill(S, X, Z), fill(S, X+1, A), |A-Z| > 10.

  % assign notes that are in the scale that shares the name with the chord played during the bar
  :- grid(S, X), assign(S, B, C, D, E, F), fill(S, X, A), scale(B, C, D, H, E, J, F, L, M), A != D, A != H, A != E, A != J, A != F, A != L, A != M. 
  
  % maximize notes that are contained within the chord being played
  % maximize 3rd fifth and 7th chord changes
  #maximize{1@1: fill(S, X, A), assign(S, B, C, D, E, F), A = D;
            1@2: fill(S, X, A), assign(S, B, C, D, E, F), A = F;
            1@3: fill(S, X, A), assign(S, B, C, D, E, F), A = E;
            1: assign(A, B, C, D, E, F), assign(A+1, G, H, I, J, K), D-I == 3;
            1: assign(A, B, C, D, E, F), assign(A+1, G, H, I, J, K), D-I == 5;
            1: assign(A, B, C, D, E, F), assign(A+1, G, H, I, J, K), D-I == 7}.

  % minimize the tritone with number 1 priority, followed by the minor second
  #minimize{1@1: fill(_, X, A), fill(_, X+1, A+6);
           1@2: fill(_, X, A), fill(_, X+1, A+1);
           1: assign(A, B, sus4, D, E, F);
           1: assign(A, B, dom7, D, E, F)}.

  #show assign/6.
  #show fill/3.
  '''
##########################################
#     Grounding, Solving, and Parsing    #
##########################################
     
# callback for clingo
def on_model(m):
  symbols = m.symbols(shown=True)
  #print(symbols)

# ground and solve
ctl = Control()
ctl.configuration.solve.models="100"
ctl.add("base", [], program)
ctl.ground([("base", [])])
print("Grounding finished")
# ctl.solve(on_model=on_model)
models = []
chords = np.ndarray((3, 16), dtype=np.uint16)
grid = np.ndarray((1, 256), dtype=np.uint16)
with ctl.solve(yield_=True, on_model=on_model) as handle:
    for model in handle:
        models.append(model.symbols(shown=True))

models = [random.choice(models)]
print("Solving finished")
print(len(models))
count = 0
for model in models:
    for symbol in model:
        if symbol.name == "fill":
            index = symbol.arguments[0].number*16 + symbol.arguments[1].number
            midiNumber = symbol.arguments[2].number
            grid[0, index] = midiNumber

        if symbol.name == 'assign':
            midi1 = symbol.arguments[3].number
            chords[0, symbol.arguments[0].number] = midi1
            midi2 = symbol.arguments[4].number
            chords[1, symbol.arguments[0].number] = midi2
            midi3 = symbol.arguments[5].number
            chords[2, symbol.arguments[0].number] = midi3
print("Parsing finished")

#########################
#     Midi Conversion   #
#########################

# Convert all the chords and notes into a numpy array 
cacn = ChordAndNoteConverter(grid.tolist(), chords.tolist())
cacn.chordConverter()
cacn.noteConverter()
cacn.mixNotesAndChords()
# print("FINAL: ", cacn.get_final_arr()) 
array_midi_converter = cacn.get_final_arr()

# Convert the numpy array into midi file
midi_converter = MidiConverter(array_midi_converter)
midi_file = midi_converter.arry2mid()
midi_file.save('convertedMidi\midi_file.mid')
print(str(midi_file))

#Play the midi file
player = MidiPlayer(midi_file='convertedMidi\midi_file.mid')

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(1)
print(chords.toList())
print(grid.toList())


#################################
#  Old Multiprocessing Method   #
#################################


'''def playChord0():
    for j in chords[0].tolist():
        print(j)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)
def playChord1():
    for j in chords[1].tolist():
        print(j)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)

def playChord2():
    for j in chords[2].tolist():
        print(j)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)
        player.note_on(j, 127)
        time.sleep(2)
        player.note_off(j, 127)
def playAllNotes0():
    for i in grid[0]:
        player.note_on(i, 127)
        time.sleep(0.25)
        player.note_off(i, 127)



# initialise variables

if __name__ == '__main__':
    # wav = sd.rec(int(20 * 44100), samplerate=44100, channels=1)
    # sd.wait()
    # e = Event()
    p1 = Process(target=playAllNotes0).start()
    p2= Process(target=playChord0).start()
    p2 = Process(target=playChord1).start()
    p2 = Process(target=playChord2).start()
'''