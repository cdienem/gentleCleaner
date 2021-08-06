#!/bin/python3
import os, sys, re, glob
from os.path import join, islink

def isRelionProjectDirectory(location):
	files = os.listdir(location)
	#print(files)
	if "default_pipeline.star" in files:
		return True
	else:
		return False


def readRelionProjectJobs(location):
# Quick and dirty retrieval of jobs from pipeline star file
# Returns a list of job folders
	file = open(join(location , "default_pipeline.star"),"r")

	wait_for_data = 0
	wait_for_header = 0
	
	jobs = []

	for line in file.read().splitlines():
		if line == "data_pipeline_processes":
			wait_for_header = 1

		if wait_for_header == 1:
			if line[0:4] == "_rln":
				wait_for_data = 1

		if wait_for_data == 1:
			if line[0:4] != "_rln":
				if line == "" or line == " ":
					break
				else:
					# Only append jobs with status == 2 (finished successfully)
					# Also check whether job directories exist
					if line.split()[3] == "2" and os.path.isdir(join(location,line.split()[0])):
						jobs.append(line.split()[0])
	print(jobs)
	return(jobs)

def readRelionProjectNodes(location):
# Quick and dirty retrieval of nodes from pipeline star file, is needed for cleaning 2D etc.
# Returns a list of node files
	file = open(join(location , "default_pipeline.star"),"r")

	wait_for_data = 0
	wait_for_header = 0
	
	nodes = []

	for line in file.read().splitlines():
		if line == "data_pipeline_nodes":
			wait_for_header = 1

		if wait_for_header == 1:
			if line[0:4] == "_rln":
				wait_for_data = 1

		if wait_for_data == 1:
			if line[0:4] != "_rln":
				if line == "" or line == " ":
					break
				else:
					nodes.append(line.split()[0])
	return(nodes)



def cleanRelionJobFiles(location, job, harsh=False, dry=True, absolute=True):
# Location: place of the relion project
# job: Job folder like Class2D/jobXX
# harsh: True = perform harsch cleaning
# dry (True/False): either print just a file list or actually do clean (e.g. move things to trash)
# absolute: only when doing dry runs, True=print absolute paths, False=print paths relative to project directory
# Return: a list of files to be cleaned (or that were clened)

	# Get job type
	job_type = job.split("/")[0]
	
	# TODO: check accurate names!
	if job_type in ["Import", "Manualpick", "Select", "MaskCreate", "JoinStar", "LocalRes"]:
		return []
	
	#print(job_type)
	delete_files = []
	
	
	if job_type == "MotionCorr":
			if harsh:
				# Just add all subfolders to the list
				delete_files.extend([d for d in os.listdir(join(location,job)) if os.path.isdir(d)])
			else:
				for root, dirs, files in os.walk(join(location,job), topdown=True):
					if root != join(location,job): # skip first level
						delete_files.extend([join(root,f) for f in files if re.match('.*\.com', f) != None])
						delete_files.extend([join(root,f) for f in files if re.match('.*\.err', f) != None])
						delete_files.extend([join(root,f) for f in files if re.match('.*\.out', f) != None])
						delete_files.extend([join(root,f) for f in files if re.match('.*\.log', f) != None])


	elif job_type == "CtfFind":
		files = os.listdir(join(location,job))
		delete_files.extend([join(location,job,f) for f in files if re.match('gctf.*\.out', f) != None])
		delete_files.extend([join(location,job,f) for f in files if re.match('gctf.*\.err', f) != None])
		# Remove entire subdirectoriy structure
		delete_files.extend([d for d in os.listdir(join(location,job)) if os.path.isdir(d)])

	elif job_type == "AutoPick":
		for root, dirs, files in os.walk(join(location,job), topdown=True):
			if root != join(location,job): # skip first level
				delete_files.extend([join(root,f) for f in files if re.match('.*\.spi', f) != None])


	elif job_type == "Extract":
		if harsh:
			# Just add all subfolders to the list
			delete_files.extend([d for d in os.listdir(join(location,job)) if os.path.isdir(d)])
		else:
			for root, dirs, files in os.walk(join(location,job), topdown=True):
				if root != join(location,job): # skip first level
					delete_files.extend([join(root,f) for f in files if re.match('.*_extract\.star', f) != None])

	elif job_type == "Class2D" or job_type == "Class3D" or job_type == "Refine3D" or job_type == "InitialModel" or job_type == "MultiBody":
		# Retrieve nodes from pipeline
		nodes = readRelionProjectNodes(location)

		# listdir gives unsorted listing, sort the files!
		files = sorted(os.listdir(join(location,job)))

		iteration_files = []
		iteration_files.extend([join(job,f).replace("_data.star","") for f in files if re.match('run_it([0-9]){3}_data.star', f) != None])
		iteration_files.extend([join(job,f).replace("_data.star","") for f in files if re.match('run_ct([0-9]){1}_it([0-9]){3}_data.star', f) != None])
		iteration_files.extend([join(job,f).replace("_data.star","") for f in files if re.match('run_ct([0-9]){2}_it([0-9]){3}_data.star', f) != None])
		iteration_files.extend([join(job,f).replace("_data.star","") for f in files if re.match('run_ct([0-9]){3}_it([0-9]){3}_data.star', f) != None])

		#print("\n\n"+job)
		#print(iteration_files)

		# Go through iteration file prefixes and check if iterations are part of the project nodes
		# Exclude last entry in the list (last iteration which should be kept)
		for iter_file in iteration_files[:-1]:
			
			is_in_pipeline = False
			#print(iter_file)
			for node in nodes:
				#print("\t"+node)
				if node.find(iter_file) == 0:
					is_in_pipeline = True
					#print(iter_file)
					break

			if not is_in_pipeline:
				delete_files.extend([join(location,job,f) for f in files if f.find(iter_file.split("/")[-1]) != -1])
				
	elif job_type == "CtfRefine":
		for root, dirs, files in os.walk(join(location,job), topdown=True):
			if root != join(location,job): # skip first level
				delete_files.extend([join(root,f) for f in files if re.match('.*_wAcc_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_xyAcc_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_aberr-Axx_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_aberr-Axy_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_aberr-Ayy_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_aberr-bx_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_aberr-by_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_mag_optics-group.*\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_fit\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_fit\.eps', f) != None])

	elif job_type == "Polish":
		# TODO: implemet harsh -> remove all *_shiny.star/mrcs files from subfolders
		for root, dirs, files in os.walk(join(location,job), topdown=True):
			if root != join(location,job): # skip first level
				delete_files.extend([join(root,f) for f in files if re.match('.*_FCC_cc\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_FCC_w0\.mrc', f) != None])
				delete_files.extend([join(root,f) for f in files if re.match('.*_FCC_w1\.mrc', f) != None])
				if harsh:
					delete_files.extend([join(root,f) for f in files if re.match('.*_shiny\.mrcs', f) != None])
					delete_files.extend([join(root,f) for f in files if re.match('.*_shiny\.star', f) != None])

	elif job_type == "Subtract":
		if harsh:
			files = os.listdir(join(location,job))
			delete_files.extend([join(location,job,f) for f in files if re.match('subtracted\..*', f) != None])

	elif job_type == "PostProcess":
		files = sorted(os.listdir(join(location,job)))
		delete_files.extend([join(location,job,f) for f in files if re.match('.*masked\.mrc', f) != None])



	# Now distinguish dry run True/False
	if dry:
		if absolute:
			return delete_files
		else:
			# make paths relative by removing location
			return [f.replace(location+"/","") for f in delete_files]
	else:
		# Make delete_files with relative paths
		move_to_trash = [f.replace(location+"/","") for f in delete_files]
		
		for file in move_to_trash:

			file_name = os.path.basename(file)
			trash_path = join(location,"Trash",os.path.dirname(file))
			
			# move
			os.renames(join(location,file), join(location, trash_path, file_name))
		
		return delete_files
