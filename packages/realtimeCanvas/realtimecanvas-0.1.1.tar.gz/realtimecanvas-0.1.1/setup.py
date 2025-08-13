from setuptools import setup, find_packages

setup(
    name="realtimeCanvas",
    version="0.1.1",
    description="A Python package for real-time image display and manipulation with Tkinter and PIL.",
    long_description="Allows for the realtime display of changes made to images using PIL."
                     "The image is displayed in a Tkinter window."
                     "At any point the current image may be saved, or all current changes may be compiled into a gif.",
    long_description_content_type="text/markdown",
    author="Charles Chaotic (Volburaal)",
    author_email="harvey.harrington@gmail.com", 
    url="https://github.com/Volburaal/realtimeCanvas",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
