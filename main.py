#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import arguments
import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()

arguments.activate_arguments()

pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.dump_stats("main.prof")
print( s.getvalue())
