#!/usr/bin/python
import os, subprocess, sys, shlex, math
import os.path as op
import pdb
import time, datetime

ALL_SIZES = [100, 200, 300, 400, 500, 600, 700]
ALL_SETS =  [  8,   5,   5,   5,   5,   5,   5]
ITR_COUNT = 5
# ALL_SIZES = [100]
# ALL_SETS =  [  1]
# ITR_COUNT = 1

sclite_path = '/data/users/ngohgia/data_drive/transliterator/utilities/sclite/sclite'
scorer_dir = '/data/users/ngohgia/data_drive/translit_scorer'
FNULL = open(os.devnull, 'w')

def main():
  exp_dir = op.join(os.getcwd(), 'exp_170421')

  for j in range(len(ALL_SIZES)):
    size = ALL_SIZES[j]
    sets = ALL_SETS[j]

    outputs = []
    refs = []

    root = op.join(exp_dir, 'size' + str(size))
    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
    output_file = op.join(root, 'PhonoAugmented_size' + str(size) + '_' + ts + '_on_dev.csv')
    with open(output_file, 'w') as output_filehandler:
      for i in xrange(1, sets + 1):
        set_name = 'size{0}_set{1}'.format(size, i)
        for k in xrange(1, ITR_COUNT+1):
          fname = 'size{0}_set{1}_itr{2}'.format(size, i, k)
          subfolder = op.join(root, set_name, fname)
          result = consolidate_outputs(subfolder, outputs, refs)

    if len(outputs) != len(refs):
      print "Mismatched number of entries"
      sys.exit(1)

    all_refs_file = op.join(root, 'all_size' + str(size) + '_test.ref')
    all_outputs_file = op.join(root, 'all_size' + str(size) + '_test.hyp')

    with open(all_refs_file, 'w') as rfh, open(all_outputs_file, 'w') as ofh:
      for i in xrange(1, len(outputs)+1):
        num = '\t(' + str(i) + ')'
        print >> rfh, refs[i-1] + num
        print >> ofh, outputs[i-1] + num

    report_dir = op.join(root, 'scorer_reports_size' + str(size))
    if not os.path.exists(report_dir):
      os.mkdir(report_dir)
    score(all_outputs_file, all_refs_file, report_dir)


def consolidate_outputs(cwd, outputs, refs):
  MERGER = '-'

  run_dir = op.join(cwd, 'phono_augmented', 'run_on_test_dir')
  orig_ref_file = op.join(cwd, 'test.ref')
  with open(orig_ref_file, 'r') as i_fh:
    for line in i_fh:
      parts = [part.strip() for part in line.split('\t')]
      curr_entry = parts[0]
      refs.append(curr_entry.replace(MERGER, ' '))

  result = []

  orig_output_file = op.join(run_dir, 'test.hyp')
  with open(orig_output_file, 'r') as i_fh:
    for line in i_fh:
      parts = [part.strip() for part in line.split('\t')]
      curr_entry = parts[0]
      outputs.append(curr_entry.replace(MERGER, ' '))

  return outputs, refs


def score(hyp_path, ref_path, report_dir):
  scorer_path = op.join(scorer_dir, 'TranslitScorer.py')
  ref_lang_specs = op.join(scorer_dir, 'CantoneseLang', 'cantonese_lang_specs.txt')
  report_path = op.join(report_dir, 'reports')
  subprocess.Popen(['python', scorer_path, hyp_path, ref_path, report_dir, report_path, ref_lang_specs, sclite_path]).communicate()


if __name__ == '__main__':
  main()
