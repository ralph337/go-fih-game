import os

# game settings for go fish

# --- asset paths ---
def get_asset_path(filename):
    """Gets the absolute path for an asset, looking in an 'assets' subfolder."""
    return os.path.join(os.path.dirname(__file__), 'assets', filename)

WIN_GIF_PATH = get_asset_path("cutscene1.gif")
MENU_BG_PATH = get_asset_path("menu_background.png")
PLAY_BUTTON_PATH = get_asset_path("play_button.png")
FISHING_BG_PATH = get_asset_path("fishing_background.png")
SUCCESS_IMG_PATH = get_asset_path("success.png")
LOSE_IMG_PATH = get_asset_path("lose.png")
FISH_CARP_PATH = get_asset_path("fish_carp.png")
FISH_SARDINE_PATH = get_asset_path("fish_sardine.png")
FISH_BREAM_PATH = get_asset_path("fish_bream.png")
FISH_BASS_PATH = get_asset_path("fish_bass.png")
FISH_TROUT_PATH = get_asset_path("fish_trout.png")
FISH_SALMON_PATH = get_asset_path("fish_salmon.png")
FISH_TUNA_PATH = get_asset_path("fish_tuna.png")
FISH_PUFFERFISH_PATH = get_asset_path("fish_pufferfish.png")
FISH_SHARK_PATH = get_asset_path("fish_shark.png")
FISH_LEGEND_PATH = get_asset_path("fish_legend.png")
FONT_PATH = get_asset_path("pirate_font.ttf")

WAITING_IMG_PATH = get_asset_path("waiting_indicator.png")
BITE_IMG_PATH = get_asset_path("bite_indicator.png")
PROGRESS_HIGH_IMG_PATH = get_asset_path("progress_high.png")
PROGRESS_MID_IMG_PATH = get_asset_path("progress_mid.png")
PROGRESS_LOW_IMG_PATH = get_asset_path("progress_low.png")

CASTING_SOUND_PATH = get_asset_path("casting.mp3")
BITE_SOUND_PATH = get_asset_path("bite.mp3")
REELING_SOUND_PATH = get_asset_path("reeling.mp3")
SUCCESS_SOUND_PATH = get_asset_path("success.mp3")
LOSE_SOUND_PATH = get_asset_path("lose.mp3")
CUTSCENE_SOUND_1_PATH = get_asset_path("cutscene_sfx_1.mp3")
CUTSCENE_SOUND_30_PATH = get_asset_path("cutscene_sfx_30.mp3")
CUTSCENE_SOUND_60_PATH = get_asset_path("cutscene_sfx_60.mp3")
MAIN_BGM_PATH = get_asset_path("main_bgm.mp3")
TENSION_BGM_PATH = get_asset_path("tension_bgm.mp3")
BUTTON_CLICK_SOUND_PATH = get_asset_path("button_click.mp3")

# --- screen settings ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# --- colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
RED = (255, 100, 100)
GREY = (50, 50, 50)

# --- fishing minigame settings ---
TRACK_H_RATIO = 0.75
TRACK_W_RATIO = 0.1
TRACK_X_RATIO = 0.1

CATCH_BAR_H_RATIO = 0.2
CATCH_BAR_SPEED_UP = -0.5
CATCH_BAR_GRAVITY = 0.25

FISH_H_RATIO = 0.075
PROGRESS_GAIN = 0.4
PROGRESS_LOSS = 0.2

PROGRESS_BAR_W_RATIO = 0.6

# --- fish ai settings ---
FISH_ACCEL = 0.2
FISH_DRAG = 0.95
FISH_CAUGHT_SLOWDOWN = 0.5 # multiplier for fish speed when being caught (e.g., 0.5 = 50% slower)

# --- fish probabilities ---
# chance to encounter a fish from a certain tier. must sum to 100.
TIER_CHANCES = {
    "Normal": 60,
    "Heavy": 40,
}

# chance to encounter a fish of a certain type, given its tier. each tier's chances must sum to 100.
TYPE_CHANCES = {
    "Normal": {
        "Tiny": 10,
        "Small": 60,
        "Medium": 30,
    },
    "Heavy": {
        "Large": 100, # only one type in Heavy, so it's 100%
    },
}

# --- fish tiers and stats ---
# define different fish types with their base stats and randomization ranges
# each fish type will have:
#   - 'speed_range': (min_speed_modifier, max_speed_modifier) for fish_vel
#   - 'progress_gain_mod_range': (min_modifier, max_modifier) for how much progress is gained
#   - 'progress_loss_mod_range': (min_modifier, max_modifier) for how much progress is lost
#   - 'weight_range': (min_weight, max_weight) in arbitrary units (e.g., lbs or kg)
#   - 'size_range': (min_size, max_size) in arbitrary units (e.g., inches or cm)

FISH_TYPES = {
    "Normal": {
        "Tiny": {
            "speed_range": (0.8, 1.0),
            "progress_gain_mod_range": (1.0, 1.2),
            "progress_loss_mod_range": (0.8, 1.0),
            "weight_range": (0.1, 0.5),
            "size_range": (5, 10),
        },
        "Small": {
            "speed_range": (1.0, 1.3),
            "progress_gain_mod_range": (0.9, 1.1),
            "progress_loss_mod_range": (0.9, 1.1),
            "weight_range": (0.5, 2.0),
            "size_range": (10, 20),
        },
        "Medium": {
            "speed_range": (1.2, 1.6),
            "progress_gain_mod_range": (0.8, 1.0),
            "progress_loss_mod_range": (1.0, 1.2),
            "weight_range": (2.0, 5.0),
            "size_range": (20, 30),
        },
    },
    "Heavy": {
        "Large": { # heavy fish might just have one type for simplicity, or more if desired
            "speed_range": (1.5, 2.0),
            "progress_gain_mod_range": (0.6, 0.9),
            "progress_loss_mod_range": (1.2, 1.5),
            "weight_range": (5.0, 20.0),
            "size_range": (30, 60),
        },
    },
}

# --- ui customization ---
GIF_SPEED_MULTIPLIER = 0.75
PLAY_BUTTON_POS_X = 0.33
PLAY_BUTTON_POS_Y = 0.33

# --- debug settings ---
# set to true to draw outlines around ui elements
DEBUG_UI_OUTLINES = True
DEBUG_FAST_CATCH_MULTIPLIER = 5.0 # how much faster progress is gained with the cheat