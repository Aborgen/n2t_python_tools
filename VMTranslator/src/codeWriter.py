class CodeWriter():
  def __init__(self):
    self.closed = True


  def open(self, out_file: str) -> None:
    if not self.closed:
      raise Exception('Cannot open file: file already opened')

    self._f = open(out_file, 'w+')
    self.closed = False


  def close(self):
    if self.closed:
      raise Exception('No file currently opened: cannot close')

    self._f.close()
    self.closed = True
  

  def out(self, assembly: str) -> None:
    if self.closed:
      raise Exception('No file currently opened: cannot write')

    self._f.write(assembly)
    self._f.write('\n')
