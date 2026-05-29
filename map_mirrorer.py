import sys
import os
import re

# i/o
input_file = sys.argv[1]
input_dir = os.path.dirname(input_file)
input_name = os.path.basename(input_file)
output_file = os.path.join(input_dir, input_name.replace(".dmm", "_mirror.dmm"))

# (x,y,z) coordinate pattern
coord_pattern = re.compile(r"\((\d+),(\d+),(\d+)\)")

# func to flip x coordinate
def mirror_coords(match):
    x, y, z = map(int, match.groups())
    return f"({256-x},{y},{z})"

# regex to fix the Space Station 13 logo after mirroring the map. what a weird decal
icon_pattern = re.compile(r'icon_state\s*=\s*"L(\d+)"')
def mirror_ss13_decal(match):
    num = int(match.group(1))
    
    if num % 2 == 0:  # top row
        new_num = 16 - num  # 2->14, 4->12, 6->10
    else:  # bottom row
        new_num = 14 - num  # 1->13, 3->11, 5->9
    
    return f'icon_state = "L{new_num}"'

# iteration flags (replace in the future)
corner1 = False
op_corner = False
half = False
corner2 = False

# stats for your viewing pleasure
pixel_shifted_items = 0
directional_items_changed = 0
decals_changed = 0
floors_changed = 0
items_changed = 0
items_unchanged = 0

# utf-8 because mapping insanity
with open(input_file, "r", encoding="utf-8") as f_in, \
    open(output_file, "w", encoding="utf-8") as f_out:

    for line in f_in:
        original_line = line # logging

        # it's flipping time (map coords)
        line = coord_pattern.sub(mirror_coords, line)

        # invert pixel_x values
        if "pixel_x" in line:
            key, value = line.split("=")
            num = int(value.strip(" ;\n")) # just the number
            line = f"{key}= {-num};\n"
            pixel_shifted_items = pixel_shifted_items + 1

        # sanitization removes default dir values in the file. to ensure they iterate properly, add it here
        if "turf_decal" in line:
            line = line.replace(",", "{ dir = 2 },")
        if "open/floor" in line:
            if "cafeteria" in line or "checker" in line or ("kitchen" in line and not "diagonal" in line or "herringbone" in line or "small" in line):
                line = line.replace(",", "{ dir = 2 },")

        # fix the 14 Space Station 13 decals
        line = icon_pattern.sub(mirror_ss13_decal, line)

        # begin tag filtering. some items with > 10 dirs like decals can't be 'universally' mirrored, so we need to filter them into their own flipping functions
        # i hope you like giant if loops
        # todo: convert tag system into a single variable set to a particular string, rather than having a bunch of unused tags that need to be added to a reset condition at the end of each block. what was i thinking?
        # ex: if "opposingcorners" in line: 



        #### sgt pepper and the quirky dirs club band

        # turf_decal/tile
        if "turf_decal/tile" in line:
            # opcorner decals
            if "opposingcorners" in line:
                decals_changed = decals_changed + 1
                op_corner = True
            # single-corner tile decals
            elif not "diagonal_center" in line and not "diagonal_edge" in line and not "fourcorners" in line and not "full" in line and not "half" in line and not "tram" in line:
                decals_changed = decals_changed + 1
                corner1 = True
       # misc corner decals
        elif "turf_decal" in line:
            if ("stripes" in line or "trimline" in line) and "corner" in line:
                decals_changed = decals_changed + 1
                corner1 = True
        # seating corners (sofas, benches, etc.)
        elif "structure/chair" in line and "corner" in line:
            corner2 = True
        # opcorner tiles
        elif "open/floor" in line:
            if ("cafeteria" in line or "checker" in line or ("kitchen" in line and not "diagonal" in line or "herringbone" in line or "small" in line)):
                floors_changed = floors_changed + 1
                op_corner = True
            elif "corner" in line:
                floors_changed = floors_changed + 1
                corner1 = True

        # conditional replacements
        # 'smithers' string is used here to prevent overwrite during the process
        if op_corner:
            line = line.replace("dir = 2", "smithers")
            line = line.replace("dir = 1", "dir = 2")
            line = line.replace("smithers", "dir = 1")
        elif corner1:
            line = line.replace("dir = 2", "smithers")
            line = line.replace("dir = 8", "dir = 2")
            line = line.replace("smithers", "dir = 8")

            line = line.replace("dir = 1", "smithers")
            line = line.replace("dir = 4", "dir = 1")
            line = line.replace("smithers", "dir = 4")
        elif corner2:
            line = line.replace("dir = 1", "smithers")
            line = line.replace("dir = 8", "dir = 1")
            line = line.replace("smithers", "dir = 8")

            line = line.replace("dir = 2", "smithers")
            line = line.replace("dir = 4", "dir = 2")
            line = line.replace("smithers", "dir = 4")
        # everything else
        else:
            line = line.replace("dir = 8", "smithers")
            line = line.replace("dir = 4", "dir = 8")
            line = line.replace("smithers", "dir = 4")

            line = line.replace("dir = 10", "smithers")
            line = line.replace("dir = 6", "dir = 10")
            line = line.replace("smithers", "dir = 6")

            line = line.replace("dir = 9", "smithers")
            line = line.replace("dir = 5", "dir = 9")
            line = line.replace("smithers", "dir = 5")

        # actual directionals that make life easy
        if "directional/west" in line or "directional/east" in line:
            directional_items_changed = directional_items_changed + 1

        line = line.replace("directional/west", "smithers")
        line = line.replace("directional/east", "directional/west")
        line = line.replace("smithers", "directional/east")

        # couches, benches, areas, two-tile objs, etc.
        line = line.replace("/left", "smithers")
        line = line.replace("/right", "/left")
        line = line.replace("smithers", "/right")

        # reset our tag system after making changes
        if "}" in line:
            corner1 = False
            op_corner = False
            half = False
            corner2 = False

        if line == original_line:
            items_unchanged = items_unchanged + 1
        else:
            items_changed = items_changed + 1

        f_out.write(line)

print("\n")
print(f"items changed: {items_changed} / {items_unchanged}")
print(f"pixel shifted items inverted: {pixel_shifted_items}")
print(f"directional items flipped: {directional_items_changed}")
print(f"decals flipped: {decals_changed}")
print(f"floors flipped: {floors_changed}")
print(f"\nSuccess! Exported as '{output_file}'\n\n")