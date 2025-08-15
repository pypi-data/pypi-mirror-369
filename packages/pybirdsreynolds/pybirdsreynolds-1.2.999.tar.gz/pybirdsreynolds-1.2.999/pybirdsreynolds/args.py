import argparse
import sys
import textwrap
from pybirdsreynolds.const import *

def display_range(prefix):
    g = globals()
    value_default   = g[f"{prefix}_DEFAULT"]
    if not isinstance(value_default, bool):
        value_min       = g[f"{prefix}_MIN"]
        value_max       = g[f"{prefix}_MAX"]
        value_free_min  = g[f"{prefix}_FREE_MIN"]
        value_free_max  = g[f"{prefix}_FREE_MAX"]
        parts = []
        
        if value_min is not None and value_max is not None:
            parts.append(f"integer between {value_min} and {value_max}")
        elif value_min is not None:
            parts.append(f"integer >= {value_min}")
        elif value_max is not None:
            parts.append(f"integer <= {value_max}")
        else:   
            parts.append(f"integer with no limit")

        if value_free_min is not None and value_free_max is not None:
            parts.append(f"if --free integer between {value_free_min} and {value_free_max}")
        elif value_free_min is not None:
            parts.append(f"if --free integer >= {value_free_min}")
        elif value_free_max is not None:
            parts.append(f"if --free integer <= {value_free_max}")
        else:   
            parts.append(f"if --free integer with no limit")

        if value_default is not None:
            parts.append(f"default: {value_default}")
        
        return f"{' , '.join(parts)}" if parts else ""
    else:
        return "boolean value"


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

def compute_args():
    controls_text = "\n".join(f"  {line}" for line in COMMON_CONTROLS)

    my_parser = argparse.ArgumentParser(
        description=textwrap.dedent(f"""\
pybirdsreynolds - Simulation of bird flocking behavior using Reynolds' rules.

Controls:
{controls_text}

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
        formatter_class=argparse.RawTextHelpFormatter
    )   


    g = globals()

    for name, doc in g.items():
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        default_name = f"{prefix}_DEFAULT"
        if default_name not in g:
            continue 

        default_value = g[default_name]
        arg_name = "--" + prefix.lower()

        if isinstance(default_value, bool):
            my_parser.add_argument(
                arg_name,
                action="store_true",
                default=default_value,
                help=g[name] + " - " +display_range(prefix)
            )
        else:
            my_parser.add_argument(
                arg_name,
                type=int,
                default=default_value,
                help=g[name] + " - " +display_range(prefix)
            )

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
    #check_values("SIZE" , args.free , args.size , my_parser)
    #check_values("REFRESH_MS" , args.free , args.refresh_ms , my_parser)
    
    return args


