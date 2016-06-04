import sys

def read_original_data(input_file):
    input = open(input_file, "r")

    src_words = []
    targ_words = []
    for line in input:
        [src, targ] = line.strip().split("\t")
        src_word = [syl.strip() for syl in src.split(" . ")]
        targ_word = [syl.strip() for syl in targ.split(" . ")]
        if len(src_word) != len(targ_word):
            print ("ERROR! Mismatched numeber of syllables in entry %s" % line.strip())
            sys.exit(1)
        src_words.append(src_word)
        targ_words.append(targ_word)

    input.close()
    return [src_words, targ_words]

def create_new_data(src_words, targ_words):
    entries = []
    for i in range(len(src_words)):
        src_syls = src_words[i]
        targ_syls = targ_words[i]
        for j in range(len(src_syls)):
            entry = src_syls[j] + "\t" + targ_syls[j]
            if entry not in entries:
                entries.append(entry)

    return entries

def write_to_files(entries, output_files_name):
    src_syl = open(output_files_name + ".src_syl.txt", "w")
    targ_syl = open(output_files_name + ".targ_syl.txt", "w")
    
    for entry in entries:
        [src, targ] = entry.split("\t")
        src_syl.write(src + "\n")
        targ_syl.write(targ + "\n")

    src_syl.close()
    targ_syl.close()

def create_reformatted_data(input_file, output_files_name):
    [src_words, targ_words] = read_original_data(input_file)
    entries = create_new_data(src_words, targ_words)
    write_to_files(entries, output_files_name)
