import numpy as np
np.set_printoptions(threshold=np.inf)

class ChordAndNoteConverter:
    def __init__(self, notes, chords): 
        self.notes = notes
        self.chords = chords
        self.final_chords = np.empty((0,88), int)
        self.final_notes = np.empty((0,88), int)
        self.final_arr = np.empty((0,88), int)
    
    def get_final_chords(self):
        return self.final_chords

    def get_final_notes(self):
        return self.final_notes

    def get_final_arr(self):
        return self.final_arr

    def chordConverter(self, vel=127):
        NUM_CHORDS_MODEL = 16 
        for col in range(NUM_CHORDS_MODEL):
            # Retrieve the corresponding notes of a chord
            note0 = self.chords[0][col]
            note1 = self.chords[1][col]
            note2 = self.chords[2][col]

            # Create a 2d numpy array and update values of those notes position
            arr = np.zeros((1,88),int)
            arr[0][note0-21] = vel
            arr[0][note1-21] = vel
            arr[0][note2-21] = vel
            
            # Now append this array to the final_chords
            self.final_chords = np.append(self.final_chords, arr, axis=0)

    def noteConverter(self, vel=100):
        NUM_NOTES_MODEL = 256
        for col in range(NUM_NOTES_MODEL):
            # Retrieve the corresponding notes of a chord
            note0 = self.notes[0][col]
            
            # Create a 2d numpy array and update values of those notes position
            arr = np.zeros((1,88),int)
            arr[0][note0-21] = vel
            
            # Now append this array to the final_chords
            self.final_notes = np.append(self.final_notes, arr, axis=0)

    def mixNotesAndChords(self):
        NUM_ROW_NOTES_MODEL = 256
        CHORD_COUNTER = 0
        for row in range(NUM_ROW_NOTES_MODEL):
            if row % 16 == 0:
                self.final_arr = np.append(self.final_arr, [self.final_chords[CHORD_COUNTER]], axis=0)
                CHORD_COUNTER += 1
            else:
                self.final_arr = np.append(self.final_arr, [self.final_notes[row]], axis=0)

# if __name__ == '__main__':
#     arr_chord = np.array([[21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52],
#                       [31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62],
#                       [41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]])
    

#     cacn = ChordAndNoteConverter([], arr_chord)
#     cacn.chordConverter()
#     print(cacn.get_final_chords())