import pygame
import os
import settings

# has everything related to loading assets (images, sounds, etc)
try:
    from PIL import Image, ImageSequence
    _GIF_SUPPORT = True
except ImportError:
    Image = ImageSequence = None
    _GIF_SUPPORT = False

# ---- error handling for image loading ----
def load_image_safely(path, variable_name):
    """Tries to load an image, printing a specific error if it fails."""
    if not os.path.exists(path):
        directory = os.path.dirname(path)
        alt_path = os.path.join(directory, variable_name + ".png")
        if os.path.exists(alt_path):
            print(f"Asset found at alternate path: {alt_path}")
            path = alt_path
        else:
            print(f"Asset not found: {path} (also checked {alt_path})")
            return None
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading {variable_name} from {path}: {e}")
        print("This can be caused by a file corruption or an 'iCCP' profile issue.")
        print("-> Try re-saving the PNG file in an image editor like GIMP or Paint.NET.")
        return None
# ---- image scaling helper ----
def _safe_scale_image(img, max_w, max_h):
    """Scale `img` to fit within (`max_w`, `max_h`) preserving aspect ratio."""
    if not img:
        return None
    iw, ih = img.get_size()
    if iw == 0 or ih == 0: return img
    scale = min(max_w / iw, max_h / ih)
    if scale <= 0: return img
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    try:
        return pygame.transform.smoothscale(img, new_size)
    except Exception:
        return pygame.transform.scale(img, new_size)

# ---- gif loading support ---- (frame counting and resizing)
    # also error handling if PIL is not installed (if gif not working)
def load_gif_frames(path):
    """Loads frames and their durations from a GIF, resizing them to fit the screen."""
    if not _GIF_SUPPORT or not os.path.exists(path):
        return None

    frames = []
    try:
        with Image.open(path) as pil_img:
            default_duration = pil_img.info.get('duration', 100)
            for pil_frame in ImageSequence.Iterator(pil_img):
                duration = int(pil_frame.info.get('duration', default_duration) * settings.GIF_SPEED_MULTIPLIER)
                pil_frame = pil_frame.copy().convert('RGBA')
                raw_surface = pygame.image.fromstring(
                    pil_frame.tobytes(), pil_frame.size, pil_frame.mode
                ).convert_alpha()
                frame_surface = pygame.transform.smoothscale(raw_surface, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
                frames.append((frame_surface, duration))
    except Exception as e:
        print(f"Error loading GIF {path}: {e}")
        return None
    print(f"Loaded {len(frames)} frames from GIF: {os.path.basename(path)}")
    return frames

class Assets:
    def __init__(self):
        # --- menu assets ---
        self.menu_bg_img = self.load_menu_bg()
        self.play_button_img = self.load_play_button()
        self.fishing_bg_img = self.load_fishing_bg()
        self.success_img = load_image_safely(settings.SUCCESS_IMG_PATH, "success_img")
        self.lose_img = load_image_safely(settings.LOSE_IMG_PATH, "lose_img")
        self.fish_carp_img = load_image_safely(settings.FISH_CARP_PATH, "fish_carp_img")
        self.fish_sardine_img = load_image_safely(settings.FISH_SARDINE_PATH, "fish_sardine_img")
        self.fish_bream_img = load_image_safely(settings.FISH_BREAM_PATH, "fish_bream_img")
        self.fish_bass_img = load_image_safely(settings.FISH_BASS_PATH, "fish_bass_img")
        self.fish_trout_img = load_image_safely(settings.FISH_TROUT_PATH, "fish_trout_img")
        self.fih = load_image_safely(settings.FISH_SALMON_PATH, "fih")
        self.fish_tuna_img = load_image_safely(settings.FISH_TUNA_PATH, "fish_tuna_img")
        self.pufferfish = load_image_safely(settings.FISH_PUFFERFISH_PATH, "pufferfish")
        self.fish_shark_img = load_image_safely(settings.FISH_SHARK_PATH, "fish_shark_img")
        self.fish_legend_img = load_image_safely(settings.FISH_LEGEND_PATH, "fish_legend_img")

        # --- game state image assets ---
        self.waiting_img = load_image_safely(settings.WAITING_IMG_PATH, "waiting_img")
        self.bite_img = load_image_safely(settings.BITE_IMG_PATH, "bite_img")
        self.progress_high_img = load_image_safely(settings.PROGRESS_HIGH_IMG_PATH, "progress_high_img")
        self.progress_mid_img = load_image_safely(settings.PROGRESS_MID_IMG_PATH, "progress_mid_img")
        self.progress_low_img = load_image_safely(settings.PROGRESS_LOW_IMG_PATH, "progress_low_img")

        # --- sound assets ---
        self.casting_sound = self.load_sound(settings.CASTING_SOUND_PATH)
        self.bite_sound = self.load_sound(settings.BITE_SOUND_PATH)
        self.reeling_sound = self.load_sound(settings.REELING_SOUND_PATH, volume=0.5)
        self.success_sound = self.load_sound(settings.SUCCESS_SOUND_PATH)
        self.lose_sound = self.load_sound(settings.LOSE_SOUND_PATH)
        self.cutscene_sound_1 = self.load_sound(settings.CUTSCENE_SOUND_1_PATH)
        self.cutscene_sound_30 = self.load_sound(settings.CUTSCENE_SOUND_30_PATH)
        self.cutscene_sound_60 = self.load_sound(settings.CUTSCENE_SOUND_60_PATH)
        self.button_click_sound = self.load_sound(settings.BUTTON_CLICK_SOUND_PATH)

        # --- cutscene frames ---
        self.cutscene_frames = load_gif_frames(settings.WIN_GIF_PATH)

        self.scale_images()

# ---- error handling for sound loading when it fails ----
    def load_sound(self, path, volume=1.0):
        if not os.path.exists(path): return None
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return None

    def load_menu_bg(self):
        try:
            img = pygame.image.load(settings.MENU_BG_PATH).convert()
            return pygame.transform.scale(img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading menu background: {e}")
            return None

    def load_play_button(self):
        try:
            img = pygame.image.load(settings.PLAY_BUTTON_PATH).convert_alpha()
            # Scale the button to be smaller
            original_size = img.get_size()
            scale_factor = 0.5 # 50% of original size
            new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            return pygame.transform.smoothscale(img, new_size)
        except Exception as e:
            print(f"Error loading play button: {e}")
            return None

    def load_fishing_bg(self):
        try:
            img = pygame.image.load(settings.FISHING_BG_PATH).convert()
            return pygame.transform.scale(img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading fishing background: {e}")
            return None

    def scale_images(self):
        indicator_max_w = int(settings.SCREEN_WIDTH * 0.8)
        indicator_max_h = int(settings.SCREEN_HEIGHT * 0.8)
        self.waiting_img = _safe_scale_image(self.waiting_img, indicator_max_w, indicator_max_h)
        self.bite_img = _safe_scale_image(self.bite_img, indicator_max_w, indicator_max_h)
        self.progress_high_img = _safe_scale_image(self.progress_high_img, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.progress_mid_img = _safe_scale_image(self.progress_mid_img, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.progress_low_img = _safe_scale_image(self.progress_low_img, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.progress_low_img = _safe_scale_image(self.progress_low_img, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)