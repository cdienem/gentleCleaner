# gentleCleaner
A Python implementation of Relions gentle clean method.

Usage:


```python
jobs = readRelionProjectJobs(location)

for job in jobs:
	for f in cleanRelionJobFiles(location, job):
		print(f) # print the files affectedd by gentle clean
```
