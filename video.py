import math, time, os
import tkinter as tk
from random import randint as rd
from sfml import sf
from objects import Settings
import scipy.io.wavfile as wf
import numpy as np
import subprocess as sp

def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)

def renderVideo(settings):
    playVideo(settings, True)

def previewVideo(settings):
    playVideo(settings, False)

def playVideo(settings, renderMode):
    res = [settings.resolution.x.get(), settings.resolution.y.get()]
    degToRad = math.pi / 180
    rotation = 0
    rate, data = wf.read(settings.musicPath)
    try: song = data[:, 0]
    except IndexError: song = data
    progress = 0
    lastParticle = 0
    wave_nbr = 20
    smoothed = []
    particles = []
    lines = []
    reminder = []
    reminder_size = 20
    reminder_threshold = settings.explosion_threshold.get()
    explosion_amount = settings.explosion_amount.get()
    songLength = len(song)/rate
    basses, mediums, partspeed = 0.5, 0.5, 0.5
    FPS = settings.framerate.get()
    deltaTime = 1/FPS

    win_set = sf.ContextSettings()
    win_set.antialiasing_level = 8
    screen = sf.RenderWindow(sf.VideoMode(res[0], res[1]), "Furalizer", sf.Style.DEFAULT, win_set)
    icon = sf.Image.from_file("./resources/icon.png")
    screen.set_icon(icon.width, icon.height, icon.pixels.tobytes())
    if not renderMode:
        screen.framerate_limit = FPS
        screen.vertical_synchronization = True

    logo_texture = sf.Texture.from_file(settings.logoPath)
    logo_sprite = sf.Sprite(logo_texture)
    logo_sprite.position = sf.Vector2(res[0]/2, res[1]/2)
    logo_sprite.origin = sf.Vector2(logo_texture.size.x/2, logo_texture.size.y/2)
    logo_threshold = settings.logo_bumping.get()
    logo_rotation = 0
    logo_bright = 0
    logo_scalefactor = logo_texture.size.x / logo_texture.size.y
    screen_scalefactor = res[0] / res[1]
    if logo_scalefactor > screen_scalefactor: #scale from x
        logo_size = logo_texture.size.x
        logo_basesize = res[0] * (settings.logo_size.get()/100)
    else: # scale from y
        logo_size = logo_texture.size.y
        logo_basesize = res[1] * (settings.logo_size.get()/100)
    logo_basebright = settings.logo_basebright.get()
    
    back_texture = sf.Texture.from_file(settings.backgroundPath)
    back_sprite = sf.Sprite(back_texture)
    back_sprite.position = sf.Vector2(res[0]/2, res[1]/2)
    back_sprite.origin = sf.Vector2(back_texture.size.x/2, back_texture.size.y/2)
    back_threshold = settings.back_bumping.get()
    back_rotation = 0
    back_bright = 0
    back_scalefactor = back_texture.size.x / back_texture.size.y
    screen_scalefactor = res[0] / res[1]
    if back_scalefactor > screen_scalefactor: #scale from x
        back_size = back_texture.size.x
        back_basesize = res[0] * (settings.back_size.get()/100)
    else: # scale from y
        back_size = back_texture.size.y
        back_basesize = res[1] * (settings.back_size.get()/100)
    back_basebright = settings.back_basebright.get()

    spikes_basesize = settings.spikes_basesize.get()/5
    particules_minspeed = settings.particules_minspeed.get()/50
    particules_speed = settings.particules_speed.get()/50

    song_title = sf.Text(settings.title.get())
    title_font = sf.Font.from_file("./resources/font.ttf")
    song_title.font = title_font
    song_title.color = sf.Color(255, 255, 255)
    font_size = settings.font_size.get()/50
    watermark = sf.Text("Made with Furalizer")
    watermark.font = title_font
    watermark.color = sf.Color(255, 255, 255, 192)
    watermark.character_size = res[1]*0.015
    watermark.position = sf.Vector2(5, 5)
    watermark.origin = sf.Vector2(0, 0)

    player = sf.Sound()
    player.buffer = sf.SoundBuffer.from_file(settings.musicPath)
    player.play()
    player.volume = 100
    if renderMode: player.volume = 0
    clock = sf.Clock()

    command = " ".join(["./resources/ffmpeg/ffmpeg.exe",
        '-f', 'rawvideo',
        '-s', str(res[0])+"x"+str(res[1]),
        '-r', str(FPS),
        '-pix_fmt', 'bgr32',
        '-i', '-',
        '-b:a '+str(settings.audio_bitrate.get())+'k',
        '-b:v '+str(settings.render_bitrate.get())+'k',
        '-c:v libx264',
        '-preset '+settings.preset_value.get(),
        '-crf '+str(clamp(settings.crf_value.get(), 0, 50)),
        '-pix_fmt', 'yuv420p',
        '-y',
        "./resources/temp.mp4"])
    if renderMode: proc = sp.Popen(command, stdin=sp.PIPE)

    run, playing = True, True

    class Particle:
        def __init__(self):
            self.angle = rd(0, 359)
            self.sizeFactor = rd(5, 10)/10
            self.vector = [math.cos(self.angle*degToRad), math.sin(self.angle*degToRad)]
            self.pos = [res[0]/2, res[1]/2]
            self.speed = 0
            self.size = 0
            self.centerDist = 0

        def draw(self):
            self.speed = 120 * deltaTime * ((self.centerDist*5)/(res[0]/2)+0.5) * (partspeed/50+particules_minspeed)
            if playing:
                self.pos[0] += self.vector[0]*self.speed
                self.pos[1] += self.vector[1]*self.speed
            self.centerDist = math.sqrt((self.pos[0]-res[0]/2)**2 + (self.pos[1]-res[1]/2)**2)
            self.size = clamp((self.centerDist/60)*self.sizeFactor, 0, 30)
            part = sf.CircleShape(self.size)
            part.position = (self.pos[0], self.pos[1])
            part.fill_color = sf.Color(255, 255, 255, clamp(logo_bright*self.size/10, 0, 255))
            screen.draw(part)

    class Line:
        def __init__(self):
            self.angle = rd(0, 360)
            self.sizeFactor = rd(5, 10)/10
            self.vector = [math.cos(self.angle*degToRad), math.sin(self.angle*degToRad)]
            self.pos = [res[0]/2, res[1]/2]
            self.speed = 0
            self.size = 0
            self.centerDist = 0
            self.positions = []
            self.nbr_pos = 20
            for i in range(self.nbr_pos):
                self.positions.append([res[0]/2, res[1]/2])

        def draw(self):
            self.speed = (partspeed/10) * (res[0]-self.centerDist/2)/2 * deltaTime
            if playing:
                for i in range(self.nbr_pos-1):
                    self.positions[i][0] = self.positions[i+1][0]
                    self.positions[i][1] = self.positions[i+1][1]
                self.positions[self.nbr_pos-1][0] += self.vector[0]*self.speed
                self.positions[self.nbr_pos-1][1] += self.vector[1]*self.speed
            for i in range(self.nbr_pos):
                self.centerDist = math.sqrt((self.positions[i][0]-res[0]/2)**2 + (self.positions[i][1]-res[1]/2)**2)
                self.size = clamp((self.centerDist/60)*self.sizeFactor, 0, 30)
                self.bright = clamp( (0.5-((self.centerDist/res[0]) - 0.5))*128 - 64 , 0, 255)
                part = sf.CircleShape(self.size)
                part.position = sf.Vector2(self.positions[i][0], self.positions[i][1])
                part.fill_color = sf.Color(255, 255, 255, self.bright)
                screen.draw(part)
            
    def sampleNbr(time):
        return int(time * rate)
    def moy(array):
        moyenne = 0
        for i in range(len(array)):
            moyenne += array[i]
        moyenne /= len(array)
        return moyenne

    def frequency_spectrum(x, sf):
        x = x - np.average(x)  # zero-centering
        n = len(x)
        k = np.arange(n)
        tarr = n / float(sf)
        frqarr = k / float(tarr)  # two sides frequency range
        frqarr = frqarr[range(n // 2)]  # one side frequency range
        x = np.fft.fft(x) / n  # fft computing and normalization
        x = x[range(n // 2)]
        return frqarr, abs(x)

    def spawnLine():
        lines.append(Line())

    levels = []
    for i in range(wave_nbr+1):
        levels.append(0)
    for i in range(wave_nbr+1):
        smoothed.append(0)
    for i in range(reminder_size):
        reminder.append(0)

    def debug(var):
        print(int(var)*"="+int(100-var)*" "+"|"+str(var))

    def popParticles():
        for i in range(explosion_amount):
            newpart = Particle()
            newpart.pos = [rd(0, res[0]), rd(0, res[1])]
            particles.append(newpart)

    # spawn random particles
    for i in range(settings.nbr_particles.get()*10):
        newpart = Particle()
        advanced = rd(0, max(res[0], res[1]))
        newpart.pos[0] += newpart.vector[0] * advanced
        newpart.pos[1] += newpart.vector[1] * advanced
        particles.append(newpart)

    while run:
        event = screen.poll_event()
        while event:
            if event.type == sf.Event.CLOSED:
                run = False
            if event.type == sf.Event.KEY_PRESSED:
                if sf.Keyboard.is_key_pressed(sf.Keyboard.ESCAPE):
                    run = False
                if sf.Keyboard.is_key_pressed(sf.Keyboard.SPACE) and not renderMode:
                    playing = not playing
                    if not playing: player.pause()
                    else: player.play()
                if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT) and not renderMode:
                    #backward by 5sec
                    progress -= 5; lastParticle = 0
                    progress = clamp(progress, 0, songLength)
                    player.playing_offset = sf.seconds(progress)
                if sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT) and not renderMode:
                    #backward by 5sec
                    progress += 5
                    progress = clamp(progress, 0, songLength)
                    player.playing_offset = sf.seconds(progress)
            event = screen.poll_event()

        #read the audio chunk
        currentChunk = song[sampleNbr(progress):sampleNbr(progress+deltaTime)]
        try: spectrum = frequency_spectrum(currentChunk, rate)
        except ValueError:
            spectrum = [0]
            spectr = []
            for e in range(len(levels)): spectr.append(0)
            spectrum.append(spectr)
            run = False
        if playing:
            for i in range(len(levels)):
                coef = 1-abs(min(i-4, 0))*(1/4)*0.3
                try: levels[i] = (spectrum[1][i]/20)*coef
                except IndexError: levels[i] = 0
        else:
            for i in range(len(levels)):
                levels[i] = 0

        low_freqs = clamp(moy(levels[1:4])/4, 0, 100)
        basses += (low_freqs*2-basses) * (settings.back_reactivity.get()/200)
        partspeed += (low_freqs*1.75*particules_speed-partspeed) * (settings.particules_reactivity.get()/100)
        mediums += (low_freqs*2-mediums) * (settings.logo_reactivity.get()/200)
        
        back_bright = clamp(back_basebright*2.55+basses*(255-back_basebright*2.55)/100, 0, 255)
        logo_bright = clamp(logo_basebright*2.55+partspeed*(255-logo_basebright*2.55)/100, 0, 255)

        cur_rot = 0
        rotation += 0

        # draw the background
        last_back_size = back_size
        back_size = back_basesize * (1 + (basses/100) * (back_threshold/100))
        back_sprite.scale((back_size/last_back_size, back_size/last_back_size))
        #back_sprite.rotation = cur_rot
        back_sprite.color = sf.Color(back_bright, back_bright, back_bright)
        screen.draw(back_sprite)

        #draw the icon
        last_logo_size = logo_size
        logo_size = logo_basesize * (1 + (mediums/100) * (logo_threshold/100))
        logo_sprite.scale((logo_size/last_logo_size, logo_size/last_logo_size))
        logo_sprite.rotation = logo_rotation
        logo_sprite.color = sf.Color(255, 255, 255, logo_bright)
        screen.draw(logo_sprite)

        #draw a circle around the icon
        radius = logo_size * (settings.spikes_radius.get()/100)
        circle = sf.CircleShape(50)
        circle.point_count = wave_nbr*2
        circle.radius = radius-spikes_basesize
        circle.origin = sf.Vector2(circle.radius, circle.radius)
        circle.position = sf.Vector2(res[0]/2, res[1]/2)
        circle.outline_thickness = spikes_basesize
        circle.outline_color = sf.Color(255, 255, 255, logo_bright)
        circle.fill_color = sf.Color(0, 0, 0, 0)
        screen.draw(circle)

        #draw spikes for sound
        points = []
        spikes_size = (settings.spikes_size.get()/100)
        for i in range(wave_nbr):
            smoothed[i] += (levels[i+1]-smoothed[i])  * (settings.spikes_reactivity.get()/100)
        for i in range(wave_nbr):
            angle = (i/wave_nbr)*math.pi-math.pi/2
            direction = [math.cos(angle), -math.sin(angle)]
            points.append( (res[0]/2+direction[0]*radius, res[1]/2+direction[1]*radius) )
            points.append( (res[0]/2+direction[0]*radius+direction[0]*smoothed[i]*spikes_size, res[1]/2+direction[1]*radius+direction[1]*smoothed[i]*spikes_size) )
            angle = ((i+1)/wave_nbr)*math.pi-math.pi/2
            direction = [math.cos(angle), -math.sin(angle)]
            points.append( (res[0]/2+direction[0]*radius+direction[0]*smoothed[i+1]*spikes_size, res[1]/2+direction[1]*radius+direction[1]*smoothed[i+1]*spikes_size) )
            points.append( (res[0]/2+direction[0]*radius, res[1]/2+direction[1]*radius) )
        for i in range(wave_nbr):
            mesh = sf.ConvexShape(4)
            mesh.set_point(0, points[i*4])
            mesh.set_point(1, points[i*4+1])
            mesh.set_point(2, points[i*4+2])
            mesh.set_point(3, points[i*4+3])
            mesh.fill_color = sf.Color(255, 255, 255, logo_bright)
            screen.draw(mesh)
        for i in range(wave_nbr):
            mesh = sf.ConvexShape(4)
            mesh.set_point(0, (res[0]-points[i*4][0], points[i*4][1]))
            mesh.set_point(1, (res[0]-points[i*4+1][0], points[i*4+1][1]))
            mesh.set_point(2, (res[0]-points[i*4+2][0], points[i*4+2][1]))
            mesh.set_point(3, (res[0]-points[i*4+3][0], points[i*4+3][1]))
            mesh.fill_color = sf.Color(255, 255, 255, logo_bright)
            screen.draw(mesh)

        for i in range(reminder_size-1):
            reminder[i] = reminder[i+1]
        reminder[reminder_size-1] = mediums

        if (reminder[0] < 185 and reminder[0] < reminder[reminder_size-1]-reminder_threshold) or \
        (reminder[0] > 180 and reminder[0] < reminder[reminder_size-1]-reminder_threshold/4):
            popParticles()

        #update and draw the particles
        for obj in particles:
            obj.draw()
            if res[0] > res[1]:
                if obj.centerDist > res[0]*0.55:
                    particles.remove(obj)
            else:
                if obj.centerDist > res[1]*0.55:
                    particles.remove(obj)
                    
        #update and draw the lines
        """for obj in lines:
            obj.draw()
            if res[0] > res[1]:
                if obj.positions[0][0] > res[0] or obj.positions[0][0] < 0:
                    lines.remove(obj)
            else:
                if obj.positions[0][1] > res[1] or obj.positions[0][1] < 0:
                    lines.remove(obj)"""
        
        #draw player gui
        backGUI = sf.ConvexShape(4)
        backGUI.set_point(0, (res[0]*0.15-mediums/2                   , res[1]*0.88+mediums/2))
        backGUI.set_point(1, (res[0]*0.15-mediums/2+res[0]*0.7+mediums, res[1]*0.88+mediums/2))
        backGUI.set_point(2, (res[0]*0.15-mediums/2+res[0]*0.7+mediums, res[1]*0.88+mediums/2+res[1]/75))
        backGUI.set_point(3, (res[0]*0.15-mediums/2                   , res[1]*0.88+mediums/2+res[1]/75))
        backGUI.fill_color = sf.Color(255, 255, 255, 64)
        screen.draw(backGUI)
        frontGUI = sf.ConvexShape(4)
        frontGUI.set_point(0, (res[0]*0.15-mediums/2                                           , res[1]*0.88+mediums/2))
        frontGUI.set_point(1, (res[0]*0.15-mediums/2+(res[0]*0.7+mediums)*(progress/songLength), res[1]*0.88+mediums/2))
        frontGUI.set_point(2, (res[0]*0.15-mediums/2+(res[0]*0.7+mediums)*(progress/songLength), res[1]*0.88+mediums/2+res[1]/75))
        frontGUI.set_point(3, (res[0]*0.15-mediums/2                                           , res[1]*0.88+mediums/2+res[1]/75))
        frontGUI.fill_color = sf.Color(255, 255, 255, logo_bright)
        screen.draw(frontGUI)

        # draw song title
        song_title.position = sf.Vector2(res[0]*0.15-mediums/2+(res[0]*0.7+mediums)/2, res[1]*0.88+mediums/2-song_title.global_bounds.height*1.2)
        song_title.origin = sf.Vector2(song_title.global_bounds.width/2, song_title.global_bounds.height/2)
        song_title.character_size = res[1]*0.03*font_size
        song_title.color = sf.Color(255, 255, 255, back_bright)
        screen.draw(song_title)

        #draw watermark
        screen.draw(watermark)

        if not renderMode: deltaTime = clock.restart().seconds
        if playing: progress += deltaTime
        if progress > lastParticle and len(particles) < 1200:
            lastParticle = progress
            numparts = 1 + int((basses / 5) * (settings.nbr_particles.get()/100))
            for i in range(numparts):
                particles.append(Particle())

        screen.display()
        if renderMode:
            tex = sf.Texture.create(screen.size.x, screen.size.y)
            tex.update(screen)
            proc.stdin.write( tex.copy_to_image().pixels.tobytes() )
    screen.close()
    if renderMode:
        time.sleep(0.5)
        proc.stdin.close()
        os.system("ffmpeg -i "+settings.musicPath+" -i ./resources/temp.mp4 -c:v copy -c:a aac -y -shortest "+settings.outputPath)

if __name__ == "__main__":
    settings = Settings(tk.Tk("debug"))
    settings.resolution.x.set(1920)
    settings.resolution.y.set(1080)
    settings.logo_size.set(20)
    settings.back_size.set(100)
    settings.back_basebright.set(30)
    settings.logo_basebright.set(60)
    playVideo(settings, False)