# see: https://www.daniweb.com/programming/software-development/code/216976/play-a-midi-music-file-using-pygame

# sudo pip install pygame

# on ubuntu
# sudo apt-get install python-pygame

import pygame

class MidiPlayer:
    def __init__(self, midi_file):
        # pick a midi music file you have ...
        # (if not in working folder use full path)

        self.midi_file = midi_file
        self.freq = 44100    # audio CD quality
        self.bitsize = -16   # unsigned 16 bit
        self.channels = 2    # 1 is mono, 2 is stereo
        self.buffer = 1024    # number of samples
        pygame.mixer.init(self.freq, self.bitsize, self.channels, self.buffer)

        # optional volume 0 to 1.0
        pygame.mixer.music.set_volume(0.8)
        try:
            self.play_music()
        except KeyboardInterrupt:
            # if user hits Ctrl/C then exit
            # (works only in console mode)
            pygame.mixer.music.fadeout(1000)
            pygame.mixer.music.stop()
            raise SystemExit

    def play_music(self):
        """
        stream music with mixer.music module in blocking manner
        this will stream the sound from disk while playing
        """
        clock = pygame.time.Clock()
        try:
            pygame.mixer.music.load(self.midi_file)
            print ("Music file %s loaded!" % self.midi_file)
        except pygame.error:
            print ("File %s not found! (%s)" % (self.midi_file, pygame.get_error()))
            return
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # check if playback has finished
            clock.tick(30)
