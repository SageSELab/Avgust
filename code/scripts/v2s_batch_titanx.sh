#!/bin/bash
#
#SBATCH --job-name=v2s_detail
#SBATCH --output=./logs/detail_%j.txt  # output file
#SBATCH -e ./logs/detail_%j.err        # File to which STDERR will be written
#SBATCH --partition=titanx-long    # Partition to submit to 
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --time=7-00:00:00         # Maximum runtime in D-HH:MM
#SBATCH --mem=64GB

exec_v2s --config="/mnt/nfs/work1/XXX/XXXzhao/video2scenario/config_files/v2s_config_detail.json"