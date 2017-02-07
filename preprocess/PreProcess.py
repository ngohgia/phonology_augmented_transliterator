SYL_DELIM = ' . '
replaced_syls = { 'e r _3': 'NULL_O e-r _3',
                  'e n _1': 'NULL_O e-n _1' }

def preprocess(raw_training_lex):
  training_lex = []
  for entry in raw_training_lex:
    src_word = entry[0]
    targ_word = entry[-1]

    targ_syls = [syl.strip() for syl in targ_word.split(SYL_DELIM)]
    new_targ_syls = []
    for syl in targ_syls:
      new_syl = replace_syllable(syl)
      new_syl = attach_coda_to_nucleus(new_syl)

      new_targ_syls.append(new_syl)
    new_targ_word = SYL_DELIM.join(new_targ_syls)
    training_lex.append([src_word, new_targ_word])

  return training_lex

def replace_syllable(syl):
  if syl in replaced_syls:
    return replaced_syls[syl]
  return syl

def attach_coda_to_nucleus(syl):
  units = syl.split()
  new_units = []

  if units[-2] == 'n' or units[-2] == 'ng' or units[-2] == 'm':
    new_nucleus = units[-3] + '$' + units[-2]
    new_units += units[:-3]
    new_units.append(new_nucleus)
    new_units.append(units[-1])
    new_syl = ' '.join(new_units)
  else:
    new_syl = syl

  return new_syl

### DEBUG ######
print attach_coda_to_nucleus('e n _2')
print attach_coda_to_nucleus('k e ng _3')
print replace_syllable('e r _3')
