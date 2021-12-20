from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

class WhiteKey(Widget):
    def __init__(self, **kwargs):
        super(WhiteKey, self).__init__(**kwargs)
        self.originalCol = (1,1,1,1)
        with self.canvas:
            self._color = Color(*self.originalCol)
            self._rect = Rectangle(pos=self.pos,size=(23,150))
