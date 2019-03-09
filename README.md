# Openpose joint fix

An add-on for openpose (human pose estimation) for the assessment and correction of predicted keypoints.

# Requirements

- openpose python api
- kivy
- opencv
- python 3+

# How to use it

- Configure openpose so that environment variables from the python api are available in your path (refer [openpose](https://github.com/CMU-Perceptual-Computing-Lab/openpose/tree/master/examples/tutorial_api_python) )
- From terminal call `python ground_truth_app.py`
- Select and Load the video from the menu on the left.
- Analyze the results by manipulating the video controlls at the bottom of the video section.
- To fix any given joint clic on the label name corresponding to that joint and then click over the screen to correct the coordinates.
- Repeat the process per frame by moving back and forth.
- Export results by clicking on Export



![Demo](https://github.com/RubenAMtz/Openpose-Joint-Fix/blob/master/demo.gif "Demo")



# TODO

- Add visual representation for modified keypoints
- Add popup message when Exporting is finished.
