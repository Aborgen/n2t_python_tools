class MockToken:
  def __init__(self, value) -> None:
    self.value = value

  def __eq__(self, other) -> bool:
    return type(other) == type(self) and self.value == other.value
