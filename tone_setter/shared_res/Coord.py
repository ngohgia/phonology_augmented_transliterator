import copy

from LangAssets import LangAssets

ANY_UNIT  = LangAssets.ANY_UNIT
TERMINAL  = LangAssets.TERMINAL

ONSET     = LangAssets.ONSET
NUCLEUS   = LangAssets.NUCLEUS
CODA      = LangAssets.CODA

PREV_TONE = LangAssets.PREV_TONE
NEXT_TONE = LangAssets.NEXT_TONE

HEAVY_PEN = LangAssets.HEAVY_PEN
MEDIUM_PEN = LangAssets.MEDIUM_PEN
LIGHT_PEN = LangAssets.LIGHT_PEN


class Coord:
  def __init__(self):
    self.coord = {}
    self.coord[ONSET] = TERMINAL
    self.coord[NUCLEUS] = TERMINAL
    self.coord[CODA] = TERMINAL
    self.coord[PREV_TONE] = ANY_UNIT
    self.coord[NEXT_TONE] = ANY_UNIT
    self.val = LangAssets.DEFAULT_TONE

  def __eq__(self, other):
    if isinstance(other, Coord):
      self_coord = self.coord
      other_coord = other.coord
      if self_coords[ONSET] == other_coord[ONSET] and self_coords[NUCLEUS] == other_coord[NUCLEUS] and self_coords[CODA] == other_coord[CODA] and self_coords[PREV_TONE] == other_coord[PREV_TONE] and self_coords[NEXT_TONE] == other_coord[NEXT_TONE]:
        return True
      else:
        return False
    return NotImplemented

  def __ne__(self, other):
    result = self.__eq__(other)
    if result is NotImplemented:
        return result
    return not result

  def encode_syl_to_coord(self, syl, prev_tone, next_tone):
    for idx in range(len(syl.roles)):
      role = syl.roles[idx]
      vie_phoneme = syl.vie_phonemes[idx]
      
      self.coord[role] = vie_phoneme
      self.coord[PREV_TONE] = str(prev_tone)
      self.coord[NEXT_TONE] = str(next_tone)
      self.val = str(syl.tone)

  def __str__(self):
    return str(self.coord[PREV_TONE]) + ", " + self.coord[ONSET] + " | " + self.coord[NUCLEUS] + " |  " + self.coord[CODA] + \
    ", " + str(self.coord[NEXT_TONE]) + " => " + str(self.val)

  def extrapolate(self):
    extrapolated_coords = [[self, 1]]

    prev_tone_less = copy.deepcopy(self)
    prev_tone_less.coord[PREV_TONE] = ANY_UNIT
    extrapolated_coords.append([prev_tone_less, LIGHT_PEN])

    next_tone_less = copy.deepcopy(self)
    next_tone_less.coord[NEXT_TONE] = ANY_UNIT
    extrapolated_coords.append([next_tone_less, LIGHT_PEN])

    tone_less = copy.deepcopy(self)
    tone_less.coord[NEXT_TONE] = ANY_UNIT
    tone_less.coord[PREV_TONE] = ANY_UNIT
    extrapolated_coords.append([tone_less, LIGHT_PEN])

    onset_less = copy.deepcopy(self)
    onset_less.coord[NEXT_TONE] = ANY_UNIT
    onset_less.coord[PREV_TONE] = ANY_UNIT
    onset_less.coord[ONSET] = ANY_UNIT
    extrapolated_coords.append([onset_less, LIGHT_PEN])

    nucleus_less = copy.deepcopy(self)
    nucleus_less.coord[NEXT_TONE] = ANY_UNIT
    nucleus_less.coord[PREV_TONE] = ANY_UNIT
    nucleus_less.coord[NUCLEUS] = ANY_UNIT
    extrapolated_coords.append([onset_less, MEDIUM_PEN])
    
    coda_less = copy.deepcopy(self)
    coda_less.coord[NEXT_TONE] = ANY_UNIT
    coda_less.coord[PREV_TONE] = ANY_UNIT
    coda_less.coord[CODA] = ANY_UNIT
    extrapolated_coords.append([coda_less, HEAVY_PEN])

    single_nucleus = copy.deepcopy(self)
    single_nucleus.coord[NEXT_TONE] = ANY_UNIT
    single_nucleus.coord[PREV_TONE] = ANY_UNIT
    single_nucleus.coord[ONSET] = ANY_UNIT
    single_nucleus.coord[CODA] = ANY_UNIT
    extrapolated_coords.append([single_nucleus, HEAVY_PEN])

    only_coda = copy.deepcopy(self)
    only_coda.coord[NEXT_TONE] = ANY_UNIT
    only_coda.coord[PREV_TONE] = ANY_UNIT
    only_coda.coord[ONSET] = ANY_UNIT
    only_coda.coord[NUCLEUS] = ANY_UNIT
    extrapolated_coords.append([only_coda, LIGHT_PEN])
    
    return extrapolated_coords

# UNIT TEST
# new_coord = Coord()
# new_coord.coord[ONSET] = 'l'
# new_coord.coord[NUCLEUS] = 'Oa'
# new_coord.coord[CODA] = 't'
# new_coord.coord[PREV_TONE] = 2
# new_coord.coord[NEXT_TONE] = 3
# new_coord.val = 2

# all_coords = new_coord.extrapolate()
# for coord in all_coords:
#   coord[0].print_str()
