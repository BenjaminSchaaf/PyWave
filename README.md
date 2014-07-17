PyWave
======

A python based GUI Application for sound cueing and mixing.

Installation
-----------

PyWave does not currently have a setup or installation process. Simply put the downloaded folder somewhere and run `main.py`.

Requirements
''''''''''''

PyWave requires Python 2.7, as well as the following modules:
 - pygame
 - wxPython
 - PyYAML

Contributions
-------------

Any contributions are welcome.

Style
'''''

Because of the use of wxPython, PyWave follows a slightly altered standard style:

 - Functions that pertain to events called by wxPython are in UpperCamelCase
   and start with `On`.
 - Functions that are solely for UI work also use UpperCamelCase

Otherwise, standard python styling is used.