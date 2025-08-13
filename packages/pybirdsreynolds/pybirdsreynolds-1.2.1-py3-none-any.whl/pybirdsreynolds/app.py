import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args
import signal
import sys
import copy
from importlib.metadata import version
import time
from tkinter import font

version_prog = version("pybirdsreynolds")
options = compute_args()
max_speed = options.max_speed
neighbor_radius = options.neighbor_radius
num_birds = options.num_birds
width, height = options.width, options.height
refresh_ms = options.refresh_ms
random_speed = options.random_speed
random_angle = options.random_angle
sep_weight = options.sep_weight
align_weight = options.align_weight
coh_weight = options.coh_weight
paused = True
frame_count = 0
last_time = time.time()
fps_value = 0
size = options.size
triangles= options.triangles
fps= False
free=options.free
color=options.color
count= not paused
if not color:
    canvas_bg = "black"
    fill_color = "white"
    outline_color = "black"
else:
    canvas_bg = "blue"
    fill_color = "white"
    outline_color = "black"

# Sauvegarde profonde
max_speed_init = copy.deepcopy(max_speed)
neighbor_radius_init = copy.deepcopy(neighbor_radius)
num_birds_init = copy.deepcopy(num_birds)
width_init = copy.deepcopy(width)
height_init = copy.deepcopy(height)
refresh_ms_init = copy.deepcopy(refresh_ms)
random_speed_init = copy.deepcopy(random_speed)
random_angle_init = copy.deepcopy(random_angle)
sep_weight_init = copy.deepcopy(sep_weight)
align_weight_init = copy.deepcopy(align_weight)
coh_weight_init = copy.deepcopy(coh_weight)
size_init = copy.deepcopy(size)
triangles_init = copy.deepcopy(triangles)
free_init = copy.deepcopy(free)
color_init= copy.deepcopy(color)

params=400
margin=1
selected_index=0
parameters = ["num_birds", "neighbor_radius", "sep_weight", "align_weight", "coh_weight" , "max_speed" , "random_speed", "random_angle", "refresh_ms", "width", "height", "size", "triangles", "color" , "free"]

# Dictionnaire de documentation associée
param_docs = {
    "num_birds"      : "Number of birds in the simulation (1–1000, default: 500)",
    "neighbor_radius": "Distance to detect neighbors in pixels (default: 50)",
    "sep_weight"     : "Separation weight (0–10, default: 1)",
    "align_weight"   : "Alignment weight (0–10, default: 1)",
    "coh_weight"     : "Cohesion weight (0–10, default: 1)",
    "max_speed"      : "Maximum speed of birds (0–100, default: 10)",
    "random_speed"   : "Random speed variation ratio (%) (0–100, default: 10)",
    "random_angle"   : "Random angle variation in degrees (0–360, default: 10)",
    "refresh_ms"     : "Refresh interval in milliseconds (min 1, default: 10)",
    "width"          : "Simulation area width (200–1500, default: 1000)",
    "height"         : "Simulation area height (200-1000, default: 500)",
    "size"           : "Visual size of birds (1–3, default: 1)",
    "triangles"      : "Render birds as triangles instead of points",
    "free"           : "Remove parameter limits (use with caution)",  
    "color"          : "Enable colors"
}

# Correspondance index -> nom du paramètre
param_order = [
    "num_birds",
    "neighbor_radius",
    "sep_weight",
    "align_weight",
    "coh_weight",
    "max_speed",
    "random_speed",
    "random_angle",
    "refresh_ms",
    "width",
    "height",
    "size",
    "triangles",
    "color",
    "free"
]

def app():

    def restore_options():
        global max_speed, neighbor_radius, num_birds, width, height
        global refresh_ms, random_speed, random_angle
        global sep_weight, align_weight, coh_weight
        global paused, size, triangles, color, canvas_bg, fill_color, outline_color, fps, free
        
        max_speed = copy.deepcopy(max_speed_init)
        neighbor_radius = copy.deepcopy(neighbor_radius_init)
        num_birds = copy.deepcopy(num_birds_init)
        width = copy.deepcopy(width_init)
        height = copy.deepcopy(height_init)
        refresh_ms = copy.deepcopy(refresh_ms_init)
        random_speed = copy.deepcopy(random_speed_init)
        random_angle = copy.deepcopy(random_angle_init)
        sep_weight = copy.deepcopy(sep_weight_init)
        align_weight = copy.deepcopy(align_weight_init)
        coh_weight = copy.deepcopy(coh_weight_init)
        size = copy.deepcopy(size_init)
        color = copy.deepcopy(color_init)
        free = copy.deepcopy(free_init)

        if not color:
            canvas_bg = "black"
            fill_color = "white"
            outline_color = "black"
        else:
            canvas_bg = "blue"
            fill_color = "white"
            outline_color = "black"    
        triangles = copy.deepcopy(triangles_init)    

    def draw():
        draw_canvas()
        draw_status()
        draw_points()
        draw_rectangle()
        draw_fps()

    def draw_fps():
        canvas.delete("fps")
        if fps:
            if not paused:
                if fps_value == 0:
                    value="..."
                else:    
                    value = f"{fps_value:.1f}"
            else:
                value = "NA"
            canvas.create_text(
                0,
                max(height,500),            
                anchor="sw",  
                fill="yellow",
                font=("Consolas", 10, "bold"),
                tags="fps",
                text=f"FPS : {value}"
        )

    def on_next_frame(event):
        global paused
        paused = True
        generate_points_and_facultative_move(True)
        draw()

        
    def toggle_pause(event=None):
        global paused
        paused = not paused
        draw_status()

    def on_other_key(event):
        global selected_index, num_birds, max_speed, neighbor_radius, sep_weight, align_weight, coh_weight, size, random_speed, random_angle, triangles, free , refresh_ms, width, height, color, canvas_bg, fill_color, outline_color, fps
        ctrl = (event.state & 0x4) != 0
        val = 10 if ctrl else 1
        if event.keysym == "Up":
            selected_index = (selected_index - 1) % len(parameters)
        elif event.keysym == "Down":
            selected_index = (selected_index + 1) % len(parameters)
        elif event.keysym == "Right":
            param = parameters[selected_index]
            if param == "num_birds":
                if not free:
                    num_birds = min(num_birds + val, 1000)
                else:  
                    num_birds = num_birds + val   
                generate_points_and_facultative_move(False)
                draw_points()
            elif param == "max_speed":
                if not free:
                    max_speed = min(max_speed + val, 100)
                else:
                    max_speed = max_speed + val   
            elif param == "neighbor_radius":
                neighbor_radius += 1
            elif param == "sep_weight":
                if not free:
                    sep_weight = min(sep_weight + val, 10)
                else:
                    sep_weight = sep_weight + val   
            elif param == "align_weight":
                if not free:
                    align_weight = min(align_weight + val, 10)
                else:
                    align_weight = align_weight + val                   
            elif param == "coh_weight":
                if not free:
                    coh_weight = min(coh_weight + val, 10)
                else:
                    coh_weight = coh_weight + val                  
            elif param == "size":
                if not free:
                    size = min(size + val, 3)
                else:
                    size = size + val                     
                draw()
            elif param == "random_speed":
                if not free:
                    random_speed = min(random_speed + val, 100)
                else:
                    random_speed = random_speed + val                    
            elif param == "random_angle":
                if not free:
                    random_angle = min(random_angle + val, 360)
                else:
                    random_angle = random_angle + val                   
            elif param == "triangles":
                triangles = not triangles
                draw()                                                                                                                                                                                                                                             
            elif param == "refresh_ms":
                refresh_ms += val
            elif param == "width":
                if not free:
                    width = min(width + val, 1500)
                else:
                    width = width + val                  
                generate_points_and_facultative_move(False)
                draw()
            elif param == "height":
                if not free:
                    height = min(height + val, 1000)
                else:
                    height = height + val                
                generate_points_and_facultative_move(False)
                draw()
            elif param == "color":
                color = not color 
                if not color:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "blue"
                    fill_color = "white"
                    outline_color = "black" 
                draw()
            elif param == "free":
                free = not free
                if not free:
                    if num_birds>1000:
                        num_birds=1000
                    if num_birds<1:
                        num_birds=1
                    if max_speed<0:
                        max_speed=0
                    if max_speed>100:
                        max_speed=100 
                    if sep_weight>10:
                        sep_weight=10
                    if sep_weight<0:
                        sep_weight=0
                    if align_weight>10:
                        align_weight=10
                    if align_weight<0:
                        align_weight=0    
                    if coh_weight>10:
                        coh_weight=10
                    if coh_weight<0:
                        coh_weight=0 
                    if size>3:
                        size=3
                    if size<1:
                        size=1
                    if random_speed>100:
                        random_speed=100
                    if random_speed<0:
                        random_speed=0
                    if random_angle>360:
                        random_angle=360
                    if random_angle<0:
                        random_angle=0
                    if width<200:
                        width=200    
                    if width>1500:
                        width=1500
                    if height<200:
                        height=200    
                    if height>1000:
                        height=1000 
                    generate_points_and_facultative_move(False)
                    draw()                                         
        elif event.keysym == "Left":
            param = parameters[selected_index]
            if param == "num_birds":
                num_birds = max(num_birds - val, 1)
                generate_points_and_facultative_move(False)
                draw_points()                
            elif param == "max_speed":
                max_speed = max(max_speed - val, 0)
            elif param == "neighbor_radius":
                neighbor_radius = max(neighbor_radius - val, 0)
            elif param == "sep_weight":
                if not free:
                    sep_weight = max(sep_weight - val, 0)
                else:
                    sep_weight = sep_weight - val                    
            elif param == "align_weight":
                if not free:
                    align_weight = max(align_weight - val, 0)
                else:
                    align_weight = align_weight - val                       
            elif param == "coh_weight":
                if not free:
                    coh_weight = max(coh_weight - val, 0)
                else:
                    coh_weight = coh_weight - val                    
            elif param == "size":
                size = max(size - val, 1)
                draw()
            elif param == "random_speed":
                random_speed = max(random_speed - val, 0) 
            elif param == "random_angle":
                if not free:
                    random_angle = max(random_angle - val, 0)
                else:
                    random_angle = random_angle - val     
            elif param == "triangles":
                triangles = not triangles
                draw()
            elif param == "free":
                free = not free
                #TODO                                     
            elif param == "refresh_ms":
                refresh_ms = max(refresh_ms - val, 1)
            elif param == "width":
                if not free:
                    width = max(width - val, 200)
                else:
                    width = max(width - val, 3)                 
                generate_points_and_facultative_move(False)
                draw()
            elif param == "height":
                if not free:
                    height = max(height - val, 200)
                else:
                    height = max(height - val, 3)   
                generate_points_and_facultative_move(False)
                draw() 
            elif param == "color":
                color = not color 
                if not color:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "blue"
                    fill_color = "white"
                    outline_color = "black" 
                draw() 
            elif param == "free":
                free = not free
                if not free:
                    if num_birds>1000:
                        num_birds=1000
                    if num_birds<1:
                        num_birds=1
                    if max_speed<0:
                        max_speed=0
                    if max_speed>100:
                        max_speed=100 
                    if sep_weight>10:
                        sep_weight=10
                    if sep_weight<0:
                        sep_weight=0
                    if align_weight>10:
                        align_weight=10
                    if align_weight<0:
                        align_weight=0    
                    if coh_weight>10:
                        coh_weight=10
                    if coh_weight<0:
                        coh_weight=0 
                    if size>3:
                        size=3
                    if size<1:
                        size=1
                    if random_speed>100:
                        random_speed=100
                    if random_speed<0:
                        random_speed=0
                    if random_angle>360:
                        random_angle=360
                    if random_angle<0:
                        random_angle=0
                    if width<200:
                        width=200    
                    if width>1500:
                        width=1500
                    if height<200:
                        height=200    
                    if height>1000:
                        height=1000 
                    generate_points_and_facultative_move(False)
                    draw()                                           
        elif event.char.lower() == 'r':
            restore_options()
            generate_points_and_facultative_move(False)
            draw()            
        elif event.char.lower() == 'n':
            global velocities
            global birds
            global paused
            pause= True
            velocities = []
            birds= [] 
            generate_points_and_facultative_move(False)
            draw()
        elif event.char.lower() == 'f':
            fps = not fps
            draw_fps()            
        draw_status()

    def draw_canvas():
        global canvas_bg
        canvas.config(width=width + params, height=max(height,500), bg=canvas_bg)

    def draw_status():
        # Polices
        normal_font = font.Font(family="Consolas", size=8, weight="normal")
        bold_font   = font.Font(family="Consolas", size=8, weight="bold")
        italic_font = font.Font(family="Consolas", size=8, slant="italic")

        lines = [
            f"num_birds        : {num_birds}",
            f"neighbor_radius  : {neighbor_radius}",
            f"sep_weight       : {sep_weight}",
            f"align_weight     : {align_weight}",
            f"coh_weight       : {coh_weight}",
            f"max_speed        : {max_speed}",
            f"random_speed     : {random_speed}",
            f"random_angle     : {random_angle}",
            f"refresh_ms       : {refresh_ms}",
            f"width            : {width}",
            f"height           : {height}",
            f"size             : {size}",
            f"triangles        : {triangles}",
            f"color            : {color}",    
            f"free             : {free}",         
            "",
            "[Space]           : Toggle start / stop",
            "[Enter]           : Advance by one frame ",
            "[Up/Down]         : Navigate between params",
            "[Left/Right]      : Adjust selected param +1/-1 True/False",
            "[Ctrl][Left/Right]: Adjust selected param +10/-10",
            "[r]               : Reset all params",
            "[n]               : New generation of birds",
            "[f]               : Toggle FPS display",
            "",      
        ]

        x_text = 10
        y_text = 10
        canvas.delete("status")
        
        for i, line in enumerate(lines):
            font_to_use = normal_font
            fill = fill_color

            if i == selected_index:
                font_to_use = bold_font
                fill = "red"
                line = "> "+line+" <"

            if line.strip().startswith("["):
                font_to_use = bold_font
                fill = "yellow"

            canvas.create_text(
                x_text,
                y_text + i * 18,
                anchor="nw",
                fill=fill,
                font=font_to_use,
                tags="status",
                text=line
            )


        param_name = param_order[selected_index]
        doc_text = param_docs.get(param_name, "")
        if doc_text:
            canvas.create_text(
                x_text + 175,
                y_text + selected_index * 18,
                anchor="nw",
                fill="yellow",
                font=italic_font,
                tags="status",
                text=doc_text,
                width=200
            )


    def draw_rectangle():
        canvas.delete("boundary")
        canvas.create_rectangle(
            params, 0, params + width, height,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def generate_points_and_facultative_move(with_move):
        global velocities
        global new_velocities
        if not birds: 
            velocities = []
            for _ in range(num_birds):
                px = random.randint(margin + params, width - margin + params)
                py = random.randint(margin, height - margin)
                birds.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            # Supprimer les birds hors du rectangle
            inside_points = []
            inside_velocities = []
            for (x, y), (vx, vy) in zip(birds, velocities):
                if params + margin <= x <= params + width - margin and 0 + margin <= y <= height - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
                # Sinon on "kill" l'oiseau en ne le gardant pas

            birds[:] = inside_points
            velocities[:] = inside_velocities            
            # Calcul Reynolds
            new_velocities = []
            current_count = len(birds)
            
            # Ajouter aléatoirement des oiseaux
            if num_birds > current_count:
                for _ in range(num_birds - current_count):
                    px = random.randint(margin + params, width - margin + params)
                    py = random.randint(margin, height - margin)
                    birds.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, max_speed)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Supprimer aléatoirement des oiseaux
            elif num_birds < current_count:
                for _ in range(current_count - num_birds):
                    idx = random.randint(0, len(birds) - 1)
                    birds.pop(idx)
                    velocities.pop(idx)
            if with_move:                    
                move()
    def move():
        global velocities
        global new_velocities
        for i, (x, y) in enumerate(birds):
            move_sep_x, move_sep_y = 0, 0
            move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = 0, 0, 0, 0
            move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
            neighbors = 0
            vx, vy = velocities[i]
            if neighbor_radius > 0 and not (sep_weight == 0 and align_weight == 0 and coh_weight == 0):
                for j, (x2, y2) in enumerate(birds):
                    if i == j:
                        continue
                    dist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
                    if dist < neighbor_radius and dist > 0:
                        # SEPARATION
                        # Si un voisin est trop proche, on ajoute un vecteur pour s’en éloigner (direction opposée au voisin).
                        move_sep_x += (x - x2) / dist
                        move_sep_y += (y - y2) / dist
                        # ALIGNEMENT
                        # On ajoute la vitesse du voisin pour que l’agent tende à s’aligner avec lui.
                        # on fait la division plus bas
                        vx2, vy2 = velocities[j]
                        move_align_x_tmp += vx2
                        move_align_y_tmp += vy2
                        # COHESION
                        # On ajoute la position du voisin pour calculer ensuite un point moyen, afin de se rapprocher du centre du groupe.
                        # on fait la division plus bas
                        move_coh_x_tmp += x2
                        move_coh_y_tmp += y2
                        neighbors += 1
                
                if neighbors > 0:
                    move_align_x = move_align_x_tmp/neighbors
                    move_align_y = move_align_y_tmp/neighbors
                    move_coh_x = move_coh_x_tmp/neighbors
                    move_coh_y = move_coh_y_tmp/neighbors
                    move_coh_x = move_coh_x - x
                    move_coh_y = move_coh_y - y

                vx += sep_weight * move_sep_x + align_weight * move_align_x + coh_weight * move_coh_x
                vy += sep_weight * move_sep_y + align_weight * move_align_y + coh_weight * move_coh_y


            
            #ALEA
            speed = math.sqrt(vx**2 + vy**2)
            speed_factor = 1 + random.uniform(-random_speed / 100, random_speed / 100)
            new_speed = speed * speed_factor
            min_speed = 0.1 * max_speed
            if speed > 0:
                factor = new_speed / speed
            else:
                vx = 1
                vy = 1                  
                factor = random.uniform(-random_speed / 100, random_speed / 100)    
            vx *= factor
            vy *= factor                
            angle = math.atan2(vy, vx)
            angle += math.radians(random.uniform(-1 * random_angle, random_angle))
            speed = math.sqrt(vx**2 + vy**2)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            vx, vy = limit_speed(vx, vy)
            
            new_velocities.append((vx, vy))

        velocities = new_velocities

        # Mise à jour des positions
        new_points = []
        for (x, y), (vx, vy) in zip(birds, velocities):
            nx = x + vx
            ny = y + vy

            # Rebonds X
            while nx < margin + params or nx > width - margin + params:
                if nx < margin + params:
                    overshoot = (margin + params) - nx
                    nx = (margin + params) + overshoot
                    vx = abs(vx)  # vers la droite
                elif nx > width - margin + params:
                    overshoot = nx - (width - margin + params)
                    nx = (width - margin + params) - overshoot
                    vx = -abs(vx)  # vers la gauche

            # Rebonds Y
            while ny < margin or ny > height - margin:
                if ny < margin:
                    overshoot = margin - ny
                    ny = margin + overshoot
                    vy = abs(vy)  # vers le bas
                elif ny > height - margin:
                    overshoot = ny - (height - margin)
                    ny = (height - margin) - overshoot
                    vy = -abs(vy)  # vers le haut
            idx = birds.index((x, y))
            velocities[idx] = (vx, vy)
            new_points.append((nx, ny))

        birds[:] = new_points


    def draw_points():
        for pid in point_ids:
            canvas.delete(pid)
        point_ids.clear()

        triangle_size = 6*size
        triangle_width = 4*size

        for (x, y), (vx, vy) in zip(birds, velocities):
            if not triangles: 
                pid = canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=fill_color, outline=outline_color)
            else:
                angle = math.atan2(vy, vx)
                tip_x = x + math.cos(angle) * triangle_size
                tip_y = y + math.sin(angle) * triangle_size
                left_angle = angle + math.radians(150)
                right_angle = angle - math.radians(150)

                left_x = x + math.cos(left_angle) * triangle_width
                left_y = y + math.sin(left_angle) * triangle_width

                right_x = x + math.cos(right_angle) * triangle_width
                right_y = y + math.sin(right_angle) * triangle_width

                pid = canvas.create_polygon(
                    tip_x, tip_y,
                    left_x, left_y,
                    right_x, right_y,
                    fill=fill_color, outline=outline_color
                )
            point_ids.append(pid)

    def limit_speed(vx, vy):
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > max_speed:
            vx = (vx / speed) * max_speed
            vy = (vy / speed) * max_speed
        return vx, vy

    def update():
        global frame_count, last_time, fps_value, count
        if not paused:
            generate_points_and_facultative_move(True)
            draw()
            frame_count += 1
            now = time.time()
            if not count:
                last_time = now
                count = True
            if now - last_time >= 1.0: 
                fps_value = frame_count / (now - last_time)
                frame_count = 0
                last_time = now 
        else:
            frame_count = 0
            count = False
            fps_value = 0          

        root.after(refresh_ms, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)

    root = tk.Tk()
    root.title(f"pybirdsreynolds {version_prog}")

    canvas = tk.Canvas(root, width=width+params, height=height, bg=canvas_bg)
    canvas.pack()

    birds = [] 
    point_ids = []

    generate_points_and_facultative_move(True)
    draw()

    root.bind("<Return>", on_next_frame)
    root.bind("<space>", toggle_pause)
    root.bind("<Key>", on_other_key)

    signal.signal(signal.SIGINT, signal_handler)
    update()
    root.mainloop()             


