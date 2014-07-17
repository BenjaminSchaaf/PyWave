# PyWave

A python based GUI Application for sound cueing and mixing.

Installation
============

PyWave does not currently have a setup or installation process. Simply put the
downloaded folder somewhere and run `main.py`.

Requirements
------------

PyWave requires Python 2.7, as well as the following modules:
 - pygame
 - wxPython
 - PyYAML

Usage
=====

To run the program use the following terminal commands:

Windows:

```bash
python main.py
```

Unix:

```bash
./main.py
```

When running for the first time, you should see a screen similar to the image
below:

![The First Time](/Data/first_time.png)

PyWave is split into three tabs, each of which has it's own important
function:
 - The Master
 - The Mixers
 - The Sounds

Master
------

The master tab gives access to a master volume control (and should eventually
have visualizers for the sound output). Currently, the master only contains one
single volume slider that is used for all sounds.

Sounds
------

The sounds tab holds the collection of all currently loaded sounds in the
project. To add a sound, click the "Add" button, opening a file dialog:

![Adding a Sound](/Data/sound_adding.png)

Once a sound has been added, it's name can be edited by double clicking on it
(In edit mode by default) and it can also be removed using the "Delete" button.

![We have Sounds!](/Data/sound_added.png)

Mixers
------

The mixers tab holds a collection of every mixer in the current project. Each
mixer contains a set of ordered cues, each describing an action to do with one
of the loaded sounds. Mixers are added using the "Add" button:

![Adding a Mixer](/Data/mixer_adding.png)

Once a mixer has been added, it's name can be edited by double clocking on it
(In edit mode by default) and it can be deleted by pressing the "Delete"
button.

![We have Mixers!](/Data/mixer_added.png)

To edit the cues of a mixer, press the "Edit" button and the mixers tab will
change into the cue editor tab:

![Editing Cues](/Data/cue_editor.png)

Cues
----

In the cue editor, individual cues can be added using the "Add" button:

![Adding a Cue](/Data/cue_adding.png)

Once a cue has been added, it's name can be edited by double clocking on it
(In edit mode by default) and it can be deleted using the "Delete" button.
A cue is defined by what action it takes and with what sound that action
happens. These options appear as drop down boxes for the cue:

![We have Cues!](/Data/cue_added.png)

The "Back" button can then be used to go back to the mixers tab.

Back to Mixers
--------------

Once cues have been added, they can be controled by the mixer, using the
following action buttons:
 - "Cue" -> Execute the next cue
 - "Back" -> Jump back one cue
 - "Reset" -> Reset back to the first cue

![Now we can run them!](/Data/cue_controls.png)

The cue that is currently active, ie. ready for execution, is labeled by a
green color. Cues that have been executed are marked Red and cues that are yet
to be executed are marked grey:

![They are even colored!!!](/Data/cue_colors.png)

You can also jump to any cue, without executing it, simply by clicking on it.
The clocked on cue then becomes the currently active cue.

Contributions
=============

Any contributions are welcome (this is an open source project after all),
as long as they follow the expected style:

 - Functions that pertain to events called by wxPython are in UpperCamelCase
   and start with `On`.
 - Functions that are solely for UI work also use UpperCamelCase

Otherwise, standard python styling is used.
