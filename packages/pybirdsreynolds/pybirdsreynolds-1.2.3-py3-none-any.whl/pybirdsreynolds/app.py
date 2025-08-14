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
from pybirdsreynolds.const import *

# variables
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
blink_state = True
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
WIDTH_PARAMS_DEFAULT=400
margin=1
selected_index=0
parameters = ["num_birds", "neighbor_radius", "sep_weight", "align_weight", "coh_weight" , "max_speed" , "random_speed", "random_angle", "refresh_ms", "width", "height", "size", "triangles", "color" , "free"]

# deep copy
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

def display_range(value_default=None, value_min=None, value_max=None):
    parts = [f"(default: {value_default}"]
    
    if value_min is not None:
        parts.append(f"min: {value_min}")
    
    if value_max is not None:
        parts.append(f"max: {value_max}")
    
    return " - ".join(parts)+")"

# doc dict
param_docs = {
    "num_birds"      : "Number of birds in the simulation ",
    "neighbor_radius": f"Distance to detect neighbors ",
    "sep_weight"     : f"Separation weight ",
    "align_weight"   : f"Alignment weight ",
    "coh_weight"     : f"Cohesion weight ",
    "max_speed"      : f"Maximum speed of birds ",
    "random_speed"   : f"Random speed variation ratio (%) ",
    "random_angle"   : f"Random angle variation in degrees ",
    "refresh_ms"     : "Refresh interval in milliseconds ",
    "width"          : "Simulation area width ",
    "height"         : "Simulation area height ",
    "size"           : "Visual size of birds ",
    "triangles"      : "Render birds as triangles instead of points",
    "color"          : "Enable colors",
    "free"           : "Remove parameter limits (use with caution)"  
}
param_order = list(param_docs.keys())

def app():

    def restore_options():

        global max_speed, neighbor_radius, num_birds, width, height
        global refresh_ms, random_speed, random_angle
        global sep_weight, align_weight, coh_weight
        global paused, size, triangles, color, canvas_bg
        global fill_color, outline_color, fps, free
        
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
        triangles = copy.deepcopy(triangles_init)    

        if not color:
            canvas_bg = "black"
            fill_color = "white"
            outline_color = "black"
        else:
            canvas_bg = "blue"
            fill_color = "white"
            outline_color = "black"    

    def draw():
        draw_canvas()
        draw_status()
        draw_points()
        draw_rectangle()
        draw_fps()
        draw_paused()

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
                max(height,CANVAS_WIDTH_DEFAULT),            
                anchor="sw",  
                fill="yellow",
                font=("Consolas", 10, "bold"),
                tags="fps",
                text=f" FPS : {value}"
        )

    def draw_paused():
        global blink_state
        canvas.delete("paused")
        if paused:
            if blink_state:
                canvas.create_text(
                    WIDTH_PARAMS_DEFAULT,
                    max(height, 400),
                    anchor="se",
                    fill="red",
                    font=("Consolas", 12, "bold"),
                    tags="paused",
                    text="PAUSED - press Space -"
                )
            blink_state = not blink_state
            canvas.after(500, draw_paused)
            
    def on_next_frame(event):
        global paused
        paused = True
        generate_points_and_facultative_move(True)
        draw()

    def toggle_pause(event=None):
        global paused
        paused = not paused
        draw_status()
        draw_paused()

    def change_value(type, val, free):
        value = globals().get(type)
        prefix = type.upper()
        default = globals().get(f"{prefix}_DEFAULT")
        min_value = globals().get(f"{prefix}_MIN")
        max_value = globals().get(f"{prefix}_MAX")
        min_free_value = globals().get(f"{prefix}_FREE_MIN")
        max_free_value = globals().get(f"{prefix}_FREE_MAX")                    
        value += val
        if not free:
            if max_value is not None:
                value = min(value, max_value)
            if min_value is not None:
                value = max(value, min_value)
        else:
            if max_free_value is not None:
                value = min(value, max_free_value)
            if min_free_value is not None:
                value = max(value, min_free_value)
        return value

    def on_other_key(event):
        global selected_index, num_birds, max_speed
        global neighbor_radius, sep_weight, align_weight
        global coh_weight, size, random_speed, random_angle
        global triangles, free , refresh_ms, width, height
        global color, canvas_bg, fill_color, outline_color, fps
        # test if ctrl is pressed
        ctrl = (event.state & 0x4) != 0
        mult = 10 if ctrl else 1
        val = mult if event.keysym == "Right" else 1*-mult
        param = parameters[selected_index]
        if event.keysym == "Up":
            selected_index = (selected_index - 1) % len(parameters)
        elif event.keysym == "Down":
            selected_index = (selected_index + 1) % len(parameters)
        elif event.keysym == "Right"  or event.keysym == "Left":
            if param == "triangles":
                triangles = not triangles
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
                for paramm in parameters:
                    if paramm not in ["free", "color" , "triangles"]:
                        globals()[paramm] = change_value(paramm, 0, free)                                                      
            else:  
                globals()[param] = change_value(param, val, free)

            if param == "num_birds":
                generate_points_and_facultative_move(False)
                draw_points()                 
            elif param == "width":  
                generate_points_and_facultative_move(False)
                draw()  
            elif param == "height":  
                generate_points_and_facultative_move(False)
                draw()
            elif param == "free":
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
        canvas.config(width=width + WIDTH_PARAMS_DEFAULT, height=max(height,CANVAS_WIDTH_DEFAULT), bg=canvas_bg)

    def draw_status():
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
        # Accéder dynamiquement aux constantes
        prefix = param_name.upper()
        default = globals().get(f"{prefix}_DEFAULT")
        min_val = globals().get(f"{prefix}_MIN")
        max_val = globals().get(f"{prefix}_MAX")        
        doc_text = param_docs.get(param_name, "") + display_range(default, min_val, max_val)
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
            WIDTH_PARAMS_DEFAULT, 0, WIDTH_PARAMS_DEFAULT + width, height,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def generate_points_and_facultative_move(with_move):
        global velocities
        global new_velocities
        if not birds: 
            velocities = []
            for _ in range(num_birds):
                px = random.randint(margin + WIDTH_PARAMS_DEFAULT, width - margin + WIDTH_PARAMS_DEFAULT)
                py = random.randint(margin, height - margin)
                birds.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            # Keep birds only if inside
            inside_points = []
            inside_velocities = []
            for (x, y), (vx, vy) in zip(birds, velocities):
                if WIDTH_PARAMS_DEFAULT + margin <= x <= WIDTH_PARAMS_DEFAULT + width - margin and 0 + margin <= y <= height - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
            birds[:] = inside_points
            velocities[:] = inside_velocities
            new_velocities = []
            current_count = len(birds)
            
            # Add birds if not enough
            if num_birds > current_count:
                for _ in range(num_birds - current_count):
                    px = random.randint(margin + WIDTH_PARAMS_DEFAULT, width - margin + WIDTH_PARAMS_DEFAULT)
                    py = random.randint(margin, height - margin)
                    birds.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, max_speed)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Delete birds if not enough
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
        #TODO n2 use Grid / Uniform Cell List 
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
                        # If a neighbor is too close, add a vector to move away from it (opposite direction of the neighbor).
                        move_sep_x += (x - x2) / dist
                        move_sep_y += (y - y2) / dist
                        # ALIGNMENT
                        # Add the neighbor's velocity so the bird tends to align with it.
                        # Division is done later
                        vx2, vy2 = velocities[j]
                        move_align_x_tmp += vx2
                        move_align_y_tmp += vy2
                        # COHESION
                        # Add the neighbor's position to later calculate an average point, 
                        # so the bird moves toward the group's center.
                        # Division is done later
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


            
            #RANDOM
            speed = math.sqrt(vx**2 + vy**2)
            speed_factor = 1 + random.uniform(-random_speed / 100, random_speed / 100)
            new_speed = speed * speed_factor
            min_speed = 0.1 * max_speed
            
            if speed > 0:
                factor = new_speed / speed
            # Give initial speed if the bird is stationary    
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

        # Update positions
        new_points = []
        for (x, y), (vx, vy) in zip(birds, velocities):
            nx = x + vx
            ny = y + vy
            # Bounces
            while nx < margin + WIDTH_PARAMS_DEFAULT or nx > width - margin + WIDTH_PARAMS_DEFAULT:
                if nx < margin + WIDTH_PARAMS_DEFAULT:
                    overshoot = (margin + WIDTH_PARAMS_DEFAULT) - nx
                    nx = (margin + WIDTH_PARAMS_DEFAULT) + overshoot
                    vx = abs(vx)
                elif nx > width - margin + WIDTH_PARAMS_DEFAULT:
                    overshoot = nx - (width - margin + WIDTH_PARAMS_DEFAULT)
                    nx = (width - margin + WIDTH_PARAMS_DEFAULT) - overshoot
                    vx = -abs(vx)
            while ny < margin or ny > height - margin:
                if ny < margin:
                    overshoot = margin - ny
                    ny = margin + overshoot
                    vy = abs(vy)
                elif ny > height - margin:
                    overshoot = ny - (height - margin)
                    ny = (height - margin) - overshoot
                    vy = -abs(vy)
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
            #add demay to stabilize fps    
            if now - last_time >= 1.0: 
                fps_value = frame_count / (now - last_time)
                frame_count = 0
                last_time = now 
        #reset fps        
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
    root.title(f"pybirdsreynolds - {version_prog}")

    canvas = tk.Canvas(root, width=width+WIDTH_PARAMS_DEFAULT, height=height, bg=canvas_bg)
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


