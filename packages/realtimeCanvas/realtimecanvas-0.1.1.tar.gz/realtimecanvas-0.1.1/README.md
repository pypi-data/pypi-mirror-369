# Realtime Image Canvas

A Python package for real-time image display and manipulation using Tkinter and PIL. This template allows users to manipulate images, display changes in real-time, and save the results as images or GIFs.

## Installation

```bash
pip install realtimeCanvas
```

## Features

- Real-time image changes with Tkinter.
- Save changes as a static image or animated GIF.
- Easy to extend and customize for different image processing tasks.

### Usage Demonstration

```py
from PIL import Image
from realtimeCanvas import RealtimeCanvas
import random

def newPNG(width, height):
    im = Image.new('RGB', (width,height), (0,0,0))
    return im

def manipulateImage(im, width, height, display): #all image manipulation logic happens in this function
    count = 0
    while count < 100:
        col = int(random.uniform(0,width))
        row = int(random.uniform(0,height))

        r = int(random.uniform(0,255))
        g = int(random.uniform(0,255))
        b = int(random.uniform(0,255))

        im.putpixel((col,row),(r,g,b))

        display.update() #update the canvas to reflect changes
        count += 1

def start_image_generation():
    width = 50
    height = 50
    image = newPNG(width,height) #Create an image or load an existing image
    display = RealtimeCanvas(image, scale=15) #initialize the canvas
    display.update() #update the canvas to reflect changes
    
    display.run(manipulateImage, image, width, height, display) #run the image manipulation function in a window loop

    #This will work too, but the window will close automatically once the function ends as the function isnt running in the window loop
    #manipulateImage (image, width, height, display)
    
    display.saveImage("image.png") #save the final image once the cnavas closes
    display.saveGif("animation.gif") #save a gif of all current changes

if __name__ == "__main__":
    start_image_generation()
```
