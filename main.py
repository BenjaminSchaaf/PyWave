#!/usr/bin/env python
""" The main file for PyWave.
This file starts the application.
"""

import os
import sys

from PyWave.application import Application

#--------------------------------------------------------
#                       Metadata
#--------------------------------------------------------

__author__ = "Benjamin Schaaf"
__copyright__ = "Copyright 2014, Benjamin Schaaf"
__license__ = "GPL"
__version__ = "1.0.0"
__status__ = "release"

#--------------------------------------------------------
#                         Main
#--------------------------------------------------------

def main():
    """ Run PyWave directly.

    Main Function.
    """
    #Check for a sys arg file loading
    path = None
    if len(sys.argv) > 1:
        path = os.path.abspath(sys.argv[1])

    #Change the active directory appropreately
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    #Start the application
    app = Application()
    app.run(path)

#Run main if this file is run directly
if __name__ == "__main__":
    main()
