from synthesizer import Player, Synthesizer, Waveform, Writer
from pychord import Chord, QualityManager, ChordProgression
from pedalboard import Pedalboard, Chorus, Reverb, Phaser, \
                        Compressor, MP3Compressor, Delay
from pedalboard.io import AudioFile
from multiprocessing import Process, Event
from threading import Thread
from clingo import Control
from playsound import playsound
import time
#import sounddevice as sd
import random
#sd.default.device = 14

#######################################################
# Player, Synth, Chord, Note, and Drum initialisation #
#######################################################

# open players for all instruments
player = Player()
player.open_stream()
player1 = Player()
player1.open_stream()
player2 = Player()
player2.open_stream()
player3 = Player()
player3.open_stream()
player4 = Player()
player4.open_stream()

#initialise synths for all instruments
harmonySynthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume = 0.1,
                                 osc2_waveform=Waveform.sine, use_osc2=True,
                                 osc2_volume=0.5)
bassSynthesizer = Synthesizer(osc1_waveform=Waveform.square, osc1_volume = 0.3)
tenorSynthesizer = Synthesizer(osc1_waveform= Waveform.sawtooth, osc1_volume = 0.3)
altoSynthesizer = Synthesizer(osc1_waveform= Waveform.sine, osc1_volume = 0.3)
highSynthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=0.0)

# initialization of pychord chords
Em7, Em7_G, Em9, Fsm7 = Chord("Em7"), Chord("Em7/G"), Chord("Em9"), Chord("F#m7")
GM7, GM9, A7, A9, Bm7  = Chord('GM7'), Chord('GM9'), Chord('Am7'), Chord('Amaj9'), Chord('Bm7')
Bm9, DM7, DM9 = Chord('Bm9'), Chord('DM7'), Chord('DM9')

# initialisation of drums
BassDrum, HiHat, Snare, Clap, Tom, Crash, SnareRoll = "playsound('drums/bassdrum.wav')", "playsound('drums/hat.wav')", \
                                                      "playsound('drums/snare.wav')", "playsound('drums/clap.wav')", \
                                                      "playsound('drums/tom.wav')", "playsound('drums/crash.wav')", \
                                                      "playsound('drums/snareroll.wav')"

# pedalboard is used for adding effects to the output to make it sounds nice
bass_board = Pedalboard([Compressor(threshold_db=-6, ratio=30),Chorus(),
                         Reverb(room_size= 0.5)])
chords_board = Pedalboard([Compressor(threshold_db=-6, ratio=30),Chorus(),
                           Reverb(room_size= 0.3)])
board = Pedalboard([Compressor(threshold_db=-6, ratio=30),Reverb(room_size= 0.3)])

#####################################################
#      Clingo answer set to python conversion       #
#####################################################

# dicts to convert clingo output into pychord chords
chord_conversion = {'em7': Em7, 'em7_g': Em7_G, 'em9':Em9, 'fsm7': Fsm7,
              'gmaj7': GM7, 'gmaj9': GM9, 'a7': A7, 'a9':A9, 'bm7': Bm7,
              'bm9': Bm9, 'dmaj7': DM7, 'dmaj9': DM9}

# dicts to convert clingo output into pychord notes
note_conversion = {'e1': 'E1', 'fs1':r'F#1', 'g1':'G1',
                   'a1':'A1','b1':'B1', 'cs1':r'C#1', 'd1':'D1',
                   'e2': 'E2', 'fs2': r'F#2', 'g2': 'G2',
                   'a2': 'A2', 'b2': 'B2', 'cs3': r'C#3',
                   'd3': 'D3', 'e3': 'E3', 
                   'false': False,
                   'fs3': r'F#2', 'g3': 'G3', 
                   'a3': 'A3', 'b3':'B3', 'cs4': r'C#4', 
                   'd4': 'D4', 'e4': 'E4', 'fs4':r'F#4', 
                   'g4': 'G4', 'a4':'A4', 'b4': 'B4',
                   'cs5': r'C#5', 'd5':'D5', 'e5':'E5'}

drum_conversion = {'bassdrum': BassDrum, 'hat': HiHat, 'snare': Snare,
                   'tom': Tom, 'clap': Clap, 'false': 'False', 'crash': Crash, 'snareroll': SnareRoll}

################################
#       Clingo Program         #
################################

program = r'''
  % Database of chords
  root(em7). root(em7_g). root(em9). chord(fsm7). chord(gmaj7).
  chord(gmaj9). chord(bm7). chord(bm9). chord(a7). chord(a9).
  chord(dmaj7). chord(dmaj9).

  % Database of notes
  rootnote(e1). note(fs1). third(g1). note(a1). fifth(b1). note(cs1). seventh(d1).
  note(e1). note(g1). note(b1). note(d1). note(false).
  rootnote(e2). note(fs2). third(g2). note(a2). fifth(b2). note(cs3). seventh(d3). rootnote(e3).
  note(e2). note(g2). note(b2). note(d3). 
  rootnote(e3). note(fs3). third(g3). note(a3). fifth(b3). note(cs4). seventh(d4). rootnote(e4).
  note(e3). note(g3). note(b3). note(d4).
  %rootnote(e4). note(fs4). third(g4). note(a4). fifth(b4). note(cs5). seventh(d5). rootnote(e5).
  %note(e4). note(g4). note(b4). note(d5).
  
  % drums
  drum(bassdrum). drum(hat). drum(snare). drum(snareroll). drum(clap). drum(tom).

  % 8 bars, 8 notes and 16 drum beats per bar, played by 4 instruments (+ drums)
  steps(0..7). grid(0..7,0..3).
  drums(0..15).
  % assign root of key to the first step

  % fill chord, note, and drum grids
  {assign(1, X): root(X)} = 1 :- steps(1).
  {assign(N, X): chord(X)} = 1 :- steps(N), N > 1.
  {fill(X, Y, Z): note(Z)} = 1 :-  grid(X,Y).
  {beat(X, Drum): drum(Drum)} = 1 :-  drums(X).
  
  % dont play the same note twice
  :- fill(X,Y,Z), fill(X+1, Y, Z).
  % specific dissonant harmonies
  :- fill(X, Y, "b2"), fill(X, Y+1, "cs3");fill(X, Y+2, "cs3");fill(X, Y-1, "cs3");fill(X, Y-2, "cs3").
  :- fill(X, Y, "e2"), fill(X, Y+1, "fs2");fill(X, Y+2, "fs2");fill(X, Y-1, "fs2");fill(X, Y-2, "fs2").
  
  % minimizes false notes (silence)
  #minimize{1, fill, X, Y, Z : fill(X, Y, Z), Z != false}.
  % maximize playing notes in the chord currently being played
  %#maximize{1, fill, X, Y, Z: fill(X,Y,Z),rootnote(z);
  %         1, fill, X, Y, Z: fill(X,Y,Z),third(z);
  %         1, fill, X, Y, Z: fill(X,Y,Z),fifth(z);
  %         1, fill, X, Y, Z: fill(X,Y,Z),seventh(z)}.
  
  % don't play the same chord twice, a chord with the same root note but different chord type
  :- assign(N, X), assign(N+1, X).
  :- assign(N, dmaj7;dmaj9), assign(N+1, dmaj7;dmaj9).
  
  % manually hardcoded drums
  :- beat(X, bassdrum), beat(X-1, snare).
  :- beat(X, bassdrum), beat(X+1, snare).
  :- beat(X, Y), X\4 = 0, Y != bassdrum.
  :- beat(X, Y), X = (2;6;10;14), Y != snare.
  :- beat(X, Y), X = (1;3;5;7;9;11;13;15), Y != hat.

  #show assign/2.
  #show fill/3.
  #show beat/2.'''

# initialise variables
barlength = 8
symbols = []


# callback for clingo
def on_model(m):
  global symbols
  symbols = m.symbols(atoms=True, terms=True)
  #print(symbols)

# ground and solve
ctl = Control()
ctl.configuration.solve.models="200"
ctl.add("base", [], program)
print("Grounding")
ctl.ground([("base", [])])

models = []
with ctl.solve(yield_=True, on_model=on_model) as handle:
    for model in handle:
        print("Solving")
        models.append(list(model.symbols(atoms=True, terms=True)))


#################################
#       Hamming Distance        #
#################################
def hammingDistance(model1, listIn, listOut):
  print("Hamming Distance")
  listOut.append(model1)
  
  if len(listOut) == 5:
    return listOut

  distances = dict()
  for i in range(1, len(listIn)):
      model2 = listIn[i]
      sum_differences = 0
      for k in range(len(model1)):
          if model1[k] != model2[k]:
              sum_differences += 1
      distances[i] = sum_differences
  for (key, value) in distances.items():
    if value == max(distances.values()):
      listIn.remove(model1)
      return hammingDistance(listIn[key], listIn, listOut)


#################################
#     Parsing Clingo Output     #
#################################
modelsOut = []
toPlay = []
print("Parsing")
for model in hammingDistance(random.choice(models), models, modelsOut):
  progression = []
  drums = ["","","","","","","","","","","","","","","", ""]
  notes = [["", "", "", "", "", "", "", ""],
           ["", "", "", "", "", "", "", ""],
           ["", "", "", "", "", "", "", ""],
           ["", "", "", "", "", "", "", ""]]
  for symbol in model:  
    if symbol.name == 'assign':
      index = symbol.arguments[0].number
      chord = symbol.arguments[1].name
      progression.append([index, chord_conversion[chord]])

    if symbol.name == "fill":
      notes[symbol.arguments[1].number][symbol.arguments[0].number] = note_conversion[symbol.arguments[2].name]

    if symbol.name == "beat":
      drums[symbol.arguments[0].number] = drum_conversion[symbol.arguments[1].name]


  drums[1] = 'hat' # unsure why but clingo is making the second beat snare when it should be hat
  progression.sort()
  progression = [i[1] for i in progression]
  
  print(len(toPlay))
  toPlay.append([progression, notes, drums])


###################################################
# functions to play in parallel to produce output #
###################################################

def play_bar(progression):
  for j in range(2):
    for i in range(barlength):
        player.play_wave(chords_board(harmonySynthesizer.generate_chord(progression[i].components_with_pitch(root_pitch=3), 1), 44100))
def play_bass(notes):
  for j in range(4):
    for i in range(barlength):
        player1.play_wave(bass_board(bassSynthesizer.generate_chord([notes[0][i]], 0.5), 44100))
def play_tenor(notes):
  for j in range(4):
    for i in range(barlength):
      player2.play_wave(board(tenorSynthesizer.generate_chord([notes[1][i]], 0.5), 44100))
def play_alto(notes):
  for j in range(4):
    for i in range(barlength):
        player3.play_wave(board(altoSynthesizer.generate_chord([notes[2][i]], 0.5), 44100))
def play_high(notes):
  for j in range(4):
    for i in range(barlength):
      player4.play_wave(board(highSynthesizer.generate_chord([notes[3][i]], 0.5), 44100))
def play_drums(drums):
    for k in range(2):
        for i in range(16):
            eval(drums[i])
            time.sleep(0.259)

if __name__ == '__main__':
  print(str(len(toPlay)))
  for i in toPlay:
    progression = i[0]
    notes = i[1]
    drums = i[2]
    #p5 = Process(target=play_drums(i[2])).start()
    p2 = Process(target=play_bass, args=(notes,)).start()
    p1 = Process(target=play_bar, args=(progression,)).start()
    p3 = Process(target=play_tenor, args=(notes,)).start()
    p4 = Process(target=play_alto, args=(notes,)).start()
    time.sleep(20)

 






'''

#minimize{
    1, call, Area, Time : call_fire_department(Area, Time, Time+1) ;
    1, send, Guard, Area, Time : send_security_guard(Guard, Area, Time, Time+1) ;
    1, activate, Area, Time : activate_fire_suppression(Area, Time, Time+1)
}.
1 means count 1 towards the fact
Tag (call, send, activate), Guard, Area and Time make sure each fact is counted. E.g. 
without the tag activate_file_suppression(foo, 20, 21) and call_fire_department(foo, 20, 21) would be merged in the set.

answered Jun 16, 2015 at 19:32
https://stackoverflow.com/questions/30852730/how-to-minimize-the-number-of-instances-of-a-literal-in-clingo-4-5


drum samples from 
https://github.com/Moragoh/KeyDrum/tree/master/KeyBand_release
'''



##############################
#       Writing to a Wav     #
##############################
'''
outputs = []
audiofiles = []
samplerateFinal = 0

writer = Writer()

count = 0
for i in final_progression:
  wave = harmonySynthesizer.generate_chord(i.components_with_pitch(root_pitch=3), 3.0)
  writer.write_wave(f'{count}.wav', wave)
  with AudioFile(f'{count}.wav', 'r') as f1:
    audio1 = f1.read(f1.frames)
    samplerate1 = f1.samplerate
    audiofiles.append([audio1, samplerate1])
    count +=1

for (audio, samplerate) in audiofiles:
  output1 = board(audio, samplerate)
  outputs.append(output1)
  samplerateFinal = samplerate

with AudioFile('output.wav', 'w', samplerateFinal, outputs[0].shape[0]) as f:
  f.write(outputs[0])
  f.write(outputs[1])
  f.write(outputs[2])
  f.write(outputs[3])
  f.write(outputs[4])
  f.write(outputs[5])
  f.write(outputs[6])
  f.write(outputs[7])
'''

