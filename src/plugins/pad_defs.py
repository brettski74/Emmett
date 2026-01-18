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

  def sync_position(self):
    if (self.footprint is not None):
      position = pcbnew.VECTOR2I_MM(self.x*1e-3, self.y*1e-3)
      self.footprint.SetPosition(position)

  def move_by(self, deltax: float, deltay: float):
    self.x += deltax
    self.y += deltay

  def move_left(self, left: float):
    self.x = left + self.width/2

  def move_clear_left(self, left: float):
    self.x = left + self.width/2 + self.courtyard

  def move_right(self, right: float):
    self.x = right - self.width/2

  def move_clear_right(self, right: float):
    self.x = right - self.width/2 - self.courtyard

  def move_top(self, top: float):
    self.y = top + self.height/2

  def move_clear_top(self, top: float):
    self.y = top + self.height/2 + self.courtyard

  def move_bottom(self, bottom: float):
    self.y = bottom - self.height/2

  def move_clear_bottom(self, bottom: float):
    self.y = bottom - self.height/2 - self.courtyard

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
