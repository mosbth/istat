#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
I got a problem with my irc log file, it had duplicate entries. So I wrote this script
to parse the logfile (52000+ rows) and check for duplicate rows and only print out 
those not duplicates. 

The duplicates are always in close relation to each other, the row above or the row 
next to it.

I choosed to store the x latest rows in a list, but that depends on how the log looks like

Run the command and use shell redirection to redirect the output to a new logfile. 

$ python3 istat.py > newlog.txt

First I made a program scanning the logfile "removing" duplicates. Then I added commandline 
options to make the script look more like a actual command line utility that can be extended
to do other operations with my logfiles.

"""



import sys
import os
from datetime import datetime
import getopt



#
# Add some stuff about this script
#
PROGRAM = "istat"
AUTHOR = "Mikael Roos"
EMAIL = "mikael.t.h.roos@gmail.com"
VERSION = "1.0.0"
USAGE = """{program} - Scan and investigate an irssi logfile. By {author} ({email}), version {version}.

Usage:
  {program} [options] logfile

Options:
  -h --help     Display this help message.
  -s --silent   Do not display any details or statistics about the execution.
  -v --version  Print version and exit.

  logfile     The filename of the irssi logfile to scan.
""".format(program=PROGRAM, author=AUTHOR, email=EMAIL, version=VERSION)
VERSION_MSG = "{program} version {version}.".format(program=PROGRAM, version=VERSION)
USAGE_MSG = "Use {program} --help to get usage.\n".format(program=PROGRAM)
LOGFILE_NOT_EXISTS = "The logfile '{logfile}' does not exists."



#
# Global default settings affecting behaviour of script in several places
#
LOGFILE = None
VERBOSE = True
NEIGHBOUR_SIZE = 2
OUTPUT_FILE = sys.stdout

EXIT_SUCCESS = 0
EXIT_USAGE = 1
EXIT_FAILED = 2



def printUsage(exitStatus):
    """
    Print usage information about the script and exit.
    """
    print(USAGE)
    sys.exit(exitStatus)



def printVersion():
    """
    Print version information and exit.
    """
    print(VERSION_MSG) 
    sys.exit(EXIT_SUCCESS)



def printNoneDuplicates():
    """
    Walk through the logfile and print out those rows not found as duplicates.
    """

    duplicates = 0
    rows = 0

    # Open and close file and take care of execptions
    with open(LOGFILE) as f:
        
        # Store neighbour entries in list
        neighbour = []
        
        # Treat the file as an iteratable and read each line into a string
        for line in f:
            
            # If a duplicate leave it, take the next row
            if line in neighbour:
                duplicates += 1
                continue

            neighbour.append(line)

            # Remove the oldes item in the list if size has reached
            if len(neighbour) > NEIGHBOUR_SIZE:
                neighbour.pop(0)

            rows += 1
            OUTPUT_FILE.write(line)

    if VERBOSE:
        sys.stderr.write("Duplicates found: %s\n" % duplicates)
        sys.stderr.write("Rows written: %s\n" % rows)



def parseOptions():
    """
    Merge default options with incoming options and arguments and return them as a dictionary.
    """

    # Swtich through all options
    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "hn:o:sv", ["help", "neighbours=", "output=", "version", "silent"])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                printUsage(EXIT_SUCCESS)

            elif opt in ("-n", "--neighbours"):
                global NEIGHBOUR_SIZE
                if not arg.isnumeric():
                    assert False, "{} is not a numeric value".format(opt)

                NEIGHBOUR_SIZE = int(arg)

            elif opt in ("-o", "--output"):
                global OUTPUT_FILE
                OUTPUT_FILE = open(arg, "w")

            elif opt in ("-s", "--silent"):
                global VERBOSE
                VERBOSE = False

            elif opt in ("-v", "--version"):
                printVersion()

            else:
                assert False, "Unhandled option"
    
        if len(args) != 1:
            assert False, "Missing logfile"

        # Path of logfile passed as argument
        global LOGFILE
        LOGFILE = args[0]

        # Check that the logfile exists and is readable
        if not (os.path.isfile(LOGFILE) and os.access(LOGFILE, os.R_OK)):
            assert False, LOGFILE_NOT_EXISTS.format(logfile=LOGFILE)

    except Exception as err:
        print(err)
        print(USAGE_MSG)
        sys.exit(EXIT_USAGE)




def main():
    """
    Main function to carry out the work.
    """
    startTime = datetime.now()
    
    parseOptions()

    printNoneDuplicates()
    
    timediff = datetime.now()-startTime
    if VERBOSE:
        sys.stderr.write("Script executed in {}.{} seconds\n".format(timediff.seconds, timediff.microseconds))
    
    sys.exit(EXIT_SUCCESS)



if __name__ == "__main__":
    main()
