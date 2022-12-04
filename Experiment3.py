from playsound import playsound
from clingo import Control
from clingo.symbol import Function, Number, parse_term
import time
import numpy as np
import random
from multiprocessing import Process

# Initialise drum sounds
BassDrum, HiHat, Snare, Clap, Tom, Crash1, SnareRoll, Ride, Crash2= "playsound('drums/bassdrum.wav', block=False)", "playsound('drums/hat.wav', block=False)", \
                                                      "playsound('drums/snare.wav', block=False)", "playsound('drums/clap.wav', block=False)", \
                                                      "playsound('drums/tom.wav', block=False)", "playsound('drums/crash.wav', block=False)", \
                                                      "playsound('drums/snareroll.wav', block=False)","playsound('drums/ride.wav', block=False)","playsound('drums/crash2.wav', block=False)"

# clingo to python conversion
drum_conversion = {'bassdrum': BassDrum, 'hat': HiHat, 'snare': Snare, \
                   'tom': Tom, 'clap': Clap, 'false': 'False', 'crash': Crash1, \
                   'snareroll': SnareRoll, 'crash2':Crash2, 'ride': Ride, \
                   'false': "False"}

#################################
#     Timing Calculations       # 
###############################################################################################
# in this section, the bpm is input, and timings are calculated for all beat types.           #
# quarter notes are the reference beat; there are 120 quarter notes a minute for a bpm of 120 #
# the relative BPM for other note types are calculated, and then 60 is divided by that bpm    #
# to obtain the time between each note. The triplets boolean should be set to true to enable  #
# odd timings. set to false to get basic 4/4 timing                                           #
###############################################################################################
TRIPLETS = False
BPM = 360

quarter = BPM
timeQuarter = 60/quarter
eighth = BPM * 2
timeEighth = 60/eighth
half = quarter/2
timeHalf = 60/half
_12th = half + eighth
time12th = 60/_12th
_16th = eighth * 2
time16th = 60/_16th
_24th = _12th * 2
time24th = 60/_24th
halftriplet = quarter/3
timehalftrip = 60/halftriplet
whole = half/2
timeWhole = 60/whole
wholetriplet = halftriplet/2
timeWholeTriplet = 60/wholetriplet
doublewhole = whole/2
timeDoubleWhole = 60/doublewhole
doublewholetrip = (wholetriplet/3)*2
timeDoubleWholeTrip = 60/doublewholetrip

################################
#       Clingo Program 1       #
################################

program = '''
 % Define drum types
 drum(snare;hat;bassdrum;tom;ride;false).
  
 % The same calculation as before is done to find the relative bpms. 
 % The bpm becomes the length of the output array for that note
 
 quarter(0..G) :- bpm(G).
 half(0..G) :- quarter(X), G = X/2.
 halftriplet(0..G) :- quarter(X), G = X/3.
 eighth(0..G) :- bpm(X), G = X*2.
 whole(0..G) :- half(X), G = X/2.
 wholetriplet(0..G) :- halftriplet(X), G = X/2.
 doublewhole(0..G) :- whole(X), G = X/2.
 doublewholetrip(0..G) :- wholetriplet(X), G = (X/3)*2.
 twelth(0..G) :- half(X), eighth(Y), G = X + Y.
 sixteenth(0..G) :- eighth(X), G = X*2.
 twentyfourth(0..G) :- twelth(X), G = X*2.
 
 % helper function to treat time signatures as data so we dont have to deal with 
 % 11 predicates in the output

 time(quarter, X) :- quarter(X). 
 time(half, X) :- half(X). 
 time(halftriplet, X) :- halftriplet(X).
 time(eighth, X) :- eighth(X). 
 time(whole, X) :- whole(X). 
 time(wholetriplet, X) :- wholetriplet(X).
 time(doublewhole, X) :- doublewhole(X). 
 time(doublewholetrip, X) :- doublewholetrip(X).
 time(twelth, X) :- twelth(X). 
 time(sixteenth, X) :- sixteenth(X). 
 time(twentyfourth, X) :- twentyfourth(X).
 
 {assign(X, Timing, Drum): drum(Drum)} = 1 :- time(Timing, X).

 :- assign(X, quarter, Drum), Drum != bassdrum.
 :- assign(X, whole, Drum), Drum != hat.
 :- assign(X, half, Drum), Drum != snare.
 :- assign(X, eighth, Drum), Drum != ride.
 :- assign(X, twentyfourth, Drum), Drum = ride.
 :- assign(X, twelth, Drum), Drum = ride.
 
 #minimize{1, assign, X, twentyfourth, Drum: assign(X, twentyfourth, Drum), Drum != false;
           1, assign, X, sixteenth, Drum: assign(X, sixteenth, Drum), Drum != false;
           1, assign, X, twelth, Drum: assign(X, twelth, Drum), Drum != false;
           1, assign, X, doublewholetrip, Drum: assign(X, doublewholetrip, Drum), Drum != false;
           1, assign, X, wholetriplet, Drum: assign(X, wholetriplet, Drum), Drum != false;
           1, assign, X, halftriplet, Drum: assign(X, halftriplet, Drum), Drum != false;
           1, assign, X, eighth, Drum: assign(X, eighth, Drum), Drum = false;
           1, assign, X, doublewhole, Drum: assign(X, doublewhole, Drum), Drum = false;
           1, assign, X, whole, Drum: assign(X, whole, Drum), Drum = false;
           1, assign, X, half, Drum: assign(X, half, Drum), Drum = false;
           1, assign, X, quarter, Drum: assign(X, quarter, Drum),Drum = false}.

#show assign/3.

'''

#############################
#     Clingo Program 2      #
#############################
program2 = '''
drum(snare;hat;bassdrum;tom;ride;false).

 quarter(G) :- bpm(G).
 half(G) :- quarter(X), G = X/2.
 eighth(G) :- bpm(X), G = X*2.
 sixteenth(G) :- eighth(X), G = X*2.
 
 time(doublewhole, 32). time(whole, 16). time(half, 8). time(quarter, 4). time(eighth, 2). time(sixteenth, 1). 

 notes(0..G) :- sixteenth(G).
 
 {assign(X, Timing, Y, Drum): drum(Drum)} = 1 :- notes(X), time(Timing, Y), X\Y == 0.

 % :- assign(X, whole, Y, Drum), Drum != bassdrum.
 % :- assign(X, quarter, Y, Drum), Drum != ride.
 % :- assign(X, half, Y, Drum), Drum != snare.
 
prevalence(Drum, B) :- B = #count{X : assign(X, Timing, Y, Drum)}, notes(X), drum(Drum).
#minimize{1@1, prevalence, bassdrum, B: prevalence(bassdrum, B), B > 150;
          1@2, prevalence, snare, B: prevalence(snare, B), B > 50;
          1@3, prevalence, ride, B: prevalence(ride, B), B > 100}.

#maximize{1@1, prevalence, false, B: prevalence(false, B), B > 50}.
#show assign/4.
'''
# if triplets enabled initialise all lists and play all beats with their independent timings
if TRIPLETS:
    ctl = Control()
    ctl.configuration.solve.models="50"
    ctl.add("base1", [], f"bpm({BPM})." + program)
    ctl.ground([("base1", [])])

    def on_model(m):
      symbols = m.symbols(shown = True)
      #print(symbols)

    
    quarternotes     = ["" for i in range(int(BPM+1))]
    eighthnotes      = ["" for i in range(int(eighth+1))]
    halfnotes        = ["" for i in range(int(half+1))]
    _12thnotes       = ["" for i in range(int(_12th+1))]
    _16thnotes       = ["" for i in range(int(_16th+1))]
    _24thnotes       = ["" for i in range(int(_24th+1))]
    halftriplets     = ["" for i in range(int(halftriplet+1))]
    wholenotes       = ["" for i in range(int(whole+1))]
    wholetriplets    = ["" for i in range(int(wholetriplet+1))]
    doublewholenotes = ["" for i in range(int(doublewhole+1))]
    doublewholetrips = ["" for i in range(int(doublewholetrip+1))]

    models = []
    with ctl.solve(yield_=True, on_model=on_model) as handle:
        for model in handle:
            models.append(model.symbols(shown=True))

    model = random.choice(models)
    for symbol in model:
        if symbol.arguments[1].name == "doublewholetrip":
            drum = symbol.arguments[2].name
            doublewholetrips[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "doublewhole":
            drum = symbol.arguments[2].name
            doublewholenotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "wholetriplet":
            drum = symbol.arguments[2].name
            wholetriplets[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "whole":
            drum = symbol.arguments[2].name
            wholenotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "halftriplet":
            drum = symbol.arguments[2].name
            halftriplets[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if  symbol.arguments[1].name == "half":
            drum = symbol.arguments[2].name
            halfnotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "quarter":
            drum = symbol.arguments[2].name
            quarternotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "eighth":
            drum = symbol.arguments[2].name
            eighthnotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "twelth":
            drum = symbol.arguments[2].name
            _12thnotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if symbol.arguments[1].name == "sixteenth":
            drum = symbol.arguments[2].name
            _16thnotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'
        if  symbol.arguments[1].name == "twentyfourth":
            drum = symbol.arguments[2].name
            _24thnotes[symbol.arguments[0].number] = f'{drum_conversion[drum]}'

    # functions for multiprocessing
    def playQuarters():
        for i in quarternotes:
            eval(i)
            time.sleep(timeQuarter)
    def playHalfs():
        for i in halfnotes:
            eval(i)
            time.sleep(timeHalf)
    def playHalfTriplets():
        for i in halftriplets[0:-1]:
            eval(i)
            time.sleep(timehalftrip)
    def playWholes():
        for i in wholenotes:
            eval(i)
            time.sleep(timehalftrip)
    def playWholeTriplets():
        for i in wholetriplets:
            eval(i)
            time.sleep(timeWholeTriplet)
    def playDoubleWholes():
        for i in doublewholenotes:
            eval(i)
            time.sleep(timeDoubleWhole)
    def playDoubleWholeTrips():
        for i in doublewholetrips:
            eval(i)
            time.sleep(timeDoubleWholeTrip)
    def playEighths():
        for i in eighthnotes:
            eval(i)
            time.sleep(timeEighth)
    def playTwelths():
        for i in _12thnotes:
            eval(i)
            time.sleep(time12th)
    def playSixteenths():
        for i in _16thnotes:
            eval(i)
            time.sleep(time16th)
    def playTwentyFourths():
        for i in _24thnotes:
            eval(i)
            time.sleep(time24th)

# if triplets not enabled, fill a single list with all note types
else:
    ctl = Control()
    ctl.configuration.solve.models="50"
    ctl.add("base1", [], f"bpm({BPM})." + program2)
    ctl.ground([("base1", [])])

    def on_model(m):
      symbols = m.symbols(shown = True)
      #print(symbols)

    range = ["" for i in range(int(BPM*4)+1)]
    models = []
    with ctl.solve(yield_=True, on_model=on_model) as handle:
        for model in handle:
            models.append(model.symbols(shown=True))

    model = random.choice(models)
    for symbol in model:
        if symbol.name == "assign":
            drum = symbol.arguments[3].name
            range[symbol.arguments[0].number] = f'{drum_conversion[drum]}'

 
if __name__ == "__main__":
    if TRIPLETS:
        P1 = Process(target = playQuarters).start()
        P2 = Process(target = playHalfs).start()
        P6 = Process(target = playSixteenths).start()
        P8 = Process(target = playTwentyFourths).start()
        P7 = Process(target = playTwelths).start()
        p9 = Process(target = playEighths).start()
        p10 = Process(target = playWholes).start()
        p11 = Process(target = playWholeTriplets).start()
        P3 = Process(target = playHalfTriplets).start()
        P4 = Process(target = playDoubleWholes).start()
        P5 = Process(target = playDoubleWholeTrips).start()
    else:
        for i in range:
            eval(i)
            time.sleep(60/BPM)
