import pygame

WHITE = (255, 255, 255)
TEXT_SIZE = 36
SPACER = 54


class GameStats:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font('fonts/PressStart2p-Squished.ttf', TEXT_SIZE)
        self.font2 = pygame.font.Font('fonts/PressStart2p-Regular.ttf', 20)

        self.s_text = "SCORE"
        self.c_text = "COINS"
        self.w_text = "WORLD"
        self.t_text = "TIME"
        self.l_text = "LIVES"

        self.Scores = None
        self.sRect = None
        self.Coins = None
        self.cRect = None
        self.World = None
        self.wRect = None
        self.Time = None
        self.tRect = None
        self.Lives = None
        self.lRect = None

        self.s_num = "0"
        self.c_num = "0"
        self.w_num = "1-1"
        self.t_num = "400"
        self.l_num = "3"

        self.SNumber = None
        self.snRect = None
        self.CNumber = None
        self.cnRect = None
        self.WNumber = None
        self.wnRect = None
        self.TNumber = None
        self.tnRect = None
        self.LNumber = None
        self.lnRect = None

        self.render(self.s_text, self.c_text, self.w_text, self.t_text, self.l_text)
        self.update(self.s_num, self.c_num, self.w_num, self.t_num, self.l_num)

    def render(self, s_text, c_text, w_text, t_text, l_text):
        # Score display text
        self.Scores = self.font.render(s_text, True, WHITE)
        self.sRect = self.Scores.get_rect()
        self.sRect.y = (self.screen.get_height() / 2) - 290
        self.sRect.x = SPACER

        # Coins display text
        self.Coins = self.font.render(c_text, True, WHITE)
        self.cRect = self.Coins.get_rect()
        self.cRect.y = ((self.screen.get_height() / 2) - 290)
        self.cRect.x = self.sRect.x + self.sRect.width + SPACER

        # World display text
        self.World = self.font.render(w_text, True, WHITE)
        self.wRect = self.World.get_rect()
        self.wRect.y = ((self.screen.get_height() / 2) - 290)
        self.wRect.x = self.cRect.x + self.cRect.width + SPACER

        # Time display text
        self.Time = self.font.render(t_text, True, WHITE)
        self.tRect = self.Time.get_rect()
        self.tRect.y = ((self.screen.get_height() / 2) - 290)
        self.tRect.left = self.wRect.x + self.wRect.width + SPACER

        # Lives display text
        self.Lives = self.font.render(l_text, True, WHITE)
        self.lRect = self.Lives.get_rect()
        self.lRect.y = ((self.screen.get_height() / 2) - 290)
        self.lRect.left = self.tRect.x + self.tRect.width + SPACER

        temp = self.screen.get_width() - (self.lRect.x + self.lRect.width)
        print(str(temp))

    def update(self, s_num, c_num, w_num, t_num, l_num):
        """ADD UPDATING VARIABLES"""
        self.SNumber = self.font.render(s_num, True, WHITE)
        self.snRect = self.SNumber.get_rect()
        self.snRect.center = self.sRect.center
        self.snRect.y += SPACER - SPACER / 2
        self.CNumber = self.font.render(c_num, True, WHITE)
        self.cnRect = self.CNumber.get_rect()
        self.cnRect.center = self.cRect.center
        self.cnRect.y += SPACER - SPACER / 2
        self.WNumber = self.font2.render(w_num, True, WHITE)
        self.wnRect = self.WNumber.get_rect()
        self.wnRect.center = self.wRect.center
        self.wnRect.y += SPACER - SPACER/2
        self.TNumber = self.font.render(t_num, True, WHITE)
        self.TNumber = self.font.render(t_num, True, WHITE)
        self.tnRect = self.TNumber.get_rect()
        self.tnRect.center = self.tRect.center
        self.tnRect.y += SPACER - SPACER / 2
        self.LNumber = self.font.render(l_num, True, WHITE)
        self.lnRect = self.LNumber.get_rect()
        self.lnRect.center = self.lRect.center
        self.lnRect.y += SPACER - SPACER / 2

    def blit(self):
        self.screen.blit(self.Scores, self.sRect)
        self.screen.blit(self.SNumber, self.snRect)
        self.screen.blit(self.Coins, self.cRect)
        self.screen.blit(self.CNumber, self.cnRect)
        self.screen.blit(self.World, self.wRect)
        self.screen.blit(self.WNumber, self.wnRect)
        self.screen.blit(self.Time, self.tRect)
        self.screen.blit(self.TNumber, self.tnRect)
        self.screen.blit(self.Lives, self.lRect)
        self.screen.blit(self.LNumber, self.lnRect)

