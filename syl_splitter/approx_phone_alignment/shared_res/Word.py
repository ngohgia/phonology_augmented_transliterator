from Syllable import Syllable

class Word:
  def __init__(self):
    self.syls = []

  def add_new_syl(self, new_syl):
    self.syls.append(new_syl)

  def print_str(self):
    print "Graphemes: " + " . ".join([syl.get_src_graphs_str() for syl in self.syls])
    print "Roles: " + " . ".join([syl.get_roles_str() for syl in self.syls])
    print "Source phonemes: " + " . ".join([syl.get_src_phons_str() for syl in self.syls])
    print "Target phonemes: " + " . ".join([syl.get_targ_phons_str() for syl in self.syls])
    print "\n"
