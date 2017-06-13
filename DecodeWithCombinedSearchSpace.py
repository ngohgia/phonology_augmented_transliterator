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

def decode(cwd, training_lex_path, input_file, output_file, native_search_space, complement_search_space, interp_const, run_dir, t2p_decoder):
  # Combine search spaces
  print "  1. Combining syllable splitting"
  combined_search_space = combine_search_spaces(native_search_space, complement_search_space, interp_const)

  # Syllable splitting for phone mapping training
  print "  2. Splitting syllable for phone mapping training"
  phone_mapping_lex_hyp_path = os.path.abspath(os.path.join(run_dir, 'lex_hyp_for_phone_mapping.txt'))
  split_words_for_phone_mapping(combined_search_space, training_lex_path, phone_mapping_lex_hyp_path, t2p_decoder, run_dir)


  # Syllable splitting
  print "  3. Splitting syllable on test data"
  os.chdir(cwd)
  output_test_file_path = os.path.abspath(os.path.join(run_dir, 'test.split.txt'))
  units_and_roles_file_path = os.path.abspath(os.path.join(run_dir, 'test.units_and_roles.txt'))
  split_test_words(combined_search_space, input_file, output_test_file_path, units_and_roles_file_path, t2p_decoder, run_dir)

  # Phone mapping
  print "  4. Phone mapping on test data"
  os.chdir(cwd)
  map_phones(phone_mapping_lex_hyp_path, units_and_roles_file_path, run_dir, t2p_decoder)

  # Tone setting
  print "  5. Setting tones"
  os.chdir(cwd)
  lex_hyp_for_tone_setting = os.path.join(run_dir, "nucleus-coda_lex_hyp.txt")
  toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.txt")
  set_tones(lex_hyp_for_tone_setting, toneles_targ_phones_with_roles_path, run_dir, output_file)
