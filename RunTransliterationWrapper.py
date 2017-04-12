import os
import sys
import time
import subprocess
import logging


if __name__ == '__main__':
  try:
    script, phone_mapping_train_dev_file_path, test_en_file_path, syl_split_lex_hyp_file_path, output_file_path, run_dir, t2p_decoder_path = sys.argv
  except ValueError:
    print "Syntax: RunTransliterationWrapper.py \t phone_mapping_train_dev_file_path \t test_en_file_path \t \tsyl_split_lex_hyp_file_path\t output_name \t run_dir \t t2p_decoder_path"
    sys.exit(1)

# Log file
log_dir = os.path.join(run_dir, 'log')
if not os.path.exists(log_dir):
  os.mkdir(log_dir)
log_path = os.path.join(log_dir, 'RunTransliterationWrapper_log.txt')
logging.basicConfig(filename= log_path, level= logging.DEBUG, format='%(message)s')

syl_split_lex_hyp_dir = '/home/ngohgia/Work/VietCantonese_fusion_transliterator/hcmus_syl_splitting_model'

# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

#Train syllable splitting
# command = "python syl_splitter/GetBestRules.py " + \
#    phone_mapping_train_dev_file_path + " " \
#    + run_dir + " " + \
#    t2p_decoder_path
# report("[COMMAND]: %s" % command)
# run_shell_command(command)

# Syllable splitting for phone mapping training
report("[SYLLABLE SPLITTING LEX HYP PATH]: %s" % syl_split_lex_hyp_file_path)
command = "python syl_splitter/SplitWordForPhoneMappingAlignment.py" + \
    " " + syl_split_lex_hyp_file_path + \
    " " + phone_mapping_train_dev_file_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report("[COMMAND]: %s" % command)
run_shell_command(command)

# Syllable splitting
report("[SYLLABLE SPLITTING LEX HYP PATH]: %s" % syl_split_lex_hyp_file_path)
command = "python syl_splitter/SplitWordWithSearchSpace.py" + \
    " " + syl_split_lex_hyp_file_path + \
    " " + test_en_file_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report("[COMMAND]: %s" % command)
run_shell_command(command)

# Phone mapping
hyp_lex_file_path = os.path.join(run_dir, "lex_hyp.txt")
test_units_roles_path = os.path.join(run_dir, "units_roles.txt")
command = "python phone_mapper/phone_mapper.py" + \
    " " + hyp_lex_file_path + \
    " " + test_units_roles_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report(command)
run_shell_command(command)

# Tone setting
lex_hyp_for_tone_setting = os.path.join(run_dir, "nucleus-coda_lex_hyp.txt")
toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.txt")
command = "python tone_setter/tone_setter.py" +  \
    " " + lex_hyp_for_tone_setting + \
    " " + toneles_targ_phones_with_roles_path + \
    " " + run_dir + \
    " " + output_file_path
report(command)
run_shell_command(command)
