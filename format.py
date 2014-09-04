#! /usr/bin/env python
import subprocess

in_str = "test test test"
outstr = subprocess.Popen(["cowsay", in_str], stdout=subprocess.PIPE).communicate()
for string in outstr:
    if string != None:
        print string
