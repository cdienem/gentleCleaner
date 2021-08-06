# gentleCleaner
A Python implementation of Relions gentle clean method.

Beware: some job types have not been tested (because they are not used here). Bug reports welcome :D

Usage:


```python
jobs = readRelionProjectJobs(location)

for job in jobs:
	for f in cleanRelionJobFiles(location, job):
		print(f) # print the files affectedd by gentle clean
```
Mostly ported from https://github.com/3dem/relion/blob/dcab7933398a8b728e56a08ea1bb2539a5ba71d4/src/pipeliner.cpp#L1432 to Python.
