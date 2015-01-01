#!/usr/bin/env python

import os, subprocess as sub

#os.system('pg_dump -U kakaostats -C folding > /folding/bak/dump/folding.dump 2>> /folding/scripts/vacuum.Err.log')
sub.call(["pg_dump",
          "-U kakaostats",
          "-C", "folding",
          "-f /folding/bak/dump/folding.dump",
          "2>> /folding/scripts/dump.Err.log"])
