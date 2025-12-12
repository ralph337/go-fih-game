import random
import settings
import pygame

class Minigame:
    """Base class for all minigames."""
    def __init__(self, gs):
        pass

    def update(self, gs):
        """Update the minigame state."""
        raise NotImplementedError("Subclasses must implement update()")

# ---- inheritance (parent)----
class Fish:
    """Base class for all fish types."""
    def __init__(self, name, difficulty, base_score, weight_mult, asset_attr):
        self.name = name
        self.difficulty = difficulty
        self.base_score = base_score
        self.weight_mult = weight_mult
        self.asset_attr = asset_attr
        
        # stats randomization based on difficulty
        base_weight = 2.0 * difficulty
        self.weight = round(random.uniform(base_weight * 0.8, base_weight * 1.5), 2)
        self.size = round(random.uniform(5.0 * difficulty, 8.0 * difficulty), 1)
        
        # physics modifiers based on difficulty
        self.speed_modifier = 0.5 + (difficulty * 0.15)
        self.progress_gain_modifier = max(0.5, 1.5 - (difficulty * 0.1))
        self.progress_loss_modifier = 0.5 + (difficulty * 0.1)

    def get_score(self):
        return int(self.base_score + (self.weight * self.weight_mult))

# --- fish types (childrens) ---
class Carp(Fish):
    def __init__(self): super().__init__("Carp", 1, 50, 10, "fish_carp_img")
class Sardine(Fish):
    def __init__(self): super().__init__("Sardine", 1, 60, 12, "fish_sardine_img")
class Bream(Fish):
    def __init__(self): super().__init__("Bream", 2, 80, 15, "fish_bream_img")
class Bass(Fish):
    def __init__(self): super().__init__("Bass", 3, 120, 20, "fish_bass_img")
class Trout(Fish):
    def __init__(self): super().__init__("Trout", 3, 130, 22, "fish_trout_img")
class Salmon(Fish):
    def __init__(self): super().__init__("Salmon", 4, 200, 25, "fih")
class Tuna(Fish):
    def __init__(self): super().__init__("Tuna", 5, 300, 30, "fish_tuna_img")
class Pufferfish(Fish):
    def __init__(self): super().__init__("Pufferfish", 6, 400, 35, "pufferfish")
class Shark(Fish):
    def __init__(self): super().__init__("Shark", 8, 800, 50, "fish_shark_img")
class Legend(Fish):
    def __init__(self): super().__init__("Legend", 10, 2000, 100, "fish_legend_img")

ALL_FISH_CLASSES = [Carp, Sardine, Bream, Bass, Trout, Salmon, Tuna, Pufferfish, Shark, Legend]

# ----- polymorphism -----
class FishingMinigame(Minigame):
    def __init__(self, gs):
        super().__init__(gs)
        # the part where polyqmorphism happens (choosing a fish randomly from the list of fish classes)
        FishClass = random.choice(ALL_FISH_CLASSES)
        
        self.fish = FishClass()
        
        # fish stats to minigame variables
        self.current_fish_tier = "Difficulty " + str(self.fish.difficulty)
        self.current_fish_type = self.fish.name
        self.current_fish_weight = self.fish.weight
        self.current_fish_size = self.fish.size
        self.current_fish_speed_modifier = self.fish.speed_modifier
        self.current_fish_progress_gain_modifier = self.fish.progress_gain_modifier
        self.current_fish_progress_loss_modifier = self.fish.progress_loss_modifier

        # --- reset minigame variables ---
        self.catch_bar_y = gs.track_y + gs.track_h - gs.catch_bar_h
        self.catch_bar_vel = 0
        self.fish_y = gs.track_y + random.randint(0, gs.track_h - gs.fish_h)
        self.fish_vel = 0
        self.fish_target_y = self.fish_y
        self.fish_move_timer = 0

        self.catch_progress = 10 # starting progress bar
        self.first_hit_made = False

    def update(self, gs):
        """Handles all game logic for the 'fishing' state."""
        # player input
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        if keys[pygame.K_SPACE] or mouse_pressed:
            self.catch_bar_vel += settings.CATCH_BAR_SPEED_UP
        
        # apply physics to the catch bar (gravity)
        self.catch_bar_vel += settings.CATCH_BAR_GRAVITY
        self.catch_bar_y += self.catch_bar_vel

        # keep catch bar within the track
        if self.catch_bar_y < gs.track_y:
            self.catch_bar_y = gs.track_y
            self.catch_bar_vel = 0
        if self.catch_bar_y > gs.track_y + gs.track_h - gs.catch_bar_h:
            self.catch_bar_y = gs.track_y + gs.track_h - gs.catch_bar_h
            self.catch_bar_vel = 0

        # for making the fish only move once in conctact with the catch bar
        if self.first_hit_made:
            self.fish_move_timer -= 1
            if self.fish_move_timer <= 0:
                # pick a new target and a new time to move
                self.fish_target_y = gs.track_y + random.randint(0, gs.track_h - gs.fish_h)
                self.fish_move_timer = random.randint(20, 80)

            # accelerate towards the target
            if self.fish_y < self.fish_target_y:
                self.fish_vel += settings.FISH_ACCEL * self.current_fish_speed_modifier
            else:
                self.fish_vel -= settings.FISH_ACCEL * self.current_fish_speed_modifier

        # check for collision (overlap)
        catch_bar_rect = pygame.Rect(gs.track_x, self.catch_bar_y, gs.track_w, gs.catch_bar_h)
        fish_rect = pygame.Rect(gs.track_x, self.fish_y, gs.track_w, gs.fish_h)
        is_catching = catch_bar_rect.colliderect(fish_rect)

        # apply drag
        self.fish_vel *= settings.FISH_DRAG

        # apply slowdown if being caught, then move the fish
        if is_catching and self.first_hit_made:
            self.fish_y += self.fish_vel * settings.FISH_CAUGHT_SLOWDOWN
        else:
            self.fish_y += self.fish_vel

        if is_catching:
            if not self.first_hit_made:
                self.first_hit_made = True
                # switch to tension music
                gs.play_bgm(settings.TENSION_BGM_PATH)
            progress_to_add = settings.PROGRESS_GAIN * self.current_fish_progress_gain_modifier
            if gs.cheats["fast_catch"]:
                progress_to_add *= settings.DEBUG_FAST_CATCH_MULTIPLIER
            self.catch_progress += progress_to_add
            
            # play reeling sound
            if self.first_hit_made and gs.assets.reeling_sound:
                if not pygame.mixer.get_busy():
                    gs.assets.reeling_sound.play(loops=-1)
        else:
            if self.first_hit_made:
                self.catch_progress -= settings.PROGRESS_LOSS * self.current_fish_progress_loss_modifier
            
            # stop reeling sound if not catching
            if gs.assets.reeling_sound:
                gs.assets.reeling_sound.stop()

        self.catch_progress = max(0, min(self.catch_progress, 100))

        if self.first_hit_made and self.catch_progress <= 0:
            if gs.assets.reeling_sound:
                gs.assets.reeling_sound.stop()
            gs.game_state = 'lost'
            if gs.assets.lose_sound:
                gs.assets.lose_sound.play()
            # stop background music
            pygame.mixer.music.stop()
            gs.current_music = None

        if self.catch_progress >= 100:
            if gs.assets.cutscene_frames:
                gs.game_state = 'cutscene'
                gs.cutscene_frame_index = 0
                gs.cutscene_last_frame_time = pygame.time.get_ticks()
                if gs.assets.reeling_sound:
                    gs.assets.reeling_sound.stop()
                if gs.assets.cutscene_sound_1:
                    gs.assets.cutscene_sound_1.play()
                # stop music during cutscene
                pygame.mixer.music.stop()
                gs.current_music = None
            else:
                gs.game_state = 'won'
                if gs.assets.success_sound:
                    gs.assets.success_sound.play()
                # switch back to main music
                gs.play_bgm(settings.MAIN_BGM_PATH)