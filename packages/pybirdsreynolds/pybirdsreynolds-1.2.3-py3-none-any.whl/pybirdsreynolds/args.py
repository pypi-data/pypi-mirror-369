import argparse
import sys
import textwrap
from pybirdsreynolds.const import *

def check_values(prefix , free , value , my_parser):
    g = globals()
    value_default   = g[f"{prefix}_DEFAULT"]
    value_min       = g[f"{prefix}_MIN"]
    value_max       = g[f"{prefix}_MAX"]
    value_free_min  = g[f"{prefix}_FREE_MIN"]
    value_free_max  = g[f"{prefix}_FREE_MAX"]  
    if not free:  
        if (value_min is not None and value_max is not None) and (value < value_min or value > value_max):
            my_parser.error(f"{prefix.lower()} must be between {value_min} and {value_max}")
        elif (value_min is None and value_max is not None) and (value > value_max):
            my_parser.error(f"{prefix.lower()} must <= {value_max}")
        elif (value_min is not None and value_max is None) and (value < value_min):
            my_parser.error(f"{prefix.lower()} must >= {value_min}") 
    else:
        if (value_free_min is not None and value_free_max is not None) and (value < value_free_min or value > value_free_max):
            my_parser.error(f"{prefix.lower()} must be between {value_free_min} and {value_free_max}")
        elif (value_free_min is None and value_free_max is not None) and (value > value_free_max):
            my_parser.error(f"{prefix.lower()} must <= {value_free_max}")
        elif (value_free_min is not None and value_free_max is None) and (value < value_free_min):
            my_parser.error(f"{prefix.lower()} must >= {value_free_min}")

def display_range(prefix):
    g = globals()
    value_default   = g[f"{prefix}_DEFAULT"]
    value_min       = g[f"{prefix}_MIN"]
    value_max       = g[f"{prefix}_MAX"]
    value_free_min  = g[f"{prefix}_FREE_MIN"]
    value_free_max  = g[f"{prefix}_FREE_MAX"]
    parts = []
    
    # on affiche min et max uniquement s'ils existent
    if value_min is not None and value_max is not None:
        parts.append(f"integer between {value_min} and {value_max}")
    elif value_min is not None:
        parts.append(f"integer >= {value_min}")
    elif value_max is not None:
        parts.append(f"integer <= {value_max}")

    if value_free_min is not None and value_free_max is not None:
        parts.append(f"if --free: integer between {value_free_min} and {value_free_max}")
    elif value_free_min is not None:
        parts.append(f"if --free: integer >= {value_free_min}")
    elif value_free_max is not None:
        parts.append(f"if --free: integer <= {value_free_max}")
    # valeur par défaut
    if value_default is not None:
        parts.append(f"default: {value_default}")
    
    return f"({' , '.join(parts)})" if parts else ""

def compute_args():
    my_parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
            pybirdsreynolds - Simulation of bird flocking behavior using Reynolds' rules.

            Controls:
             [Space]           : Toggle start / stop
             [Enter]           : Advance by one frame
             [Up/Down]         : Navigate between parameters
             [Left/Right]      : Adjust selected parameter +1/-1 True/False
             [Ctrl][Left/Right]: Adjust selected parameter +10/-10
             [r]               : Reset all parameters
             [n]               : New generation of birds
             [f]               : Toggle FPS display
            Thanks to Mehdi Moussaïd - http://www.mehdimoussaid.com/a-propos/ - https://youtu.be/xuKrkOh_mzk  
            """),
        epilog=textwrap.dedent("""\
            Full documentation:  https://github.com/thib1984/pybirdsreynolds
            Report bugs:         https://github.com/thib1984/pybirdsreynolds/issues

            License: MIT
            Copyright (c) 2025 thib1984

            This is free software: you can modify and redistribute it.
            There is NO WARRANTY, to the extent permitted by law.
            Written by thib1984.
            """),
        formatter_class=argparse.RawTextHelpFormatter,
    )    
    my_parser.add_argument(
        "--num_birds",
        type=int,
        default=500,
        help="Number of birds in the simulation " + display_range(prefix="NUM_BIRDS")
    )
    my_parser.add_argument(
        "--max_speed",
        type=int,
        default=10,
        help="Maximum speed of birds " + display_range(prefix="MAX_SPEED")
    )
    my_parser.add_argument(    
        "--neighbor_radius",
        default=50,
        type=int,
        help="Distance to detect neighbors " + display_range(prefix="NEIGHBOR_RADIUS")
    )
    my_parser.add_argument(
        "--sep_weight",
        type=int,
        default=1,
        help="Separation weight " + display_range(prefix="SEP_WEIGHT")
    )
    my_parser.add_argument(
        "--align_weight",
        type=int,
        default=1,
        help="Alignment weight " + display_range(prefix="ALIGN_WEIGHT")
    )
    my_parser.add_argument(
        "--coh_weight",
        type=int,
        default=1,
        help="Cohesion weight " + display_range(prefix="COH_WEIGHT")
    ) 
    my_parser.add_argument(
        "--random_speed",
        type=int,
        default=10,
        help="Random speed variation ratio (percentage of max speed) " + display_range(prefix="RANDOM_SPEED")
    )
    my_parser.add_argument(
        "--random_angle",
        type=int,
        default=10,
        help="Random angle variation in degrees " + display_range(prefix="RANDOM_ANGLE")
    )
    my_parser.add_argument(        
        "--refresh_ms",
        type=int,
        default=10,
        help="Refresh interval in milliseconds " + display_range(prefix="REFRESH_MS")
    )    
    my_parser.add_argument(
        "--width",
        type=int,
        default=1000,
        help="Simulation area width " + display_range(prefix="WIDTH")
    )
    my_parser.add_argument(
        "--height",
        type=int,
        default=500,
        help="Simulation area height " + display_range(prefix="HEIGHT")
    )
    my_parser.add_argument(
        "--size",
        type=int,
        default=1,
        help="Visual size of birds " + display_range(prefix="SIZE")
    )
    my_parser.add_argument("--color", action="store_true", help="Enable colors")
    my_parser.add_argument("--triangles", action="store_true", help="Render birds as triangles instead of single points")
    my_parser.add_argument("--free", action="store_true", help="Remove parameter limits (use with caution)")

    args = my_parser.parse_args()
    check_values("NUM_BIRDS" , args.free , args.num_birds , my_parser)
    check_values("MAX_SPEED" , args.free , args.max_speed , my_parser)
    check_values("NEIGHBOR_RADIUS" , args.free , args.neighbor_radius , my_parser)
    check_values("SEP_WEIGHT" , args.free , args.sep_weight , my_parser)
    check_values("ALIGN_WEIGHT" , args.free , args.align_weight , my_parser)
    check_values("COH_WEIGHT" , args.free , args.coh_weight , my_parser)
    check_values("RANDOM_SPEED" , args.free , args.random_speed , my_parser)
    check_values("RANDOM_ANGLE" , args.free , args.random_angle , my_parser)
    check_values("WIDTH" , args.free , args.width , my_parser)
    check_values("HEIGHT" , args.free , args.height , my_parser)
    check_values("SIZE" , args.free , args.size , my_parser)
    check_values("REFRESH_MS" , args.free , args.refresh_ms , my_parser)
    
    return args


