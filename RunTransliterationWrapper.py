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
log_path = os.path.join(run_dir, 'log', 'RunTransliterationWrapper_log.txt')
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

# # Syllable splitting
lex_hyp_file_path = os.path.join(run_dir, "lex_hyp.txt")
report("[BEST LEX HYP PATH]: %s" % lex_hyp_file_path)
command = "python syl_splitter/SplitWordWithSearchSpace.py" + \
    " " + lex_hyp_file_path + \
    " " + test_en_file_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report("[COMMAND]: %s" % command)
run_shell_command(command)

# Phone mapping
test_units_roles_path = os.path.join(run_dir, "units_roles.txt")
command = "python phone_mapper/phone_mapper.py" + \
    " " + lex_hyp_file_path + \
    " " + test_units_roles_path + \
    " " + t2p_decoder_path
report(command)
run_shell_command(command)

# Tone setting
toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.output.txt")
command = "python tone_setter/tone_setter.py" +  \
    " " + lex_hyp_file_path + \
    " " + toneles_targ_phones_with_roles_path + \
    " " + output_name
report(command)
run_shell_command(command)
