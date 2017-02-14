# coding=utf-8

import os

class LangAssets:
  N_GRAM_LEN = 5

  # Possible labels of an alphabet
  VOWEL = "V"
  CONSONANT = "C"
  ANY = "ANY"

  DELIMITER = "#"

  GENERIC_VOWEL = "@"

  # All possible roles of an alphabet
  ONSET = "O"
  NUCLEUS = "N"
  CODA = "Cd"
  ONSET_NUCLEUS = "O_N"
  NUCLEUS_ONSET = "N_O"
  NUCLEUS_NUCLEUS = "N_N"
  NUCLEUS_CODA = "N_Cd"
  CODA_ONSET = "Cd_O"
  CODA_NUCLEUS = "Cd_N"
  CODA_CODA = "Cd_Cd"
  ONSET_NUCLEUS_CODA = "O_N_Cd"
  CODA_ONSET_NUCLEUS = "Cd_O_N"
  REMOVE = "R"

  # All possible roles
  POSSIBLE_ROLES = [ONSET, NUCLEUS, CODA, 
    ONSET_NUCLEUS, NUCLEUS_ONSET, NUCLEUS_NUCLEUS,
    NUCLEUS_CODA, CODA_ONSET, CODA_NUCLEUS, CODA_CODA, ONSET_NUCLEUS_CODA, CODA_ONSET_NUCLEUS, REMOVE]

  # All valid roles for a vowel
  VALID_VOWEL_ROLES = [ONSET, NUCLEUS, CODA,
      ONSET_NUCLEUS, NUCLEUS_NUCLEUS, NUCLEUS_CODA, REMOVE]

  # All valid roles for a consonant
  # A consonant assigned the ONSET_NUCLEUS role can only form
  # an independent syllable
  VALID_CONSO_ROLES = [ONSET, NUCLEUS, CODA, CODA_NUCLEUS, NUCLEUS_ONSET,
      ONSET_NUCLEUS, NUCLEUS_NUCLEUS, NUCLEUS_CODA, CODA_ONSET, REMOVE]

  # SET OF CONSONANTS ALLOWED TO PRECEDE SCHWA
  VALID_CONSO_PRECED_SCHWA = ['p', 'w', 'r', 'b', 't', 'd', 'k', 'g', 's', 'f', 'z', 'q']

  def __init__(self):
    cur_dir = os.path.dirname(__file__) + "/"

    self.valid_src_vowels = self.get_valid_units(cur_dir + "valid_src_vowels.txt")
    self.valid_src_consos = self.get_valid_units(cur_dir + "valid_src_consos.txt")

    self.valid_targ_vowels = self.get_valid_units(cur_dir + "valid_targ_vowels.txt")
    self.valid_targ_consos = self.get_valid_units(cur_dir + "valid_targ_consos.txt")

    self.valid_src_codas = self.get_valid_units(cur_dir + "valid_src_codas.txt")
    self.valid_src_nuclei = self.get_valid_units(cur_dir + "valid_src_nuclei.txt")
    self.valid_src_onsets = self.get_valid_units(cur_dir + "valid_src_onsets.txt")

  def get_valid_units(self, input_fname):
    input_file = open(input_fname, "r")
    result = []

    for line in input_file:
      if line.strip() not in result:
        result.append(line.strip())
    return result
