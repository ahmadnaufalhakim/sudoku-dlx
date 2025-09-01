import pygame

class Button :
  def __init__(self,
               width_height:tuple,
               text:str,
               text_size:int,
               text_color:pygame.Color=(0, 0, 0),
               border_width:int=0,
               border_radius:int=-1,
               border_color:pygame.Color=(0, 0, 0),
               center_pos:tuple=None,
               top_left_pos:tuple=None,
               bg_color:pygame.Color=(255, 255, 255),
               toggle_button:bool=None,
               toggle_state:bool=None,
               toggle_color:pygame.Color=None) -> None :
    assert (center_pos is not None) ^ (top_left_pos is not None)
    assert not ((toggle_button is not None) ^ (toggle_state is not None))
    self.width_height = width_height
    self.text = text
    self.text_size = text_size
    self.text_color = text_color
    self.border_width = border_width
    self.border_radius = border_radius
    self.border_color = border_color
    self.center_pos = center_pos
    self.top_left_pos = top_left_pos
    self.bg_color = bg_color
    self.toggle_button = toggle_button
    self.toggle_state = toggle_state
    if (self.toggle_button is not None) and (self.toggle_state is not None) :
      if toggle_color is None :
        toggle_color = tuple((255-c) for c in self.bg_color)
      self.toggle_color = toggle_color

    self.font = pygame.font.Font(None, self.text_size)
    self.text_surface = self.font.render(f"{self.text}", True, self.text_color)
    self.text_surface_rect = self.text_surface.get_rect(center=self.center_pos or (
      self.top_left_pos[0]+self.width_height[0]/2,
      self.top_left_pos[1]+self.width_height[1]/2
    ))
    button_surface = pygame.surface.Surface(size=width_height).convert()
    self.button_surface_rect = button_surface.get_rect(center=self.center_pos or (
      self.top_left_pos[0]+self.width_height[0]/2,
      self.top_left_pos[1]+self.width_height[1]/2
    ))

  def update_text(self, new_text:str) -> None :
    if self.text != new_text :
      self.text = new_text
      self.text_surface = self.font.render(self.text, True, self.text_color)
      # self.text_surface_rect = self.text_surface.get_rect(center=self.center_pos or (
      #   self.top_left_pos[0]+self.width_height[0]/2,
      #   self.top_left_pos[1]+self.width_height[1]/2
      # ))

  def render(self, screen:pygame.Surface) -> None :
    # Recalculate the button's text size, width and height, and color
    # based on its is_hovered condition
    hover_scale = 1.05 if self.is_hovered() else 1
    text_size = int(self.text_size * hover_scale)
    width_height = tuple(size*hover_scale for size in self.width_height)
    bg_color = tuple(min(c+64, 255) for c in self.bg_color) if self.is_hovered()\
      else self.toggle_color if self.toggle_state\
      else self.bg_color

    self.font = pygame.font.Font(None, text_size)
    self.text_surface = self.font.render(f"{self.text}", True, self.text_color)
    self.text_surface_rect = self.text_surface.get_rect(center=self.center_pos or (
      self.top_left_pos[0]+self.width_height[0]/2,
      self.top_left_pos[1]+self.width_height[1]/2
    ))
    button_surface = pygame.surface.Surface(size=width_height).convert()
    self.button_surface_rect = button_surface.get_rect(center=self.center_pos or (
      self.top_left_pos[0]+self.width_height[0]/2,
      self.top_left_pos[1]+self.width_height[1]/2
    ))
    # Draw the button body
    pygame.draw.rect(
      surface=screen,
      color= bg_color,
      rect=self.button_surface_rect,
      border_radius=self.border_radius
    )
    # Draw the button text
    screen.blit(self.text_surface, self.text_surface_rect)
    # Draw border if border_width is > 0
    if self.border_width > 0 :
      pygame.draw.rect(
        surface=screen,
        color=self.border_color,
        rect=self.button_surface_rect,
        width=self.border_width,
        border_radius=self.border_radius
      )

  def is_clicked(self, events:pygame.event.Event) -> bool :
    mouse_pos = pygame.mouse.get_pos()
    for event in events :
      if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] :
        if self.button_surface_rect.collidepoint(mouse_pos[0], mouse_pos[1]) :
          if self.toggle_button is not None :
            self.toggle_state = not self.toggle_state
          return True
    return False

  def is_hovered(self) -> bool :
    return self.button_surface_rect.collidepoint(
      pygame.mouse.get_pos()
    )