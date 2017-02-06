SYL_DELIM = ' . '
replaced_syls = { 'NULL_O e-r _3': 'e r _3',
                  'NULL_O e-n _1': 'e n _1' }

def replace_syllables(raw_output):
  outputs = []

  for entry in raw_output:
    targ_syls = [syl.strip() for syl in entry.split(SYL_DELIM)]
    new_targ_syls = []
    for syl in targ_syls:
      if syl in replaced_syls:
        new_targ_syls.append(replaced_syls[syl])
      else:
        new_targ_syls.append(syl)
    new_targ_word = SYL_DELIM.join(new_targ_syls)
    outputs.append(new_targ_word)

  return outputs
