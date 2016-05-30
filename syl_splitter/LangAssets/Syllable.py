class Syllable:
  onset = ""
  nucleus = ""
  coda = ""

  def __str__(self):
    return "[ %s ]" % " ".join([self.onset, self.nucleus, self.coda])

  def get_encoded_units(self):
    struct = []
    if self.onset != "":
      struct.append("O")
    if self.nucleus != "":
      struct.append("N") 
    if self.coda != "":
      struct.append("Cd") 
    return " ".join(struct)

  def to_plain_text(self):
    return "".join([self.onset, self.nucleus, self.coda])

  def get_unit_count(self):
    return len(self.get_encoded_units().split(" "))

