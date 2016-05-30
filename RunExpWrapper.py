import os
import sys
import subprocess
import re
import shutil
import logging
import time


if __name__ == '__main__':
  try:
    script, exp_dir, path_to_t2p = sys.argv
  except ValueError:
    print "Syntax: RunExpWrapper.py \
    \n 1. Path to the folder containing the lexicon of the exp_path \
    \n 2. Path to t2p decoder folder"
    sys.exit(1)

# Initialize absolute paths to necessary folders
exp_path = os.path.abspath(exp_dir)
path_to_t2p = os.path.abspath(path_to_t2p)

ts = time.strftime("%Y-%m-%d_%H-%M-%S")
# Log file
log_file = os.path.join(exp_path, "log__" + ts)
logging.basicConfig(filename= log_file, level= logging.DEBUG, format='%(message)s')
logging.info("\n--------------------------- NEW EXPERIMENT -----------------------------")

output_dir_path = "2015-02-14_02-43-04"
  
# Look for "Proposed" folder
def run_exp(exp_path):
  for fname in os.listdir(exp_path):
    model_path = os.path.join(exp_path, fname)
    if fname == "Proposed" and os.path.isdir(model_path):
      report("[MODEL FOLDER] %s" % fname)
      run_on_proposed_model(model_path)

# Run experiment on the data of the Proposed model
def run_on_proposed_model(model_path):
  for fname in os.listdir(model_path):
    subcorpus_path = os.path.join(model_path, fname)
    if os.path.isdir(subcorpus_path) and fname != "outputs":
      report("[SUBCORPUS FOLDER] %s" % fname)
      output_dir_path = "/".join(subcorpus_path.split("/")[:-1]) + "/outputs"
      if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

      run_on_one_set(subcorpus_path, output_dir_path)

# Run exp on each set
def run_on_one_set(set_path, output_dir_path):
  for fname in os.listdir(set_path):
    iter_path = os.path.join(set_path, fname)
    if os.path.isdir(iter_path):
      report("[ITER FOLDER]: %s" % fname)
      run_on_one_iter(iter_path, output_dir_path)

# Get training, dev, and test files
def run_on_one_iter(iter_path, output_dir_path):
  [training_dev_lex, test_en, test_vie] = ["", "", ""]

  for fname in os.listdir(iter_path):
    curr_folder = os.path.join(iter_path, fname)
    if os.path.isdir(curr_folder):
      if fname == "training_dev":
        report("[TRAINING_DEV FOLDER]: %s" % fname)
        training_dev_lex = get_lex_file(curr_folder)
      elif fname == "test":
        report("[TEST FOLDER]: %s" % fname)
        [test_en, test_vie] = get_en_vie_files(curr_folder)

  output_file_path = output_dir_path + "/" + test_en.split("/")[-1].split(".")[0]
  print "OUTPUT PATH " + output_file_path

  # Run experiment on the iter data
  command = "python RunTransliterationWrapper.py" + \
       " " + training_dev_lex + \
       " " + test_en + \
       " " + output_file_path + \
       " "  + path_to_t2p + \
       " "  + log_file
  report(command)
  run_shell_command(command)


# Get .lex file from the source_path
def get_lex_file(source_path):
  lex_file_path = ""
  for fname in os.listdir(source_path):
    if fname.split(".")[-1] == "lex":
      lex_file_path = os.path.join(source_path, fname)
  return lex_file_path

# Get .en and .vie file from the source_path
def get_en_vie_files(source_path):
  en_file_path = ""
  vie_file_path = ""
  for fname in os.listdir(source_path):
    if fname.split(".")[-1] == "en":
      en_file_path = os.path.join(source_path, fname)
    elif fname.split(".")[-1] == "vie":
      vie_file_path = os.path.join(source_path, fname)
  return [en_file_path, vie_file_path]

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)


run_exp(exp_path)