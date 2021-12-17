from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from kivy.graphics import Rectangle, Color

#midi integration
import mido
import time
from collections import deque
import os
import random

import time

from kivy.uix.boxlayout import BoxLayout

from kivy.config import Config
Config.set('graphics', 'width', '1248')
Config.set('graphics', 'height', '500')

class WhiteKey(Widget):
    def __init__(self, **kwargs):
        super(WhiteKey, self).__init__(**kwargs)
        self.col = (1,1,1,1)
        self.originalCol = self.col
        self.pos = kwargs.get("pos")
        with self.canvas:
            Color(*self.col)
            Rectangle(pos=self.pos,size=(23,150))
    def update(self):
        with self.canvas:
            Color(*self.col)
            Rectangle(pos=self.pos,size=(23,150))

class BlackKey(Widget):
    def __init__(self, **kwargs):
        super(BlackKey, self).__init__(**kwargs)
        self.col = (0,0,0,1)
        self.originalCol = self.col
        self.pos = kwargs.get("pos")
        with self.canvas:
            Color(*self.col)
            Rectangle(pos=self.pos,size=(12,100))
    def update(self):
        with self.canvas:
            Color(*self.col)
            Rectangle(pos=self.pos,size=(12,100))

class Piano(Widget):
    keys = list()
    msglog = deque()
    echo_delay = 2
    loaded = False
    songQueue = list()

    for inp in mido.get_input_names():
        if "Roland Digital Piano" in inp:
            inport = mido.open_input(inp)

    for outp in mido.get_output_names():
        if "Roland Digital Piano" in outp:
            outport = mido.open_output(outp)

    def playSong(self, song):
        self.songQueue = list(mido.MidiFile(song))

    def searchSongInDir(self, name, dir="/home/haywire/midi/"):
        songs = self.ListSongsInDir(dir)
        matching = [s for s in songs if name in s.lower()]
        for song in matching:
            return os.path.join(dir, song)

    def ListSongsInDir(self, dir):
        songs = list()
        for filename in os.listdir(dir):
            if filename.endswith(".mid"):
                songs.append(filename)
            else:
                continue
        return songs

    def setupPiano(self):
        #First 3 notes of the piano on the left
        self.keys.append(WhiteKey(pos=(0,0)))
        self.keys.append(BlackKey(pos=(20,50)))
        self.keys.append(WhiteKey(pos=(24,0)))

        #Middle of keyboard
        for i in range(7):
            self.drawOctave(i)

        #Last key
        self.keys.append(WhiteKey(pos=(48+(7*168),0)))

        for key in self.keys:
            if isinstance(key, WhiteKey):
                self.canvas.add(key.canvas)

        for key in self.keys:
            if isinstance(key, BlackKey):
                self.canvas.add(key.canvas)

    def drawOctave(self, nr):
        offset = 48+(nr*168)

        for i in range(7):
            self.keys.append(WhiteKey(pos=(offset+(24*i),0)))
            if i == 0:
                self.keys.append(BlackKey(pos=(offset+15,50)))
            if i == 1:
                self.keys.append(BlackKey(pos=(offset+44,50)))
            if i == 3:
                self.keys.append(BlackKey(pos=(offset+86,50)))
            if i == 4:
                self.keys.append(BlackKey(pos=(offset+113,50)))
            if i == 5:
                self.keys.append(BlackKey(pos=(offset+139,50)))


    def update(self, dt):
        # msg = self.inport.receive()
        # if msg.type != "clock":
        #     self.msglog.append({"msg": msg, "due": time.time() + self.echo_delay})
        #     if msg.type == "note_on":
        #         # print(f"Note nr {msg.note} was hit with velocity {msg.velocity}")
        #         self.keys[msg.note-21].col = (0,(msg.velocity/127) + 0.3,0)
        #         self.keys[msg.note-21].update()
        #     if msg.type == "note_off":
        #         # print(f"Note nr {msg.note} was released with velocity {msg.velocity}")
        #         self.keys[msg.note-21].col = self.keys[msg.note-21].originalCol
        #         self.keys[msg.note-21].update()
        if self.loaded:
            if not self.songQueue:
                self.playSong(self.searchSongInDir("galop"))
            else:
                msg = self.songQueue.pop(0)
                time.sleep(msg.time)
                if not msg.is_meta:
                    if msg.type == "note_on":
                        # print(f"Note nr {msg.note} was hit with velocity {msg.velocity}")
                        self.keys[msg.note-21].col = (0,(msg.velocity/127),0)
                        self.keys[msg.note-21].update()
                    if msg.type == "note_off":
                        # print(f"Note nr {msg.note} was released with velocity {msg.velocity}")
                        self.keys[msg.note-21].col = self.keys[msg.note-21].originalCol
                        self.keys[msg.note-21].update()
                    self.outport.send(msg)
        else:
            self.loaded = True


class PianoApp(App):
    def build(self):
        game = Piano()
        game.setupPiano()
        Clock.schedule_interval(game.update, 1.0/200.0)
        return game


if __name__ == '__main__':
    PianoApp().run()
