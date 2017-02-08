# coding=utf-8

# Generate all possible syllable structure hypothesis of a foreign word,
# given its transliterated entry
# IMPROVED VERSION: treat syllable generated by CONSONANT, assigned NUCLEUS role as a normal syllable

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LangAssets.LangAssets import LangAssets
from LangAssets.Syllable import Syllable
from LangAssets.Word import Word
from LangAssets.WordHyp import WordHyp

#---------------- IMPORT ALL VALID ENGLISH CONSONANTS/ VOWELS ---------------

# All possible roles of an alphabet
ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
ONSET_NUCLEUS = "O_N"
ONSET_CODA = "O_Cd"
NUCLEUS_ONSET = "N_O"
NUCLEUS_NUCLEUS = "N_N"
NUCLEUS_CODA = "N_Cd"
CODA_ONSET = "Cd_O"
CODA_NUCLEUS = "Cd_N"
CODA_CODA = "Cd_Cd"
ONSET_NUCLEUS_CODA = "O_N_Cd"
CODA_ONSET_NUCLEUS = "Cd_O_N"
REMOVE = "R"


lang_assets = LangAssets()
VOWEL = LangAssets.VOWEL
CONSONANT = LangAssets.CONSONANT
DELIMITER = LangAssets.DELIMITER

GENERIC_VOWEL = LangAssets.GENERIC_VOWEL

PossibleRoles = LangAssets.POSSIBLE_ROLES
ValidSrcConsos = lang_assets.valid_src_consos
ValidSrcVowels = lang_assets.valid_src_vowels

ValidTargConsos = lang_assets.valid_targ_consos
ValidTargVowels = lang_assets.valid_targ_vowels

# Strict role constraints
ValidConsoRoles = [ONSET, NUCLEUS, CODA, NUCLEUS_CODA, ONSET_NUCLEUS, CODA_ONSET_NUCLEUS, CODA_ONSET, REMOVE]
ValidVowelRoles = [NUCLEUS, NUCLEUS_NUCLEUS, NUCLEUS_CODA, ONSET_NUCLEUS_CODA, REMOVE]

ValidSubSylUnit = {
  ONSET: lang_assets.valid_src_onsets,
  NUCLEUS: lang_assets.valid_src_nuclei,
  CODA: lang_assets.valid_src_codas
}

# Each role can only be assigned to more than a specific ratio of all the letters
# TO-DO estimate the maximum ratio of each role from the Vietnamese entries in training data
MAX_ROLES_RATIOS = {
  ONSET: 0.4,
  NUCLEUS: 0.4,
  CODA: 0.4,
  ONSET_NUCLEUS: 0.1,
  CODA_ONSET_NUCLEUS: 0.0,
  NUCLEUS_ONSET: 0.0,
  NUCLEUS_NUCLEUS: 0.1,
  NUCLEUS_CODA: 0.4,
  CODA_ONSET: 0.0,
  CODA_NUCLEUS: 0.0,
  CODA_CODA: 0.0,
  ONSET_NUCLEUS_CODA: 0.0,
  REMOVE: 0.0,
}
# roels = [N_Cd, O, N, Cd, O, N, Cd, O_N, O, N, O, N, Cd, Cd]

#print ValidSrcConsos
#print ValidSrcVowels
#print ValidSubSylUnit[ONSET]
#print ValidSubSylUnit[NUCLEUS]
#print ValidSubSylUnit[CODA]

#---------------- LABEL ALL LETTERS IN A WORD ------------------#
def label_letters(word):
  labels = [None] * len(word)

  for pos in range(len(word)):
    if word[pos] not in ValidSrcVowels and word[pos] not in ValidSrcConsos \
    and word[pos] != DELIMITER:
      print "ERROR: Unlabeled letter %s in word %s" % (word[pos], word)
      sys.exit(1)
    else:
      if word[pos] in ValidSrcVowels:
        labels[pos] = VOWEL
      elif word[pos] in ValidSrcConsos:
        labels[pos] = CONSONANT

  return labels

#---------------- ENCODE A VIETNAMESE ENTRY IN SUBSYLLABIC UNITS ------------------#
def export_syl_struct_of_targ_word(word):
  GLIDED_VOWEL_DASH = '-'

  syls = word.split(".")
  toneless_syls = [(" ").join(syl.strip().split(" ")[:-1]) for syl in syls]

  encoded_units = []
  for syl in toneless_syls:
    targ_phons = syl.split(" ")

    if len(targ_phons) == 3:
      if targ_phons[1] in ValidTargVowels or GLIDED_VOWEL_DASH in targ_phons[1]:
        syl_struct = [ONSET, NUCLEUS, CODA]
      else:
        print("[ERROR] Syllable of 3 units does not have a valid nucleus")
        print "Syllable: " + syl
        print "Word: " + word
        raise SystemExit
        sys.exit(1)
    elif len(targ_phons) == 2:
      if targ_phons[1] in ValidTargVowels or GLIDED_VOWEL_DASH in targ_phons[1]:
        syl_struct = [ONSET, NUCLEUS]
      elif targ_phons[0] in ValidTargVowels or GLIDED_VOWEL_DASH in targ_phons[0]:
        syl_struct = [NUCLEUS, CODA]
      else:
        print("[ERROR] Syllable of 2 units does not have a valid nucleus")
        print "Syllable: " + syl
        print "Word: " + word
        raise SystemExit
        sys.exit(1)
    elif len(targ_phons) == 1:
      if targ_phons[0] in ValidTargVowels or GLIDED_VOWEL_DASH in targ_phons[0]:
        syl_struct = [NUCLEUS]
    encoded_units.append(" ".join(syl_struct))

  return " . ".join(encoded_units)

#---------------- GENERATE ALL POSSIBLE ROLES FOR ALPHABETS IN A WORD ------------------#

# Use a dictionary to keep count on the number times a role is assigned to a letter
role_count = {}
for role in PossibleRoles:
  role_count[role] = 0

def try_generate_roles(word, labels, roles, pos, targ_syl_struct, best_word_hyps_list, MAX_ROLES_COUNT):
  if pos >= len(labels):
    # print ("Word: %s" % word)
    # print ("Labels: %s" % str(labels))
    # print ("Roles: %s" % str(roles))
    checked = [False] * len(roles)
    hyp_word = construct_syls(word, labels, roles, checked)
    # print ("hyp_word: %s" % str(hyp_word))
    update_best_hyp_words_list(word, targ_syl_struct, roles, hyp_word, checked, best_word_hyps_list)
    return

  if labels[pos] == CONSONANT:
    for idx in range(len(ValidConsoRoles)):
      role = ValidConsoRoles[idx]
      if role_count[role] >= (MAX_ROLES_COUNT[role]):
        continue
      else:
        role_count[role] = role_count[role] + 1
        if is_valid_subsyllabic_unit(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos):
          try_generate_roles(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, targ_syl_struct, best_word_hyps_list, MAX_ROLES_COUNT)
        role_count[role] = role_count[role] - 1
  elif labels[pos] == VOWEL:
    tmp_ValidVowelRoles = ValidVowelRoles
    if word[pos] == "y" or word[pos] == "i" or word[pos] == "u" or word[pos] == "e":
      tmp_ValidVowelRoles = tmp_ValidVowelRoles + [ONSET]
    if word[pos] == "u" or word[pos] == "e":
      tmp_ValidVowelRoles = tmp_ValidVowelRoles + [CODA]
    for idx in range(len(tmp_ValidVowelRoles)):
      role = tmp_ValidVowelRoles[idx]
      if role_count[role] >= (MAX_ROLES_COUNT[role]):
        continue
      else:
        role_count[role] = role_count[role] + 1
        if is_valid_subsyllabic_unit(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos):
          try_generate_roles(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, targ_syl_struct, best_word_hyps_list, MAX_ROLES_COUNT)
        role_count[role] = role_count[role] - 1

#---------------- CHECK IF A SUBSYLLABIC UNIT IS VALID ------------------#
# From position pos, look backwards along the string to check if the current
# subsyllabic unit is valid
def is_valid_subsyllabic_unit(word, labels, roles, pos):
  # if the letter under consideration is at the beginning of the string
  # check if the letter is assigned a valid role to be at the
  # beginning of the word
  word_beginning = 0
  for i in range(len(roles)):
    if roles[i] != REMOVE:
      word_beginning = i
      break
  # impossible assignment for a word beginning
  # print word_beginning
  if pos == word_beginning:
    if labels[pos] == CONSONANT and \
    (roles[pos] == CODA or roles[pos] == NUCLEUS or roles[pos] == CODA_ONSET \
      or roles[pos] == CODA_ONSET_NUCLEUS):
      return False

  # if pos is at the end of the word
  # check if the final letter is a valid subsyllabic unit
  if pos == len(roles) - 1:
    word_ending = -1
    for i in reversed(range(0, len(roles))):
      if roles[i] != REMOVE:
        word_ending = i
        break

    #print "word_ending: " + str(word_ending)
    if word_ending >= 0:
      curr_role = roles[word_ending].split("_")[-1]
      if roles[word_ending] == ONSET or roles[word_ending] == CODA_ONSET or roles[word_ending] == NUCLEUS:
        return False


  last_non_R_pos = -1
  end_of_unit = -1
  curr_role = ""
  subsyl_unit = ""

  # Get the last position in the word that is not assgined the REMOVE role
  for i in reversed(range(0, pos)):
    if roles[i] != REMOVE:
      last_non_R_pos = i
      break

  # Check if pos is a subsyllabic unit's boundary
  if last_non_R_pos >= 0:
    # if a syllable can be formed by the letter alone
    # check the previous sub-syllabic unit
    if roles[pos] == ONSET_NUCLEUS_CODA:
      curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role CODA_ONSET_NUCLEUS
    elif roles[pos] == CODA_ONSET_NUCLEUS:
      # the letter must be a CONSONANT
      # if the last_non_R is also assigned CODA, expand
      if roles[last_non_R_pos] == CODA:
        subsyl_unit = word[pos]
        curr_role = CODA
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role ONSET_NUCLEUS
    elif roles[pos] == ONSET_NUCLEUS:
      # the letter must be a CONSONANT
      # if the last_non_R is also assigned ONSET, expand
      if roles[last_non_R_pos] == ONSET:
        subsyl_unit = word[pos]
        curr_role = ONSET
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role NUCLEUS_CODA
    elif roles[pos] == NUCLEUS_CODA:
      # the letter must be a VOWEL
      # if the last_non_R is also assigned NUCLEUS, expand
      if roles[last_non_R_pos] == NUCLEUS:
        subsyl_unit = word[pos]
        curr_role = NUCLEUS
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    elif roles[pos] == CODA_ONSET:
      # the letter must be the end of a coda and the beginning of an onset
      # if the last_non_R is also assigned CODA, expand
      if roles[last_non_R_pos] == CODA:
        subsyl_unit = word[pos]
        curr_role = CODA
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]

      end_of_unit = last_non_R_pos
    else:
      if roles[pos] != roles[last_non_R_pos]:
        curr_role = roles[last_non_R_pos].split("_")[-1]
        end_of_unit = last_non_R_pos

        # Ignore if the role assignment at last_non_R_pos
        # is ONSET_NUCLEUS or ONSET_NUCLEUS_CODA or CODA_ONSET_NUCLEUS
        if roles[last_non_R_pos] in [ONSET_NUCLEUS, ONSET_NUCLEUS_CODA, CODA_ONSET_NUCLEUS]:
          return True
      else:
        # not yet at a subsyllabic unit's boundary
        if pos < len(roles)-1:
          return True
        else:
          curr_role = roles[pos]
          end_of_unit = len(roles)-1
  

    # If an ONSET is immediately followed by a CODA, CODA_ONSET_NUCLEUS
    # or ONSET_NUCLEUS_CODA, return false
    if roles[last_non_R_pos].split("_")[-1] == ONSET and \
    (roles[pos].split("_")[0] == CODA or roles[pos] == ONSET_NUCLEUS_CODA):
      return False

    # If a ONSET_NUCLEUS_CODA or NUCLEUS_CODA is immediately followed by a CODA, return false
    if (roles[last_non_R_pos] == ONSET_NUCLEUS_CODA or roles[last_non_R_pos] == NUCLEUS_CODA)and \
    roles[pos].split("_")[0] == CODA:
      return False

    # if roles[last_non_R_pos] == NUCLEUS
    # and roles[pos] == ONSET or ONSET_NUCLEUS_CODA, return False
    # since an equivalent hypothesis of which roles[last_non_R_pos] == NUCLEUS_CODA
    if roles[last_non_R_pos] == NUCLEUS and \
    roles[pos].split("_")[0] == ONSET:
      return False

    # # if a NUCLEUS or NUCLEUS CODA can form an single syllable, return False
    # # since an equivalent hypothesis with a ONSET_NUCLEUS_CODA can be used instead
    last_last_non_R_pos = -1
    for j in reversed(range(0, last_non_R_pos)):
      if roles[j] != REMOVE:
        last_last_non_R_pos = j
        break

    if last_last_non_R_pos >= 0:
      if roles[last_last_non_R_pos].split("_")[-1] == CODA and \
      (roles[last_non_R_pos] == NUCLEUS or roles[last_non_R_pos] == NUCLEUS_CODA) and \
      roles[pos].split("_")[0] == ONSET:
        return False


  #print ("end_of_unit: %d" % end_of_unit)
  # create the sub-syllabic unit
  if end_of_unit >= 0:
    for i in reversed(range(0, end_of_unit+1)):
      # if the role assigned to the letter at position i is REMOVE, skip the letter
      #print "i: " + str(i)
      if roles[i] == REMOVE:
        continue

      # break if NUCLEUS_CODA or ONSET_NUCLEUS_CODA is hit
      elif roles[i] == NUCLEUS_CODA or roles[i] == ONSET_NUCLEUS_CODA:
        break

      # if the role assigned to the letter at position i is the same as
      # curr_role, prepend the letter to the subsyllabic unit of consideration
      elif roles[i].split("_")[-1] == curr_role:
        #print "roles[i][-1]: " + roles[i].split("_")[-1]
        subsyl_unit = word[i] + subsyl_unit

        # stop if CODA_ONSET is hit
        if roles[i] == CODA_ONSET:
          break

      # stop if a new subsyllabic unit is hit
      else:
        break

    #print ("Curr role: %s" % curr_role)
    #print ("Subsyllabic unit: %s" % subsyl_unit)

    # Check if the subsyl_unit is a valid subsyllabic unit of the role curr_role (onset, nucleus, coda)
    if subsyl_unit != "" and \
    subsyl_unit not in ValidSubSylUnit[curr_role]:
      return False

  return True

#---------------- CONSTRUCT SYLLABLES ------------------#
def construct_syls(word, labels, roles, checked):
  reconstructed_word = Word()
  # Search for the first letter that is assigned the NUCLEUS role
  # print str(roles)
  idx = 0
  while idx < len(roles):
    # print idx
    if roles[idx] == ONSET_NUCLEUS_CODA:
      new_syl = Syllable()
      checked[idx] = True

      new_syl.nucleus = word[idx]
      # Add the new syllable to the reconstructed word
      idx = idx + 1
      reconstructed_word.add_new_syl(new_syl)

    elif roles[idx] == NUCLEUS or roles[idx] == NUCLEUS_CODA or \
    roles[idx] == NUCLEUS_NUCLEUS or roles[idx] == ONSET_NUCLEUS or roles[idx] == CODA_ONSET_NUCLEUS:
      new_syl = Syllable()
      # print idx
      # look for onset
      if roles[idx] != CODA_ONSET_NUCLEUS:
        if roles[idx] == ONSET_NUCLEUS:
          new_syl.onset = word[idx]
        new_syl = add_onset(word, labels, roles, checked, new_syl, idx-1)
      checked[idx] = True

      if roles[idx] == NUCLEUS_NUCLEUS:
        new_syl.nucleus = word[idx]
        reconstructed_word.add_new_syl(new_syl)

        # add another syllable
        new_syl = Syllable()
        new_syl.nucleus = word[idx]
        idx = idx + 1
        [new_syl, idx] = add_coda(word, labels, roles, checked, new_syl, idx)
        reconstructed_word.add_new_syl(new_syl)

      elif roles[idx] == CODA_ONSET_NUCLEUS:
        new_syl.onset = word[idx]
        new_syl.nucleus = GENERIC_VOWEL
        idx = idx + 1
        [new_syl, idx] = add_coda(word, labels, roles, checked, new_syl, idx)
        reconstructed_word.add_new_syl(new_syl)
      elif roles[idx] == ONSET_NUCLEUS:
        new_syl.nucleus = GENERIC_VOWEL

        idx = idx + 1
        [new_syl, new_idx] = add_coda(word, labels, roles, checked, new_syl, idx)
        reconstructed_word.add_new_syl(new_syl)
      else:
        # Expand the nucleus
        start_idx = idx
        for j in range(start_idx, len(roles)):
          # if the end of the nucleus is reached
          if roles[j] != NUCLEUS:
            checked[idx] = True
            if roles[j] == NUCLEUS_CODA:
              new_syl.nucleus = new_syl.nucleus + word[j]
              idx = j + 1
              # no need to look for coda
              break
            else:
              # look for coda
              [new_syl, idx] = add_coda(word, labels, roles, checked, new_syl, j)
              # print "after coda: " + str(idx)
              break
          # append the letter to the nucleus
          else:
            new_syl.nucleus = new_syl.nucleus + word[j]
            checked[idx] = True
            idx = j+1

        # Add the new syllable to the reconstructed word
        reconstructed_word.add_new_syl(new_syl)
    elif roles[idx] == REMOVE:
      checked[idx] = True
      idx = idx + 1
    else:
      idx = idx + 1


  return reconstructed_word

#---------------- ADD ONSET -------------------------#
def add_onset(word, labels, roles, checked, new_syl, end_idx):
  # Search backwards from the end_idx to 0 to find all letters
  # that can be prepended to the new_syl's onset
  for idx in reversed(range(0, end_idx+1)):
    # print "AA: " + str(idx) + "   " + str(roles[idx])
    if roles[idx] == REMOVE:
      checked[idx] = True
      continue
    elif roles[idx].split("_")[-1] == ONSET:
      # print "onset idx: " + str(idx)
      new_syl.onset = word[idx] + new_syl.onset
      checked[idx] = True
      # print "onset checked: " + str(checked)
      if len(roles[idx].split("_")) > 1:
        return new_syl
    else:
      return new_syl
  return new_syl

#---------------- ADD CODA -------------------------#
def add_coda(word, labels, roles, checked, new_syl, start_idx):
  ## Search forwards from the start_idx to the end to find all letters
  ## that can be appended to the new_syl's coda
  # print "add_coda start_idx: " + str(start_idx)
  idx = start_idx
  while idx < len(roles):
    # print "add_coda idx: " + str(idx)
    # print "add_coda roles[idx]: " + str(roles[idx])
    if roles[idx] == REMOVE:
      # print "add_coda roles[idx] == REMOVE: " + roles[idx]
      checked[idx] = True
    elif roles[idx].split("_")[0] == CODA:
      new_syl.coda = new_syl.coda + word[idx]
      checked[idx] = True
      if len(roles[idx].split("_")) > 1:
        return [new_syl, idx]
    else:
      return [new_syl, idx]
    idx = idx + 1
  # print "idx after add_coda: " + str(idx)
  return [new_syl, idx]

#---------------- CHECK IF ALL LETTERS IN THE WORD HAVE BEEN USED -------------------------#
def are_all_letters_used(checked):
  # print str(checked)
  for item in checked:
    if item == False:
      return False
  return True

#---------------- CHECK VALID RECONSTRUCTED SUBSYLLABIC UNITS -------------------------#
def are_all_subsyl_units_valid(new_word):
  roles_txt = new_word.get_encoded_units()
  roles_by_syl = [syl.strip().split() for syl in roles_txt.split(" . ")]

  # check if the number of syllables and the number of syls in
  # roles by syl match
  if len(roles_by_syl) != len(new_word.syls):
    return False

  for idx in range(len(new_word.syls)):
    # if the number of units inside a syllable
    # does not match the number of units in the syllable's roles list
    # the new_word is not valid
    if len(roles_by_syl[idx]) != new_word.syls[idx].get_unit_count():
      return False

    # Check if each unit in the reconstructed word is valid
    # If a unit contains both the GENERIC VOWEL and normal letters,
    # the unit is not valid
    syl = new_word.syls[idx]
    if syl.onset != "":
      if GENERIC_VOWEL in syl.onset:
        return False
      if syl.onset not in ValidSubSylUnit[ONSET]:
        # print "Invalid reconstructed onset: " + syl.onset
        return False
    if syl.nucleus != "":
      if GENERIC_VOWEL in syl.nucleus and syl.nucleus != GENERIC_VOWEL:
        # print "Invalid reconstructed nucleus: " + syl.nucleus
        return False
      if syl.nucleus not in ValidSubSylUnit[NUCLEUS] and syl.nucleus != GENERIC_VOWEL:
        # print "Invalid reconstructed nucleus: " + syl.nucleus
        return False
    if syl.coda != "":
      if GENERIC_VOWEL in syl.coda:
        return False
      if syl.coda not in ValidSubSylUnit[CODA]:
        # print "Invalid reconstructed coda: " + syl.coda
        return False

  return True

#---------------- UPDATE BEST HYP WORD LIST -------------------------#
def update_best_hyp_words_list(orig_word, targ_syl_struct, roles, new_word, checked, best_word_hyps_list):
  if not are_all_subsyl_units_valid(new_word):
    return

  if not are_all_letters_used(checked):
    return

  if new_word.get_encoded_units() == targ_syl_struct:
    new_word_hyp = WordHyp()
    new_word_hyp.original = orig_word
    new_word_hyp.labels = label_letters(orig_word)
    new_word_hyp.roles = roles
    new_word_hyp.reconstructed_word = new_word

    new_word_hyp.compute_mod_error()
    new_word_hyp.award_hyp()
    new_word_hyp.extra_letter_count = new_word.to_plain_text().count(GENERIC_VOWEL)
    new_word_hyp.count_removal()
    new_word_hyp.count_compound_role()

    best_word_hyps_list.append(new_word_hyp)

    # if len(best_word_hyps_list) == 0:
    #   best_word_hyps_list.append(new_word_hyp)
    #   return
    # If the new hypothesized word has the same edit distance to the original word
    # as it is of the first word in the list of current best hypothesized words list,
    # add the new hypothesized word to the list
    # if new_word_hyp.mod_pen == best_word_hyps_list[0].mod_pen:
    #   best_word_hyps_list.append(new_word_hyp)
    # If the new hypothesized word has a LOWER edit distance to the original word
    # as it is of the first word in the list of current best hypothesized words list,
    # CLEAR the list and add the new hypothesized word into the list
    # elif new_word_hyp.mod_pen < best_word_hyps_list[0].mod_pen:
    #   best_word_hyps_list.append(new_word_hyp)
  return

#------------------ INCREASE MAXIMUM COUNT FOR EACH COMPOUND AND REMOVAL ROLE ----------#
def set_thres_per_role(lvl, word, MAX_ROLES_COUNT):
  if lvl == 0:
    for role in MAX_ROLES_RATIOS:
      MAX_ROLES_COUNT[role] = MAX_ROLES_RATIOS[role] * len(word) + 1
  else:
    for role in MAX_ROLES_RATIOS:
      MAX_ROLES_COUNT[role] = MAX_ROLES_RATIOS[role] * len(word) + lvl

  return MAX_ROLES_COUNT


#------------------ GENERATE ROLES ----------#
def generate_roles(word, labels, targ_syl_struct):
  thres_lvl = 0

  MAX_ROLES_COUNT = {}

  while thres_lvl < 3:
    MAX_ROLES_COUNT = set_thres_per_role(thres_lvl, word, MAX_ROLES_COUNT)


    best_word_hyps_list = []
    roles = [None] * len(labels)
    try_generate_roles(word, labels, roles, 0, targ_syl_struct, best_word_hyps_list, MAX_ROLES_COUNT)

    best_word_hyps_list = sorted(best_word_hyps_list, key=lambda hyp: hyp.mod_pen)

    if len(best_word_hyps_list) > 0:
      # for word_hyp in best_word_hyps_list:
      #   print word_hyp.get_str()
      min_mod_pen = best_word_hyps_list[0].mod_pen
      for hyp in best_word_hyps_list:
        print hyp.get_str()
        if hyp.mod_pen > min_mod_pen:
          break
      print ("Roles generation time: %0.1f" % (time.time() - start_time))

      return best_word_hyps_list

    thres_lvl = thres_lvl + 1
    print "New threshold per role"

  return []


# Timing
start_time = time.time()

# -------- Unit test for target word encoding ------------
# targ_word = "g e _1 . NULL_O e-r _3 . k e _1 . w ei _1 . c i _2"
# targ_word = "g e _1 . NULLO e-n _1 . k e _1 . w ei _1 . c i _2"
# targ_word = "e _2 . l u-n _2 . d ai _4 . NULL_O e-n _1"
# targ_syl_struct = export_syl_struct_of_targ_word(targ_word)
# print ("Target word: %s" % targ_word)
# print ("Target syllabic structure: %s" % targ_syl_struct)

# -------- Unit test for labelling a word ------------
#labels = label_letters(word)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))

# -------- Unit test for checking if a subsyllabic unit is valid ------------
#word = "asterisk"
#print ("Word: %s" % word)
#labels = label_letters(word)
#roles = [NUCLEUS, ONSET, ONSET, NUCLEUS, NUCLEUS_ONSET, NUCLEUS, CODA, CODA]
#print "Valid onset at position 2: " + str(is_valid_subsyllabic_unit(word, labels, roles, 2))
#print "Valid nucleus at position 4: " + str(is_valid_subsyllabic_unit(word, labels, roles, 4))

# -------- Unit test for syllables construction ------------
#word = "palestine"
#labels = label_letters(word)
#roles = [ONSET, NUCLEUS, ONSET, NUCLEUS, CODA_NUCLEUS, ONSET, NUCLEUS, CODA, REMOVE]
#roles = ['O', 'N', 'O', 'O', 'Cd_O', 'Cd', 'N', 'N', 'N']

#constructed_syls = construct_syls(word, labels, roles)
# print ("Word: %s" % word)
# print ("Labels: %s" % str(labels))
# print ("Roles: %s" % str(roles))
# print ("Constructed syllables: %s" % str(constructed_syls))
