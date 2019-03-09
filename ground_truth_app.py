# pylint: disable=import-error
from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1366') # 1280
Config.set('graphics', 'height', '768') # 720

import cv2
import sys
import cv2
import os
from sys import platform
import argparse 
import numpy as np
import pandas as pd
import time

# Import Openpose (Windows/Ubuntu/OSX)
PYOPENPOSE_DIR = "C:/Users/ruben/Documents/Github/openpose/build/python/openpose/Release"
MODELS_DIR = "C:/Users/ruben/Documents/Github/openpose/models/"

sys.path.append(PYOPENPOSE_DIR)
import pyopenpose as op


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.properties import NumericProperty #, ReferenceListProperty,ObjectProperty
# from kivy.properties import Property, NumericProperty, StringProperty
from kivy.vector import Vector
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import escape_markup
# from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line



KEYPOINTS = ['nose', 'neck', 'rshoulder', 'relbow', 'rwrist', 'lshoulder','lelbow', 
            'lwrist', 'midhip', 'rhip', 'rknee', 'rankle', 'lhip', 'lknee', 'lankle',
            'reye', 'leye', 'rear', 'lear', 'lbigtoe', 'lsmalltoe', 'lheel', 'rbigtoe',
            'rsmalltoe', 'rheel']

params = {
    'model_folder': MODELS_DIR,
    'number_people_max': 1
}

# Starting OpenPose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

class WindowShape(FloatLayout):
    
    orientation = 'horizontal'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print(self.ids)

class LeftLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.video_path = TextInput(text="")
        #self.add_widget(self.video_path)
        # path_label = self.ids["path_label"]
        print(self.ids)
        # path = self.ids["path_input"]
        self.add_widget(LoadButton())
        # print(path)
        # self.add_widget(Label(text="Enter video path"))

class MiddleLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RightLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Files(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(Files, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.fichoo = FileChooserListView()
        self.add_widget(self.fichoo)
        

class Description(GridLayout):
    pass
    # def __init__(self, *args, **kwargs):
    #     super(Description, self).__init__(*args, **kwargs)
    #     #self.frame_num = None
    #     pass

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
        # frame_number_label.text += str(len(video_canvas.frames))


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
        joint_data.display_data()
        # video_canvas.texture = video_canvas.video_to_texture(video_canvas.frames[video_canvas.counter])
        current_frame_label = self.parent.parent.ids['current_frame']
        current_frame_label.text = "Current Frame: " + str(video_canvas.counter)

class JointData(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_pos = None

    def display_data(self):
        video_canvas = self.parent.parent.ids["video_canvas"]
        for i, keypoint in enumerate(KEYPOINTS):
            for j, element in enumerate(["_x", "_y"]):
                self.parent.parent.ids[keypoint + element].text = str(round(video_canvas.bodykeypoints[video_canvas.counter][0][i][j], 2))           
                self.parent.parent.ids[keypoint + element + "_real"].text = str(round(video_canvas.real_bodykeypoints[video_canvas.counter][0][i][j], 2))

    def get_active_label(self):
        active_element = None
        # self.mouse_pos
        for element in KEYPOINTS:
            label_obj = self.parent.parent.ids[element + "_label"]
            if label_obj.active:
                active_element = label_obj
                return active_element, element

        
    

class LabelGrid(Label):
    pass

class LabelTitle(ButtonBehavior, Label):
    one_active = False
    active_label = None

    def __init__(self, **kwargs):
        super(LabelTitle, self).__init__(**kwargs)
        self.active = False
        
        # self.bind(pos=self.on_pressed)
        
    # def on_pressed(self, instance, pos):
    #     print(instance, pos)

    def on_press(self):
        # print(instance)
        # print(pos)
        # print(LabelTitle.one_active)
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
        # joint_data = self.parent.parent.parent.ids["joint_data"]
        # joint_data.fix_data()
        # print(joint_data.mouse_pos) # this print doesnt work because you are out of video_canvas object

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 1, 0, 0)
            Rectangle(pos=self.pos, size=self.size)

class VideoCanvas(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(VideoCanvas, self).__init__(**kwargs)
        self.frames = []
        self.processed_frames = []
        self.bodykeypoints = []
        self.real_bodykeypoints = []
        self.cap = None
        self.fill_event = None
        self.play_event = None
        self.counter = 0
        self.datum = op.Datum()
        self.file_selected = ""
        self.current_mouse_pos = None
        Window.bind(mouse_pos=self.mouse_pos)

    # def on_touch_down(self, touch):
    #     # return super().on_touch_down(touch)
    #     print(touch)

    def on_press(self):
        joint_data = self.parent.parent.ids['joint_data']

        if LabelTitle.one_active:
            joint_data.mouse_pos = self.current_mouse_pos
            print(joint_data.mouse_pos)
            active_element, active_label = joint_data.get_active_label()
            # print(active_element)
            print(active_label)
            i = KEYPOINTS.index(active_label)
            # self.parent.parent.ids[active_label +  "_x_real"].text = str(round(self.real_bodykeypoints[self.counter][0][i][0], 2))
            # self.parent.parent.ids[active_label + "_y_real"].text = str(round(self.real_bodykeypoints[self.counter][0][i][1], 2))
            print(joint_data.mouse_pos)
            self.parent.parent.ids[active_label +  "_x_real"].text = str(round(joint_data.mouse_pos[0], 2))
            self.parent.parent.ids[active_label + "_y_real"].text = str(round(joint_data.mouse_pos[1], 2))
            self.real_bodykeypoints[self.counter][0][i][0] = round(joint_data.mouse_pos[0], 2)
            self.real_bodykeypoints[self.counter][0][i][1] = round(joint_data.mouse_pos[1], 2)

            print(self.real_bodykeypoints[self.counter][0][i][0])
            print(self.real_bodykeypoints[self.counter][0][i][1])

    def mouse_pos(self, instance, pos):

        if pos[0] > self.pos[0] and pos[1] > self.pos[1]:
            relative_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
            corrected_pos = (relative_pos[0], self.size[1] - relative_pos[1])
            ratio_x = self.texture_size[0] / self.size[0]
            ratio_y = self.texture_size[1] / self.size[1]
            scaled_pos = (corrected_pos[0] * ratio_x, corrected_pos[1] * ratio_y)
            # print(scaled_pos, self.texture_size)
            
            self.current_mouse_pos = scaled_pos
        # print(pos)

    def fill(self, dt):
        if self.cap is not None:
            ret, image = self.cap.read()

            if ret:
                self.frames.append(image)
                processed_image, bodykp = self.run_openpose(image)
                self.processed_frames.append(processed_image)
                self.bodykeypoints.append(bodykp.copy())
                self.real_bodykeypoints.append(bodykp.copy())

                video_name_label = self.parent.parent.ids['video_name']
                video_name_label.text = "Loading..." # we can add a split
                frame_number_label = self.parent.parent.ids['total_frames']
                frame_number_label.text = "Loading..." # we can add a split
                video_length_label = self.parent.parent.ids['video_length']
                video_length_label.text = "Loading..."
                current_frame_label = self.parent.parent.ids['current_frame']
                current_frame_label.text = "Loading..."
            else:
                # print(self.frames)
                # file_selected = self.parent.parent.ids["files"].fichoo.selection[0]
                
                video_name_label = self.parent.parent.ids['video_name']
                video_name_label.text = self.file_selected[-9:] # we can add a split
                frame_number_label = self.parent.parent.ids['total_frames']
                frame_number_label.text = str(len(self.frames)) # we can add a split
                video_length_label = self.parent.parent.ids['video_length']
                video_length_label.text = str(round(len(self.frames) / 30, 2)) + ' sec'
                current_frame_label = self.parent.parent.ids['current_frame']
                current_frame_label.text = "Current Frame: " + str(self.counter)
                
                # print(dir(self.datum))
                # opWrapper.stop()


                self.fill_event.cancel()
                self.fill_event = None

            
            if self.texture is None:
                self.texture = self.video_to_texture(self.frames[0])

        
    def run_openpose(self, frame):
        self.datum.cvInputData = frame
        # aki
        opWrapper.emplaceAndPop([self.datum])
        # aki
        # self.datum.poseNetOutput = self.datum.poseHeatMaps.copy() * 0
        texture = self.video_to_texture(self.datum.cvOutputData)
        return [texture, self.datum.poseKeypoints.copy()]

    def play(self, dt):
        # self.run_openpose(self.frames[self.counter])
        self.texture = self.processed_frames[self.counter]
        joint_data = self.parent.parent.ids['joint_data']

        joint_data.display_data()
        # self.texture = self.video_to_texture(self.frames[self.counter])

        current_frame_label = self.parent.parent.ids['current_frame']
        current_frame_label.text = "Current Frame: " + str(self.counter)
        
        if self.counter < len(self.frames) - 1:
            self.counter += 1
        else:
            self.play_event.cancel()
    
    def video_to_texture(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt='bgr'
        )
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return image_texture


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
            bodykp = pd.DataFrame(frame[0], columns=['x','y','confidence'], index= KEYPOINTS)
            bodykps = bodykps.append(bodykp)
        bodykps.to_csv('./bodykeypoints/'+ video_canvas.file_selected[-9:-3] + 'csv')
        print("DONE CSVING :)")


class GroundTruthApp(App):
    def build(self):
        return WindowShape()


if __name__ == '__main__':
    GroundTruthApp().run()



