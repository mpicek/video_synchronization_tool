import cv2
import tkinter as tk
from tkinter import filedialog
from subprocess import run
from PIL import Image, ImageTk
import os
import ffmpeg
from tqdm import tqdm

INITIAL_DIR = '/home/mpicek/repos/Trunk_KinRec/data/HON006/250Hz_L5/'

class App:
    def __init__(self, master, same_fps):
        self.master = master
        self.frame1 = 0
        self.frame2 = 0
        self.video_path1 = filedialog.askopenfilename(initialdir=INITIAL_DIR)
        self.video_path2 = filedialog.askopenfilename(initialdir=INITIAL_DIR)

        print(self.video_path1)
        print(self.video_path2)

        self.cap1, fps1 = self.load_video(self.video_path1)
        self.cap2, fps2 = self.load_video(self.video_path2)

        original_fps1 = fps1
        original_fps2 = fps2

        fps1 = round(fps1)
        fps2 = round(fps2)

        target_fps = None
        self.temp_file_path = None

        # predefined_fps = 30
        predefined_fps = None

        if predefined_fps is None and same_fps:
            # we need both videos to have the same FPS
            target_fps = min(fps1, fps2)
            if fps1 > fps2:
                print(f"The first video has {fps1} FPS, while the second has {fps2} FPS. Converting the first video to {target_fps} FPS.")
                self.temp_file_path = self.convert_fps(self.video_path1, target_fps=target_fps)
                self.cap1.release()
                self.cap1, fps1 = self.load_video(self.temp_file_path)
            elif fps1 < fps2:
                print(f"The first video has {fps1} FPS, while the second has {fps2} FPS. Converting the second video to {target_fps} FPS.")
                self.temp_file_path = self.convert_fps(self.video_path2, target_fps=target_fps)
                self.cap2.release()
                self.cap2, fps2 = self.load_video(self.temp_file_path)
            else:
                print(f"The first video has {fps1} FPS, and the second has {fps2} FPS. No conversion needed.")
        
        if predefined_fps is not None:
            self.temp_file_path = self.convert_fps(self.video_path1, target_fps=predefined_fps)
            self.cap1.release()
            self.cap1, fps1 = self.load_video(self.temp_file_path)

            self.temp_file_path = self.convert_fps(self.video_path2, target_fps=predefined_fps)
            self.cap2.release()
            self.cap2, fps2 = self.load_video(self.temp_file_path)

        self.target_fps1 = original_fps1 if abs(fps1 - original_fps1) < 1 else fps1
        self.target_fps2 = original_fps2 if abs(fps2 - original_fps2) < 1 else fps2
        print(self.target_fps1)
        print(self.target_fps2)
        # self.target_fps1 = self.load_video(self.video_path1)
        # self.target_fps2 = self.load_video(self.video_path2)
        
        self.total_frames_video1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_frames_video2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))

        # GUI setup
        self.canvas1 = tk.Canvas(master, width=500, height=700)
        self.canvas2 = tk.Canvas(master, width=500, height=700)
        self.canvas1.grid(row=0, column=0)
        self.canvas2.grid(row=0, column=1)

        self.button1_left_super = tk.Button(master, text="<< -150", command=lambda: self.skip_frames1(-150))
        self.button1_right_super = tk.Button(master, text="+150 >>", command=lambda: self.skip_frames1(150))
        self.button2_left_super = tk.Button(master, text="<< -150", command=lambda: self.skip_frames2(-150))
        self.button2_right_super = tk.Button(master, text="+150 >>", command=lambda: self.skip_frames2(150))

        self.button1_left_super.grid(row=3, column=0, sticky='w')
        self.button1_right_super.grid(row=3, column=0, sticky='e')
        self.button2_left_super.grid(row=3, column=1, sticky='w')
        self.button2_right_super.grid(row=3, column=1, sticky='e')


        self.button1_left = tk.Button(master, text="<< -20", command=lambda: self.skip_frames1(-20))
        self.button1_right = tk.Button(master, text="+20 >>", command=lambda: self.skip_frames1(20))
        self.button2_left = tk.Button(master, text="<< -20", command=lambda: self.skip_frames2(-20))
        self.button2_right = tk.Button(master, text="+20 >>", command=lambda: self.skip_frames2(20))

        self.button1_left.grid(row=2, column=0, sticky='w')
        self.button1_right.grid(row=2, column=0, sticky='e')
        self.button2_left.grid(row=2, column=1, sticky='w')
        self.button2_right.grid(row=2, column=1, sticky='e')

        self.button1_left_one = tk.Button(master, text="< -1", command=lambda: self.skip_frames1(-1))
        self.button1_right_one = tk.Button(master, text="+1 >", command=lambda: self.skip_frames1(1))
        self.button2_left_one = tk.Button(master, text="< -1", command=lambda: self.skip_frames2(-1))
        self.button2_right_one = tk.Button(master, text="+1 >", command=lambda: self.skip_frames2(1))

        self.button1_left_one.grid(row=1, column=0, sticky='w')
        self.button1_right_one.grid(row=1, column=0, sticky='e')
        self.button2_left_one.grid(row=1, column=1, sticky='w')
        self.button2_right_one.grid(row=1, column=1, sticky='e')


        self.frame_entry1 = tk.Entry(master)
        self.frame_entry1.grid(row=4, column=0)
        self.frame_entry1.bind('<Return>', lambda event: self.jump_to_frame(event, 1))

        self.frame_entry2 = tk.Entry(master)
        self.frame_entry2.grid(row=4, column=1)
        self.frame_entry2.bind('<Return>', lambda event: self.jump_to_frame(event, 2))

        self.frame_label1 = tk.Label(master)
        self.frame_label1.grid(row=5, column=0)

        self.frame_label2 = tk.Label(master)
        self.frame_label2.grid(row=5, column=1)

        self.time_label1 = tk.Label(master, text="")
        self.time_label1.grid(row=6, column=0)

        self.time_label2 = tk.Label(master, text="")
        self.time_label2.grid(row=6, column=1)

        self.ok_button = tk.Button(master, text="OK", command=self.run_ffmpeg)
        self.ok_button.grid(row=4, column=0, columnspan=2)

        self.image1 = None
        self.image2 = None

        self.show_frame()
    
    def load_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        return cap, fps

    def convert_fps(self, video_path, target_fps):
        temp_file_path = os.path.join(os.path.dirname(video_path), video_path.split('/')[-1] + "_temp_same_fps_video_file.mp4")
        print(temp_file_path)
        ffmpeg.input(video_path).output(temp_file_path, r=target_fps).run()

        return temp_file_path
    
    def resize_image(self, image, max_width, max_height):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        
        if aspect_ratio > 1:
            # Image is wider than tall
            new_width = min(original_width, max_width)
            new_height = int(new_width / aspect_ratio)
        else:
            # Image is taller than wide or square
            new_height = min(original_height, max_height)
            new_width = int(new_height * aspect_ratio)
    
        return image.resize((new_width, new_height), Image.ANTIALIAS)

    def show_frame(self):
        self.cap1.set(cv2.CAP_PROP_POS_FRAMES, self.frame1)
        self.cap2.set(cv2.CAP_PROP_POS_FRAMES, self.frame2)

        _, frame1 = self.cap1.read()
        _, frame2 = self.cap2.read()

        self.frame_label1.config(text=f"Current frame: {self.frame1}")
        self.frame_label2.config(text=f"Current frame: {self.frame2}")

        self.time_label1.config(text=f"Current time: {round(self.frame1 / self.target_fps1, 3)} s")
        self.time_label2.config(text=f"Current time: {round(self.frame2 / self.target_fps2, 3)} s")

        frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

        # Resize to fit in 500x500 canvas
        frame1 = Image.fromarray(frame1)
        frame2 = Image.fromarray(frame2)

        frame1 = self.resize_image(frame1, 500, 700)
        frame2 = self.resize_image(frame2, 500, 700)

        self.image1 = ImageTk.PhotoImage(frame1)
        self.image2 = ImageTk.PhotoImage(frame2)

        self.canvas1.create_image(0, 0, image=self.image1, anchor='nw')
        self.canvas2.create_image(0, 0, image=self.image2, anchor='nw')
    
    def jump_to_frame(self, event, video_index):
        if video_index == 1:
            entry = self.frame_entry1
            self.frame1 = int(entry.get())
            if self.frame1 < 0:
                self.frame1 = 0
            elif self.frame1 >= self.total_frames_video1:
                self.frame1 = self.total_frames_video1 - 2
            self.show_frame()
        elif video_index == 2:
            entry = self.frame_entry2
            self.frame2 = int(entry.get())
            if self.frame2 < 0:
                self.frame2 = 0
            elif self.frame2 >= self.total_frames_video2:
                self.frame2 = self.total_frames_video2 - 2
            self.show_frame()

    def skip_frames1(self, frames):
        self.frame1 += frames
        if self.frame1 < 0:
            self.frame1 = 0
        elif self.frame1 >= self.total_frames_video1:
            self.frame1 = self.total_frames_video1 - 2
        self.show_frame()

    def skip_frames2(self, frames):
        self.frame2 += frames
        if self.frame2 < 0:
            self.frame2 = 0
        elif self.frame2 >= self.total_frames_video2:
            self.frame2 = self.total_frames_video2 - 2
        self.show_frame()


    def run_ffmpeg(self):
        # get directory of the original videos
        directory1 = os.path.dirname(self.video_path1)
        directory2 = os.path.dirname(self.video_path2)

        # create 'synchronized' subdirectories if they don't exist
        sync_dir1 = os.path.join(directory1, 'synchronized')
        sync_dir2 = os.path.join(directory2, 'synchronized')
        os.makedirs(sync_dir1, exist_ok=True)
        os.makedirs(sync_dir2, exist_ok=True)

        # get filenames of the original videos
        filename1 = os.path.basename(self.video_path1)
        filename2 = os.path.basename(self.video_path2)

        # generate output paths
        output_path1 = os.path.join(sync_dir1, filename1)
        output_path2 = os.path.join(sync_dir2, filename2)

        print("Output paths:")
        print(output_path1)
        print(output_path2)

        self.write_video(self.cap1, self.frame1, output_path1, self.target_fps1)
        self.write_video(self.cap2, self.frame2, output_path2, self.target_fps2)

        if self.temp_file_path is not None and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

        # Print success message and close application
        print("FINISHED - the synchronized videos are saved")
        self.master.destroy()

    
    def write_video(self, cap, start_frame, output_path, target_fps):
        # get video properties
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))
        
        for i in tqdm(range(start_frame, frame_count), desc=f'Processing video {output_path}'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        # Release everything when the job is finished
        cap.release()
        out.release()

root = tk.Tk()
app = App(root, same_fps=True)
root.mainloop()
