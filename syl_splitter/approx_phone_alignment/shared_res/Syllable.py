class Syllable:
  def __init__(self):
    self.src_graphs = []
    self.roles = []
    self.src_phons = []
    self.targ_phons = []

  def create_new_syl(self, src_graphs, roles, src_phons, targ_phons):
    self.src_graphs = src_graphs
    self.src_phons = src_phons
    self.roles = roles
    self.targ_phons = targ_phons

  def get_src_graphs_str(self):
    return (" ").join(self.src_graphs)

  def get_roles_str(self):
    return (" ").join(self.roles)

  def get_src_phons_str(self):
    print str(self.src_phons)
    return (" - ").join(self.src_phons)

  def get_targ_phons_str(self):
    return (" ").join(self.targ_phons)

