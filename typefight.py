#!/bin/python

import logging, os, pygame, pygame.mixer, sys, webbrowser
from pygame.locals import *
from gameglobals import *
import gamelog
from commandentry import CommandEntry
from commandoutput import CommandOutput
from hud import Hud
from opponent import Opponent
from player import Player

pygame.init()

fps_clock = pygame.time.Clock()

# Game window setup
window_size = DEFAULT_WINDOW_SIZE
pygame.display.set_caption("Type Fight!")
app_icon = pygame.image.load(os.path.join('graphics', 'app_icon_256.png'))
pygame.display.set_icon(app_icon)
# Set flags to FULLSCREEN | DOUBLEBUF | HWSURFACE if we add fullscreen support later
flags = HWSURFACE|DOUBLEBUF|RESIZABLE
screen = pygame.display.set_mode(window_size, flags)
screen.set_alpha(None)
game_surface = pygame.Surface((screen.get_width(), screen.get_height()))
hud = Hud(screen)
player = Player(screen)
fight_bkg = pygame.image.load(os.path.join('graphics', 'fight_bkg.png')).convert()
win_fg = pygame.image.load(os.path.join('graphics', 'win_fg.png')).convert_alpha()
lose_fg = pygame.image.load(os.path.join('graphics', 'lose_fg.png')).convert_alpha()
pause_fg = pygame.image.load(os.path.join('graphics', 'pause_menu.png')).convert_alpha()
gamelog.log_display_info()

pygame.key.set_repeat(500, 50)

# Mouse setup
mouse_list = [MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]
mouse_button_list = [MOUSEBUTTONDOWN, MOUSEBUTTONUP]
pygame.event.set_allowed([QUIT, VIDEORESIZE, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

# Pygame mixer setup for sounds
try:
    pygame.mixer.init()
    mus_fight = pygame.mixer.music.load(os.path.join('music', 'Harmful or Fatal.ogg'))
    pygame.mixer.music.play()
except Exception as e:
    logging.exception('Could not play game music')

# Main objects setup
c_entry = CommandEntry()
c_output = CommandOutput()

def run_fight(opponent=Opponent(screen)):
    '''Main loop code for each fight. Takes an Opponent to use.'''
    window_size = (1080, 911)
    screen = pygame.display.set_mode(window_size, flags)
    screen.set_alpha(None)
    menu_button_rect = pygame.Rect(0, 0, 148, 40)
    resume_button_rect = pygame.Rect(156, 336, 766, 103)
    help_button_rect = pygame.Rect(156, 460, 766, 103)
    quit_button_rect = pygame.Rect(156, 583, 766, 103)
    menu_button_rect.right = screen.get_rect().right
    sf = calculate_scale_factor(DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
    menu_rects = {'menu': scale_rect(menu_button_rect, sf[0], sf[1]),
                  'resume': scale_rect(resume_button_rect, sf[0], sf[1]),
                  'help': scale_rect(help_button_rect, sf[0], sf[1]),
                  'quit': scale_rect(quit_button_rect, sf[0], sf[1])}
    paused = False
    hud.set_opponent_name(opponent.opponent_name)
    c_output.add_line('Fight initiated')
    while 1:
        # Event handling
        for event in pygame.event.get():
            if event.type is QUIT:
                pygame.quit()
                sys.exit()
            if event.type is VIDEORESIZE:
                # The game window is being resized
                window_size = event.dict['size']
                sf = calculate_scale_factor(DEFAULT_WINDOW_SIZE, window_size)
                menu_rects = {'menu': scale_rect(menu_button_rect, sf[0], sf[1]),
                              'resume': scale_rect(resume_button_rect, sf[0], sf[1]),
                              'help': scale_rect(help_button_rect, sf[0], sf[1]),
                              'quit': scale_rect(quit_button_rect, sf[0], sf[1])}
                screen = pygame.display.set_mode(window_size, flags)
            elif event.type in mouse_list:
                mouse_x, mouse_y = event.pos
                mouse_event = event
                if event.type in mouse_button_list:
                    mouse_button = event.button
                    if event.type is MOUSEBUTTONDOWN:
                        if menu_rects['menu'].collidepoint(event.pos):
                            # Toggle pause menu
                            paused = not paused
                        elif menu_rects['resume'].collidepoint(event.pos):
                            paused = False
                        elif menu_rects['help'].collidepoint(event.pos):
                            if paused:
                                help_location = os.path.join(os.getcwd(), 'help/typefight.html')
                                webbrowser.open_new(help_location)
                        elif menu_rects['quit'].collidepoint(event.pos):
                            if paused:
                                pygame.quit()
                                sys.exit()
                    else:
                        # TODO: Assume mouse button up
                        pass
                else:
                    # TODO: Handle mouse movement event
                    pass
            elif event.type is KEYDOWN:
                if not paused:
                    paused = c_entry.handle_keydown_event(event,
                                                          player,
                                                          opponent,
                                                          c_output)

        # State updating
        if not paused:
            opponent.update_state(player, c_output)

        # Draw graphics
        if not paused:
            c_entry.render()
            c_output.render()
        game_surface.blit(fight_bkg, game_surface.get_rect())
        hud_surface = hud.render(c_entry,
                                 c_output,
                                 player.health_percent,
                                 opponent)
        game_surface.blit(opponent.render(), opponent.get_rect())

        if not paused:
            player.render()
        game_surface.blit(player.left_arm_image, player.la_center_rect)
        game_surface.blit(player.right_arm_image, player.ra_center_rect)

        game_surface.blit(hud_surface, hud_surface.get_rect())
        if paused:
            game_surface.blit(pause_fg, screen.get_rect())
        if opponent.state == 'defeated':
            game_surface.blit(win_fg, screen.get_rect())
        elif player.health_percent <= 0:
            game_surface.blit(lose_fg, screen.get_rect())

        # Display all rendered graphics
        screen.blit(pygame.transform.scale(game_surface, window_size), (0,0))
        pygame.display.flip()

        # Proceed to next frame. We are aiming to run at 60 FPS
        fps_clock.tick(FPS_TARGET)

#*****************
# Main game code *
#*****************
run_fight(Opponent(screen))
