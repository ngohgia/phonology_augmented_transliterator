import sys
import os
import time
import logging

from syl_struct_generator.SylStructGenerator import *
from approx_phone_alignment.ApproxPhoneAlignment import get_approx_phone_alignment
from approx_phone_alignment.ApproxPhoneAlignment import score_hyp_with_phone_alignment
from src_phons_generator.SrcPhonsGenerator import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

if __name__ == '__main__':
  try:
    script, training_lex_path, run_dir, t2p_decoder = sys.argv
  except ValueError:
    print "Syntax: GetBestRules.py \t training_lex_path \t run_dir \t t2p_decoder"
    sys.exit(1)

#----------------------------------- LOG ---------------------------------------#
log_file = os.path.abspath(os.path.join(run_dir, "log", "GetBestRules_log"))
logging.basicConfig(filename= log_file, level= logging.DEBUG, format='%(message)s')

unresolved_file = open(os.path.abspath(os.path.join(run_dir, "unresolved_words.txt")), "w")
least_mod_pen_file = open(os.path.abspath(os.path.join(run_dir, "least_mod_pen.txt")), "w")

lex_hyp_file = open(os.path.abspath(os.path.join(run_dir, "lex_hyp.txt")), "w")

simple_words_hyp_path = os.path.abspath(os.path.join(run_dir, "simple_words_hyp.txt"))
complex_words_hyp_path = os.path.abspath(os.path.join(run_dir, "complex_words_hyp.txt"))
simple_words_hyp_file = open(simple_words_hyp_path, "w")
complex_words_hyp_file = open(complex_words_hyp_path, "w")

split_words_file = open(os.path.abspath(os.path.join(run_dir, "split_words.txt")), "w")

#-------------------------------------------------------------------------------#
t2p_decoder_path = os.path.abspath(t2p_decoder)

training_lex_file = open(training_lex_path, "r")
training_lex = []

# Get words from training-dev lex file
for line in training_lex_file:
  training_lex.append([part for part in line.split("\t")])
training_lex_file.close()

def add_targ_word_to_best_word_hyps(best_word_hyps_list, targ_word, targ_syl_struct):
  for idx in range(len(best_word_hyps_list)):
    best_word_hyps_list[idx].ref_targ = targ_word
    targ_syls = targ_word.split(".")
    toneless_targ_syls = [(" ").join(syl.strip().split(" ")) for syl in targ_syls]
    best_word_hyps_list[idx].toneless_targ_ref = toneless_targ_syls
    best_word_hyps_list[idx].targ_roles = targ_syl_struct


#------- GET ALL THE BEST WORD HYPOTHESIS FROM A SINGLE TRAINING FILE -----------#
def get_best_hyps_from_single_training(training_lex):
  simple_words_hyps = []
  complex_words_hyps = []

  for idx in range(len(training_lex)):
    start_time = time.time()

    report("\n#----------------------------------------------#\n")
    least_mod_pen_file.write("\n#----------------------------------------------#\n")
    word = training_lex[idx][0]
    labels = label_letters(word)

    # TRY GENERATING THE ORIGINAL WORD
    # Format targ words
    targ_word = training_lex[idx][-1].strip()
    targ_syl_struct = export_syl_struct_of_targ_word(targ_word)
    print targ_word
    print targ_syl_struct

    best_word_hyps_list = []
    # Generate possible roles for letters in the foreign word
    best_word_hyps_list = generate_roles(word, labels, targ_syl_struct)
    add_targ_word_to_best_word_hyps(best_word_hyps_list, targ_word, targ_syl_struct)
    
    # TRY BACK OFF THE FOREIGN WORD
    new_targ_word = back_off_words_with_glides(targ_word)
    if new_targ_word != None:
      targ_syl_struct = export_syl_struct_of_targ_word(new_targ_word)
      new_best_word_hyps_list = []
      # Generate possible roles for letters in the foreign word
      new_best_word_hyps_list = generate_roles(word, labels, targ_syl_struct)
      add_targ_word_to_best_word_hyps(new_best_word_hyps_list, new_targ_word, targ_syl_struct)
      best_word_hyps_list = best_word_hyps_list + new_best_word_hyps_list

    if len(best_word_hyps_list) == 0:
      report("No hypothesis found for %s" % word)
      unresolved_file.write("\t".join(training_lex[idx]))
    else:
      for word_hyp in best_word_hyps_list:
        # Count the number of generic vowels in the word
        word_hyp.count_generic_vowel()
        report(word_hyp.get_str())

      report("Roles generation time: %0.1f" % (time.time() - start_time))

      # SCORING:
      # Least compound modification penalty
      best_hyps = get_least_mod_pen_hyps(best_word_hyps_list)

      # Collect all the simple words that are sure to be correctly split
      if len(best_hyps) == 1 and best_hyps[0].compound_role_count == 0 \
      and best_hyps[0].removal_count == 0 \
      and best_hyps[0].generic_vowel_count == 0:
        hyp = best_hyps[0]
        simple_words_hyps.append(hyp)
        simple_words_hyp_file.write(word + "\t" + " ".join(hyp.roles) +
        "\t" + str(hyp.reconstructed_word) + "\t" + \
        hyp.reconstructed_word.get_encoded_units() + "\t" +
        targ_word.strip() + "\n")
      else:
        # Solve the more complicated words
        best_hyps = sorted(best_word_hyps_list, key=lambda hyp: hyp.mod_pen)
        complex_words_hyps.append(best_hyps[0:10])


  simple_words_t2p_input_path = os.path.abspath(os.path.join(run_dir, "simple_words_t2p_input.txt"))
  complex_words_t2p_input_path = os.path.abspath(os.path.join(run_dir, "complex_words_hyp_t2p_input.txt"))
  complex_words_t2p_output_path = os.path.abspath(os.path.join(run_dir, "complex_words_hyp_t2p_output.txt"))

  # Get t2p output on simple words
  create_input_for_t2p(simple_words_hyps, simple_words_t2p_input_path)

  # Get t2p output on complex words
  all_complex_words = []
  for word_hyps in complex_words_hyps:
    all_complex_words.append(word_hyps[0])
  create_input_for_t2p(all_complex_words, complex_words_t2p_input_path)

  get_phons_with_t2p(t2p_decoder_path, complex_words_t2p_input_path, complex_words_t2p_output_path)
  all_phons = get_src_phons(complex_words_t2p_output_path)

  for i in range(len(complex_words_hyps)):
    for j in range(len(complex_words_hyps[i])):
      complex_words_hyps[i][j].original_en_phonemes = all_phons[i]


  simple_words_hyp_file.close()
  complex_words_hyp_file.close()

  # Get approximate phoneme alignment using simple words
  approx_phone_alignments = get_approx_phone_alignment(simple_words_hyp_path, run_dir)

  best_complex_words_hyps = []

  # Score the hypothesis on complex words
  report("SCORE HYP WITH PHONE ALIGMENTS")
  for word_hyps in complex_words_hyps:
    best_hyp = score_hyp_with_phone_alignment(word_hyps, approx_phone_alignments)
    best_complex_words_hyps.append(best_hyp)
    for hyp in best_complex_words_hyps:
      print hyp.get_str()

  best_hyps = simple_words_hyps + best_complex_words_hyps
  for hyp in best_hyps:
    if hyp.phone_alignment_pen <= 2:
      split_words_file.write(str(hyp.reconstructed_word) + "\n")
      least_mod_pen_file.write(hyp.get_str())
      lex_hyp_file.write(hyp.original + "\t" + " ".join(hyp.roles) +
        "\t" + str(hyp.reconstructed_word) + "\t" + \
        hyp.reconstructed_word.get_encoded_units() + "\t" +
        hyp.ref_targ + "\n")


#------- GET HYPOTHESIS WITH LEAST MODIFICATION PENALTY --------------------#
# Reconstructed word with the shortest levenstein distance is favored
# Implicitly, this scoreing favors single over compound roles (eg. Cd > Cd_O)
def get_least_mod_pen_hyps(best_word_hyps_list):
  word_hyps_sorted_by_mod_pen = sorted(best_word_hyps_list, key=lambda hyp: hyp.mod_pen)
  min_pen = word_hyps_sorted_by_mod_pen[0].mod_pen
  best_mod_pen_hyps = []
  for hyp in word_hyps_sorted_by_mod_pen:
    if hyp.mod_pen > min_pen:
      break
    else:
      best_mod_pen_hyps.append(hyp)

  return best_mod_pen_hyps

#------- GET HYPOTHESIS WITH LEAST REMOVAL COUNT --------------------#
# Reconstructed word with the fewest number of letters removed from the
# original word is favored

def get_least_removal_count_hyps(hyps_list):
  sorted_list = sorted(hyps_list, key=lambda hyp: hyp.removal_count)
  min_removal_count = sorted_list[0].removal_count
  best_hyps = []
  for hyp in sorted_list:
    if hyp.removal_count > min_removal_count:
      break
    else:
      best_hyps.append(hyp)

  return best_hyps

#------- GET HYPOTHESIS WITH FEWEST COMPOUND ROLES COUNT --------------------#
# Reconstructed word with the fewest number of letters assigned a compound
# role is favoreds
def get_least_compound_role_count_hyps(hyps_list):
  sorted_list = sorted(hyps_list, key=lambda hyp: hyp.compound_role_count)
  min_compound_role_count = sorted_list[0].compound_role_count
  best_hyps = []
  for hyp in sorted_list:
    if hyp.compound_role_count > min_compound_role_count:
      break
    else:
      best_hyps.append(hyp)

  return best_hyps

#------- BACK OFF ENTRIES WITH GLIDES --------------------#
# If no hypothesis can be found for a word with glides, merge the glides to the succeeding vowels
def back_off_words_with_glides(targ_word):
  GLIDES = ['y', 'w']
  DASH = '-'

  syls = [part.strip() for part in targ_word.split('.')]
  new_syls = []
  for syl in syls:
    units = [unit.strip() for unit in syl.split()]
    new_units = []
    if units[0] in GLIDES:
      new_units.append(units[0] + '-' + units[1])
      for i in range(2, len(units)):
        new_units.append(units[i])
    else:
      new_units = units
    new_syls.append(' '.join(new_units))
  new_targ_word = ' . '.join(new_syls)
  if new_targ_word != targ_word:
    return new_targ_word
  else:
    return None

# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)

get_best_hyps_from_single_training(training_lex)
unresolved_file.close()
split_words_file.close()
