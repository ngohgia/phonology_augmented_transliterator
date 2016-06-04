import sys

if __name__ == '__main__':
  try:
    script, source_file_name, dest_files_name = sys.argv
  except ValueError:
    print "Split two columns of a lex file into two separate dest files with extension .src_syl and .ref_syl"
    print "Syntax: python split_columns.py source_file_name"
    sys.exit(1)

def split(source_file_name):
  syl_lex_file = open(source_file_name, "r")
  src_syl_file = open(dest_files_name + ".src_syl.txt", "w")
  ref_syl_file = open(dest_files_name + ".ref_syl.txt", "w")

  src_syls = []
  targ_syls = []
  for line in syl_lex_file:
    [src, targ] = line.strip().split("\t")
    src_syls.append(src.strip())
    targ_syls.append(targ.strip())

  for i in range(len(src_syls)):
    src_syl_file.write(src_syls[i] + "\n")
    ref_syl_file.write(targ_syls[i] + "\n")


  src_syl_file.close()
  ref_syl_file.close()
  syl_lex_file.close()

split(source_file_name)

