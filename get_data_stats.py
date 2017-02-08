data_path = 'data/randomized_training_set_g2p_form.lex'
data_file = open(data_path, 'r')

tone_count = {}
coda_count = {}

CODA = [
'b',
'c',
'ch',
'd',
'f',
'g',
'h',
'j',
'k',
'l',
'm',
'n',
'ng',
'p',
'q',
'r',
's',
'sh',
't',
'w',
'x',
'z',
'zh',
'y',
'NULL_O'
]

for line in data_file:
  [src, targ] = line.split("\t")
  syls = [syl.strip() for syl in targ.split(".")]

  for syl in syls:
    units = [unit.strip() for unit in syl.split()]

    tone = units[-1]
    second_last_unit = units[-2]

    if tone not in tone_count:
      tone_count[tone] = 0
    tone_count[tone] += 1

    if second_last_unit in CODA:
      if second_last_unit not in coda_count:
        coda_count[second_last_unit] = 0
      coda_count[second_last_unit] += 1

print "TONES"
for tone in tone_count:
  print str(tone) + ": " + str(tone_count[tone]) + " - " + str(tone_count[tone] * 100.0 / sum(tone_count.values())) + "%"
for coda in coda_count:
  print str(coda) + ": " + str(coda_count[coda]) + " - " + str(coda_count[coda] * 100.0 / sum(coda_count.values())) + "%"
