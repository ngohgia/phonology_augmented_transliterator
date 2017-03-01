import os
import sys
import subprocess
import re
import shutil
import logging
import time

sizes = [100, 200, 300, 400, 500, 600, 700]
iters = [  8,   5,   5,   5,   5,   5,   5]
for j in range(len(sizes)):
  size = sizes[j]
  itr = iters[j]

  curr_data_set = 'size' + str(size) + '_iter' + str(itr)

  root_dir = os.path.join('/home/ngohgia/Work/Cantonese_onset-final_transliterator', 'exp_170301_j-merged', 'size' + str(size), curr_data_set)
  data_dir = os.path.join(root_dir, 'corpus')

  ts = time.strftime("%Y-%m-%d_%H-%M-%S")
  # Working directory
  output_dir = os.path.join(root_dir, 'phono_augmented')
  # run_dir = os.path.join(output_dir, 'run_' + ts)
  run_dir = os.path.join(output_dir, 'run_on_test_dir')
  log_dir = os.path.join(run_dir, 'log')

  if os.path.exists(run_dir):
    shutil.rmtree(run_dir)

  os.makedirs(run_dir)
  os.makedirs(log_dir)

  training_dev_file_path = os.path.join(data_dir, 'train+dev.lex')
  # dev_src_file_path = os.path.join(data_dir, 'dev.src')
  test_src_file_path = os.path.join(data_dir, 'test.lex')
  # output_file_path = os.path.join(run_dir, 'dev.output')
  output_file_path = os.path.join(run_dir, 'test.output')
  path_to_t2p = '/home/ngohgia/Work/utilities/t2p/t2p_dt.pl'


  # Get training, dev, and test files
  def run_exp(training_dev_file_path, test_src_file_path, output_file_path, run_dir, path_to_t2p):
    # Run experiment on the iter data
    command = "python RunTransliterationWrapper.py" + \
         " " + training_dev_file_path + \
         " " + test_src_file_path + \
         " " + output_file_path + \
         " " + run_dir + \
         " " + path_to_t2p
    report("\n[COMMAND]: %s" % command)
    run_shell_command(command)


  # Helper function to run a shell command
  def run_shell_command(command):
    p = subprocess.Popen(command, shell=True)
    p.communicate()

  # Helper function to log and print a message
  def report(msg):
    print "%s" % msg
    logging.info(msg)


  report("")
  report("[RUN DIR]: %s" % run_dir)
  report("[LOG DIR]: %s" % log_dir)

  # RUN!
  run_exp(training_dev_file_path, test_src_file_path, output_file_path, run_dir, path_to_t2p)
