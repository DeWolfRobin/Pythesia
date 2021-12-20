from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

class WhiteKey(Widget):
    def __init__(self, **kwargs):
        super(WhiteKey, self).__init__(**kwargs)
        self.col = (1,1,1,1)
        self.originalCol = self.col
        with self.canvas:
            self._color = Color(*self.col)
            self._rect = Rectangle(pos=self.pos,size=(23,150))
