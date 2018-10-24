"""This script creates a PBS file that runs one hyperameter setting."""


training_file = "main.py"
walltime = "06:00:00"
jobname = "gan-visualization"
netid = "zna2"
directory = "~/scratch/mp6/src/part-2/src/"

print "#!/bin/bash"
print "#PBS -l nodes=1:ppn=16:xk"

# Change this if your hyperparameters change
print "#PBS -N {0}".format(jobname)
print "#PBS -l walltime={0}".format(walltime)
print "#PBS -e $PBS_JOBNAME.$PBS_JOBID.err"
print "#PBS -o $PBS_JOBNAME.$PBS_JOBID.out"
print "#PBS -M {0}@illinois.edu".format(netid)

print "cd {0}".format(directory)

print ". /opt/modules/default/init/bash"
print "module load bwpy/2.0.0-pre2"
print "module load cudatoolkit"

# Change this if your hyperameters change
print "aprun -n 1 -N 1 python {0}".format(training_file)
