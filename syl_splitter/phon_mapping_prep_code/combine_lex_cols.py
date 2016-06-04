import sys

def combine_lex_cols(source_files_name):
  src_syl_file = open(source_files_name + ".src_syl.txt", "r")
  targ_syl_file = open(source_files_name + ".targ_syl.txt", "r")
  lex_syl_file = open(source_files_name + ".lex", "w")

  src_syls = []
  targ_syls = []
  for line in src_syl_file:
    src_syls.append(line.strip())

  for line in targ_syl_file:
    targ_syls.append(line.strip())

  for i in range(len(src_syls)):
    lex_syl_file.write(src_syls[i] + "\t" + targ_syls[i] + "\n")


  src_syl_file.close()
  targ_syl_file.close()
  lex_syl_file.close()
