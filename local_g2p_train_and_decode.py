#!/usr/bin/python
import os, subprocess, sys, shlex, math
import os.path as op
import pdb
import time, datetime

size = 100
order = 6
iterations = 5
g2p='/home/ngohgia/Work/g2p/g2p.py'
sclite='/home/ngohgia/Work/utilities/sclite/sclite'
FNULL = open(os.devnull, 'w')

def main():
    root = op.join(os.getcwd(), 'exp_170221');
    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
    output_file = op.join(root, 'report' + ts + '.csv')
    # try:
    for i in xrange(1, iterations + 1):
        sizefolder = 'size{0}'.format(size)
        fname = 'size{0}_iter{1}'.format(size, i)
        subfolder = op.join(root, sizefolder, fname)
        result = run_experiment(order, subfolder)
        with open(output_file, 'a') as output_filehandler:
            print >> output_filehandler, ','.join(['g2p ' + fname] + [str(a) for a  in result])
    # except Exception as ex:
    #     template = "An exception of type {0} occured. Arguments:\n{1!r}"
    #     message = template.format(type(ex).__name__, ex.args)
    #     print message

def run_experiment(order, cwd):
    train_file = op.join(cwd, 'corpus', 'train+dev.lex')
    test_file = op.join(cwd, 'corpus', 'test.lex')
    ref_file = op.join(cwd, 'test.ref')

    modelFolder = op.join(cwd, 'g2p_model')
    if not os.path.exists(modelFolder):
        os.mkdir(modelFolder)
    result = []

    for M in xrange(1, order + 1):
        modelFile = op.join(modelFolder, '{0}-gram-g2p.jsm'.format(M))
        output_file = op.join(cwd, '{0}-gram-g2p.out'.format(M))
        hyp_file = op.join(cwd, '{0}-gram-g2p.hyp'.format(M))

        if M > 1:
            prevModelFile = op.join(modelFolder, '{0}-gram-g2p.jsm'.format(M-1))
            init = ["-m", prevModelFile , "-r"]
        else:
            init = []
        params = ['-t', train_file, '-d 25%', '-n', modelFile]
        subprocess.Popen(['python', g2p] + init + params , stdout=FNULL, stderr=FNULL).communicate()

        with open(hyp_file, 'w') as hyp_filehandler, open(output_file, 'w') as output_filehandler:
            out, err = subprocess.Popen(['python', g2p, '-m', modelFile, '-a', test_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print >> output_filehandler, out
            lines = [l.split('\t')[1] for l in out.split('\n') if len(l) > 0]
            failures = set([l[l.find('"')+1:l.rfind('"')] for l in err.split('\n')[:-2] if len(l) > 0])
            entries = []
            index = 0
            lookup = [l.strip() for l in open(test_file).readlines()]
            for i in xrange(len(lookup)):
                if lookup[i] in failures:
                    entries.append('')
                else:
                    entries.append(lines[index])
                    index += 1
            print >> hyp_filehandler, '\n'.join([entries[i] + ' ({0})'.format(i+1) for i in xrange(len(entries))])
            if len(failures) > 0:
                print len(failures), 'failures:', ' '.join(failures)

        report_name = '{0}-gram_report'.format(M)
        report_file = op.join(cwd, report_name + '.dtl')
        subprocess.Popen([sclite, '-h', hyp_file, '-r', ref_file,
              '-i', 'wsj', '-o', 'dtl', '-n', report_name], stdout=open(os.devnull, 'w')).communicate()
        temp, err = subprocess.Popen(['grep', 'Total Error', report_file], stdout=subprocess.PIPE).communicate()
        temp = temp.replace(' ', '')
        wer = temp[ temp.find('=')+1 : temp.find('%') ]
        temp, err = subprocess.Popen(['grep', 'with errors', report_file], stdout=subprocess.PIPE).communicate()
        temp = temp.replace(' ', '')
        ser = temp[ temp.find('s')+1 : temp.find('%') ]
        if M == order:
            result.append(wer)
            result.append(ser)

        print "Finish " + str(M) + "-gram"
    return result


if __name__ == '__main__':
    main()
