import os
import sys
import subprocess
import re
import shutil
import logging
import time


if __name__ == '__main__':
  try:
    script, data_dir, output_dir, base_name, path_to_t2p = sys.argv
  except ValueError:
    print "Syntax: RunExpWrapper.py \
    \n 1. Data path \
    \n 2. Output path \
    \n 3. Base name \
    \n 4. t2p decoder directory"
    sys.exit(1)


ts = time.strftime("%Y-%m-%d_%H-%M-%S")
# Run directory
run_dir = os.path.join(output_dir, 'run_' + ts)
log_dir = os.path.join(run_dir, 'log')
os.makedirs(run_dir)
os.makedirs(log_dir)




# Get training, dev, and test files
def run_exp(data_dir, output_dir):
  [training_dev_lex_path, test_graph_file_path, test_phon_file_path] = ["", "", ""]

  for fname in os.listdir(data_dir):
    curr_folder = os.path.join(data_dir, fname)
    if os.path.isdir(curr_folder):
      if fname == "training_dev":
        training_dev_lex_path = get_src_lex_file_path(curr_folder)
        report("[TRAINING_DEV PATH]: %s" % training_dev_lex_path)
      elif fname == "test":
        [test_graph_file_path, test_phon_file_path] = get_test_graph_phon_file_path(curr_folder)
        report("[TEST GRAPH PATH]: %s" % test_graph_file_path)
        report("[TEST PHON PATH]: %s" % test_phon_file_path)

  output_file_path = os.path.join(output_dir, base_name + '.targ.test.txt')
  report("[OUTPUT PATH]: %s" % output_file_path)

  # Run experiment on the iter data
  command = "python RunTransliterationWrapper.py" + \
       " " + training_dev_lex_path + \
       " " + test_graph_file_path + \
       " " + output_file_path + \
       " " + run_dir + \
       " " + path_to_t2p
  report("\n[COMMAND]: %s" % command)
  run_shell_command(command)


# Get .lex file from the data_dir
def get_src_lex_file_path(data_dir):
  lex_file_path = ""
  for fname in os.listdir(data_dir):
    if "lex" in fname:
      lex_file_path = os.path.abspath(os.path.join(data_dir, fname))
  return lex_file_path

# Get graphemes and phonemes file from the data_dir
def get_test_graph_phon_file_path(data_dir):
  targ_graph_file_path = ""
  targ_phon_file_path = ""
  for fname in os.listdir(data_dir):
    if "src.txt" in fname:
      targ_graph_file_path = os.path.abspath(os.path.join(data_dir, fname))
    elif "targ.phonemes.txt" in fname:
      targ_phon_file_path = os.path.abspath(os.path.join(data_dir, fname))
  return [targ_graph_file_path, targ_phon_file_path]

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
run_exp(data_dir, output_dir)
