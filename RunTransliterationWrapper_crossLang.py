import os
import sys
import time
import subprocess

from syl_splitter.GetBestRules import train_syl_split
from syl_splitter.ComplementNativeSearchSpace import get_search_space
from TuneModelInterpolation import pick_best_interp
from DecodeWithCombinedSearchSpace import decode

if __name__ == '__main__':
  try:
    script, training_lex_file, trainingdev_lex_file, test_input_file, test_output_file, dev_input_file, dev_ref_file, complementary_sylsplit_hyp_file, run_dir, t2p_decoder, sclite = sys.argv
  except ValueError:
    print "Syntax: RunTransliterationWrapper.py training_lex_file, test_input_file, test_output_file, dev_input_file, dev_output_file, dev_ref_file, complement_sylsplit_hy_file, run_dir, t2p_decoder"
    sys.exit(1)

training_lex_file = os.path.abspath(training_lex_file)
trainingdev_lex_file = os.path.abspath(trainingdev_lex_file)
test_input_file = os.path.abspath(test_input_file)
test_output_file = os.path.abspath(test_output_file)
dev_input_file = os.path.abspath(dev_input_file)
dev_ref_file = os.path.abspath(dev_ref_file)
complementary_sylsplit_hyp_file = os.path.abspath(complementary_sylsplit_hyp_file)
run_dir = os.path.abspath(run_dir)
t2p_decoder = os.path.abspath(t2p_decoder)
sclite = os.path.abspath(sclite)

cwd = os.path.abspath(os.getcwd())

# Train syllable splitting
print "########### TRAINING AND TUNING ################"
print "A. Training syllable splitting"
tuning_run_dir = os.path.join(run_dir, 'tuning')
if not os.path.exists(tuning_run_dir):
  os.makedirs(tuning_run_dir)

native_sylsplit_hyp_file = os.path.join(tuning_run_dir, "native_lex_hyp.txt")
train_syl_split(training_lex_file, native_sylsplit_hyp_file, tuning_run_dir, t2p_decoder)

# Tune interpolation constants
print "B. Tuning interpolation constants"
native_search_space = get_search_space(native_sylsplit_hyp_file)
complement_search_space = get_search_space(complementary_sylsplit_hyp_file)
interp = pick_best_interp(cwd, training_lex_file, dev_input_file, dev_ref_file, native_search_space, complement_search_space, tuning_run_dir, t2p_decoder, sclite)

# Decode on test set
print "########### TRAINING AND DECODING ################"
print "  Training syllable splitting"
traindev_native_sylsplit_hyp_file = os.path.join(run_dir, "traindev_native_lex_hyp.txt")
train_syl_split(trainingdev_lex_file, traindev_native_sylsplit_hyp_file, run_dir, t2p_decoder)
traindev_native_search_space = get_search_space(traindev_native_sylsplit_hyp_file)

decode(cwd, trainingdev_lex_file, test_input_file, test_output_file, traindev_native_search_space, complement_search_space, interp, run_dir, t2p_decoder)
