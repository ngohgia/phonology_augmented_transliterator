import os
import sys
import time
import subprocess

from syl_splitter.ComplementNativeSearchSpace import combine_search_spaces
from syl_splitter.SplitWordForPhoneMappingAlignment import split_words_for_phone_mapping
from syl_splitter.SplitWordWithSearchSpace import split_test_words
from syl_splitter.GetBestRules import train_syl_split
from phone_mapper.phone_mapper import map_phones
from tone_setter.tone_setter import set_tones


if __name__ == '__main__':
  try:
    script, training_lex_path, input_test_path, complement_syl_split_hypothesis_path, output_path, run_dir, t2p_decoder_path = sys.argv
  except ValueError:
    print "Syntax: RunTransliterationWrapper.py \t training_lex_path \t input_test_path \t \tcomplement_syl_split_hypothesis_path\t output_name \t run_dir \t t2p_decoder_path"
    sys.exit(1)

training_lex_path = os.path.abspath(training_lex_path)
input_test_path = os.path.abspath(input_test_path)
complement_syl_split_hypothesis_path = os.path.abspath(complement_syl_split_hypothesis_path)
output_path = os.path.abspath(output_path)
run_dir = os.path.abspath(run_dir)
t2p_decoder_path = os.path.abspath(t2p_decoder_path)

cwd = os.path.abspath(os.getcwd())

# Train syllable splitting
print "1. Training syllable splitting"
native_lex_hyp_path = os.path.join(run_dir, "native_lex_hyp.txt")
train_syl_split(training_lex_path, native_lex_hyp_path, run_dir, t2p_decoder_path)

# Combine search spaces
print "2. Combining syllable splitting"
INTERPOLATION_CONST = 1.0
combined_search_space = combine_search_spaces(native_lex_hyp_path, complement_syl_split_hypothesis_path, INTERPOLATION_CONST)

# Syllable splitting for phone mapping training
print "3. Splitting syllable for phone mapping training"
phone_mapping_lex_hyp_path = os.path.abspath(os.path.join(run_dir, 'lex_hyp_for_phone_mapping.txt'))
split_words_for_phone_mapping(combined_search_space, training_lex_path, phone_mapping_lex_hyp_path, t2p_decoder_path, run_dir)


# Syllable splitting
print "4. Splitting syllable on test data"
os.chdir(cwd)
output_test_file_path = os.path.abspath(os.path.join(run_dir, 'test.split.txt'))
units_and_roles_file_path = os.path.abspath(os.path.join(run_dir, 'test.units_and_roles.txt'))
split_test_words(combined_search_space, input_test_path, output_test_file_path, units_and_roles_file_path, t2p_decoder_path, run_dir)

# Phone mapping
print "5. Phone mapping on test data"
os.chdir(cwd)
map_phones(phone_mapping_lex_hyp_path, units_and_roles_file_path, run_dir, t2p_decoder_path)

# Tone setting
print "6. Setting tones"
os.chdir(cwd)
lex_hyp_for_tone_setting = os.path.join(run_dir, "nucleus-coda_lex_hyp.txt")
toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.txt")
set_tones(lex_hyp_for_tone_setting, toneles_targ_phones_with_roles_path, run_dir, output_path)
