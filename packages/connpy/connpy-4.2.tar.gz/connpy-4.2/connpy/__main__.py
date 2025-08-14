#!/usr/bin/env python3
import sys
from connpy import *

def main():
    conf = configfile()
    app = connapp(conf)
    app.start()

if __name__ == '__main__':
    sys.exit(main())
