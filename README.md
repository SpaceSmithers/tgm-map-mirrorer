# TGM map mirrorer
This tool lets you mirror SS13 maps in the TGM format along the x-axis

## Before you run mirrored maps
Certain elements will not work perfectly. For example, some shuttles (labor shuttles, notably) will probably clip into the surrounding area. This is because shuttles are a seperate template loaded into the map at runtime, and will not be mirrored with the script.

## How do I use it?
Drag and drop a map file onto `map_mirrorer.bat`, and it'll export a new file with `_mirrored` to the end of the name.

## How does it work?
SS13 maps are just coordinate grids that re-use map keys.

This is a python script so you might need python

For example:

`1,1,1 = {
    AAA,
    AAA,
    AAA,
    LOL,
}`

`2,1,1 = {
    AAA,
    AAA,
    AAA,
    BBQ,
}`

`...`

For more information on map formats, read up on the /tg/station guide
https://hackmd.io/@tgstation/ry4-gbKH5#Map-Keys-no-holds-barred

First, we mirror the coordinate map on the x-axis. For stations, the normal size is 255x255, so apply `255-X`. Map keys are re-used.

Next, there's a lot of map objects that are shifted from the center of the tile. For objects with directionals, we use a regex replacement.
`obj/machinery/air_alarm/directional/west` -> `obj/machinery/air_alarm/directional/east`.
For regular pixel-shifted items, we just flip the integer value.

Handling object/tile dirs isn't as easy. There's a lot of them without uniformity, like decals, cameras, pipes, or chapel tiles. For these special cases, they are hard-coded into a giant if-loop. Other issues are also handled in this same loop, such as multi-tile objects with "left" or "right" suffixes (benches, maps, etc.)

## Does this work for the y-axis?
No, you'd probably need to reverse the order of the map keys inside a given coordinate instead of moving the coordinate itself. Other than that, the object & tile modifying can probably be modified and re-used.

## Does it work for the DMM format?
I don't know, I seldom come across any maps formatted this way, so I haven't tested it.
