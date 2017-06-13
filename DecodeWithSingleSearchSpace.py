import os
import sys
import time
import subprocess

from syl_splitter.SplitWordForPhoneMappingAlignment import split_words_for_phone_mapping
from syl_splitter.SplitWordWithSearchSpace import split_test_words
from syl_splitter.GetBestRules import train_syl_split
from phone_mapper.phone_mapper import map_phones
from phone_mapper.final_splitter import train_final_splitting
from phone_mapper.final_splitter import split_final
from tone_setter.tone_setter import set_tones

def decode(cwd, searchspace, valid_units, lex_hyp_file, input_file, output_file, run_dir, t2p_decoder):
  print "  1. Train final splitting"
  onc_hyp_file = os.path.join(run_dir, 'traindev_lex_hyp.onc.txt')
  final_splitting_model = train_final_splitting(lex_hyp_file, onc_hyp_file, run_dir)
  # for e in final_splitting_model[0]:
  #   print str(e) + ": " + str(final_splitting_model[0][e])
  # sys.exit(1)

  # Syllable splitting
  print "  2. Splitting syllable into initial-final on test data"
  os.chdir(cwd)
  init_final_test_file_path = os.path.abspath(os.path.join(run_dir, 'test.init-final.split.txt'))
  init_final_with_roles_file_path = os.path.abspath(os.path.join(run_dir, 'test.initi-final.units_and_roles.txt'))
  split_test_words(searchspace, valid_units, input_file, init_final_test_file_path, init_final_with_roles_file_path, t2p_decoder, run_dir)
  
  # ONCd splitting
  print "  3. Splitting final into ONCd on test data"
  onc_with_roles_file_path = os.path.abspath(os.path.join(run_dir, 'test.onc.units_and_roles.txt'))
  split_final(init_final_with_roles_file_path, final_splitting_model, onc_with_roles_file_path)

  # Phone mapping
  print "  4. Phone mapping on test data"
  os.chdir(cwd)
  map_phones(onc_hyp_file, onc_with_roles_file_path, run_dir, t2p_decoder)

  # Tone setting
  print "  5. Setting tones"
  os.chdir(cwd)
  toneles_targ_phones_with_roles_path = os.path.join(run_dir, "test.toneless_with_roles.txt")
  set_tones(onc_hyp_file, toneles_targ_phones_with_roles_path, run_dir, output_file)
