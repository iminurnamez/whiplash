from itertools import cycle

import pygame as pg

from .. import prepare


class MusicHandler(object):
    """Manages playback of background music."""
    def __init__(self):
        self.songs = cycle(["Lights", "Moon_Party", "Regards_from_Mars",
                                     "Stars_path", "Ultraspeed"])
        self.bpm = {"Lights": 480,
                           "Moon_Party": 420,
                           "Regards_from_Mars": 448,
                           "Stars_path": 500,
                           "Ultraspeed": 422}
        
    def next_song(self):
        """Start playback of next song in cycle."""
        self.current_song = next(self.songs)
        pg.mixer.music.load(prepare.MUSIC[self.current_song])
        pg.mixer.music.play()
        
    def update(self):
        """Check if current song has finished. If so, start next song."""
        if not pg.mixer.music.get_busy():
            self.next_song()
            
    @property
    def current_bpm(self):
        """
        Return beats per minute of current song according to
        the relevant value in self.bpm.
        """
        return self.bpm[self.current_song]