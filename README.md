# Depth_Map

A simple Blender plugin to export depth maps. Initially useful for the AI depth control net workflow

Addon creates a "one hit" button in the render settings tab that will set up a normalised z-pass compositor node and export a png depthmap.

Currently, a camera is required in the scene (soon to change), and it is adviseable to set compose the camera view and set to orthographic with a 1:1 ratio as that is what will be exported by the addon.

Install : Download the depthmap.py file, go to Blender preferences, add-ons, install and select the downloaded python file - check enable box
