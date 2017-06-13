import os
import operator
import sys
import subprocess

from shared_res.LangAssets import LangAssets

FINAL = LangAssets.FINAL
ONSET = LangAssets.ONSET
NUCLEUS = LangAssets.NUCLEUS
CODA = LangAssets.CODA

NULL = LangAssets.NULL

MERGER = LangAssets.MERGER

FINAL_SPLIT_SMOOTH = LangAssets.FINAL_SPLIT_SMOOTH

def read_split_lex_file(lex_file_path, only_final_train_file):
  all_words = []
  simple_finals = []
  complex_finals = []
  with open(lex_file_path, 'r') as lex_file, open(only_final_train_file, 'w') as fh:
    for line in lex_file:
      [src_syls_str, roles_str, targ_syls_str] = line.split("\t")[2:5]

      src_syls = [[unit.strip() for unit in src_syl.strip().split(" ")] for src_syl in src_syls_str[1:len(src_syls_str)-1].split("] [")]
      roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
      targ_syls = [[unit.strip() for unit in targ_syl.split(" ")] for targ_syl in targ_syls_str.split(" . ")]

      print str(src_syls) + "\t" + str(roles) + "\t" + str(targ_syls)
      for i in range(len(roles)):
        syl_roles = roles[i]
        src_syl = src_syls[i]
        targ_syl = targ_syls[i]
        for j in range(len(syl_roles)):
          if syl_roles[j] == NUCLEUS:
            print >> fh, src_syl[j] + "\t" + targ_syl[j]
            new_entry = (src_syl[j], targ_syl[j])
            if MERGER not in targ_syl[j]:
              if new_entry not in simple_finals:
                simple_finals.append(new_entry)
            else:
              if new_entry not in complex_finals:
                complex_finals.append(new_entry)

  complex_final_dict = get_final_to_onc_mapping(simple_finals, complex_finals)
  return complex_final_dict

def build_final_splitting_model(lex_file_path, final_train_file, complex_final_dict):
  finals_data = []
  with open(lex_file_path, 'r') as lex_file, open(final_train_file, 'w') as fh:
    for line in lex_file:
      [src_syls_str, roles_str, targ_syls_str] = line.split("\t")[2:5]

      src_syls = [[unit.strip() for unit in src_syl.strip().split(" ")] for src_syl in src_syls_str[1:len(src_syls_str)-1].split("] [")]
      roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
      targ_syls = [[unit.strip() for unit in targ_syl.split(" ")] for targ_syl in targ_syls_str.split(" . ")]

      # print str(src_syls) + "\t" + str(roles) + "\t" + str(targ_syls)
      for i in range(len(roles)):
        syl_roles = roles[i]
        src_syl = src_syls[i]
        targ_syl = targ_syls[i]

        old_syl = {}
        new_final = ''
        for j in range(len(syl_roles)):
          if syl_roles[j] == NUCLEUS:
            src_nucleus = src_syl[j]
            targ_nucleus = targ_syl[j] 

            old_syl[NUCLEUS] = src_nucleus
            if MERGER in targ_nucleus and len(src_nucleus) > 1:
              new_final = (src_nucleus,)
              key = (src_nucleus, targ_nucleus)
              if FINAL not in complex_final_dict[key]:
                new_final = (complex_final_dict[key][NUCLEUS][0], complex_final_dict[key][CODA][0])
          elif syl_roles[j] == ONSET:
            src_init = src_syl[j]
            old_syl[ONSET] = src_init
          else:
            print("Wrong subsyllabic role, neither Onset or Nucleus!")
        if len(new_final) > 0:
          finals_data.append((old_syl, new_final))
  unigrams_dist, bigrams_dist = construct_language_models(finals_data)

  finals_model = []
  finals_model.append(unigrams_dist)
  finals_model.append(bigrams_dist)
  return finals_model


def construct_language_models(finals_data):
  unigrams_dist = {}
  bigrams_dist = {}

  for entry in finals_data:
    old_syl, new_final = entry
    bigram_key = [NULL, NULL]
    if ONSET in old_syl:
      bigram_key[0] = old_syl[ONSET]
    bigram_key[-1] = old_syl[NUCLEUS]
    
    bigram_key = tuple(bigram_key)
    unigram_key = (old_syl[NUCLEUS],)

    if unigram_key not in unigrams_dist:
      unigrams_dist[unigram_key] = {}
    if new_final not in unigrams_dist[unigram_key]:
      unigrams_dist[unigram_key][new_final] = 0.0
    unigrams_dist[unigram_key][new_final] += 1

    if bigram_key not in bigrams_dist:
      bigrams_dist[bigram_key] = {}
    if new_final not in bigrams_dist[bigram_key]:
      bigrams_dist[bigram_key][new_final] = 0.0
    bigrams_dist[bigram_key][new_final] += 1

  for unigram_key in unigrams_dist:
    sum_vals = sum(unigrams_dist[unigram_key].values())
    for final in unigrams_dist[unigram_key]:
      unigrams_dist[unigram_key][final] /= sum_vals
  for bigram_key in bigrams_dist:
    sum_vals = sum(bigrams_dist[bigram_key].values())
    for final in bigrams_dist[bigram_key]:
      bigrams_dist[bigram_key][final] /= sum_vals
   
  return unigrams_dist, bigrams_dist

def combine_dists(unigrams_dist, bigrams_dist):
  bigrams_model = {}
  for bigram_key in bigrams_dist:
    bigrams_model[bigram_key] = {}
    nucleus_key = (bigram_key[-1], )
   
    if nucleus_key not in unigrams_dist: 
      bigrams_model[bigram_key] = bigrams_dist[bigram_key]
    else:
      for final in unigrams_dist[nucleus_key]:
        if final in bigrams_dist[bigram_key]:
          bigrams_model[bigram_key][final] = bigrams_dist[bigram_key][final] * FINAL_SPLIT_SMOOTH + unigrams_dist[nucleus_key][final] * (1 - FINAL_SPLIT_SMOOTH)
        else:
          bigrams_model[bigram_key][final] = unigrams_dist[nucleus_key][final] * (1 - FINAL_SPLIT_SMOOTH)

    sum_vals = sum(bigrams_model[bigram_key].values())
    for final in bigrams_model[bigram_key]:
      bigrams_model[bigram_key][final] /= sum_vals
  return bigrams_model

def split_final(init_final_with_roles_file_path, final_splitting_model, onc_with_roles_file_path):
  unigram_dist, bigram_dist = final_splitting_model

  with open(init_final_with_roles_file_path, 'r') as ifh:
    for line in ifh:
      src, roles = [part.strip() for part in line.split('\t')]
      src_syls = [s.strip() for s in src.split('.')]
      role_syls = [s.strip() for s in roles.split('.')]

      for i in range(len(role_syls)):
        src_syl = [s.strip() for s in src_syls[i].split()]
        syl_roles = tuple([s.strip() for s in role_syls[i].split()])

        if len(syl_roles) == 2:
          key = tuple(src_syl)
        else:
          key = tuple([NULL] + src_syl)
        nucleus = (src_syl[-1], )
        if key not in bigram_dist:
          if nucleus in unigram_dist:
            bigram_dist[key] = {}
          else:  # simple nucleus, no splitting
            bigram_dist[key] = { nucleus : 1.0 }
  bigrams_model = combine_dists(unigram_dist, bigram_dist)

  with open(init_final_with_roles_file_path, 'r') as ifh, open(onc_with_roles_file_path, 'w') as ofh:
    for line in ifh:
      src, roles = [part.strip() for part in line.split('\t')]
      src_syls = [s.strip() for s in src.split('.')]
      role_syls = [s.strip() for s in roles.split('.')]

      new_src_syls = []
      new_role_syls = []
      for i in range(len(role_syls)):
        src_syl = [s.strip() for s in src_syls[i].split()]
        syl_roles = [s.strip() for s in role_syls[i].split()]

        if len(syl_roles) == 2:
          key = tuple(src_syl)
    
          sorted_items = sorted(bigrams_model[key].items(), key=operator.itemgetter(1), reverse=True)
          new_final = sorted_items[0][0]
          if len(new_final) == 1:
            src_syl[-1] = new_final[0]
          else:
            syl_roles.append(CODA)
            src_syl = [src_syl[0]] + list(new_final)
        else:
          key = tuple([NULL] + src_syl)
          sorted_items = sorted(bigrams_model[key].items(), key=operator.itemgetter(1), reverse=True)
          new_final = sorted_items[0][0]
          src_syl[-1] = new_final[0]
        print src_syl
        new_src_syls.append(' '.join(src_syl))
        new_role_syls.append(' '.join(syl_roles))
      print >> ofh, '\t'.join([' . '.join(new_src_syls), ' . '.join(new_role_syls)])
  
    
        


def get_final_to_onc_mapping(simple_finals, complex_finals):
  simple_nuclei_dict_by_targ = {}
  complex_nuclei_dict = {}
  for e in simple_finals:
    src, targ = e
    if targ not in simple_nuclei_dict_by_targ:
      simple_nuclei_dict_by_targ[targ] = []
    simple_nuclei_dict_by_targ[targ].append(src)
  for e in complex_finals:
    src, targ = e
    [nucleus, coda] = targ.split(MERGER)

    complex_nuclei_dict[e] = { FINAL: e }
    if nucleus in simple_nuclei_dict_by_targ:
      src_nucleus = ''
      src_coda = ''
      for ref_src in simple_nuclei_dict_by_targ[nucleus]:
        if src.find(ref_src) == 0:
          if len(ref_src) > len(src_nucleus):
            src_nucleus = ref_src
            src_coda = src[len(ref_src):]
      if len(src_nucleus) > 0 and len(src_coda) > 0:
        complex_nuclei_dict[e] = { NUCLEUS: (src_nucleus, nucleus), CODA: (src_coda, coda) }

  # print ""
  # for e in simple_finals:
  #   print e

  # print ""
  # for src in complex_nuclei_dict:
  #   print str(src) + ": " + str(complex_nuclei_dict[src])
  # sys.exit(1)

  return complex_nuclei_dict

def split_hyp_file_further(lex_file_path, complex_finals_dict, new_lex_file): 
  with open(lex_file_path, 'r') as lex_file, open(new_lex_file, 'w') as fh:
    for line in lex_file:
      [src_syls_str, roles_str, targ_syls_str] = line.split("\t")[2:5]

      src_syls = [[unit.strip() for unit in src_syl.strip().split(" ")] for src_syl in src_syls_str[1:len(src_syls_str)-1].split("] [")]
      roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
      targ_syls = [[unit.strip() for unit in targ_syl.split(" ")] for targ_syl in targ_syls_str.split(" . ")]

      new_src_syls = []
      new_roles = []
      new_targ_syls = []
      for i in range(len(roles)):
        syl_roles = roles[i]
        src_syl = src_syls[i]
        targ_syl = targ_syls[i]

        new_syl_roles = []
        new_src_syl = []
        new_targ_syl = []
        for j in range(len(syl_roles)):
          if syl_roles[j] == ONSET:
            new_syl_roles.append(ONSET)
            new_src_syl.append(src_syl[j])
            new_targ_syl.append(targ_syl[j])
          elif syl_roles[j] == NUCLEUS:
            new_syl_roles.append(NUCLEUS)

            src_nucleus = src_syl[j]
            targ_nucleus = targ_syl[j]
            if MERGER in targ_nucleus:
              key = (src_nucleus, targ_nucleus)

              new_final = complex_finals_dict[key]
              if FINAL in new_final:
                new_src_syl.append(src_syl[j])
                new_targ_syl.append(targ_syl[j])
              else:
                new_syl_roles.append(CODA)
                new_src_syl = new_src_syl + [complex_finals_dict[key][NUCLEUS][0], complex_finals_dict[key][CODA][0]]
                new_targ_syl = new_targ_syl + targ_syl[j].split(MERGER)
            else:
              new_src_syl.append(src_syl[j])
              new_targ_syl.append(targ_syl[j])
        new_targ_syl.append(targ_syl[-1])

        new_src_syls.append(' '.join(new_src_syl))
        new_targ_syls.append(' '.join(new_targ_syl))
        new_roles.append(' '.join(new_syl_roles))

      new_src_syls_str = ' . '.join(new_src_syls)
      new_targ_syls_str = ' . '.join(new_targ_syls)
      new_roles_str = ' . '.join(new_roles)
      print >> fh, '\t'.join([new_src_syls_str, new_roles_str, new_targ_syls_str])


def train_final_splitting(hyp_file, new_hyp_file, run_dir):
  only_only_final_train_file = os.path.join(run_dir, 'only_final_train.txt')
  final_train_file = os.path.join(run_dir, 'final_train.txt')

  complex_final_dict = read_split_lex_file(hyp_file, only_only_final_train_file)

  split_hyp_file_further(hyp_file, complex_final_dict, new_hyp_file)
  finals_model = build_final_splitting_model(hyp_file, final_train_file, complex_final_dict)
  return finals_model
