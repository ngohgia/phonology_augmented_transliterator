import os
import os.path as op

lex_file = '/Users/ngohgia/Dropbox/Transliteration/Gia/data/cantonese/original/cantonese_lex.txt'
vowels_file = '/Users/ngohgia/Work/transliteration/cantonese_transliterator/syl_splitter/LangAssets/valid_src_vowels.txt'

vowels = []
with open(vowels_file, 'r') as fh:
  for line in fh:
    vowels.append(line.strip())

lex = []
with open(lex_file, 'r') as lex_fh:
  for line in lex_fh:
    lex.append([part.strip() for part in line.split('\t')])

schwas = []
for entry in lex:
  src = entry[0]
  targ = entry[-1]

  syls = [syl.strip() for syl in targ.split('.')]
  last_syl =  syls[-1]

  tokens = last_syl.split(' ')

  if src[-1] in vowels and len(tokens) == 4:
    new_entry = src[-2:] + '\t' + last_syl
    if new_entry not in schwas:
      schwas.append(new_entry)

for e in schwas:
  print e
