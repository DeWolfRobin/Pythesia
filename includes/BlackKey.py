from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

class BlackKey(Widget):
    def __init__(self, **kwargs):
        super(BlackKey, self).__init__(**kwargs)
        self.col = (0,0,0,1)
        self.originalCol = self.col
        with self.canvas:
            self._color = Color(*self.col)
            self._rect = Rectangle(pos=self.pos,size=(12,100))
    def update(self):
        self._color.rgba = self.col
