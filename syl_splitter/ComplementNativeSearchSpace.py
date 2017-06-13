import os
import math
import copy
import sys
import shutil
import csv
import time
import logging
import pickle

from LangAssets.LangAssets import LangAssets
from LangAssets.WordHyp import WordHyp
from LangAssets.SearchSpace import SearchCoord
from LangAssets.Rule import Rule
from GetSearchSpace import get_search_space_from_lex_hyps
from GetSearchSpace import read_lex_hyps_from_file

# if __name__ == '__main__':
#   try:
#     script, native_lex_hyp_path, complementary_lex_hyp_path, output_lex_hyp_path, run_dir = sys.argv
#   except ValueError:
#     print "Syntax: ComplementNativeSearchSpace.py    native_lex_hyp       complementary_lex_hyp     output_lex_hyp_path     run_dir"
#     sys.exit(1)
# 
# run_dir = os.path.abspath(run_dir)
# 
# native_lex_hyp_path = os.path.abspath(native_lex_hyp_path)
# complementary_lex_hyp_path = os.path.abspath(complementary_lex_hyp_path)
# output_lex_hyp_path = os.path.abspath(output_lex_hyp_path)
# 
# #----------------------------------- LOG ---------------------------------------#
# log_file = os.path.abspath(os.path.join(run_dir, "log", "ComplementNativeSearchSpace_log"))
# logging.basicConfig(filename= log_file, level= logging.DEBUG, format='%(message)s')

#---------------- GET SEARCH SPACE ------------------#
# Retrieve the best search space from the training + dev
def get_search_space(lex_hyp_path):
  start_time = time.time()
  print "Get search space"
  lex_hyp = read_lex_hyps_from_file(lex_hyp_path)
  [search_space, valid_units] = get_search_space_from_lex_hyps(lex_hyp)
  print "Elapsed: " + str(time.time() - start_time)
  return search_space, valid_units

def combine_search_spaces(native_search_space, complementary_search_space, interpolation):
  combined_search_space = copy.deepcopy(complementary_search_space)
  for item in combined_search_space.space:
    if item in native_search_space.space:
      for targ in combined_search_space.space[item]:
        if targ in native_search_space.space[item]:
          combined_search_space.space[item][targ] = interpolation * combined_search_space.space[item][targ] + (1-interpolation) * native_search_space.space[item][targ]
      tmp_sum = sum(combined_search_space.space[item].values())

  for item in native_search_space.space:
    if item not in combined_search_space.space:
      combined_search_space.space[item] = native_search_space.space[item]
  combined_search_space.normalized()
  return combined_search_space
  
  for item in complementary_search_space.space:
    print str(item) + "\t" + str(sum(complementary_search_space.space[item].values()))

  # for item in complementary_search_space.space:
  #   if item in native_search_space.space:
  #     print item 
  #     print "\t" + str(combined_search_space.space[item])
  #     print "\t" + str(complementary_search_space.space[item])
  #     print "\t" + str(native_search_space.space[item])
