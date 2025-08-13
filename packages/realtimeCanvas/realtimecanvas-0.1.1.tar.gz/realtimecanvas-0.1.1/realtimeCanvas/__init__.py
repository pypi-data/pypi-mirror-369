import tkinter as tk
from PIL import Image, ImageTk

class RealtimeCanvas:
    """
    A class to create a real-time image display using Tkinter and PIL. 
    The image can be manipulated and updated in real-time. 
    It supports scaling, displaying on a Tkinter canvas, and saving the image or a GIF of the changes.

    Attributes:
        image (PIL.Image): The image to display and manipulate.
        scale (int): The scaling factor to resize the image for display.
        root (tk.Tk): The main Tkinter window.
        canvas (tk.Canvas): The Tkinter canvas where the image is displayed.
        image_on_canvas (tk.PhotoImage): The image displayed on the canvas.
        frames (list): A list of image frames for creating a GIF.
    """

    def __init__(self, image, scale=-1, title="Realtime Image Display"):
        """
        Initializes the RealtimeCanvas object with the given image and scale.

        Args:
            image (PIL.Image): The image to be displayed on the canvas.
            scale (int, optional): The scale factor for the image (adjusted automatically if not provided).
            title (str, optional): The title of the Tkinter window (default is "Realtime Image Display").
        """
        if(scale == -1):
            size = max(image.size[0], image.size[1])
            scale = int(905/size)
        self.image = image
        self.scale = scale
        self.root = tk.Tk()
        self.root.title(title)

        # Create a Tkinter canvas to display the image
        self.canvas = tk.Canvas(
            self.root, width=image.size[0] * scale, height=image.size[1] * scale
        )
        self.canvas.pack()

        self.image_on_canvas = None
        self.frames = []

    def update(self):
        """
        Updates the image displayed on the Tkinter canvas by resizing the image and 
        refreshing the canvas with the new image.
        The image is resized based on the scale factor and displayed at a higher resolution.

        This method is called repeatedly for real-time image display.
        """
        # Resize the image according to the scale factor
        image_resized = self.image.resize(
            (self.image.width * self.scale, self.image.height * self.scale),
            resample=Image.Resampling.NEAREST  # NEAREST is the most efficient for real-time rendering
        )
        
        # Convert the image to a Tkinter-compatible format
        img_tk = ImageTk.PhotoImage(image_resized)

        # Save the frame for GIF creation later
        self.frames.append(image_resized.copy())

        # Display the image on the canvas
        self.canvas.image = img_tk
        if self.image_on_canvas is None:
            # If no image is on the canvas yet, create one
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        else:
            # Update the existing image on the canvas
            self.canvas.itemconfig(self.image_on_canvas, image=img_tk)
        self.canvas.update()

    def run(self, func, *args):
        """
        Runs the Tkinter main loop and executes a function repeatedly every 100 milliseconds.

        Args:
            func (callable): The function to call periodically. It will be executed every 100 ms.
            *args: Additional arguments to pass to the function.
        """
        self.root.after(100, func, *args)
        self.root.mainloop()

    def saveImage(self, name):
        """
        Saves the current image as a file.

        Args:
            name (str): The filename to save the image as (e.g., "output.png").
        """
        self.image.save(name)
        print(f"Image saved as {name}")

    def saveGif(self, name):
        """
        Saves the collected frames as an animated GIF.

        Args:
            name (str): The filename to save the GIF as (e.g., "output.gif").
        """
        if self.frames:
            # Save the frames as a GIF with 1 ms duration per frame
            self.frames[0].save(
                name, save_all=True, append_images=self.frames[1:], optimize=True,
                duration=1, loop=0
            )
            print(f"GIF saved as {name}")
        else:
            print("No frames to save as GIF.")