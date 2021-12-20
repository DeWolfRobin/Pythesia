from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')

import mido
import time
from collections import deque
import os
import random
from threading import Thread
import threading
from functools import partial
import pickle

class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class WhiteKey(Widget):
    def __init__(self, **kwargs):
        super(WhiteKey, self).__init__(**kwargs)
        self.col = (1,1,1,1)
        self.originalCol = self.col
        self.pos = kwargs.get("pos")
        with self.canvas:
            self._color = Color(*self.col)
            self._rect = Rectangle(pos=self.pos,size=(23,150))
    def update(self):
        self._color.rgba = self.col

class BlackKey(Widget):
    def __init__(self, **kwargs):
        super(BlackKey, self).__init__(**kwargs)
        self.col = (0,0,0,1)
        self.originalCol = self.col
        self.pos = kwargs.get("pos")
        with self.canvas:
            self._color = Color(*self.col)
            self._rect = Rectangle(pos=self.pos,size=(12,100))
    def update(self):
        self._color.rgba = self.col

class Piano(Widget):
    keys = list()
    msglog = deque()
    echo_delay = 2
    skipSong = False
    autocancel = None
    preferences = dict()
    graphicsQueue = list()

    midiInportDropdown = DropDown()
    midiOutportDropdown = DropDown()

    activeOutputThreads = list()
    allActiveThreads = list()

    def playSong(self, song):
        self.outport.panic()

        #clear midi channels. CLEAR THIS IF MIDI SOUNDS BAD
        for i in ["B0 79 00","B0 64 00","B0 65 00","B0 06 0C","B0 64 7F","B0 65 7F","C0 00","B0 07 64","B0 0A 40","B0 5B 00","B0 5D 00"]:
            self.outport.send(mido.Message.from_hex(f"{i}"))
        self.autocancel = Clock.schedule_once(self.skipSongFunc,mido.MidiFile(song).length+5)
        for msg in mido.MidiFile(song).play():
            if (not threading.currentThread().stopped()) and (not self.skipSong):
                if not msg.is_meta:
                    self.outport.send(msg)

                    # try to move this to seperate thread as well, might not be good tho
                    if msg.type == "note_on":
                        if msg.velocity != 0:
                            self.graphicsQueue.append({
                                "action": "highlight",
                                "msg": msg
                                })
                        else:
                            self.graphicsQueue.append({
                                "action": "clear",
                                "msg": msg
                                })
                    if msg.type == "note_off":
                        self.graphicsQueue.append({
                            "action": "clear",
                            "msg": msg
                            })
            else:
                self.skipSong = False
                break

    def highlightKey(self, msg):
        self.keys[msg.note-21].col = (0,msg.velocity/127,0,1)
        self.keys[msg.note-21].update()

    def clearKey(self, msg):
        self.keys[msg.note-21].col = self.keys[msg.note-21].originalCol
        self.keys[msg.note-21].update()

    def skipSongFunc(self, dt):
        skipSong = True

    def playAllSongsIn(self, shuffle=True):
        songs = self.ListSongsInDir(self.preferences["dir"])

        if shuffle:
            random.shuffle(songs)
        for song in songs:
            if not threading.currentThread().stopped():
                print(f"Now playing: {song.replace('.mid','')}")
                try:
                    self.playSong(os.path.join(self.preferences["dir"], song))
                except Exception as e:
                    print(e)
                    pass
                    self.clearKeys()
            else:
                break

    def clearKeys(self):
        for key in self.keys:
            if key.col != key.originalCol:
                key.col = key.originalCol
            key.update()

    def searchSongInDir(self, name):
        songs = self.ListSongsInDir(self.preferences["dir"])
        matching = [s for s in songs if name.lower() in s.lower()]
        for song in matching:
            return os.path.join(self.preferences["dir"], song)

    def ListSongsInDir(self, dir):
        songs = list()
        for filename in os.listdir(dir):
            if filename.endswith(".mid"):
                songs.append(filename)
            else:
                continue
        return songs

    def setupPiano(self):
        self.loadPreferences()

        if "dir" not in self.preferences:
            self.preferences["dir"] = "/home/haywire/midi/"

        for inp in list(dict.fromkeys(mido.get_input_names())):
            btn = Button(text = inp, size_hint_y = None, height = 30)
            btn.bind(on_release = lambda btn: (
            setattr(self, "inport", mido.open_input(btn.text)),
            Clock.schedule_once(self.startListen),
            self.updatePreferences("inport", btn.text),
            self.midiInportDropdown.dismiss()
            ))
            self.midiInportDropdown.add_widget(btn)

        for outp in list(dict.fromkeys(mido.get_output_names())):
            btn = Button(text = inp, size_hint_y = None, height = 30)
            btn.bind(on_release = lambda btn: (
            setattr(self, "outport", mido.open_output(btn.text)),
            self.updatePreferences("outport", btn.text),
            self.midiOutportDropdown.dismiss()
            ))
            self.midiOutportDropdown.add_widget(btn)

        midiInportDropdownButton = Button(text ='Midi inport')
        midiInportDropdownButton.bind(on_release = self.midiInportDropdown.open)

        midiOutportDropdownButton = Button(text ='Midi outport')
        midiOutportDropdownButton.bind(on_release = self.midiOutportDropdown.open)

        layout = BoxLayout(orientation='vertical')
        songSelection = BoxLayout(orientation='horizontal')
        layout.add_widget(midiInportDropdownButton)
        layout.add_widget(midiOutportDropdownButton)

        selectedSong = TextInput(text='Song...', multiline=False)
        btnstartPlaybackSong = Button(text='Start song')
        # BUG: When no output is selected, nothing works yet, can be fixed with except: show error and don't play on outport
        btnstartPlaybackSong.bind(
            on_release = lambda btn: self.startPlayback(selectedSong.text))
        songSelection.add_widget(selectedSong)
        songSelection.add_widget(btnstartPlaybackSong)

        layout.add_widget(songSelection)

        dirSelection = BoxLayout(orientation='horizontal')

        selectedDir = TextInput(text=self.preferences["dir"], multiline=False)
        btnSetDir = Button(text='Set dir')
        btnSetDir.bind(on_release = lambda btn: (
        self.updatePreferences("dir", selectedDir.text),
        ))
        dirSelection.add_widget(selectedDir)
        dirSelection.add_widget(btnSetDir)

        layout.add_widget(dirSelection)

        btnstartPlaybackAllSongs = Button(text='Start random songs')
        # BUG: When no output is selected, nothing works yet, can be fixed with except: show error and don't play on outport
        btnstartPlaybackAllSongs.bind(
            on_release = self.startPlaybackAllSongs)

        layout.add_widget(btnstartPlaybackAllSongs)

        btnStopPlayback = Button(text='Stop songs')
        btnStopPlayback.bind(
            on_release = self.stopAllThreads)

        layout.add_widget(btnStopPlayback)

        btnSave = Button(text='Save preferences')
        btnSave.bind(
            on_release = self.savePreferences)

        layout.add_widget(btnSave)

        self.settings_popup = Popup(content=layout,
                                    title='Settings',
                                    size_hint=(0.8, 0.5),
                                    pos_hint={'right': .9, 'top': 1})

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

        settingsLayout = FloatLayout(size=(1248,500))

        btnSettings = Button(text='Open settings',
        size_hint=(0.1, 0.1),
        pos_hint={'left': .9, 'top': 1})
        btnSettings.bind(on_release = self.settings_popup.open)

        settingsLayout.add_widget(btnSettings)
        self.add_widget(settingsLayout)

        self.settings_popup.open()

    def savePreferences(self, e):
        f = open("preferences.pkl", "wb")
        pickle.dump(self.preferences, f)
        f.close()

    def loadPreferences(self):
        try:
            f = open("preferences.pkl", "rb")
            self.preferences = pickle.load(f)
            f.close()
            for full in list(dict.fromkeys(mido.get_input_names())):
                if " ".join(self.preferences['inport'].split(" ")[0:2]) in full:
                    self.inport = mido.open_input(full)
                    Clock.schedule_once(self.startListen)

            for full in list(dict.fromkeys(mido.get_output_names())):
                if " ".join(self.preferences['outport'].split(" ")[0:2]) in full:
                    self.outport = mido.open_output(full)

            self.outport = mido.open_output(self.preferences['outport'])
        except Exception as e:
            print(e)

    def updatePreferences(self, key, value):
        self.preferences[key] = value

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
        for i,e in enumerate(self.graphicsQueue):
            if e["action"] == "highlight":
                self.highlightKey(e["msg"])
            else:
                self.clearKey(e["msg"])
            self.graphicsQueue.pop(i)

    def startListen(self, dt):
        newThread = StoppableThread(target=self.listen)
        self.allActiveThreads.append(newThread)
        newThread.start()

    def stopAllThreads(self, e):
        for t in self.allActiveThreads:
            t.stop()
        self.allActiveThreads.clear()
        self.activeOutputThreads.clear()
        self.outport.panic()
        try:
            self.autocancel.cancel()
        except:
            pass
        self.clearKeys()
        Clock.schedule_once(self.startListen)

    def listen(self):
        if not threading.currentThread().stopped():
            msg = self.inport.receive()
            if msg.type != "clock":
                self.msglog.append({"msg": msg, "due": time.time() + self.echo_delay})
                if msg.type == "note_on":
                    # print(f"Note nr {msg.note} was hit with velocity {msg.velocity}")
                    self.keys[msg.note-21].col = (0,(msg.velocity/127) + 0.3,0,1)
                    self.keys[msg.note-21].update()
                if msg.type == "note_off":
                    # print(f"Note nr {msg.note} was released with velocity {msg.velocity}")
                    self.keys[msg.note-21].col = self.keys[msg.note-21].originalCol
                    self.keys[msg.note-21].update()
            self.listen()

    def startPlaybackAllSongs(self, dt):
        if not self.activeOutputThreads:
            newThread = StoppableThread(target=self.playAllSongsIn)
            self.activeOutputThreads.append(newThread)
            self.allActiveThreads.append(newThread)
            newThread.start()

    def startPlayback(self, song):
        if not self.activeOutputThreads:
            newThread = StoppableThread(target=self.playSong, args=(self.searchSongInDir(song),))
            self.activeOutputThreads.append(newThread)
            self.allActiveThreads.append(newThread)
            newThread.start()

class PianoApp(App):

    def build(self):
        self.game = Piano()
        self.game.setupPiano()

        Window.size = (1248, 500)
        Window.clearcolor = (0.22, 0.22, 0.22, 1)
        Window.bind(on_request_close=self.on_request_close)
        Window.bind(on_key_down=self.key_action)

        Clock.schedule_interval(self.game.update, 1.0/60.0)
        return self.game

    def key_action(self, window, keycode, *args):
        pass
        # print("got a key event: %s" % list(args))

    def on_request_close(self, *args):
        try:
            self.game.outport.panic()
        except:
            pass
        os._exit(1)
        return True

if __name__ == '__main__':
    PianoApp().run()
