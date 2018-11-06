from pygame import image, sprite, font, K_RETURN, KEYDOWN
import json


class Logo(sprite.Sprite):
    """Represents the logo shown at the menu screen"""
    def __init__(self, screen):
        self.screen = screen
        self.image = image.load('map/Super-Mario-Logo.png')
        self.rect = self.image.get_rect()
        self.position()
        super(Logo, self).__init__()

    def position(self):
        """Position the logo on the screen so that it is well centered for the menu"""
        self.rect.centerx = int(self.screen.get_width() * 0.5)
        self.rect.centery = int(self.screen.get_height() * 0.4)

    def blit(self):
        """Blit the logo image to the screen"""
        self.screen.blit(self.image, self.rect)


class TextDisplay(sprite.Sprite):
    """Represents a text display on the screen"""
    def __init__(self, x, y, text, screen, size=24):
        self.text = text
        self.font = font.Font('fonts/PressStart2P-Regular.ttf', size)
        self.screen = screen
        self.x_pos, self.y_pos = x, y
        self.image = None
        self.rect = None
        self.render()
        super(TextDisplay, self).__init__()

    def update(self, n_text):
        self.text = str(n_text)
        self.render()

    def render(self):
        """Render the text and position it on the screen"""
        self.image = self.font.render(self.text, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.x_pos, self.y_pos

    def blit(self):
        """Blit the text to the screen"""
        self.screen.blit(self.image, self.rect)


class HighScore(sprite.Sprite):
    """Manages the display and storage of the high score for the game"""
    def __init__(self, x, y, screen):
        self.score = None
        self.retrieve()
        text = 'High Score - ' + str(self.score)
        self.display = TextDisplay(x, y, text, screen)
        super(HighScore, self).__init__()

    def save(self, n_score):
        """Save the given score if it is higher than the current score"""
        if int(n_score) > self.score:
            with open('high_score.json', 'w') as outfile:
                json.dump(n_score, outfile)
            self.score = n_score
            text = 'High Score - ' + str(self.score)
            self.display.update(text)

    def retrieve(self):
        """Retrieve the high score from the local high score file"""
        try:
            with open('high_score.json', 'r') as infile:
                self.score = int(json.load(infile))
        except (FileNotFoundError, ValueError):
            self.score = 0

    def blit(self):
        """Blit the score display to the screen"""
        self.display.blit()


class Menu:
    """Displays the menu for the game with its logo"""
    def __init__(self, screen):
        self.screen = screen
        self.logo = Logo(screen)
        start_text_x, start_text_y = int(screen.get_width() * 0.5), int(screen.get_height() * 0.7)
        self.start_text = TextDisplay(start_text_x, start_text_y, 'Press Enter', screen)
        hs_x, hs_y = int(screen.get_width() * 0.5), int(screen.get_height() * 0.85)
        self.high_score = HighScore(hs_x, hs_y, screen)
        self.action_map = {KEYDOWN: self.check_start, }
        self.start = False

    def check_start(self, event):
        """Check if the enter key has been pressed to start the game"""
        key = event.key
        if key == K_RETURN:
            self.start = True

    def blit(self):
        """Blit the menu display to the screen"""
        self.logo.blit()
        self.start_text.blit()
        self.high_score.blit()
