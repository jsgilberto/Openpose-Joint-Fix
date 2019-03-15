from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line


class LabelGrid(Label):
    pass

class LabelTitle(ButtonBehavior, Label):
    one_active = False
    active_label = None

    def __init__(self, **kwargs):
        super(LabelTitle, self).__init__(**kwargs)
        self.active = False

    def on_press(self):
        video_canvas = self.parent.parent.parent.ids['video_canvas']
        print(video_canvas.mouse_pos)
        # if there is one label active:
        if LabelTitle.one_active:
            if self.active:
                LabelTitle.one_active = False
                LabelTitle.active_label = None
                self.active = False
                self.markup = False
                self.text = self.text.replace('[b][color=000000]', "").replace("[/color][/b]", "")
                self.canvas.before.clear()
            else:
                LabelTitle.active_label.active = False
                LabelTitle.active_label.markup = False
                LabelTitle.active_label.text = LabelTitle.active_label.text.replace('[b][color=000000]', "").replace("[/color][/b]", "")
                LabelTitle.active_label.canvas.before.clear()

                LabelTitle.active_label = self
                self.active = True
                self.markup = True
                self.text = '[b][color=000000]' + self.text + '[/color][/b]'
                self.canvas.before.clear()
                with self.canvas.before:
                    Color(1, 1, 1, 1)
                    Rectangle(pos=self.pos, size=self.size)
                    Line(width=1, rectangle=(self.x, self.y, self.width, self.height))
                return

        # activates flag:  
        else: 
            LabelTitle.one_active = True
            LabelTitle.active_label = self

            self.active = True
            self.markup = True
            self.text = '[b][color=000000]' + self.text + '[/color][/b]'
            self.canvas.before.clear()
            with self.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Line(width=1, rectangle=(self.x, self.y, self.width, self.height))
        

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 1, 0, 0)
            Rectangle(pos=self.pos, size=self.size)