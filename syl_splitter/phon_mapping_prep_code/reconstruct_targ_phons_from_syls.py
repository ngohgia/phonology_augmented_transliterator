import sys

def retrieve_syls_mapping(syls_mapping_file_name):
  syls_mapping_file = open(syls_mapping_file_name, "r")
  mapping_dict = {}

  for line in syls_mapping_file:
    [src_syl, targ_syl] = line.strip().split("\t")
    mapping_dict[src_syl] = targ_syl

  syls_mapping_file.close()
  return mapping_dict

def reconstruct(syls_seq_file_name, syls_output_file_name, mapping_dict):
  syls_seq_file = open(syls_seq_file_name, "r")  
  syls_output_file = open(syls_output_file_name, "w")

  for line in syls_seq_file:
    src_syls = [syl.strip() for syl in line.strip().split(" . ")]

    for src_syl in en_syls:
      if src_syl not in mapping_dict:
        return False
      else:
        targ_syls = [mapping_dict[src_syl] for src_syl in src_syls]
    
    syls_output_file.write(" . ".join(targ_syls) + "\n")

  syls_seq_file.close()
  syls_output_file.close()
  return True

def reconstruct_targ_phons_from_syls(syls_seq_file, syls_mapping_file, syls_output_file):
  mapping_dict = retrieve_syls_mapping(syls_mapping_file)
  return reconstruct(syls_seq_file, syls_output_file, mapping_dict)
