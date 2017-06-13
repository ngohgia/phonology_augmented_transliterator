import os
import sys
import time
import subprocess

from syl_splitter.GetBestRules import train_syl_split
from syl_splitter.ComplementNativeSearchSpace import get_search_space
from TuneModelInterpolation import pick_best_interp
from DecodeWithSingleSearchSpace import decode

if __name__ == '__main__':
  try:
    script, traindev_lex_file, test_input_file, test_output_file, run_dir, t2p_decoder, sclite = sys.argv
  except ValueError:
    print "Syntax: RunTransliterationWrapper.py training_dev_lex_file, test_input_file, test_output_file, run_dir, t2p_decoder sclite"
    sys.exit(1)

traindev_lex_file = os.path.abspath(traindev_lex_file)
test_input_file = os.path.abspath(test_input_file)
test_output_file = os.path.abspath(test_output_file)
run_dir = os.path.abspath(run_dir)
t2p_decoder = os.path.abspath(t2p_decoder)
sclite = os.path.abspath(sclite)

cwd = os.path.abspath(os.getcwd())

print "A. Training syllable splitting"

sylsplit_hyp_file = os.path.join(run_dir, 'traindev_lex_hyp.txt')
train_syl_split(traindev_lex_file, sylsplit_hyp_file, run_dir, t2p_decoder)

searchspace, valid_units = get_search_space(sylsplit_hyp_file)

# Decode on test set
print "########### TRAINING AND DECODING ################"
print "  Training syllable splitting"
decode(cwd, searchspace, valid_units, sylsplit_hyp_file, test_input_file, test_output_file, run_dir, t2p_decoder)
