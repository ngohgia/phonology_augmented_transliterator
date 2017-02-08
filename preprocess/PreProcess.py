SYL_DELIM = ' . '
GLIDED_VOWEL_DASH = '-'
NULL_ONSET = 'NULL_O'
replaced_syls = { 'e r _3': ' '.join(['NULL_O', 'e' + GLIDED_VOWEL_DASH + 'r', '_3']),
                  'e n _1': ' '.join(['NULL_O', 'e' + GLIDED_VOWEL_DASH + 'n', '_1']),
                  'sh e n _2': ' '.join(['sh', 'e' + GLIDED_VOWEL_DASH + 'n', '_2']) }

def preprocess(raw_training_lex):
  training_lex = []
  for entry in raw_training_lex:
    src_word = entry[0]
    targ_word = entry[-1]

    targ_syls = [syl.strip() for syl in targ_word.split(SYL_DELIM)]
    new_targ_syls = []
    for syl in targ_syls:
      new_syl = replace_syllable(syl)

      new_targ_syls.append(new_syl)
    new_targ_word = SYL_DELIM.join(new_targ_syls)
    training_lex.append([src_word, new_targ_word])

  return training_lex

def replace_syllable(syl):
  if syl in replaced_syls:
    return replaced_syls[syl]
  return syl

### DEBUG ######
# print attach_coda_to_nucleus('e n _2')
# print attach_coda_to_nucleus('k e ng _3')
# print replace_syllable('e r _3')
