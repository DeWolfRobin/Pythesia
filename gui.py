from kivy.app import App
from includes import Piano
from kivy.clock import Clock
from kivy.core.window import Window
import os
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')

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
