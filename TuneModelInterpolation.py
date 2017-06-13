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
from DecodeWithCombinedSearchSpace import decode

INTERP_CONSTANTS = [0.0, 0.01, 0.1, 0.3, 0.5, 0.7, 1.0]
# INTERP_CONSTANTS = [0.0, 0.5, 1.0]
# INTERP_CONSTANTS = [0.5, 1.0]

def score(output_file, ref_file, run_dir, sclite):
  MERGER = '-'
  hyp_file = output_file + '.hyp'
  clean_ref_file = os.path.join(run_dir, ref_file + '.clean')

  with open(ref_file, 'r') as ref_fh, open(clean_ref_file, 'w') as clean_ref_fh:
    for line in ref_fh:
      clean_ref_fh.write(line.replace(MERGER, ' ')) 

  with open(output_file, 'r') as output_fh, open(hyp_file, 'w') as hyp_fh:
    count = 1
    for line in output_fh:
      line = line.strip()
      hyp_fh.write("\t".join([line.replace(MERGER, ' '), '(' + str(count) + ')']) + "\n")
      count = count + 1

  report_file = os.path.join(run_dir, 'sclite_report.dtl')
  print " ".join([sclite, '-h', hyp_file, '-r', clean_ref_file, '-i', 'wsj', '-o', 'dtl', '-n', 'sclite_report'])
  subprocess.Popen([sclite, '-h', hyp_file, '-r', clean_ref_file,
        '-i', 'wsj', '-o', 'dtl', '-n', 'sclite_report'], stdout=open(os.devnull, 'w')).communicate()
  temp, err = subprocess.Popen(['grep', 'Total Error', report_file], stdout=subprocess.PIPE).communicate()
  temp = temp.replace(' ', '')
  wer = temp[ temp.find('=')+1 : temp.find('%') ]
  temp, err = subprocess.Popen(['grep', 'with errors', report_file], stdout=subprocess.PIPE).communicate()
  temp = temp.replace(' ', '')
  ser = temp[ temp.find('s')+1 : temp.find('%') ]

  return wer, ser

def pick_best_interp(cwd, training_lex_path, input_file, ref_file, native_search_space, complement_search_space, run_dir, t2p_decoder, sclite_path):
  tuning_log = os.path.join(run_dir, 'tuning.log')

  best_interp = 0
  best_ser = 1000
  best_wer = 1000
  with open(tuning_log, 'w') as tuning_fh:
    for interp in INTERP_CONSTANTS:
      interp_run_dir = os.path.join(run_dir, 'interp' + str(interp))
      if not os.path.exists(interp_run_dir):
        os.makedirs(interp_run_dir)
      
      dev_output_file = os.path.join(interp_run_dir, 'dev_interp' + str(interp) + '.output')

      decode(cwd, training_lex_path, input_file, dev_output_file, native_search_space, complement_search_space, interp, interp_run_dir, t2p_decoder)
      wer, ser = score(dev_output_file, ref_file, interp_run_dir, sclite_path)

      tuning_fh.write(' '.join([str(item) for item in [interp, wer, ser]]) + "\n")
      if ser < float(best_ser):
        best_ser, best_wer = ser, wer
        best_interp = interp
      elif ser == float(best_ser):
        if ter < float(best_wer):
          best_ser, best_wer = ser, wer
          best_interp = interp
  
  return best_interp
