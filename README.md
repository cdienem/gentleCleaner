# gentleCleaner
A Python implementation of Relions gentle clean method.

Usage:
<code>
  jobs = readRelionProjectJobs(location)

for job in jobs:
	for f in cleanRelionJobFiles(location, job):
		print(f)
</code>
