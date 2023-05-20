import pygame as pg


class InputBox():
    def __init__(self):
        self.screen = pg.display.set_mode((1280, 720))
        self.font = pg.font.Font("assets/font.ttf", 20)
        self.clock = pg.time.Clock()
        self.input_box = pg.Rect(1280/2 - 150, 300, 140, 32)
        self.color_inactive = pg.Color('black')
        self.color_active = pg.Color('black')
        self.color = self.color_inactive
        self.active = False
        self.text = ''
        self.done = False

    def startInput(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if self.input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        self.active = not self.active
                    else:
                        self.active = False
                    # Change the current color of the input box.
                    self.color = self.color_active if self.active else self.color_inactive
                if event.type == pg.KEYDOWN:
                    if self.active:
                        if event.key == pg.K_RETURN:
                            print(self.text)
                            self.text = ''
                        elif event.key == pg.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode

            self.screen.fill("white")
            # Render the current text.
            txt_surface = self.font.render(self.text, True, self.color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width()+10)
            self.input_box.w = width
            # Blit the text.
            self.screen.blit(txt_surface, (self.input_box.x+5, self.input_box.y+5))
            # Blit the input_box rect.
            pg.draw.rect(self.screen, self.color, self.input_box, 2)

            pg.display.flip()
            self.clock.tick(30)
