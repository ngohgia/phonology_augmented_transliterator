#!/usr/bin/python
import os, subprocess, sys, shlex, math
import os.path as op
import pdb
import time, datetime

size = 1000
iterations = range(1, 6)
sclite='/Users/ngohgia/Work/transliteration/utilities/sclite'
FNULL = open(os.devnull, 'w')

def main():
    root = op.join(os.getcwd(), 'exp_170214', 'size' + str(size));
    output_file = op.join(root, 'phono_augmented_report.csv')
    # try:
    for i in iterations:
        fname = 'size{0}_iter{1}'.format(size, i)
        subfolder = op.join(root, fname)
        result = score(subfolder)
        with open(output_file, 'a') as output_filehandler:
            print >> output_filehandler, ','.join(['PhonoAugmented ' + fname] + [str(a) for a  in result])
    # except Exception as ex:
    #     template = "An exception of type {0} occured. Arguments:\n{1!r}"
    #     message = template.format(type(ex).__name__, ex.args)
    #     print message

def score(cwd):
    test_file = op.join(cwd, 'corpus', 'test.lex')
    ref_file = op.join(cwd, 'test.ref')
    run_dir = op.join(cwd, 'phono_augmented', 'run_dir')

    result = []

    output_file = op.join(run_dir, 'test.output')
    hyp_file = op.join(run_dir, 'test.hyp')

    with open(hyp_file, 'w') as hyp_filehandler, open(output_file, 'r') as output_filehandler:
        index = 0
        for line in output_filehandler:
            print >> hyp_filehandler, line.strip() + '\t({0})'.format(index+1)
            index += 1

    report_file = op.join(run_dir, 'sclite_report.dtl')
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
