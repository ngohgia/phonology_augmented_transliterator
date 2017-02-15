import os
import sys
import time
import subprocess
import logging


if __name__ == '__main__':
  try:
    script, training_dev_lex_file_path, test_en_file_path, output_file_path, run_dir, t2p_decoder_path = sys.argv
  except ValueError:
    print "Syntax: RunTransliterationWrapper.py \t training_dev_lex_file_path \t test_en_file_path \t output_name \t run_dir \t t2p_decoder_path"
    sys.exit(1)

# Log file
log_dir = os.path.join(run_dir, 'log')
if not os.path.exists(log_dir):
  os.mkdir(log_dir)
log_path = os.path.join(log_dir, 'RunTransliterationWrapper_log.txt')
logging.basicConfig(filename= log_path, level= logging.DEBUG, format='%(message)s')


# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

#Train syllable splitting
command = "python syl_splitter/GetBestRules.py " + \
   training_dev_lex_file_path + " " \
   + run_dir + " " + \
   t2p_decoder_path
report("[COMMAND]: %s" % command)
run_shell_command(command)

# Syllable splitting
hyp_lex_file_path = os.path.join(run_dir, "lex_hyp.txt")
report("[BEST LEX HYP PATH]: %s" % hyp_lex_file_path)
command = "python syl_splitter/SplitWordWithSearchSpace.py" + \
    " " + hyp_lex_file_path + \
    " " + test_en_file_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report("[COMMAND]: %s" % command)
run_shell_command(command)

# Phone mapping
test_units_roles_path = os.path.join(run_dir, "units_roles.txt")
command = "python phone_mapper/phone_mapper.py" + \
    " " + hyp_lex_file_path + \
    " " + test_units_roles_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report(command)
run_shell_command(command)

toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.txt")
with open(output_file_path, 'w') as ofh:
  with open(toneles_targ_phones_with_roles_path, 'r') as tfh:
    for line in tfh:
      parts = [part.strip() for part in line.split('\t')]
      print >> ofh, parts[0]
