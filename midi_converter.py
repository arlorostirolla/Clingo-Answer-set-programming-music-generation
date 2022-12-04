import mido
import string
import numpy as np
from regex import FULLCASE
np.set_printoptions(threshold=np.inf)

class MidiConverter:
    def __init__(self, arr=None, midi=None):
        self.arr = arr
        self.midi = midi

    def mid2arry(self, min_msg_pct=0.1):
        tracks_len = [len(tr) for tr in self.midi.tracks]
        min_n_msg = max(tracks_len) * min_msg_pct
        # convert each track to nested list
        all_arys = []
        for i in range(len(self.midi.tracks)):
            if len(self.midi.tracks[i]) > min_n_msg:
                ary_i = track2seq(self.midi.tracks[i])
                all_arys.append(ary_i)
        # make all nested list the same length
        max_len = max([len(ary) for ary in all_arys])
        for i in range(len(all_arys)):
            if len(all_arys[i]) < max_len:
                all_arys[i] += [[0] * 88] * (max_len - len(all_arys[i]))
        all_arys = np.array(all_arys)
        all_arys = all_arys.max(axis=0)
        # trim: remove consecutive 0s in the beginning and at the end
        sums = all_arys.sum(axis=1)
        ends = np.where(sums > 0)[0]
        return all_arys[min(ends): max(ends)]

    def arry2mid(self, tempo=500000):
        mid_new = mido.MidiFile()
        track = mido.MidiTrack()
        mid_new.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        for row in self.arr:
            on_notes = np.where(row > 0)[0]
            on_notes_vel = row[on_notes]
            first_ = True

            # Check if there is a chord
            if len(on_notes) > 1:
                # pass
                for n,v in zip(on_notes, on_notes_vel):
                    if first_:
                        track.append(mido.Message('note_on', note=n+21, velocity=120,
                                                                       time=0))
                        # first_ = False
                    else:
                        track.append(mido.Message('note_on', note=n+21, velocity=120,
                                                                       time=0))
                for n,v in zip(on_notes, on_notes_vel):
                    if first_:
                        track.append(mido.Message('note_off', note=n+21, velocity=120, time=880))
                        first_ = False
                    else:
                        track.append(mido.Message('note_off', note=n+21, velocity=120, time=0))

            else:
                for n,v in zip(on_notes, on_notes_vel):
                    track.append(mido.Message('note_on', note=n+21, velocity=120, time=0))
                    track.append(mido.Message('note_off', note=n+21, velocity=120, time=180))
        return mid_new


###############################################################
#                      HELPER FUNCTIONS                       #
###############################################################
def switch_note(last_state, note, velocity, on_=True):
        # piano has 88 notes, corresponding to note id 21 to 108, any note out of this range will be ignored
        result = [0] * 88 if last_state is None else last_state.copy()
        if 21 <= note <= 108:
            result[note-21] = velocity if on_ else 0
        return result

def msg2dict(msg):
        result = dict()
        if 'note_on' in msg:
            on_ = True
        elif 'note_off' in msg:
            on_ = False
        else:
            on_ = None
        result['time'] = int(msg[msg.rfind('time'):].split(' ')[0].split('=')[1].translate(
            str.maketrans({a: None for a in string.punctuation})))

        if on_ is not None:
            for k in ['note', 'velocity']:
                result[k] = int(msg[msg.rfind(k):].split(' ')[0].split('=')[1].translate(
                    str.maketrans({a: None for a in string.punctuation})))
        return [result, on_]

def get_new_state(new_msg, last_state):
        new_msg, on_ = msg2dict(str(new_msg))
        new_state = switch_note(last_state, note=new_msg['note'], velocity=new_msg['velocity'], on_=on_) if on_ is not None else last_state
        return [new_state, new_msg['time']]

def track2seq(track):
    # piano has 88 notes, corresponding to note id 21 to 108, any note out of the id range will be ignored
    result = []
    last_state, last_time = get_new_state(str(track[0]), [0]*88)
    for i in range(1, len(track)):
        new_state, new_time = get_new_state(track[i], last_state)
        if new_time > 0:
            result += [last_state]*new_time
        last_state, last_time = new_state, new_time
    return result

# mid = mido.MidiFile('debussy-clair-de-lune.mid', clip=True)
# result_array = mid2arry(mid)
# with open('arrMidi/arr_clair.txt','w') as f:
#     f.write(str(result_array))
# clair_midi = arry2mid(array_midi_converter, 1111111)
# clair_midi.save('convertedMidi/clair_midi.mid')

# # Reading the midi file
# mid = mido.MidiFile('convertedMidi/clair_midi.mid', clip=True)
# # print(str(mid))

# # Writing the content on text file 
# with open('convertedMidi\clair_midi.txt','w') as f:
#     f.write(str(mid))