#!/usr/bin/env python
import sys
from rq import Connection, Worker

with Connection():
    qs = sys.argv[1:] or ['libcrowds_analyst']
    w = Worker(qs)
    w.work()
