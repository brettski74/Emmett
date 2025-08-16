import pcbnew

class RectangularPad:
  def __init__(self, x: float, y: float, width: float, height: float, courtyard: float = 0.0):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.courtyard = courtyard
    self.footprint = None

  def left(self):
    return self.x - self.width/2

  def right(self):
    return self.x + self.width/2

  def top(self):
    return self.y - self.height/2

  def bottom(self):
    return self.y + self.height/2

  def clear_left(self):
    return self.x - self.width/2 - self.courtyard

  def clear_right(self):
    return self.x + self.width/2 + self.courtyard

  def clear_top(self):
    return self.y - self.height/2 - self.courtyard

  def clear_bottom(self):
    return self.y + self.height/2 + self.courtyard

  def clear_width(self):
    return self.width + self.courtyard * 2

  def clear_height(self):
    return self.height + self.courtyard * 2

  def scale(self, factor: float):
    self.x *= factor
    self.y *= factor
    self.width *= factor
    self.height *= factor
    self.courtyard *= factor

  def __str__(self):
    return f"RectangularPad(x={self.x}, y={self.y}, width={self.width}, height={self.height}, courtyard={self.courtyard})"

class CircularPad:
  def __init__(self, x: float, y: float, radius: float, courtyard: float = 0.0):
    self.x = x
    self.y = y
    self.radius = radius
    self.courtyard = courtyard
    self.footprint = None

  def __str__(self):
    return f"CircularPad(x={self.x}, y={self.y}, radius={self.radius}, courtyard={self.courtyard})"

  def clear_radius(self):
    return self.radius + self.courtyard

  def clear_diameter(self):
    return self.clear_radius() * 2

  def clear_width(self):
    return self.clear_diameter()

  def clear_height(self):
    return self.clear_diameter()
  
  def clear_left(self):
    return self.x - self.clear_radius()

  def clear_right(self):
    return self.x + self.clear_radius()

  def clear_top(self):
    return self.y - self.clear_radius()
  
  def clear_bottom(self):
    return self.y + self.clear_radius()

  def scale(self, factor: float):
    self.x *= factor
    self.y *= factor
    self.radius *= factor
    self.courtyard *= factor
