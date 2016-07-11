import os
import sys
import subprocess

from shared_res.Syllable import Syllable
from shared_res.Word import Word
from shared_res.Coord import Coord
from shared_res.TestCoord import TestCoord
from shared_res.SearchSpace import SearchSpace

from shared_res.LangAssets import LangAssets

RANK_WEIGHT = LangAssets.RANK_WEIGHT

DEFAULT_NUCLEUS = 'e'
DEFAULT_CODA_ONSET = 't'

if __name__ == '__main__':
  try:
    script, lex_hyp_file_path, test_units_roles_path, run_dir, t2p_decoder = sys.argv
  except ValueError:
    print "Syntax: phone_mapper.py \t lex_hyp_file_path \t test_units_roles_path \t run_dir \t t2p_decoder"
    sys.exit(1)

t2p_decoder_path = os.path.abspath(t2p_decoder)

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"

GENERIC_VOWEL = LangAssets.SCHWA

class RankedSearchPt:
  def __init__(self):
    self.search_pt = ""
    self.rank = 0

  def print_str(self):
    print self.search_pt + " - " + str(self.rank)




def read_split_lex_file(lex_file_path):
  lex_file = open(lex_file_path, "r")

  all_words = []
  for line in lex_file:
    [src_syls_str, roles_str, targ_syls_str] = line.split("\t")[2:5]

    src_syls = [[unit.strip() for unit in src_syl.strip().split(" ")] for src_syl in src_syls_str[1:len(src_syls_str)-1].split("] [")]
    roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
    targ_syls = [[unit.strip() for unit in targ_syl.split(" ")[0:len(targ_syl.split(" "))-1]] for targ_syl in targ_syls_str.split(" . ")]

    new_word = Word()
    for idx in range(len(src_syls)):
      new_syl = Syllable()
      new_syl.create_new_syl(src_syls[idx], roles[idx], [], targ_syls[idx])
      new_word.add_new_syl(new_syl)

    all_words.append(new_word)

  return all_words
  lex_file.close()

def create_input_for_t2p(all_words, t2p_input_path):
  t2p_input_file = open(t2p_input_path, "w")

  for word in all_words:
    word.print_str()
    for syl in word.syls:
      print "".join(syl.src_graphs).upper()
      t2p_input_file.write("".join(syl.src_graphs).upper() + "\n")

  t2p_input_file.close()

def get_phons_with_g2p(t2p_decoder_path, t2p_input_path, t2p_output_path):
  t2p_output_path_tmp = t2p_output_path + ".tmp"

  curr_dir = "/".join(os.path.realpath(__file__).split("/")[0:-2])
  t2p_dir = os.path.dirname(os.path.realpath(t2p_decoder_path))

  # cd to the t2p folder
  os.chdir(t2p_dir)
  # run t2p
  command = "perl " + t2p_decoder_path + " < " + t2p_input_path + " > " + t2p_output_path_tmp
  run_shell_command(command)
  # cd back
  os.chdir(curr_dir)

  t2p_output_file_tmp = open(t2p_output_path_tmp, "r")
  t2p_output_file = open(t2p_output_path, "w")

  count = 0
  for line in t2p_output_file_tmp:
    if count > 2:
      t2p_output_file.write(line[2:len(line)])
    count = count + 1

  t2p_output_file_tmp.close()
  t2p_output_file.close()

def add_src_phons_to_syls(all_words, t2p_output_path):
  count = 0;
  all_phonemes = []

  t2p_output_file = open(t2p_output_path, "r")

  for line in t2p_output_file:
    all_phonemes.append([phoneme.strip() for phoneme in line.split(" ")])

  for word in all_words:
    for syl in word.syls:
      idx = 0
      for i in range(len(syl.src_graphs)):
        if len(syl.src_graphs[i]) == 1:
          syl.src_phons.append([all_phonemes[count][idx]])
          idx = idx + 1
        else:
          syl.src_phons.append(all_phonemes[count][idx:idx+len(syl.src_graphs[i])])
          idx = idx + len(syl.src_graphs[i])   
      count = count + 1;

  # Remove indeterminate phonemes
  for word in all_words:
    for syl in word.syls:
      for i in range(len(syl.src_graphs)):
        tmp_unit_phonemes = ""
        for phoneme in syl.src_phons[i]:
          if phoneme != "_":
            tmp_unit_phonemes = tmp_unit_phonemes + phoneme
            # Just pick the first phoneme
            break
        syl.src_phons[i] = tmp_unit_phonemes

  # Solve the special cases of compound R-colored ER and AXR
  for word in all_words:
    for syl in word.syls:
      for j in range(len(syl.src_phons)-1):
        if syl.src_phons[j] == "" and \
        (syl.src_phons[j+1] == "ER" or syl.src_phons[j+1] == "AXR"):
          if syl.src_phons[j+1] == "ER":
            syl.src_phons[j] = "EH"
            syl.src_phons[j+1] = "R"
          if syl.src_phons[j+1] == "AXR":
            syl.src_phons[j] = "AX"
            syl.src_phons[j+1] = "R"
  for word in all_words:
    word.print_str()

  t2p_output_file.close()

def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

def print_search_space_to_file(search_space, output_file_name):
  output_file = open(output_file_name, "w")
  output_file.write(str(search_space))
  output_file.close()

def read_test_units_roles(units_roles_path):
  units_roles_file = open(units_roles_path, "r")

  all_words = []
  for line in units_roles_file:
    [units, roles] = [part.strip() for part in line.split("\t")]
    unit_syls = [part.strip() for part in units.split(" . ")]
    role_syls = [part.strip() for part in roles.split(" . ")]

    new_word = Word()
    for idx in range(len(unit_syls)):
      new_syl = Syllable()
      new_syl.src_graphs = [part.strip() for part in unit_syls[idx].split(" ")]
      new_syl.roles = [part.strip() for part in role_syls[idx].split(" ")]

      new_word.add_new_syl(new_syl)
    all_words.append(new_word)

  return all_words

def get_all_test_coords(all_words, search_space):
  all_test_coords = []

  for word in all_words:
    for syl in word.syls:
      new_test_coord = TestCoord()
      new_test_coord.create_from_syl(syl)
      all_tagged_coords = new_test_coord.get_tagged_coords()
      all_extrapolated_coords_ranks = []

      for coord in all_tagged_coords:
        tmp = coord.extrapolate_and_rank()
        for extrapolated_coord_rank in tmp:
          all_extrapolated_coords_ranks.append(extrapolated_coord_rank)

      get_targ_phons_from_syl(syl, all_extrapolated_coords_ranks, search_space)


def get_targ_phons_from_syl(syl, all_coords_ranks, search_space):
  search_pt_rank_by_role = {ONSET: [], NUCLEUS: [], CODA: []}
  for role in syl.roles:
    for coord_rank in all_coords_ranks:
      if coord_rank[0].tags[role] == 1 and coord_rank[0].form_search_pt() != "":
        new_ranked_search_pt = RankedSearchPt()
        new_ranked_search_pt.search_pt = coord_rank[0].form_search_pt()
        new_ranked_search_pt.rank = coord_rank[1]
        search_pt_rank_by_role[role].append(new_ranked_search_pt)

  for idx in range(len(syl.roles)):
    role = syl.roles[idx]
    en_grapheme = syl.src_graphs[idx]

    all_matches = {}

    for search_pt_rank in search_pt_rank_by_role[role]:
      search_pt = search_pt_rank.search_pt
      rank = search_pt_rank.rank

      if search_pt in search_space:     
        tmp_matches = search_space[search_pt]
        
        for phoneme in tmp_matches:
          if phoneme not in all_matches:
            all_matches[phoneme] = tmp_matches[phoneme]/(rank * RANK_WEIGHT)
          else:
            all_matches[phoneme] = all_matches[phoneme] + tmp_matches[phoneme]/(rank * RANK_WEIGHT)

    # print all_matches

    max_score = 0.0
    best_match = ""
    if len(all_matches) > 0:
      for phoneme in all_matches.keys():
        if all_matches[phoneme] > max_score:
          max_score = all_matches[phoneme]
          best_match = phoneme
    else:
      if role == NUCLEUS:
        best_match = DEFAULT_NUCLEUS
      else:
        best_match = DEFAULT_CODA_ONSET

    # print best_match
    syl.targ_phons.append(best_match)




#------------------------- GET SEARCH SPACE -----------------------------#
all_train_dev_words = read_split_lex_file(lex_hyp_file_path)

phon_t2p_input_path = os.path.abspath(os.path.join(run_dir, "phon_t2p_input.txt"))
phon_t2p_output_path = os.path.abspath(os.path.join(run_dir, "phon_t2p_output.txt"))
create_input_for_t2p(all_train_dev_words, phon_t2p_input_path)
get_phons_with_g2p(t2p_decoder_path, phon_t2p_input_path, phon_t2p_output_path)
add_src_phons_to_syls(all_train_dev_words, phon_t2p_output_path)

search_space_path = os.path.abspath(os.path.join(run_dir, "phon_search_space.txt"))
tone_searchspace = SearchSpace()
for word in all_train_dev_words:
  for syl in word.syls:
    new_coord = Coord()
    new_coord.encode_unit_to_coord(syl)
    unit_list = new_coord.to_list()

    all_coords = []
    new_coord.extrapolate(unit_list, all_coords, 0)

    for coord in all_coords:
      #coord.print_str()
      tone_searchspace.add_new_search_point(coord)

tone_searchspace.normalize()
print_search_space_to_file(tone_searchspace, search_space_path)

#------------------------- DECODE ---------------------------------------#
all_test_words = read_test_units_roles(test_units_roles_path)

test_units_roles_t2p_input_path = os.path.abspath(os.path.join(run_dir, "test_units_roles_t2p_input.txt"))
test_units_roles_t2p_output_path = os.path.abspath(os.path.join(run_dir, "test_units_roles_t2p_output.txt"))
print all_test_words
create_input_for_t2p(all_test_words, test_units_roles_t2p_input_path)
get_phons_with_g2p(t2p_decoder_path, test_units_roles_t2p_input_path, test_units_roles_t2p_output_path)
add_src_phons_to_syls(all_test_words, test_units_roles_t2p_output_path)

get_all_test_coords(all_test_words, tone_searchspace.space)

test_toneless_output_path = os.path.abspath(os.path.join(run_dir, "test.toneless_with_roles.txt"))
test_toneless_output_file = open(test_toneless_output_path, "w")
for word in all_test_words:
  result = " . ".join([syl.get_targ_phons_str() for syl in word.syls])
  result = result + "\t" + " . ".join([syl.get_roles_str() for syl in word.syls])
  # print result
  test_toneless_output_file.write(result + "\n")
test_toneless_output_file.close()

print test_units_roles_t2p_input_path

#------------------------- UNIT TEST ------------------------------------#
# for word in all_words:
#   word.print_str()

#print "Unmatched graphemes and phonemes"
# for word in all_words:
#   found = False
#   for syl in word.syls:
#     for i in range(len(syl.src_graphs)):
#       if syl.src_graphs[i] != "@" and syl.src_phons[i] == "":
#         found = True
#         break
#     if found:
#       break
#   # if found:
#   #   word.print_str()

# tone_searchspace = SearchSpace()
# for word in all_words:
#   for syl in word.syls:
#     new_coord = Coord()
#     new_coord.encode_unit_to_coord(syl)
#     unit_list = new_coord.to_list()

#     all_coords = []
#     new_coord.extrapolate(unit_list, all_coords, 0)

#     for coord in all_coords:
#       tone_searchspace.add_new_search_point(coord)

# print_search_space_to_file(tone_searchspace, search_space_path)

