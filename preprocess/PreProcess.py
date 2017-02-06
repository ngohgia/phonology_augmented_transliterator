SYL_DELIM = ' . '
replaced_syls = { 'e r _3': 'NULL_O e-r _3',
                  'e n _1': 'NULL_O e-n _1' }

def replace_syllables(raw_training_lex):
  training_lex = []
  for entry in raw_training_lex:
    src_word = entry[0]
    targ_word = entry[-1]

    targ_syls = [syl.strip() for syl in targ_word.split(SYL_DELIM)]
    new_targ_syls = []
    for syl in targ_syls:
      if syl in replaced_syls:
        new_targ_syls.append(replaced_syls[syl])
      else:
        new_targ_syls.append(syl)
    new_targ_word = SYL_DELIM.join(new_targ_syls)
    training_lex.append([src_word, new_targ_word])

  return training_lex
