from tkinter.constants import *
from tkinter import Menu, filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
from numpy.core.numeric import flatnonzero
from numpy.lib.function_base import blackman
from objects import *
from video import renderVideo, previewVideo
import tkinter as tk
import os, time, webbrowser

mainwin = tk.Tk()
screenres = (mainwin.winfo_screenwidth(), mainwin.winfo_screenheight())
mainwin.geometry(str(int(screenres[0]*0.5))+"x"+str(int(screenres[1]*0.8))+"+"+str(int(screenres[0]*0.25))+"+"+str(int(screenres[1]*0.1)))
mainwin.title("Furalizer")

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=COLOR_BLACK, relief=FLAT, highlightthickness=0, borderwidth=0)
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, relief=FLAT)
        self.scrollable_frame = tk.Frame(self.canvas)

        container.bind("<MouseWheel>", self.onmousewheel)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox(ALL)
            )
        )

        self.canvas.create_window((int(mainwin.winfo_width()/2), int(mainwin.winfo_height()/2)), window=self.scrollable_frame, anchor=CENTER)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(fill=BOTH, side=LEFT, expand=True)
        self.scrollbar.pack(fill=Y, side=RIGHT)
    def onmousewheel(self, event):
        self.canvas.yview("scroll", int(-event.delta/100), "unit")

# ---- RESOURCES LOADING ---- #
settings = Settings(mainwin)
iconimage = ImageTk.PhotoImage(Image.open("./resources/icon.png"))
font_big = ("Helvetica", int(screenres[1]/60), "bold")
font_medium = ("Helvetica", int(screenres[1]/100))
font_small = ("Helvetica", int(screenres[1]/140))
lastUpdate = time.time()-1
bottom_height = screenres[1]/10
    
def startVideo():
    if settings.mode == settings.RENDER:
        renderVideo(settings)
    else:
        previewVideo(settings)

def launchApp():
    if settings.mode == settings.RENDER:
        popup_win = tk.Toplevel(mainwin)
        popup_win.iconphoto(False, iconimage)
        popup_win.resizable(0, 0)
        popup_win.title("Information")
        popup = tk.Frame(popup_win, bg=COLOR_BLACK)
        popup.pack()
        if (settings.output.get() == settings.NO_SELECTION): 
            tk.Label(popup, text="Please select an output file.", font=font_medium, fg=COLOR_WHITE, bg=COLOR_BLACK).pack(side=TOP)
            tk.Button(popup, command=popup_win.destroy, text="Cancel", font=font_medium, fg=COLOR_BLACK, bg=COLOR_PRIMARY, relief=FLAT).pack(side=BOTTOM)
        else:
            tk.Label(popup, text="Please do not close, move, or minimize the render window until the video rendering is complete,\n otherwise the render would be altered or stopped.",
                     font=font_medium, fg=COLOR_WHITE, bg=COLOR_BLACK).pack(side=TOP)
            tk.Label(popup, text="The render window will automaticaly close when rendering is complete.", font=font_medium, fg=COLOR_WHITE, bg=COLOR_BLACK).pack(side=TOP)
            tk.Button(popup, command=startVideo, text="Continue", font=font_medium, fg=COLOR_BLACK, bg=COLOR_PRIMARY, relief=FLAT).pack(side=BOTTOM)
    else: startVideo()

def updatePreview(val=5):
    global lastUpdate
    if lastUpdate+0.03 > time.time(): return
    lastUpdate = time.time()
    #create preview image
    factor = settings.resolution.x.get() / settings.resolution.y.get()
    prevDims = (int(bottom_height*factor), int(bottom_height))
    prev = Image.new('RGB', prevDims)
    # load background
    back = Image.open(settings.backgroundPath)
    back = ImageEnhance.Brightness(back).enhance(settings.back_basebright.get()/100)
    zoom = settings.back_size.get()/100
    scaleFactor = (screenres[1]/10)*(zoom) / back.size[1]
    newSize = (int(back.size[0]*scaleFactor), int(back.size[1]*scaleFactor))
    back = back.resize(newSize)
    backPos = (int(-(zoom-1)*prevDims[0]/2), int(-(zoom-1)*prevDims[1]/2))
    # load logo
    logo = Image.open(settings.logoPath)
    scaleFactor = (settings.logo_size.get()/100)*prevDims[0] / logo.size[0]
    logo_size = (int(logo.size[0]*scaleFactor), int(logo.size[1]*scaleFactor))
    logo_bright = settings.logo_basebright.get()/100
    logo.putalpha(ImageEnhance.Brightness(logo).enhance(logo_bright).convert("L"))
    logo = logo.resize(logo_size)
    logoPos = (int(prev.size[0]/2-logo.size[0]/2), int(prev.size[1]/2-logo.size[1]/2))
    # paste the images onto the preview
    prev.paste(back, backPos)
    try: prev.paste(logo, logoPos, logo)
    except: prev.paste(logo, logoPos)
    # draw the circle
    draw = ImageDraw.Draw(prev, 'RGBA')
    center = (int(prevDims[0]/2), int(prevDims[1]/2))
    radius = settings.spikes_radius.get()/50
    pos = (center[0]-logo_size[0]*radius*0.5,
           center[1]-logo_size[1]*radius*0.5)
    bounds = (pos[0], pos[1], pos[0]+logo_size[0]*radius, pos[1]+logo_size[1]*radius)
    draw.ellipse(bounds, fill=(0, 0, 0, 0), outline=(255, 255, 255, int(logo_bright*255)), width=int(settings.spikes_basesize.get()/5))

    # show the preview
    previewImage = ImageTk.PhotoImage(prev)
    try:
        imgLabel.configure(image=previewImage)
        imgLabel.image = previewImage
    except: pass

def showYouTube():
    webbrowser.open_new("https://www.youtube.com/channel/UCYw9qRksXslrsgMELYPCWNw")
def showGitHub():
    webbrowser.open_new("https://github.com/FurWaz")

def showCredits():
    popup_win = tk.Toplevel(mainwin)
    popup_win.iconphoto(False, iconimage)
    popup_win.resizable(0, 0)
    popup_win.title("About")
    popup = tk.Frame(popup_win, bg=COLOR_BLACK)
    popup.pack()
    tk.Label(popup, text="Furalizer version 1.0", font=font_medium, fg=COLOR_WHITE, bg=COLOR_BLACK).pack(side=TOP, padx=5, pady=10)
    tk.Label(popup, text="Application made by: FurWaz", font=font_medium, fg=COLOR_WHITE, bg=COLOR_BLACK).pack(side=TOP, padx=5, pady=10)
    links = tk.Frame(popup, bg=COLOR_BLACK)
    tk.Button(links, text="YouTube", command=showYouTube, bg=COLOR_PRIMARY, fg=COLOR_BLACK, relief=FLAT, font=font_medium).pack(side=LEFT, padx=10)
    tk.Button(links, text="GitHub", command=showGitHub, bg=COLOR_PRIMARY, fg=COLOR_BLACK, relief=FLAT, font=font_medium).pack(side=RIGHT, padx=10)
    links.pack(fill=X, padx=5, pady=10, side=TOP)
    tk.Button(popup, command=popup_win.destroy, text="OK", font=font_medium, fg=COLOR_BLACK, bg=COLOR_PRIMARY, relief=FLAT).pack(side=BOTTOM, pady=10)

# ---- WINDOW SETUP ---- #
mainwin.iconphoto(False, iconimage)

# ---- HEADER SECTION SETUP ---- #
headerFrame = tk.Frame(mainwin, bg=COLOR_PRIMARY, height=int(screenres[1]/30))
headerFrame.pack(side=TOP, fill=X)
headerFrame.pack_propagate(FALSE)
headerTitle = tk.Label(headerFrame, text="Furalizer", bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_big)
headerTitle.pack(side=LEFT)
tk.Button(headerFrame, command=showCredits, text="Credits", font=font_medium, fg=COLOR_PRIMARY, bg=COLOR_BLACK, relief=FLAT).pack(side=RIGHT, padx=5)

# ---- MAINFRAME SECTION SETUP ---- #
mainframe = ScrollableFrame(mainwin, bg=COLOR_BLACK)
mainframe.pack(fill=BOTH, expand=TRUE)
mainframe = mainframe.scrollable_frame

# ---- BOTTOM SECTION SETUP ---- #
bottomFrame = tk.Frame(mainwin, bg=COLOR_BLACK, height=bottom_height)
bottomFrame.pack(side=BOTTOM, fill=X)
bottomFrame.pack_propagate(FALSE)
tk.Frame(mainwin, bg=COLOR_PRIMARY, height=2).pack(side=BOTTOM, fill=X)

# ---- MODE SECTION SETUP ---- #
def setPrevMode():
    prevButton.configure(bg=COLOR_PRIMARY, fg=COLOR_BLACK)
    rendButton.configure(bg=COLOR_BLACK, fg=COLOR_PRIMARY)
    settings.mode = settings.PREVIEW
    renderContent.pack_forget()
def setRendMode():
    prevButton.configure(bg=COLOR_BLACK, fg=COLOR_PRIMARY)
    rendButton.configure(bg=COLOR_PRIMARY, fg=COLOR_BLACK)
    settings.mode = settings.RENDER
    renderContent.pack()

modeFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
modeFrame.pack(fill=X)
modeTitle = tk.Label(modeFrame, text="Mode:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
modeTitle.pack(side=TOP)
modeButtonFrame = tk.Frame(modeFrame, bg=COLOR_BLACK)
modeButtonFrame.pack()
prevButton = tk.Button(modeButtonFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_medium, command=setPrevMode, relief=FLAT, text="Preview")
prevButton.pack(side=LEFT, padx=5)
rendButton = tk.Button(modeButtonFrame, bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium, command=setRendMode, relief=FLAT, text="Render")
rendButton.pack(side=RIGHT, padx=5)

# ---- RESOLUTION SECTION SETUP ---- #
resFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
resFrame.pack(fill=X)
resTitle = tk.Label(modeFrame, text="Resolution:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
resTitle.pack(side=TOP)
resEntryFrame = tk.Frame(modeFrame, bg=COLOR_BLACK)
resEntryFrame.pack()
resWidthText = tk.Entry(resEntryFrame, textvariable=settings.resolution.x, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=4, validate="all", validatecommand=updatePreview)
resWidthText.pack(side=LEFT)
resSpaceText = tk.Label(resEntryFrame, text="x", bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
resSpaceText.pack(side=LEFT)
resHeightText = tk.Entry(resEntryFrame, textvariable=settings.resolution.y, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=4, validate="all", validatecommand=updatePreview)
resHeightText.pack(side=LEFT)

# ---- FRAMERATE SECTION SETUP ---- #
resFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
resFrame.pack(fill=X)
resTitle = tk.Label(resFrame, text="Framerate:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
resTitle.pack(side=TOP)
resEntryFrame = tk.Frame(resFrame, bg=COLOR_BLACK)
resEntryFrame.pack()
resWidthText = tk.Entry(resEntryFrame, textvariable=settings.framerate, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=3)
resWidthText.pack(side=LEFT)
resSpaceText = tk.Label(resEntryFrame, text="FPS", bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
resSpaceText.pack(side=RIGHT)

# ---- BACKGROUND IMAGE SETUP ---- #
def selectBackFile():
    f = filedialog.askopenfilename(title="Choose a background image", filetypes=(("Image file", "*.png;*.jpg;*.jpeg"), ("All files", "*.*")))
    if f != "":
        settings.background.set(os.path.basename(f))
        settings.backgroundPath = f
        updatePreview()
def resetBackFile():
    settings.background.set(settings.NO_SELECTION)
    settings.backgroundPath = settings.DEFAULT_BACK_PATH
    updatePreview()
backFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
backFrame.pack(fill=X)
backTitle = tk.Label(backFrame, text="Background:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
backTitle.pack(side=TOP)
backInputFrame = tk.Frame(backFrame, bg=COLOR_BLACK)
backInputFrame.pack()
backButton = tk.Button(backInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_medium, command=selectBackFile, relief=FLAT, text="Select file")
backButton.pack(side=LEFT, padx=5)
backButton = tk.Button(backInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_small, command=resetBackFile, relief=FLAT, text="reset")
backButton.pack(side=RIGHT, padx=5)
backLabel = tk.Label(backInputFrame, textvariable=settings.background, bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
backLabel.pack(side=RIGHT)

# ---- ICON IMAGE SETUP ---- #
def selectLogoFile():
    f = filedialog.askopenfilename(title="Choose a icon image", filetypes=(("Image file", "*.png;*.jpg;*.jpeg"), ("All files", "*.*")))
    if f != "":
        settings.logo.set(os.path.basename(f))
        settings.logoPath = f
        updatePreview()
def resetLogoFile():
    settings.logo.set(settings.NO_SELECTION)
    settings.logoPath = settings.DEFAULT_LOGO_PATH
    updatePreview()
logoFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
logoFrame.pack(fill=X)
logoTitle = tk.Label(logoFrame, text="Logo:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
logoTitle.pack(side=TOP)
logoInputFrame = tk.Frame(logoFrame, bg=COLOR_BLACK)
logoInputFrame.pack()
logoButton = tk.Button(logoInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_medium, command=selectLogoFile, relief=FLAT, text="Select file")
logoButton.pack(side=LEFT, padx=5)
logoButton = tk.Button(logoInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_small, command=resetLogoFile, relief=FLAT, text="reset")
logoButton.pack(side=RIGHT, padx=5)
logoLabel = tk.Label(logoInputFrame, textvariable=settings.logo, bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
logoLabel.pack(side=RIGHT)

# ---- MUSIC SELECTION SETUP ---- #
def selectMusicFile():
    f = filedialog.askopenfilename(title="Choose a music file", filetypes=(("Music file", "*.wav"), ("All files", "*.*")))
    if f != "":
        settings.music.set(os.path.basename(f))
        settings.musicPath = f
def resetMusicFile():
    settings.music.set(settings.NO_SELECTION)
    settings.musicPath = settings.DEFAULT_MUSIC_PATH
musicFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
musicFrame.pack(fill=X)
musicTitle = tk.Label(musicFrame, text="Music:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
musicTitle.pack(side=TOP)
musicInputFrame = tk.Frame(musicFrame, bg=COLOR_BLACK)
musicInputFrame.pack()
musicButton = tk.Button(musicInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_medium, command=selectMusicFile, relief=FLAT, text="Select file")
musicButton.pack(side=LEFT, padx=5)
musicButton = tk.Button(musicInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_small, command=resetMusicFile, relief=FLAT, text="reset")
musicButton.pack(side=RIGHT, padx=5)
musicLabel = tk.Label(musicInputFrame, textvariable=settings.music, bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
musicLabel.pack(side=RIGHT)

# ---- TITLE SECTION SETUP ---- #
titleFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
titleFrame.pack(fill=X)
titleTitle = tk.Label(titleFrame, text="Song title:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
titleTitle.pack(side=TOP)
titleEntryFrame = tk.Frame(titleFrame, bg=COLOR_BLACK)
titleEntryFrame.pack()
titleWidthText = tk.Entry(titleEntryFrame, textvariable=settings.title, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=30)
titleWidthText.pack(side=LEFT)

# ---- RENDER SECTION SETUP ---- #
renderFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
renderFrame.pack(fill=X)
renderContent = tk.Frame(renderFrame, bg=COLOR_BLACK)
renderContent.pack(fill=X)

# ---- OUTPUT SELECTION SETUP ---- #
def selectOutputFile():
    f = filedialog.asksaveasfilename(title="Choose a output file")
    f = str(f)
    if f[len(f)-1] != "4": f += ".mp4"
    if f != "":
        settings.output.set(os.path.basename(f))
        settings.outputPath = f
        settings.outputWithoutExtension = f.split('.')[0]
def resetOutputFile():
    settings.output.set(settings.NO_SELECTION)
    settings.outputPath = settings.DEFAULT_OUTPUT_PATH
    settings.outputWithoutExtension = settings.DEFAULT_OUTPUT_PATH.split('.')[0]
outputFrame = tk.Frame(renderContent, bg=COLOR_BLACK)
outputFrame.pack()
outputTitle = tk.Label(outputFrame, text="Output:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
outputTitle.pack(side=TOP)
outputInputFrame = tk.Frame(outputFrame, bg=COLOR_BLACK)
outputInputFrame.pack()
outputButton = tk.Button(outputInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_medium, command=selectOutputFile, relief=FLAT, text="Select file")
outputButton.pack(side=LEFT, padx=5)
outputButton = tk.Button(outputInputFrame, bg=COLOR_PRIMARY, fg=COLOR_BLACK, font=font_small, command=resetOutputFile, relief=FLAT, text="reset")
outputButton.pack(side=RIGHT, padx=5)
outputLabel = tk.Label(outputInputFrame, textvariable=settings.output, bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
outputLabel.pack(side=RIGHT)

# ---- VIDEO BITRATE SECTION SETUP ---- #
videoBitrateFrame = tk.Frame(renderContent, bg=COLOR_BLACK)
videoBitrateFrame.pack(fill=X)
videoBitrateTitle = tk.Label(videoBitrateFrame, text="Video bitrate:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
videoBitrateTitle.pack(side=TOP)
videoBitrateEntryFrame = tk.Frame(videoBitrateFrame, bg=COLOR_BLACK)
videoBitrateEntryFrame.pack()
videoBitrateWidthText = tk.Entry(videoBitrateEntryFrame, textvariable=settings.render_bitrate, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=6)
videoBitrateWidthText.pack(side=LEFT)
videoBitrateSpaceText = tk.Label(videoBitrateEntryFrame, text="kB/s", bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
videoBitrateSpaceText.pack(side=RIGHT)

# ---- AUDIO BITRATE SECTION SETUP ---- #
audioBitrateFrame = tk.Frame(renderContent, bg=COLOR_BLACK)
audioBitrateFrame.pack(fill=X)
audioBitrateTitle = tk.Label(audioBitrateFrame, text="Audio bitrate:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
audioBitrateTitle.pack(side=TOP)
audioBitrateEntryFrame = tk.Frame(audioBitrateFrame, bg=COLOR_BLACK)
audioBitrateEntryFrame.pack()
audioBitrateWidthText = tk.Entry(audioBitrateEntryFrame, textvariable=settings.audio_bitrate, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=6)
audioBitrateWidthText.pack(side=LEFT)
audioBitrateSpaceText = tk.Label(audioBitrateEntryFrame, text="kB/s", bg=COLOR_BLACK, fg=COLOR_PRIMARY, font=font_medium)
audioBitrateSpaceText.pack(side=RIGHT)

# ---- PRESET SECTION SETUP ---- #
def updatePreset(h):
    slidTitle.config(text=settings.presetNbrToStr(settings.preset_number.get()))
presetFrame = tk.Frame(renderContent, bg=COLOR_BLACK)
presetFrame.pack(fill=X)
presetTitle = tk.Label(presetFrame, text="Preset:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
presetTitle.pack(side=TOP)
presetEntryFrame = tk.Frame(presetFrame, bg=COLOR_BLACK)
presetEntryFrame.pack()
slidFrame = tk.Frame(presetEntryFrame, bg=COLOR_BLACK)
slidFrame.pack(side=TOP)
slidSlide = tk.Scale(slidFrame, orient=HORIZONTAL, bg=COLOR_WHITE, fg=COLOR_PRIMARY, sliderrelief=FLAT, border=0, 
                    highlightthickness=0, showvalue=FALSE, sliderlength=10, width=14, troughcolor=COLOR_PRIMARY, length=600,
                    command=updatePreset, variable=settings.preset_number, from_=0, to=8)
slidSlide.pack(side=RIGHT, padx=5)
slidTitle = tk.Label(slidFrame, text="veryfast", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
slidTitle.pack(side=LEFT)

# ---- CRF SECTION SETUP ---- #
crfFrame = tk.Frame(renderContent, bg=COLOR_BLACK)
crfFrame.pack(fill=X)
crfTitle = tk.Label(crfFrame, text="CRF value:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
crfTitle.pack(side=TOP)
crfEntryFrame = tk.Frame(crfFrame, bg=COLOR_BLACK)
crfEntryFrame.pack()
crfWidthText = tk.Entry(crfEntryFrame, textvariable=settings.crf_value, bg=COLOR_BLACK, fg=COLOR_PRIMARY, relief=FLAT, font=font_medium, width=6)
crfWidthText.pack(side=LEFT)

# ---- SLIDERS SECTION SETUP ---- #
slidersFrame = tk.Frame(mainframe, bg=COLOR_BLACK)
slidersFrame.pack(fill=X)
slidersTitle = tk.Label(slidersFrame, text="Settings:", bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
slidersTitle.pack(side=TOP)
def addSlider(label, variable, from_, to_):
    slidFrame = tk.Frame(slidersFrame, bg=COLOR_BLACK)
    slidFrame.pack(side=TOP)
    slidSlide = tk.Scale(slidFrame, orient=HORIZONTAL, bg=COLOR_WHITE, fg=COLOR_PRIMARY, sliderrelief=FLAT, border=0, 
                        highlightthickness=0, showvalue=FALSE, sliderlength=10, width=14, troughcolor=COLOR_PRIMARY, length=600,
                        command=updatePreview, variable=variable, from_=from_, to=to_)
    slidSlide.pack(side=RIGHT, padx=5)
    slidTitle = tk.Label(slidFrame, text=label, bg=COLOR_BLACK, fg=COLOR_WHITE, font=font_medium)
    slidTitle.pack(side=LEFT)
addSlider("Title size: ", settings.font_size, 0, 100)
addSlider("Logo size: ", settings.logo_size, 0, 140)
addSlider("Logo bumping: ", settings.logo_bumping, 0, 100)
addSlider("Logo min brightness: ", settings.logo_basebright, 0, 100)
addSlider("Logo reactivity: ", settings.logo_reactivity, 0, 100)
addSlider("Background size: ", settings.back_size, 100, 250)
addSlider("Background bumping: ", settings.back_bumping, 0, 100)
addSlider("Background min brightness: ", settings.back_basebright, 0, 100)
addSlider("Background reactivity: ", settings.back_reactivity, 0, 100)
addSlider("Spikes length: ", settings.spikes_size, 0, 150)
addSlider("Spikes radius: ", settings.spikes_radius, 0, 100)
addSlider("Spikes min size: ", settings.spikes_basesize, 0, 100)
addSlider("Spikes reactivity: ", settings.spikes_reactivity, 0, 100)
addSlider("Particles amount: ", settings.nbr_particles, 0, 100)
addSlider("Particules reactivity: ", settings.particules_reactivity, 0, 100)
addSlider("Particules speed: ", settings.particules_speed, 0, 100)
addSlider("Particles min speed: ", settings.particules_minspeed, 0, 100)
addSlider("Explosions threshold: ", settings.explosion_threshold, 0, 30)
addSlider("Explosions particle amount: ", settings.explosion_amount, 0, 8)

# ---- PREVIEW IMAGE SETUP ---- #
img = Image.open(settings.backgroundPath)
scaleFactor = (screenres[1]/10) / img.size[1]
newSize = (int(img.size[0]*scaleFactor), int(img.size[1]*scaleFactor))
previewImage = ImageTk.PhotoImage(img.resize(newSize))
imgLabel = tk.Label(bottomFrame, image=previewImage, bg=COLOR_BLACK)
imgLabel.pack(side=LEFT)
updatePreview()

# ---- LAUNCH BUTTON SETUP ---- #
launchButton = tk.Button(bottomFrame, text="run", font=font_big, bg=COLOR_PRIMARY, fg=COLOR_BLACK, relief=FLAT, command=launchApp)
launchButton.pack(side=RIGHT, padx=5)

# ---- KEEP BUTTONS IN FLAT MODE ---- #
def keep_flat(event):
    if isinstance(event.widget, tk.Button):
        event.widget.config(relief=FLAT)
mainwin.bind('<Button-1>', keep_flat)
mainwin.after(100, setPrevMode)
mainwin.mainloop()