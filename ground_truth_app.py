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
PYOPENPOSE_DIR = "C:/Programming/github/repos/openpose/build/python/openpose/Release"
MODELS_DIR = "C:/Programming/github/repos/openpose/models"

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
from kivy.graphics import Color, Rectangle, Line, Ellipse
from buttons import LoadButton, BackwardButton, ForwardButton, PauseButton, PlayButton, ResetRealButton, SetLastButton, ExportButton
from labels import LabelGrid, LabelTitle
from constants import KEYPOINTS, COLORS, BODY_PAIRS

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
        Window.bind(on_key_down=self._on_keyboard_down)
        print(self.ids)
    
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        backward_btn = self.ids['backward']
        forward_btn = self.ids['forward']
        if keycode == 80: # left key:
            backward_btn.backward(self)
        elif keycode == 79: # right key
            forward_btn.forward(self)
        print(keycode)

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


class JointData(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_pos = None

    def display_data(self):
        video_canvas = self.parent.parent.ids["video_canvas"]
        percentage = self.parent.parent.ids["percentage"]
        percentage.text = str(round((video_canvas.counter / len(video_canvas.processed_frames))* 100, 2)) + "%"
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
        # self.draw_point(50, 50)

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
            self.show_lines()
            self.show_points()

    def show_points(self):
        # self.canvas.after.clear()
        for i, e in enumerate(self.real_bodykeypoints[self.counter][0]):
            self.draw_point(e[0], e[1], color=COLORS[i])

    def draw_point(self, x, y, color):
        ratio_x = self.texture_size[0] / self.size[0]
        ratio_y = self.texture_size[1] / self.size[1]
        x = x / ratio_x
        y = y / ratio_y
        y = self.size[1] - y
        x = self.pos[0] + x
        y = self.pos[1] + y
        
        with self.canvas.after:
            r, g, b = color
            Color(r / 255, g / 255, b / 255)
            Ellipse(pos=(x-5, y-5), size=(10, 10))


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


    def draw_line(self, x1, y1, x2, y2, color):
        if x1 == 0.0 and y1 == 0.0:
            return
        if x2 == 0.0 and y2 == 0.0:
            return
        ratio_x = self.texture_size[0] / self.size[0]
        ratio_y = self.texture_size[1] / self.size[1]
        x1 = x1 / ratio_x
        y1 = y1/ ratio_y
        y1 = self.size[1] - y1
        x1 = self.pos[0] + x1
        y1 = self.pos[1] + y1

        x2 = x2 / ratio_x
        y2 = y2 / ratio_y
        y2 = self.size[1] - y2
        x2 = self.pos[0] + x2
        y2 = self.pos[1] + y2

        with self.canvas.after:
            r, g, b = color
            Color(r / 255, g / 255, b / 255, 0.5)
            Line(points=[x1, y1, x2, y2], width=3, close=True)
        
    def show_lines(self):
        self.canvas.after.clear()
        for i, e in enumerate(BODY_PAIRS):
            x1, y1, _ = self.real_bodykeypoints[self.counter][0][e[0]]
            x2, y2, _ = self.real_bodykeypoints[self.counter][0][e[1]]
            self.draw_line(x1, y1, x2, y2, color=COLORS[e[0]])

    def run_openpose(self, frame):
        self.datum.cvInputData = frame
        # aki
        opWrapper.emplaceAndPop([self.datum])
        # aki
        # self.datum.poseNetOutput = self.datum.poseHeatMaps.copy() * 0
        # texture = self.video_to_texture(self.datum.cvOutputData)
        texture = self.video_to_texture(frame)

        
        return [texture, self.datum.poseKeypoints.copy()]

    def play(self, dt):
        # self.run_openpose(self.frames[self.counter])
        self.texture = self.processed_frames[self.counter]
        # self.texture = self.frames[self.counter]

        joint_data = self.parent.parent.ids['joint_data']

        joint_data.display_data()
        self.show_lines()
        self.show_points()
        
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


class GroundTruthApp(App):
    def build(self):
        return WindowShape()


if __name__ == '__main__':
    GroundTruthApp().run()



