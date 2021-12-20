from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

class BlackKey(Widget):
    def __init__(self, **kwargs):
        super(BlackKey, self).__init__(**kwargs)
        self.originalCol = (0,0,0,1)
        with self.canvas:
            self._color = Color(*self.originalCol)
            self._rect = Rectangle(pos=self.pos,size=(12,100))
