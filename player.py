#!/bin/python

import math, os, pygame
from gameglobals import *

# Sound effects for attacks
pygame.mixer.init()
snd_punch = pygame.mixer.Sound(os.path.join('sounds', 'punch.wav'))
snd_block = pygame.mixer.Sound(os.path.join('sounds', 'Swords_Collide-Sound_Explorer-2015600826.wav'))

player_arm_spacing = 128 / 2

class Player:
    '''Class representing the player's character onscreen'.'''
    def __init__(self, screen):
        self.img_left_arm = self._load_image('player_left_arm.png')
        self.img_right_arm = self._load_image('player_right_arm.png')
        self.img_left_block = self._load_image('player_block_left.png')
        self.img_right_block = self._load_image('player_block_right.png')
        self.left_arm_image = self.img_left_arm
        self.right_arm_image = self.img_right_arm
        self.la_center_rect = self.left_arm_image.get_rect().copy()
        self.ra_center_rect = self.right_arm_image.get_rect().copy()
        self.updown_juice = 0
        self.health_percent = 100
        self.left_arm_state = 'idle'
        self.right_arm_state = 'idle'

    def _load_image(self, filename):
        '''Internal function for loading image assets.'''
        path = os.path.join('graphics', filename)
        return pygame.image.load(path).convert_alpha()

    def take_damage(self, damage, direction):
        '''Deals damage to this Player.'''
        if direction == 'left':
            if self.left_arm_state == 'blocking':
                self.left_arm_state = 'idle'
                self.left_arm_image = self.img_left_arm
                snd_block.play()
                return
            else:
                self.health_percent -= damage
                snd_punch.play()
        if direction == 'right':
            if self.right_arm_state == 'blocking':
                self.right_arm_state = 'idle'
                self.right_arm_image = self.img_right_arm
                snd_block.play()
                return
            else:
                self.health_percent -= damage
                snd_punch.play()
        if direction == 'both':
            if not self.left_arm_state == 'blocking':
                self.health_percent -= int(math.floor(damage / 2.0))
                snd_punch.play()
            else:
                snd_block.play()
            if not self.right_arm_state == 'blocking':
                self.health_percent -= int(math.floor(damage / 2.0))
                snd_punch.play()
            else:
                snd_block.play()
            self.left_arm_state = 'idle'
            self.left_arm_image = self.img_left_arm
            self.right_arm_state = 'idle'
            self.right_arm_image = self.img_right_arm

        # Check if defeated
        if self.health_percent <= 0:
            self.health_percent = 0
            self.left_arm_state = 'defeated'
            self.right_arm_state = 'defeated'
            self.updown_juice = 0

    def block(self, direction=''):
        '''Block in the specified direction.'''
        if direction == '' or direction == 'both' or direction == 'center':
            self.left_arm_state = 'blocking'
            self.left_arm_image = self.img_left_block
            self.right_arm_state = 'blocking'
            self.right_arm_image = self.img_right_block
        elif direction == 'left':
            self.left_arm_state = 'blocking'
            self.left_arm_image = self.img_left_block
        elif direction == 'right':
            self.right_arm_state = 'blocking'
            self.right_arm_image = self.img_right_block

    def unblock(self, direction=''):
        '''Cancels block in the specified direction, returning to idle.'''
        if direction == '' or direction == 'both' or direction == 'center':
            self.left_arm_state = 'idle'
            self.left_arm_image = self.img_left_arm
            self.right_arm_state = 'idle'
            self.right_arm_image = self.img_right_arm
        elif direction == 'left':
            self.left_arm_state = 'idle'
            self.left_arm_image = self.img_left_arm
        elif direction == 'right':
            self.right_arm_state = 'idle'
            self.right_arm_image = self.img_right_arm

    def render(self):
        '''Updates the player arm rects. Takes the display Surface for
        positioning.'''
        self.updown_juice += (2.0 * math.pi) / 45.0
        juice_amt = 15 * math.sin(self.updown_juice)

        # Left arm
        self.la_center_rect = self.left_arm_image.get_rect().copy()
        self.la_center_rect.right = DEFAULT_WINDOW_CENTERX - player_arm_spacing
        self.la_center_rect.top = DEFAULT_WINDOW_CENTERY + juice_amt

        # Right arm
        self.ra_center_rect = self.right_arm_image.get_rect().copy()
        self.ra_center_rect.left = DEFAULT_WINDOW_CENTERX + player_arm_spacing
        self.ra_center_rect.top = DEFAULT_WINDOW_CENTERY + juice_amt
