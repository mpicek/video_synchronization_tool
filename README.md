# Video synchronization tool

A Python GUI manual synchronization tool developed for NeuroRestore.

## Dependencies

It is necessary to have `ffmpeg`` installed is it used during the process.

## Usage

Run the program by running `python3 app.py`.
Select the first and consequently the second video in the pop-up file browser.
If the videos have different FPS, the one with higher FPS is converted to the FPS of the other video using `ffmpeg`.

After that, the GUI appears. Select the proper starting frame using the arrows. One arrow (`>` or `<`) stands for jumping
by one frame, two arrows (`>>` or `<<`) stand for jumping by 20 frames.

When you found the proper two starting frames, press OK button. In the terminal, you will see the progress of trimming the video.
The whole part before the starting frame will be erased and saved under the same filename
in a new subfolder called `/synchronized`, while the original videos will be kept unchanged.