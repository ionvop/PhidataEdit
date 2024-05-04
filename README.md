# PhidataEdit
A level data generator for RePhiEditor using Simai-based syntax

## Properties and Metadata

```
&id=
&title=
&artist=
&first=0
&des=

&lv=0
&inote=
(120) {4}
```

`id` The number that points to the RPE chart ID.

`title` The name of the song.

`artist` The composer of the song.

`first` The offset of the song in ms.

`des` The charter of the song.

`lv` The level name of the chart.

`inote` The code that constructs the chart.

### Example

```
&id=81324710
&title=Oriental Blossom
&artist=影翔鼓舞
&first=0
&des=ionvop

&lv=12
&inote=
(180) {4}
```

## Syntax

### Timing

`(BPM)` Numbers enclosed in parenthesis define the BPM of the chart at the current beat similar to Simai. `e.g. (150)`

`{DIV}` Integers enclosed in curly braces define the beat divisor at the current beat similar to Simai. It defines the number of beats per measure. `e.g. {4}`

`<=BEAT:NUM:DEN>` `<=NUM:DEN>` Sets the current position. Can either be set like a mixed number or an improper fraction. Uses RPE's time notation.

- `e.g. <=2:1:4>` Sets the current position to the 2nd beat and 1/4 towards the 3rd.

- `e.g. <=7:4>` Sets the current position to the dividend of 7 with a beat divisor of 4, which translates to the 1st beat and 3/4 towards the 2nd.

### Notes

`TYPE[DIV:BEAT]LINE:X:PATH:FAKE` A string that describes the note. The note is defined with 3 optional positional arguments.

- `TYPE` (Required) The type of note to be used.

    - `n` Note

    - `d` Drag

    - `f` Flick

- `[DIV:BEAT]` (Optional) Turns the note into a hold and defines the length. Uses Simai's length notation.

- `LINE` (Required) The line that the note belongs to.

- `X` (Optional) The X position of the note relative to the line. Default is `0`.

- `PATH` (Optional) Defines the path of the note.

    - `0` Note spawns above the line. (Default)

    - `1` Note spawns below the line.

- `FAKE` (Optional) Defines whether the note is fake or not.

    - `0` Note is real. (Default)

    - `0` Note is fake.

#### Explanations

`n0` A note at line 0 with an X position of 0.

`d1:50` A drag note at line 1 with an X position of 50.

`n[4:1]2:-100` A hold note with a length of 1 beat (1/4 a measure) at line 2 with an X position of -100.

`n[1:1]3:150:1` A hold note with a length of 1 measure at line 3 with an X position of 150 that spawns below the line.

`f4:-200:0:1` A fake flick note at line 4 with an X position of -200

#### Examples

```
(170) {4}
,,,,
f0:-100/f0:100,n0,n0,n0,
f0:-300/f0:-100,n0:-200,n0:-200,n0:-200,
f0:100/f0:300,n0:200,n0:200,n0:200,
f0:-100/f0:100,n0,n0,n0,
```

It will look something like this:

```
---_---
---_---
---_---
--_-_--
-----_-
-----_-
-----_-
----_-_
-_-----
-_-----
-_-----
_-_----
---_---
---_---
---_---
--_-_--
-------
-------
-------
-------
```

### Events

`TYPE[DIV:BEAT]LINE:START:END:EASE` A string that describes the event. The note is defined with 2 optional positional arguments.

- `TYPE` (Required) The property of the event to be controlled.

    - `x` The X position of the line.

    - `y` The y position of the line.

    - `r` The roation of the line in degrees.

    - `a` The alpha channel of the line from 0 to 255.

    - `s` The speed of the notes of the line.

- `[DIV:BEAT]` (Optional) Defines the length of the transition. If omitted, the effect happens instantaneously. Uses Simai's length notation.

- `LINE` (Required) The line to be controlled.

- `START` (Required) The starting value.

- `END` (Optional) The ending value.

- `EASE` (Optional) The ease type of the transition. Uses RPE's ease type ID.

#### Explanations

`x0:50` Sets the X position of line 0 to 50.

`y[1:4]1:-50:50` Moves the Y position of line 1 from -50 to 50 over 1 beat (1/4 a measure).

`r[1:1]2:0:360:4` Rotates line 2 from 0 degrees to 360 easing out over 1 measure with an ease type of quad.