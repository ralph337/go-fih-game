import pygame
import sys
import random
import os
import settings
import traceback
from assets import Assets, _GIF_SUPPORT
from game_logic import FishingMinigame

# --- initialization ---
pygame.init()
pygame.mixer.init() # initialize the sound mixer

# fishing minigame settings
# fake the minigame size relative to the screen height for better scaling.
TRACK_H = int(settings.SCREEN_HEIGHT * settings.TRACK_H_RATIO)
TRACK_W = int(TRACK_H * settings.TRACK_W_RATIO)
TRACK_X = int(settings.SCREEN_WIDTH * settings.TRACK_X_RATIO)
TRACK_Y = (settings.SCREEN_HEIGHT - TRACK_H) // 2

CATCH_BAR_H = int(TRACK_H * settings.CATCH_BAR_H_RATIO)
FISH_H = int(TRACK_H * settings.FISH_H_RATIO)

PROGRESS_BAR_W = int(TRACK_W * settings.PROGRESS_BAR_W_RATIO)
PROGRESS_BAR_H = TRACK_H
PROGRESS_BAR_X = TRACK_X + TRACK_W + 15
PROGRESS_BAR_Y = TRACK_Y

# --- game setup ---
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("Go Fish")
clock = pygame.time.Clock()

try:
    font = pygame.font.Font(settings.FONT_PATH, 40)
except Exception:
    font = pygame.font.Font(None, 36)

assets = Assets()

# --- debug: check loaded assets ---
# --- error handling for missing fish assets ----
print("--- Checking Fish Assets ---")
fish_assets = ["fish_carp_img", "fish_sardine_img", "fish_bream_img", "fish_bass_img", 
               "fish_trout_img", "fih", "fish_tuna_img", "pufferfish", "fish_shark_img", "fish_legend_img"]
for attr in fish_assets:
    if getattr(assets, attr, None) is None:
        print(f"[MISSING] {attr}")
    else:
        print(f"[OK] {attr}")
print("----------------------------")

play_button_rect = None
debug_button_rect = None
try_again_button_rect = None
exit_button_rect = None

# --- block transfer (blit) functions (centering and positioning some of the pngs) ---
def center_blit(surface, image):
    """Helper function to blit an image to the center of a surface."""
    if image: # only blit if the image loaded successfully
        rect = image.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(image, rect)

def position_blit(surface, image, x_pos, y_pos):
    """Helper function to blit an image at a specific position."""
    if image: # only blit if the image loaded successfully
        surface.blit(image, (x_pos, y_pos))
# --------decorator----- (used for highscore announcements) -----
def new_highscore_announcer(func):
    def wrapper(instance, new_score):
        old_highscore = instance.highscore
        func(instance, new_score) # call the original update_highscore method
        if instance.highscore > old_highscore:
            print(f"New Highscore: {int(instance.highscore)}!")
    return wrapper

class GameState:
    def __init__(self):
        self.game_state = 'menu' # 'menu', 'waiting_for_bite', 'fishing', 'won', 'lost', 'cutscene'

        self.minigame = None

        # waiting for bite variables
        self.bite_time = 0
        self.waiting_start_time = 0
        self.show_bite_indicator = False

        # cutscene variables
        self.cutscene_frames = assets.cutscene_frames
        self.cutscene_frame_index = 0
        self.cutscene_last_frame_time = 0

        self.highscore = 0.0

        # --- cheats / debug state (for easy testing) ---
        self.cheats = {
            "fast_catch": False,
        }

        # store constants for easy access in game_logic
        self.track_x, self.track_y, self.track_w, self.track_h = TRACK_X, TRACK_Y, TRACK_W, TRACK_H
        self.catch_bar_h, self.fish_h = CATCH_BAR_H, FISH_H
        self.assets = assets
        
        self.current_music = None

    # ---error handling for bgm loading when it fails ----
    def play_bgm(self, track_path):
        """Plays background music, only if it's not already playing."""
        if self.current_music == track_path:
            return
        
        if not os.path.exists(track_path):
            print(f"Music not found: {track_path}")
            return

        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1)
            self.current_music = track_path
        except Exception as e:
            print(f"Error playing music {track_path}: {e}")

    @new_highscore_announcer
    def update_highscore(self, new_score):
        """Updates the highscore if the new score is higher."""
        if new_score > self.highscore:
            self.highscore = new_score

gs = GameState()

def reset_minigame():
    gs.minigame = FishingMinigame(gs)
    gs.play_bgm(settings.MAIN_BGM_PATH)

def start_waiting_for_bite():
    """Sets up the state to wait for a fish to bite."""
    gs.game_state = 'waiting_for_bite'
    gs.waiting_start_time = pygame.time.get_ticks()
    # fish will bite in 2 to 7 seconds
    gs.bite_time = gs.waiting_start_time + random.randint(2000, 7000)
    gs.show_bite_indicator = False
    if assets.casting_sound:
        assets.casting_sound.play()

def start_fishing_minigame():
    """Starts the main fishing minigame."""
    reset_minigame()
    gs.game_state = 'fishing'

def draw_fishing_minigame(is_catching, vibration_offset=(0, 0)):
    """Draws all elements for the fishing minigame state."""
    if assets.fishing_bg_img:
        screen.blit(assets.fishing_bg_img, (0, 0))
    else:
        screen.fill(settings.GREY)

    progress_overlay_img = None
    if not gs.minigame.first_hit_made:
        progress_overlay_img = assets.progress_mid_img
    else:
        # after the first hit, show high for catching, low for losing.
        if is_catching:
            progress_overlay_img = assets.progress_high_img
        else:
            progress_overlay_img = assets.progress_low_img
            
    # for pngs on top of png, make it semi-transparent.
    if progress_overlay_img:
        # draw the overlay normally. preserves its original colors.
        screen.blit(progress_overlay_img, vibration_offset)

    # draw fishing track
    pygame.draw.rect(screen, settings.BLACK, (TRACK_X, TRACK_Y, TRACK_W, TRACK_H))

    # draw fish
    pygame.draw.rect(screen, settings.BLUE, (TRACK_X, gs.minigame.fish_y, TRACK_W, FISH_H))

    # draw player's catch bar
    pygame.draw.rect(screen, settings.GREEN, (TRACK_X, gs.minigame.catch_bar_y, TRACK_W, CATCH_BAR_H), 4)

    # --- draw functional progress bar ---
    #  draw black background for the bar
    pygame.draw.rect(screen, settings.BLACK, (PROGRESS_BAR_X, PROGRESS_BAR_Y, PROGRESS_BAR_W, PROGRESS_BAR_H))

    #  draw yellow fill rectangle that shows current progress
    progress_height = int(PROGRESS_BAR_H * (gs.minigame.catch_progress / 100.0))
    if progress_height > 0:
        pygame.draw.rect(screen, settings.YELLOW,
            (PROGRESS_BAR_X, PROGRESS_BAR_Y + PROGRESS_BAR_H - progress_height, PROGRESS_BAR_W, progress_height))

    #  debug outlines to verify UI element positions
    if settings.DEBUG_UI_OUTLINES:
        pygame.draw.rect(screen, (255, 0, 255), (TRACK_X, TRACK_Y, TRACK_W, TRACK_H), 1)
        pygame.draw.rect(screen, (0, 255, 255), (TRACK_X, gs.minigame.catch_bar_y, TRACK_W, CATCH_BAR_H), 1)
        pygame.draw.rect(screen, (255, 255, 255), (TRACK_X, gs.minigame.fish_y, TRACK_W, FISH_H), 1)
        pygame.draw.rect(screen, (255, 0, 0), (PROGRESS_BAR_X, PROGRESS_BAR_Y, PROGRESS_BAR_W, PROGRESS_BAR_H), 1)

def show_crash_screen(error_message):
    """Displays a crash screen with the error and a close button."""
    crash_font = pygame.font.Font(None, 24)
    close_button_rect = pygame.Rect(0, 0, 150, 50)
    close_button_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 50)

    # Split the error message into lines
    error_lines = error_message.strip().split('\n')

    crash_screen_running = True
    while crash_screen_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crash_screen_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and close_button_rect.collidepoint(event.pos):
                    crash_screen_running = False

        screen.fill(settings.GREY)

        # Draw the error message
        y_offset = 20
        for line in error_lines:
            error_surf = crash_font.render(line, True, settings.WHITE)
            screen.blit(error_surf, (20, y_offset))
            y_offset += 25

        # Draw the close button
        pygame.draw.rect(screen, settings.RED, close_button_rect)
        close_text_surf = font.render("Close", True, settings.WHITE)
        screen.blit(close_text_surf, close_text_surf.get_rect(center=close_button_rect.center))

        pygame.display.flip()
        clock.tick(30)

# --- main game loop ---
# start main bgm
gs.play_bgm(settings.MAIN_BGM_PATH)

running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # r to restart the minigame at any time
            if event.key == pygame.K_r:
                reset_minigame()
        
        if gs.game_state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and play_button_rect and play_button_rect.collidepoint(event.pos):
                    if assets.button_click_sound:
                        assets.button_click_sound.play()
                    start_waiting_for_bite()
                
                # for the debug button
                if event.button == 1 and debug_button_rect and debug_button_rect.collidepoint(event.pos):
                    if assets.button_click_sound:
                        assets.button_click_sound.play()
                    # toggle cheats (for testing)
                    gs.cheats["fast_catch"] = not gs.cheats["fast_catch"]
        
        if gs.game_state == 'lost':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if try_again_button_rect and try_again_button_rect.collidepoint(event.pos):
                    if assets.button_click_sound:
                        assets.button_click_sound.play()
                    if assets.lose_sound:
                        assets.lose_sound.stop()
                    gs.play_bgm(settings.MAIN_BGM_PATH)
                    start_waiting_for_bite() # restart to the start
                elif exit_button_rect and exit_button_rect.collidepoint(event.pos):
                    if assets.button_click_sound:
                        assets.button_click_sound.play()
                    if assets.lose_sound:
                        assets.lose_sound.stop()
                    gs.play_bgm(settings.MAIN_BGM_PATH)
                    gs.game_state = 'menu' # back to menu
                    if not pygame.mouse.get_visible():
                        pygame.mouse.set_visible(True)

        if gs.game_state == 'waiting_for_bite':
             # click to start the game ( forgot to add timer to 
             # the bite indicator so technically you can just wait forever without losing bait)
            if gs.show_bite_indicator and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                start_fishing_minigame()
        #when the cutscene is over, a click or key press will restart to the game
        if gs.game_state == 'won' and (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN):
             if event.type == pygame.MOUSEBUTTONDOWN and assets.button_click_sound:
                 assets.button_click_sound.play()
             if assets.reeling_sound:
                assets.reeling_sound.stop()
             if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True) # for cursor to be visible on menu
             gs.game_state = 'menu'
             gs.show_bite_indicator = False

    # --- game logic ---
    if gs.game_state == 'menu':
        pass # no logic needed for menu, only drawing
    elif gs.game_state == 'fishing':
        # we need to know if we are catching to draw the correct overlay.
        catch_bar_rect = pygame.Rect(TRACK_X, gs.minigame.catch_bar_y, TRACK_W, CATCH_BAR_H)
        fish_rect = pygame.Rect(TRACK_X, gs.minigame.fish_y, TRACK_W, FISH_H)
        is_currently_catching = catch_bar_rect.colliderect(fish_rect)

        # calculate vibration offset for the progress_high image
        vibration_offset = (0, 0)
        if is_currently_catching and gs.minigame.first_hit_made:
            vibration_intensity = 2 # pixels (reduced from 4)
            vibration_offset = (random.randint(-vibration_intensity, vibration_intensity), 
                                random.randint(-vibration_intensity, vibration_intensity))

    elif gs.game_state == 'waiting_for_bite':
        now = pygame.time.get_ticks()
        if not gs.show_bite_indicator and now >= gs.bite_time:
            gs.show_bite_indicator = True
            if assets.bite_sound:
                assets.bite_sound.play()

    elif gs.game_state == 'cutscene':
        _, current_frame_duration = gs.cutscene_frames[gs.cutscene_frame_index]
        now = pygame.time.get_ticks()
        if now - gs.cutscene_last_frame_time > current_frame_duration:
            gs.cutscene_frame_index += 1
            gs.cutscene_last_frame_time = now
            if gs.cutscene_frame_index >= len(gs.cutscene_frames):
                # stop any cutscene sounds that might still be playing
                if assets.cutscene_sound_1 and assets.cutscene_sound_1.get_num_channels() > 0: assets.cutscene_sound_1.stop()
                if assets.cutscene_sound_30 and assets.cutscene_sound_30.get_num_channels() > 0: assets.cutscene_sound_30.stop()
                if assets.cutscene_sound_60 and assets.cutscene_sound_60.get_num_channels() > 0: assets.cutscene_sound_60.stop()
                
                gs.game_state = 'won'
                if assets.success_sound:
                    assets.success_sound.play()
                gs.play_bgm(settings.MAIN_BGM_PATH)
            else:
                # play sounds at specific frames
                if gs.cutscene_frame_index == 19 and assets.cutscene_sound_30: assets.cutscene_sound_30.play() # frame 20 (index 19)
                if gs.cutscene_frame_index == 39 and assets.cutscene_sound_60: assets.cutscene_sound_60.play() # frame 40 (index 39)

    # --- drawing ---
    screen.fill(settings.GREY)

    if gs.game_state == 'menu':
        if assets.menu_bg_img:
            screen.blit(assets.menu_bg_img, (0, 0))
        else:
            # fallback text if background image is missing
            menu_text = font.render("Main Menu", True, settings.WHITE)
            screen.blit(menu_text, menu_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3)))

        if assets.play_button_img:
            pos_x = int(settings.SCREEN_WIDTH * settings.PLAY_BUTTON_POS_X)
            pos_y = int(settings.SCREEN_HEIGHT * settings.PLAY_BUTTON_POS_Y)
            play_button_rect = assets.play_button_img.get_rect(center=(pos_x, pos_y))
            screen.blit(assets.play_button_img, play_button_rect)
        else:
            # fallback text if play button image is missing
            play_text = font.render("Click to Play", True, settings.WHITE)
            play_button_rect = play_text.get_rect(center=(int(settings.SCREEN_WIDTH * settings.PLAY_BUTTON_POS_X), int(settings.SCREEN_HEIGHT * settings.PLAY_BUTTON_POS_Y)))
            screen.blit(play_text, play_button_rect)

        # --- draw debug/cheats button ---
        debug_button_color = settings.GREEN if gs.cheats["fast_catch"] else settings.RED
        debug_button_text = "Cheats ON" if gs.cheats["fast_catch"] else "Cheats OFF"
        debug_text_surf = font.render(debug_button_text, True, settings.WHITE)
        
        debug_button_rect = pygame.Rect(0, 0, 200, 50)
        debug_button_rect.bottomright = (settings.SCREEN_WIDTH - 20, settings.SCREEN_HEIGHT - 20)
        
        pygame.draw.rect(screen, debug_button_color, debug_button_rect)
        screen.blit(debug_text_surf, debug_text_surf.get_rect(center=debug_button_rect.center))

        # display cheat status
        if gs.cheats["fast_catch"]:
            cheat_status_text = font.render("Fast Catch Active", True, settings.YELLOW)
            screen.blit(cheat_status_text, (debug_button_rect.left, debug_button_rect.top - 40))

    elif gs.game_state == 'waiting_for_bite': # no change
        # use the same background as the fishing minigame
        if assets.fishing_bg_img:
            screen.blit(assets.fishing_bg_img, (0, 0))
        else:
            screen.fill(settings.GREY)

        if not gs.show_bite_indicator: # waiting state
            if assets.waiting_img:
                center_blit(screen, assets.waiting_img)
            else: # fallback text
                wait_text = font.render("Waiting for a bite...", True, settings.WHITE)
                screen.blit(wait_text, wait_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)))
        else: # bite state
            if assets.bite_img:
                center_blit(screen, assets.bite_img)
            else: # fallback text
                bite_text = font.render("BITE! CLICK NOW!", True, settings.YELLOW)
                screen.blit(bite_text, bite_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)))

    elif gs.game_state == 'fishing': # no change
        gs.minigame.update(gs) # update logic first
        draw_fishing_minigame(is_currently_catching, vibration_offset) # then draw with the correct state

        instructions_text = font.render("Hold [SPACE] or Left-Click to reel up", True, settings.WHITE)        
        screen.blit(instructions_text, (instructions_text.get_rect(centerx=settings.SCREEN_WIDTH // 2).x, 20))
        restart_text = font.render("Press [R] to restart", True, settings.WHITE)        
        screen.blit(restart_text, (restart_text.get_rect(centerx=settings.SCREEN_WIDTH // 2).x, 50))

    elif gs.game_state == 'cutscene': # no change
        if gs.cutscene_frames:
            safe_index = gs.cutscene_frame_index % len(gs.cutscene_frames)
            frame_to_draw, _ = gs.cutscene_frames[safe_index]
            # Since the frame is the same size as the screen, blit it at (0, 0)
            screen.blit(frame_to_draw, (0, 0))

    elif gs.game_state == 'won': # display fish stats here
        # draw the specific fish image centered on the screen
        attr_name = gs.minigame.fish.asset_attr
        fish_img = getattr(gs.assets, attr_name, None)

        # draw background first (using success img as bg or fallback)
        if gs.assets.success_img:
             scaled_bg = pygame.transform.scale(gs.assets.success_img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
             screen.blit(scaled_bg, (0, 0))
        else:
             screen.fill((34, 139, 34))

        # draw the fish overlay
        if fish_img:
            # scale it up a bit if it's small
            scaled_fish = pygame.transform.scale(fish_img, (210, 210))
            fish_rect = scaled_fish.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 100))
            screen.blit(scaled_fish, fish_rect)
        else:
            # fallback: draw a placeholder rectangle if image is missing so it's not invisible
            placeholder_rect = pygame.Rect(0, 0, 210, 210)
            placeholder_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 100)
            pygame.draw.rect(screen, settings.BLUE, placeholder_rect)
            pygame.draw.rect(screen, settings.WHITE, placeholder_rect, 2)
            
            # draw text indicating missing asset
            missing_text = font.render(f"Missing: {attr_name}", True, settings.WHITE)
            text_rect = missing_text.get_rect(center=placeholder_rect.center)
            screen.blit(missing_text, text_rect)

        score = gs.minigame.fish.get_score()
        # update highscore
        gs.update_highscore(score)

        # display victory message
        text_center_x = settings.SCREEN_WIDTH // 2
        text_top_y = 50

        if not gs.cutscene_frames:
            win_text = font.render("You caught the fish!", True, settings.YELLOW)
            win_rect = win_text.get_rect(center=(text_center_x, text_top_y))
            screen.blit(win_text, win_rect)

            # display fish stats
            fish_info_text = font.render(
                f"{gs.minigame.current_fish_type} - {gs.minigame.current_fish_weight} lbs | Score: {score}",
                True, settings.WHITE
            )
            fish_info_rect = fish_info_text.get_rect(center=(text_center_x, text_top_y + 40))
            screen.blit(fish_info_text, fish_info_rect)

            
            if not assets._GIF_SUPPORT:
                sub_text = font.render("Pillow not installed for GIF support.", True, settings.WHITE)
            else:
                sub_text = font.render(f"'{settings.WIN_GIF_PATH}' not found.", True, settings.WHITE)
            sub_rect = sub_text.get_rect(center=(text_center_x, text_top_y + 80))
            screen.blit(sub_text, sub_rect)
        else:
            win_text = font.render("Success!", True, settings.YELLOW)
            win_rect = win_text.get_rect(center=(text_center_x, text_top_y))
            screen.blit(win_text, win_rect)

            # display fish stats below "Success!"
            fish_info_text = font.render(
                f"{gs.minigame.current_fish_type} - {gs.minigame.current_fish_weight} lbs | Score: {score}",
                True, settings.WHITE
            )
            fish_info_rect = fish_info_text.get_rect(center=(text_center_x, text_top_y + 40))
            screen.blit(fish_info_text, fish_info_rect)

        restart_text = font.render("Click or press any key to fish again.", True, settings.WHITE)
        restart_rect = restart_text.get_rect(center=(text_center_x, settings.SCREEN_HEIGHT - 50))
        screen.blit(restart_text, restart_rect)
    
    elif gs.game_state == 'lost':
        # draw lose image if available
        if gs.assets.lose_img:
            scaled_lose = pygame.transform.scale(gs.assets.lose_img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            screen.blit(scaled_lose, (0, 0))
        else:
            # fallback if image is missing
            screen.fill((139, 0, 0)) # dark red

        lose_text = font.render("The fish got away...", True, settings.RED)
        # ensure mouse is visible on lose screen
        if not pygame.mouse.get_visible():
            pygame.mouse.set_visible(True)

        lose_rect = lose_text.get_rect(center=(settings.SCREEN_WIDTH // 2, 50))
        screen.blit(lose_text, lose_rect)

        # draw "Try Again" button
        try_again_button_rect = pygame.Rect(0, 0, 200, 50)
        try_again_button_rect.center = (settings.SCREEN_WIDTH // 2 - 120, settings.SCREEN_HEIGHT - 80)
        pygame.draw.rect(screen, settings.GREEN, try_again_button_rect)
        try_again_text = font.render("Try Again", True, settings.WHITE)
        screen.blit(try_again_text, try_again_text.get_rect(center=try_again_button_rect.center))

        # draw "Exit" button
        exit_button_rect = pygame.Rect(0, 0, 200, 50)
        exit_button_rect.center = (settings.SCREEN_WIDTH // 2 + 120, settings.SCREEN_HEIGHT - 80)
        pygame.draw.rect(screen, settings.RED, exit_button_rect)
        exit_text = font.render("Exit to Menu", True, settings.WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

    # draw highscore (always on top)
    highscore_surf = font.render(f"Highscore: {int(gs.highscore)}", True, settings.WHITE)
    screen.blit(highscore_surf, (20, 20))

    # update the display
    pygame.display.flip()

    # cap the frame rate
    clock.tick(60)