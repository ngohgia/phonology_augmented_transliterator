import os
import os.path as op

sizes =     [100, 200, 500, 1000, 2000, 3000, 4000, 5000, 6000]
num_iters = [79,   40,  16,    8,    5,    5,    5,    5,    5]

for i in range(len(sizes)):
  size = sizes[i]
  for itr in range(1, num_iters[i]+1):
    corpus_dir = op.join('/home/ngohgia/Work/NEWS2016_EnKor/data_for_exp', 'size' + str(size), 'size' + str(size) + '_iter' + str(itr), 'corpus')
    train_dev_file = op.join(corpus_dir, 'train+dev.lex')
    train_file = op.join(corpus_dir, 'train.lex')
    dev_file = op.join(corpus_dir, 'dev.lex')

    with open(train_dev_file, 'w') as td_fh:
      with open(train_file, 'r') as t_fh:
        for line in t_fh:
          print >> td_fh, line.strip()

    with open(train_dev_file, 'a') as td_fh:
      with open(dev_file, 'r') as d_fh:
        for line in d_fh:
          print >> td_fh, line.strip()
