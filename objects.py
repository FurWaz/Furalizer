import tkinter as tk

COLOR_BLACK = "#344A5F"
COLOR_PRIMARY = "#2A94D6"
COLOR_GREY = "#F0F1F2"
COLOR_WHITE = "#FFFFFF"

class Settings:
    def __init__(self, root):
        # constants
        self.PREVIEW = 1
        self.RENDER = 2
        self.NO_SELECTION = "No file selected"
        self.DEFAULT_LOGO_PATH = "./resources/logo.png"
        self.DEFAULT_BACK_PATH = "./resources/background.png"
        self.DEFAULT_MUSIC_PATH = "./resources/music.wav"
        self.DEFAULT_OUTPUT_PATH = "./resources/output.mp4"
        # variables
        self.mode = self.PREVIEW
        self.resolution = Vector2(root, 1280, 720)
        self.framerate = tk.IntVar(root, 60)
        self.background = tk.StringVar(root, self.NO_SELECTION)
        self.music = tk.StringVar(root, self.NO_SELECTION)
        self.title = tk.StringVar(root, "Title")
        self.font_size = tk.IntVar(root, 50)
        self.logo = tk.StringVar(root, self.NO_SELECTION)
        self.output = tk.StringVar(root, self.NO_SELECTION)
        self.outputWithoutExtension = self.NO_SELECTION
        self.backgroundPath = self.DEFAULT_BACK_PATH
        self.logoPath = self.DEFAULT_LOGO_PATH
        self.musicPath = self.DEFAULT_MUSIC_PATH
        self.outputPath = self.DEFAULT_OUTPUT_PATH
        
        self.render_bitrate = tk.IntVar(root, 2000)
        self.audio_bitrate = tk.IntVar(root, 192)
        self.render_percent = tk.IntVar(root, 0)
        self.crf_value = tk.IntVar(root, 20)
        self.preset_value = tk.StringVar(root, "veryfast")
        self.preset_number = tk.IntVar(root, 6) # from 0 to 8 [veryslow, slower, slow, medium, fast, faster, veryfast, superfast, ultrafast]

        self.logo_size = tk.IntVar(root, 20) # from 1 to 100
        self.logo_bumping = tk.IntVar(root, 30) # from 0 to 100
        self.logo_basebright = tk.IntVar(root, 60) # from 0 to 100
        self.logo_reactivity = tk.IntVar(root, 12) # from 0 to 100 (divided by 200)
        self.back_size = tk.IntVar(root, 100) # from 100 to 200
        self.back_bumping = tk.IntVar(root, 20) # from 0 to 100
        self.back_basebright = tk.IntVar(root, 40) # from 0 to 100
        self.back_reactivity = tk.IntVar(root, 8) # from 0 to 100 (divided by 200)
        self.spikes_size = tk.IntVar(root, 45) # from 0 to 100
        self.spikes_basesize = tk.IntVar(root, 10) # from 0 to 100 (divided by 5)
        self.spikes_radius = tk.IntVar(root, 55) # from 0 to 100
        self.spikes_reactivity = tk.IntVar(root, 40) # from 0 to 100 
        self.nbr_particles = tk.IntVar(root, 40) # from 0 to 100
        self.particules_reactivity = tk.IntVar(root, 50) # from 0 to 100 
        self.particules_minspeed = tk.IntVar(root, 50) # from 0 to 100 (divided by 50)
        self.particules_speed = tk.IntVar(root, 50) # from 0 to 100 (divided by 50)
        self.explosion_threshold = tk.IntVar(root, 12) # from 0 to 30
        self.explosion_amount = tk.IntVar(root, 4) # from 0 to 8

    def presetNbrToStr(self, number):
        return ["veryslow", "slower", "slow", "medium", "fast", "faster", "veryfast", "superfast", "ultrafast"][number]

class Vector2:
    def __init__(self, root, x, y):
        self.x = tk.IntVar(root, x)
        self.y = tk.IntVar(root, y)