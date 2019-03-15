import cv2
import pandas as pd
from constants import KEYPOINTS
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock


class LoadButton(Widget):
    def __init__(self, **kwargs):
        super(LoadButton, self).__init__(**kwargs)
        btn = Button(text='Load Video', size_hint=(None, None), height=30, width=100, pos=(235, 330))
        btn.bind(on_press=self.load_video)
        self.add_widget(btn)

    def load_video(self, instance):
        
        video_canvas = self.parent.parent.ids['video_canvas']
        file_selected = self.parent.parent.ids["files"].fichoo.selection[0]
        
        if video_canvas.fill_event is not None:
            return
        
        if video_canvas.play_event is not None:
            video_canvas.play_event.cancel()
        video_canvas.texture = None
        video_canvas.frames = []
        video_canvas.processed_frames = []
        video_canvas.bodykeypoints = []
        video_canvas.real_bodykeypoints = []
        video_canvas.counter = 0
        video_canvas.cap = cv2.VideoCapture(file_selected)
        video_canvas.file_selected = file_selected
        video_canvas.fill_event = Clock.schedule_interval(video_canvas.fill, 1 / 30)



class PlayButton(Widget):
    def __init__(self, **kwargs):
        super(PlayButton, self).__init__(**kwargs)
        btn = Button(text='Play', size_hint=(1, 1), height=30, width=100, pos=(100 + 654, 192))
        btn.bind(on_press=self.play)
        self.add_widget(btn)

    def play(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        video_canvas.play_event = Clock.schedule_interval(video_canvas.play, 1 / 30)


class PauseButton(Widget):
    def __init__(self, **kwargs):
        super(PauseButton, self).__init__(**kwargs)
        btn = Button(text='Pause', size_hint=(1, 1), height=30, width=100, pos=(200 + 654, 192))
        btn.bind(on_press=self.pause)
        self.add_widget(btn)

    def pause(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        # cancel play
        video_canvas.play_event.cancel()


class SetLastButton(Widget):
    def __init__(self, **kwargs):
        super(SetLastButton, self).__init__(**kwargs)
        btn = Button(text='Set Last', size_hint=(1, 1), height=30, width=100, pos=(-100 + 654, 192))
        btn.bind(on_press=self.set_last)
        self.add_widget(btn)

    def set_last(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        joint_data = self.parent.parent.ids['joint_data']

        if video_canvas.counter > 0:
            video_canvas.real_bodykeypoints[video_canvas.counter][0] = video_canvas.real_bodykeypoints[video_canvas.counter - 1].copy()
        video_canvas.show_lines()
        video_canvas.show_points()
        joint_data.display_data()
        # video_canvas.
        # cancel play
        # video_canvas.play_event.cancel()

class ResetRealButton(Widget):
    def __init__(self, **kwargs):
        super(ResetRealButton, self).__init__(**kwargs)
        btn = Button(text='Reset Frame', size_hint=(1, 1), height=30, width=100, pos=(-200 + 654, 192))
        btn.bind(on_press=self.reset_real)
        self.add_widget(btn)

    def reset_real(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        joint_data = self.parent.parent.ids['joint_data']

        video_canvas.real_bodykeypoints[video_canvas.counter][0] = video_canvas.bodykeypoints[video_canvas.counter].copy()
        video_canvas.show_lines()
        video_canvas.show_points()
        joint_data.display_data()

class BackwardButton(Widget):
    def __init__(self, **kwargs):
        super(BackwardButton, self).__init__(**kwargs)
        btn = Button(text='Backward', size_hint=(None, 1), height=30, width=100, pos=(0 + 654, 192))
        btn.bind(on_press=self.backward)
        self.add_widget(btn)

    def backward(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        joint_data = self.parent.parent.ids['joint_data']
        if video_canvas.counter > 0:
            video_canvas.counter -= 1
        # video_canvas.texture = video_canvas.video_to_texture(video_canvas.frames[video_canvas.counter])
        #video_canvas.run_openpose(video_canvas.frames[video_canvas.counter])
        video_canvas.texture = video_canvas.processed_frames[video_canvas.counter]
        video_canvas.show_lines()
        video_canvas.show_points()
        joint_data.display_data()
        current_frame_label = self.parent.parent.ids['current_frame']
        current_frame_label.text = "Current Frame: " + str(video_canvas.counter)


class ForwardButton(Widget):
    def __init__(self, **kwargs):
        super(ForwardButton, self).__init__(**kwargs)
        btn = Button(text='Forward', size_hint=(1, 1), height=30, width=100, pos=(300 + 654, 192))
        btn.bind(on_press=self.forward)
        self.add_widget(btn)

    def forward(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        joint_data = self.parent.parent.ids['joint_data']
        if video_canvas.counter < len(video_canvas.frames) - 1:
            video_canvas.counter += 1
        # video_canvas.run_openpose(video_canvas.frames[video_canvas.counter])
        video_canvas.texture = video_canvas.processed_frames[video_canvas.counter]
        video_canvas.show_lines()
        video_canvas.show_points()
        joint_data.display_data()

        # video_canvas.texture = video_canvas.video_to_texture(video_canvas.frames[video_canvas.counter])
        current_frame_label = self.parent.parent.ids['current_frame']
        current_frame_label.text = "Current Frame: " + str(video_canvas.counter)

class ExportButton(Widget):
    def __init__(self, **kwargs):
        super(ExportButton, self).__init__(**kwargs)
        btn = Button(text='Export', size_hint=(None, None), height=30, width=100, pos=(5, 330))
        btn.bind(on_press=self.export)
        self.add_widget(btn)

    def export(self, instance):
        video_canvas = self.parent.parent.ids['video_canvas']
        bodykps = pd.DataFrame(columns=['x','y','confidence'])
        for frame in video_canvas.real_bodykeypoints:
            # print(frame[0])
            bodykp = pd.DataFrame(frame[0], columns=['x','y','confidence'], index=KEYPOINTS)
            bodykps = bodykps.append(bodykp)
        bodykps.to_csv('./bodykeypoints/'+ video_canvas.file_selected[-9:-3] + 'csv')
        print("DONE CSVING :)")