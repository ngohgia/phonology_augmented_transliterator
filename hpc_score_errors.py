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

sclite='/data/users/ngohgia/data_drive/transliterator/utilities/sclite/sclite'
FNULL = open(os.devnull, 'w')

def main():
  for j in range(len(ALL_SIZES)):
    size = ALL_SIZES[j]
    sets = ALL_SETS[j]

    root = op.join(os.getcwd(), 'exp_170403', 'size' + str(size));
    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
    output_file = op.join(root, 'PhonoAugmented_size' + str(size) + '_' + ts + '_on_dev.csv')
    with open(output_file, 'w') as output_filehandler:
      for i in xrange(1, sets + 1):
        set_name = 'size{0}_set{1}'.format(size, i)
        for k in xrange(1, ITR_COUNT+1):
          fname = 'size{0}_set{1}_itr{2}'.format(size, i, k)
          subfolder = op.join(root, set_name, fname)
          result = score(subfolder)
          print >> output_filehandler, ','.join(['PhonoAugmented ' + fname] + [str(a) for a  in result])

def score(cwd):
    MERGER = '-'

    run_dir = op.join(cwd, 'phono_augmented', 'run_on_dev_dir')
    orig_ref_file = op.join(cwd, 'corpus', 'dev.ref')
    # ref_file = op.join(cwd, 'corpus', 'dev.ref')
    ref_file = op.join(cwd, 'corpus', 'dev_for_scoring.ref')
    with open(orig_ref_file, 'r') as i_fh:
      with open(ref_file, 'w') as o_fh:
        for line in i_fh:
          o_fh.write(line.replace(MERGER, ' '))

    result = []

    orig_output_file = op.join(run_dir, 'dev.output')
    output_file = op.join(run_dir, 'dev_for_scoring.output')
    # output_file = op.join(run_dir, 'dev.output')
    with open(orig_output_file, 'r') as i_fh:
      with open(output_file, 'w') as o_fh:
        for line in i_fh:
          o_fh.write(line.replace(MERGER, ' '))

    hyp_file = op.join(run_dir, 'dev.hyp')

    with open(hyp_file, 'w') as hyp_filehandler, open(output_file, 'r') as output_filehandler:
        index = 0
        for line in output_filehandler:
            print >> hyp_filehandler, line.strip() + '\t({0})'.format(index+1)
            index += 1

    report_file = op.join(run_dir, 'sclite_report.dtl')
    # print(' '.join([sclite, '-h', hyp_file, '-r', ref_file,
    #       '-i', 'wsj', '-o', 'dtl', '-n', 'sclite_report']))
    subprocess.Popen([sclite, '-h', hyp_file, '-r', ref_file,
          '-i', 'wsj', '-o', 'dtl', '-n', 'sclite_report'], stdout=open(os.devnull, 'w')).communicate()
    temp, err = subprocess.Popen(['grep', 'Total Error', report_file], stdout=subprocess.PIPE).communicate()
    temp = temp.replace(' ', '')
    wer = temp[ temp.find('=')+1 : temp.find('%') ]
    temp, err = subprocess.Popen(['grep', 'with errors', report_file], stdout=subprocess.PIPE).communicate()
    temp = temp.replace(' ', '')
    ser = temp[ temp.find('s')+1 : temp.find('%') ]

    result.append(wer)
    result.append(ser)

    return result


if __name__ == '__main__':
    main()
