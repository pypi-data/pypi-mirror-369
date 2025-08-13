import argparse
import sys
import textwrap


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
    my_parser.add_argument("--free", action="store_true", help="Remove parameter limits (use with caution)")
    
    my_parser.add_argument(
        "--num_birds",
        default=500,
        help="Number of birds in the simulation (integer between 1 and 1000, default: 500)"
    )
    my_parser.add_argument(
        "--max_speed",
        default=10,
        help="Maximum speed of birds (integer between 0 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--neighbor_radius",
        default=50,
        help="Distance to detect neighbors (pixels, default: 50)"
    )
    my_parser.add_argument(
        "--sep_weight",
        default=1,
        help="Separation weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--align_weight",
        default=1,
        help="Alignment weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--coh_weight",
        default=1,
        help="Cohesion weight (integer between 0 and 10, default: 1)"
    ) 
    my_parser.add_argument(
        "--random_speed",
        default=10,
        help="Random speed variation ratio (percentage of max speed, integer 0 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--random_angle",
        default=10,
        help="Random angle variation in degrees (integer between 0 and 360, default: 10)"
    )
    my_parser.add_argument(
        "--refresh_ms",
        default=10,
        help="Refresh interval in milliseconds (min 10, default: 10)"
    )    
    my_parser.add_argument(
        "--width",
        default=1000,
        help="Simulation area width (integer between 200 and 1500, default: 1000)"
    )
    my_parser.add_argument(
        "--height",
        default=500,
        help="Simulation area height (integer between 200 and 1000, default: 500)"
    )


    my_parser.add_argument("--color", action="store_true", help="Enable colors")
    my_parser.add_argument("--triangles", action="store_true", help="Render birds as triangles instead of single points")

    my_parser.add_argument(
        "--size",
        default=1,
        help="Visual size of birds (integer between 1 and 3, default: 1)"
    )

    args = my_parser.parse_args()
    
    if not args.free:
        if args.num_birds < 1 or args.num_birds > 1000:
            my_parser.error("num_birds must be between 1 and 1000")
        if args.max_speed < 0 or args.max_speed > 100:
            my_parser.error("max_speed must be between 0 and 100")  
        if args.sep_weight < 0 or args.sep_weight > 10:
            my_parser.error("sep_weight must be between 0 and 10") 
        if args.coh_weight < 0 or args.coh_weight > 10:
            my_parser.error("coh_weight must be between 0 and 10")   
        if args.align_weight < 0 or args.align_weight > 10:
            my_parser.error("align_weight must be between 0 and 10")
        if args.random_speed < 0 or args.random_speed > 100:
            my_parser.error("random_speed must be between 0 and 100") 
        if args.random_angle < 0 or args.random_angle > 360:
            my_parser.error("random_angle must be between 0 and 360")
        if args.width < 200 or args.width > 1500:
            my_parser.error("width must be between 200 and 1500")    
        if args.height < 200 or args.height > 1000:
            my_parser.error("height must be between 200 and 1000")
        if args.size < 1 or args.size > 3:
            my_parser.error("size must be between 1 and 3")              
    else:
        if args.num_birds < 1:
            my_parser.error("num_birds must be greater than or equal to 1")
        if args.max_speed < 0:
            my_parser.error("max_speed must be greater than or equal to 0")  
        if args.random_speed < 0:
            my_parser.error("random_speed must be greater than or equal to 0") 
        if args.width < 3:
            my_parser.error("width must be greater than or equal to 3")    
        if args.height < 3:
            my_parser.error("height must be greater than or equal to 3")
        if args.size < 1:
            my_parser.error("size must be greater than or equal to 1")                                                                                                                                
    return args

