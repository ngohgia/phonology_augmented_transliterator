import copy

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GRAPHEME = "G"
PHONEME = "P"
PREV_SYL_NUCLEUS = "PSN"
PREV_SYL_CODA = "PSC"

class Coord:
  def __init__(self):
    self.coords = {}
    self.coords[PREV_SYL_NUCLEUS] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[PREV_SYL_CODA] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[ONSET] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[NUCLEUS] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[CODA] = {GRAPHEME: '#', PHONEME: '#'}
    self.vals = {ONSET: '#', NUCLEUS: '#', CODA: '#'}

  def encode_unit_to_coord(self, syl, prev_syl_coord):
    if prev_syl_coord != None:
      self.coords[PREV_SYL_NUCLEUS][GRAPHEME] = prev_syl_coord.coords[NUCLEUS][GRAPHEME]
      self.coords[PREV_SYL_NUCLEUS][PHONEME] = prev_syl_coord.coords[NUCLEUS][PHONEME]
      self.coords[PREV_SYL_CODA][GRAPHEME] = prev_syl_coord.coords[CODA][GRAPHEME]
      self.coords[PREV_SYL_CODA][PHONEME] = prev_syl_coord.coords[CODA][PHONEME]

    for idx in range(len(syl.roles)):
      role = syl.roles[idx]
      grapheme = syl.src_graphs[idx]
      phoneme = syl.src_phons[idx]
      if phoneme == "":
        phoneme = "_"

      self.coords[role][GRAPHEME] = grapheme
      self.coords[role][PHONEME] = phoneme

      self.vals[role] = syl.targ_phons[idx]

  def gp_str(self, gp):
    return "<" + gp[GRAPHEME] + ">/" + gp[PHONEME] + "/"

  def print_str(self):
    gp = self.coords
    print self.gp_str(gp[PREV_SYL_NUCLEUS]) + " | " + self.gp_str(gp[PREV_SYL_CODA]) + " @ " \
    + self.gp_str(gp[ONSET]) + " | " + self.gp_str(gp[NUCLEUS]) + " |  " + self.gp_str(gp[CODA]) \
    + " => " + self.vals[ONSET] + " | " + self.vals[NUCLEUS] + " | " + self.vals[CODA]

  def to_list(self):
    coords = self.coords
    vals = self.vals

    result = [coords[PREV_SYL_NUCLEUS][GRAPHEME], coords[PREV_SYL_NUCLEUS][PHONEME], \
      coords[PREV_SYL_CODA][GRAPHEME], coords[PREV_SYL_CODA][PHONEME], \
      coords[ONSET][GRAPHEME], coords[ONSET][PHONEME], \
      coords[NUCLEUS][GRAPHEME], coords[NUCLEUS][PHONEME], \
      coords[CODA][GRAPHEME], coords[CODA][PHONEME] , \
      vals[ONSET], vals[NUCLEUS], vals[CODA]]
    return result

  def list_to_coord(self, unit_list):
    new_coord = Coord()
    new_coord.coords[PREV_SYL_NUCLEUS][GRAPHEME] = unit_list[0]
    new_coord.coords[PREV_SYL_NUCLEUS][PHONEME] = unit_list[1]
    
    new_coord.coords[PREV_SYL_CODA][GRAPHEME] = unit_list[2]
    new_coord.coords[PREV_SYL_CODA][PHONEME] = unit_list[3]

    new_coord.coords[ONSET][GRAPHEME] = unit_list[4]
    new_coord.coords[ONSET][PHONEME] = unit_list[5]

    new_coord.coords[NUCLEUS][GRAPHEME] = unit_list[6]
    new_coord.coords[NUCLEUS][PHONEME] = unit_list[7]

    new_coord.coords[CODA][GRAPHEME] = unit_list[8]
    new_coord.coords[CODA][PHONEME] = unit_list[9]

    new_coord.vals[ONSET] = unit_list[10]
    new_coord.vals[NUCLEUS] = unit_list[11]
    new_coord.vals[CODA] = unit_list[12]

    return new_coord
  
  def extrapolate(self, unit_list, all_coords):
    self.extrapolate_within_syl(unit_list, all_coords, 4)
    
    # hide previous syllable's nucleus
    new_unit_list = ["_", "_"] + unit_list[2:len(unit_list)]
    self.extrapolate_within_syl(new_unit_list, all_coords, 4)
    
    # hide previous syllable's coda
    new_unit_list = unit_list[0:len(unit_list)]  + ["_", "_"] + unit_list[4:len(unit_list)]
    self.extrapolate_within_syl(new_unit_list, all_coords, 4)
    
   # hide both previous syllable's nucleus and coda
    new_unit_list = ["_", "_", "_", "_"] + unit_list[4:len(unit_list)]
    self.extrapolate_within_syl(new_unit_list, all_coords, 4)

  def extrapolate_within_syl(self, unit_list, all_coords, pos):
    if pos > 10:
      return
    else:
      new_coord = self.list_to_coord(unit_list)
      completed_coords = self.assign_val_to_extrapolated_coord(new_coord)
      for coord in completed_coords:
        all_coords.append(coord)

      for i in range(pos, len(unit_list)):
        if unit_list[i] == "#" and unit_list[i-1] != "#":
          self.extrapolate_within_syl(unit_list[0:i] + ["_", "_"] + unit_list[i+2:len(unit_list)], all_coords, i+1)
        elif unit_list[i] != "_": 
          self.extrapolate_within_syl(unit_list[0:i] + ["_"] + unit_list[i+1:len(unit_list)], all_coords, i+1)


  def assign_val_to_extrapolated_coord(self, coord):
    results = []
    vals = coord.vals
    coords = coord.coords

    for unit in vals:
      if vals[unit] != "#" and coords[unit][GRAPHEME] != "#" and coords[unit][PHONEME] != "#" \
      and (coords[unit][GRAPHEME] != "_" or coords[unit][PHONEME] != "_"):        
        new_vals = {ONSET: "#", NUCLEUS: "#", CODA: "#"}
        new_vals[unit] = vals[unit]

        new_coord = copy.deepcopy(coord)
        new_coord.vals = new_vals

        results.append(new_coord)

    return results

# # Unit test
# new_coord = Coord()
# new_coord.coords[PREV_SYL_NUCLEUS] = {GRAPHEME: 'e', PHONEME: 'EH'}
# new_coord.coords[PREV_SYL_CODA] = {GRAPHEME: 'n', PHONEME: 'N'}
# new_coord.coords[ONSET] = {GRAPHEME: 'l', PHONEME: 'L'}
# new_coord.coords[NUCLEUS] = {GRAPHEME: 'oa', PHONEME: 'OW'}
# new_coord.coords[CODA] = {GRAPHEME: 'd', PHONEME: 'D'}
# new_coord.vals = {ONSET: '#', NUCLEUS: '#', CODA: 'd'}
# 
# unit_list = new_coord.to_list()
# print unit_list
# all_coords = []
# new_coord.extrapolate(unit_list, all_coords)
# 
# print len(all_coords)
# for coord in all_coords:
#   coord.print_str()
