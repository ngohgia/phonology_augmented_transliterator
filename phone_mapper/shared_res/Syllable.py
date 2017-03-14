SRC_VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']

class Syllable:
  def __init__(self):
    self.src_graphs = []
    self.roles = []
    self.src_phons = []
    self.targ_phons = []

  def create_new_syl(self, src_graphs, roles, src_phons, targ_phons):
    self.src_graphs = src_graphs
    self.targ_phons = targ_phons
    self.src_phons = src_phons 
    self.roles = roles

  def get_src_graphs_str(self):
    return (" ").join(self.src_graphs)

  def get_roles_str(self):
    return (" ").join(self.roles)

  def get_src_phons_str(self):
    print str(self.src_phons)
    return (" - ").join(self.src_phons)

  def get_targ_phons_str(self):
    return (" ").join(self.targ_phons)

  def expand_nucleus_coda(self, src_graphs, targ_phons):
    MERGER = '-'
    new_src_graphs = []
    new_targ_phons = []

    src_final_pos = len(src_graphs)-1

    for i in range(len(src_graphs)):
      if i == src_final_pos:
        src_final = src_graphs[src_final_pos]
        targ_final = targ_phons[src_final_pos]
    
        if MERGER in targ_final:
          pos = self.get_coda_start_pos(src_final)

          if pos > 0 and pos < len(src_final):
            vowel = ''.join(src_final[:pos])
            coda = ''.join(src_final[pos:])
            src_final = [vowel, coda]
            targ_final = targ_final.split(MERGER)
        
            new_src_graphs = new_src_graphs + src_final
            new_targ_phons = new_targ_phons + targ_final
          else:
            new_src_graphs.append(src_final)
            new_targ_phons.append(targ_final)
        else:
          new_src_graphs.append(src_final)
          new_targ_phons.append(targ_final)
      else:
        new_src_graphs.append(src_graphs[i])
        new_targ_phons.append(targ_phons[i])
    new_targ_phons.append(targ_phons[-1])
    return [new_src_graphs, new_targ_phons]

  def get_coda_start_pos(self, src_graphs):
    vowels = ''
    for i in range(len(src_graphs)):
      if src_graphs[i] not in SRC_VOWELS:
        return i
    return -1
