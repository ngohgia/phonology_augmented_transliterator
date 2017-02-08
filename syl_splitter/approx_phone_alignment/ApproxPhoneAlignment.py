import os

from shared_res.Syllable import Syllable
from shared_res.Word import Word

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GENERIC_VOWEL = "@"

EN_DIPTHONGS = ["EY", "AY", "OW", "AW", "OY", "ER", "AXR", "UW", "IY", "AX", "AO", "UH"]
COMPOUND_EN_CONSOS = ["CH", "TH", "DH", "SH", "K", "KD", "TS"]

def read_split_lex_file(lex_file_path):
  lex_file = open(lex_file_path, "r")

  all_words = []
  for line in lex_file:
    [src_syls_str, roles_str, targ_syls_str] = line.split("\t")[2:5]

    src_syls = [[unit.strip() for unit in src_syl.strip().split(" ")] for src_syl in src_syls_str[1:len(src_syls_str)].split("] [")]
    roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
    targ_syls = [[unit.strip() for unit in targ_syl.split(" ")[0:len(targ_syl.split(" "))]] for targ_syl in targ_syls_str.split(" . ")]

    new_word = Word()
    for idx in range(len(src_syls)):
      new_syl = Syllable()
      new_syl.create_new_syl(src_syls[idx], roles[idx], [], targ_syls[idx])
      new_word.add_new_syl(new_syl)

    all_words.append(new_word)

  return all_words
  lex_file.close()

def get_approx_phone_alignment(lex_file_path, run_dir):
  all_words = read_split_lex_file(lex_file_path);
  phone_alignment_by_role = {ONSET: {}, NUCLEUS: {}, CODA: {}}
  targ_to_src_phon_alignment_prob = {ONSET: {}, NUCLEUS: {}, CODA: {}}

  for word in all_words:
    for syl in word.syls:
      for idx in range(len(syl.roles)):
        role = syl.roles[idx]
        src_graph = syl.src_graphs[idx]
        targ_phon = syl.targ_phons[idx]
        if src_graph not in phone_alignment_by_role[role]:
          phone_alignment_by_role[role][src_graph] = [targ_phon]
        else:
          if targ_phon not in phone_alignment_by_role[role][src_graph]:
            phone_alignment_by_role[role][src_graph].append(targ_phon)

        if targ_phon not in targ_to_src_phon_alignment_prob[role]:
          targ_to_src_phon_alignment_prob[role][targ_phon] = {src_graph: 1}
        else:
          if src_graph not in targ_to_src_phon_alignment_prob[role][targ_phon]:
            targ_to_src_phon_alignment_prob[role][targ_phon][src_graph] = 1
          else:
            targ_to_src_phon_alignment_prob[role][targ_phon][src_graph] = targ_to_src_phon_alignment_prob[role][targ_phon][src_graph] + 1

  # normalize targ_to_src_phon_alignment_prob
  for role in targ_to_src_phon_alignment_prob:
    for targ_phon in targ_to_src_phon_alignment_prob[role]:
      sum_count = sum(targ_to_src_phon_alignment_prob[role][targ_phon].values())
      for src_graph in targ_to_src_phon_alignment_prob[role][targ_phon]:
        targ_to_src_phon_alignment_prob[role][targ_phon][src_graph] = 1.0 * targ_to_src_phon_alignment_prob[role][targ_phon][src_graph] / sum_count

  phone_alignment_dict_file = open(os.path.join(run_dir, "phone_alignment_dict.txt"), "w")
  targ_to_src_phone_alignment_file = open(os.path.join(run_dir, "targ_to_src_phon_alignment.txt"), "w")

  phone_alignment_dict_file.write("ONSET\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[ONSET]) + "\n\n")
  targ_to_src_phone_alignment_file.write("ONSET\n")
  targ_to_src_phone_alignment_file.write(str(targ_to_src_phon_alignment_prob[ONSET]) + "\n\n")

  phone_alignment_dict_file.write("NUCLEUS\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[NUCLEUS]) + "\n\n")
  targ_to_src_phone_alignment_file.write("NUCLEUS\n")
  targ_to_src_phone_alignment_file.write(str(targ_to_src_phon_alignment_prob[NUCLEUS]) + "\n\n")

  phone_alignment_dict_file.write("CODA\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[CODA]) + "\n\n")
  targ_to_src_phone_alignment_file.write("CODA\n")
  targ_to_src_phone_alignment_file.write(str(targ_to_src_phon_alignment_prob[CODA]) + "\n\n")

  phone_alignment_dict_file.close()
  targ_to_src_phone_alignment_file.close()


  return phone_alignment_by_role

def identify_compound_phones_in_hyp(hyp):
  correct_compound_phones_count = 0
  for idx in range(len(hyp.original_src_phons)):
    curr_phone = hyp.original_src_phonmes[idx]; curr_role = hyp.roles[idx]
    if curr_phone in EN_DIPTHONGS or curr_phone in COMPOUND_EN_CONSOS:
      prev_phone = "" ; prev_role = ""
      next_phone = "" ; next_role = ""
      if idx > 0:
        prev_phone = hyp.original_src_phonmes[idx-1]
        prev_role = hyp.roles[idx-1]
      if idx < len(hyp.original_src_phonmes) - 1:
        next_phone = hyp.original_src_phonmes[idx+1]
        next_role = hyp.roles[idx+1]
      if prev_phone == "_":
        if prev_role.split("_")[-1] == curr_role.split("_")[0]:
          correct_compound_phones_count = correct_compound_phones_count + 1
          print prev_phone + " " + curr_phone
      if next_phone == "_":
        if next_role.split("_")[0] == curr_role.split("_")[-1]:
          correct_compound_phones_count = correct_compound_phones_count + 1
          print curr_phone + " " + next_phone
  return correct_compound_phones_count


def score_hyp_with_phone_alignment(word_hyps, phone_alignment_dict):
  lowest_phone_alignment_pen = 1000
  best_hyps = []

  for hyp in word_hyps:
    targ_phons = [syl.strip().split() for syl in hyp.toneless_targ_ref]
    targ_roles = [syl.strip().split() for syl in hyp.targ_roles.split(" . ")]

    tmp_src_word = str(hyp.reconstructed_word)[1:-1]
    src_phons = [syl.strip().split(" ") for syl in tmp_src_word.split(" ] [")]

    phone_alignment_pen = 0
    for syl_idx in range(len(targ_roles)):
      if len(targ_roles[syl_idx]) != len(targ_phons[syl_idx]):
        print targ_roles
        print targ_phons
      for role_idx in range(len(targ_roles[syl_idx])):
        role = targ_roles[syl_idx][role_idx]
        targ_phon = targ_phons[syl_idx][role_idx]
        src_phon = src_phons[syl_idx][role_idx]

        if src_phon != GENERIC_VOWEL:
          if src_phon in phone_alignment_dict[role]:
            if targ_phon not in phone_alignment_dict[role][src_phon]:
              print("Wrong phone alignment: " + " - ".join([role, src_phon, targ_phon]))
              phone_alignment_pen = phone_alignment_pen + 1
    hyp.phone_alignment_pen = phone_alignment_pen
    # print hyp.get_str()
    if phone_alignment_pen < lowest_phone_alignment_pen:
      lowest_phone_alignment_pen = phone_alignment_pen
      best_hyps = [hyp]
    elif phone_alignment_pen == lowest_phone_alignment_pen:
      best_hyps.append(hyp)
  
  print("---------------- COMPLEX WORDS BEST HYPS ----------------------")
  for idx in range(len(best_hyps)):
    best_hyps[idx].compound_phones_count = identify_compound_phones_in_hyp(best_hyps[idx])
    print(best_hyps[idx].get_str())

  max_mod_pen = 0
  max_phone_alignment_pen = 0
  max_compound_phones_count = 0
  for idx in range(len(best_hyps)):
    if best_hyps[idx].mod_pen > max_mod_pen:
      max_mod_pen = best_hyps[idx].mod_pen
    if best_hyps[idx].phone_alignment_pen > max_phone_alignment_pen:
      max_phone_alignment_pen = best_hyps[idx].phone_alignment_pen
    if best_hyps[idx].compound_phones_count > max_compound_phones_count:
      max_compound_phones_count = best_hyps[idx].compound_phones_count

  for idx in range(len(best_hyps)):
    best_hyps[idx].compound_pen = best_hyps[idx].phone_alignment_pen * 1.0 / (max_phone_alignment_pen + 0.1) + \
      best_hyps[idx].phone_alignment_pen * 1.0 / (max_phone_alignment_pen + 0.1) - \
      best_hyps[idx].compound_phones_count * 1.0 / (max_compound_phones_count + 0.1)

  print("---------------- COMPLEX WORDBEST HYP ----------------------")
  best_hyps = sorted(best_hyps, key=lambda hyp: hyp.compound_pen)
  return best_hyps[0]
