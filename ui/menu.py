"""
Underwater Treasure Hunt - Main Menu System
Presents an animated underwater title scene with volumetric god rays,
schools of fish, rising bubbles, and interactive glassmorphic buttons.
"""

import math
import time
from typing import Callable, Optional, Tuple
import pygame

from config import (
    TITLE,
    SUBTITLE,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from ui.buttons import Button
from audio.sound_manager import SoundManager
from game.particles import ParticleSystem
from game.enemy import MarineLifeManager
from ui.underwater_3d_scene import Underwater3DScene

class MainMenu:
    """Animated cinematic 3D underwater title menu screen."""

    def __init__(
        self,
        on_play: Callable[[], None],
        on_level_select: Callable[[], None],
        on_challenges: Callable[[], None],
        on_instructions: Callable[[], None],
        on_camera_check: Callable[[], None],
        on_quit: Callable[[], None],
        on_museum: Optional[Callable[[], None]] = None,
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_play = on_play
        self.on_level_select = on_level_select
        self.on_challenges = on_challenges
        self.on_instructions = on_instructions
        self.on_camera_check = on_camera_check
        self.on_quit = on_quit
        self.on_museum = on_museum
        self.sound_manager = sound_manager

        if not pygame.font.get_init():
            pygame.font.init()
        self.font_title_1 = pygame.font.SysFont("segoeui", 42, bold=True)
        self.font_title_2 = pygame.font.SysFont("segoeui", 46, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_warning = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_swim = pygame.font.SysFont("segoeui", 13, bold=True)

        # Photorealistic 3D cinematic underwater environment
        self.scene_3d = Underwater3DScene(theme="front_page")

        # Ambient particles and legacy managers preserved for full backward compatibility
        self.particles = ParticleSystem()
        self.marine_manager = MarineLifeManager(fish_count=0)
        self.marine_manager.fish = []

        # Interactive Menu Buttons (Preserved exactly for perfect alignment, tests, and clean visual layout)
        btn_w, btn_h = 330, 40
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 236
        spacing = 46

        self.play_btn = Button(
            pygame.Rect(cx, start_y, btn_w, btn_h),
            "START EXPEDITION >",
            font_size=17,
            on_click=self.on_play,
            sound_manager=self.sound_manager,
            accent_color=(0, 235, 255)
        )
        self.level_select_btn = Button(
            pygame.Rect(cx, start_y + spacing, btn_w, btn_h),
            "EXPEDITION ZONES",
            font_size=16,
            on_click=self.on_level_select,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )
        self.museum_btn = Button(
            pygame.Rect(cx, start_y + spacing * 2, btn_w, btn_h),
            "UNDERWATER MUSEUM",
            font_size=16,
            on_click=self.on_museum if self.on_museum else self.on_play,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )
        self.challenges_btn = Button(
            pygame.Rect(cx, start_y + spacing * 3, btn_w, btn_h),
            "ABYSSAL CHALLENGES",
            font_size=16,
            on_click=self.on_challenges,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )
        self.instructions_btn = Button(
            pygame.Rect(cx, start_y + spacing * 4, btn_w, btn_h),
            "HOW TO PLAY / GESTURES",
            font_size=16,
            on_click=self.on_instructions,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )
        self.camera_btn = Button(
            pygame.Rect(cx, start_y + spacing * 5, btn_w, btn_h),
            "CAMERA & GESTURE CHECK",
            font_size=16,
            on_click=self.on_camera_check,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )
        self.quit_btn = Button(
            pygame.Rect(cx, start_y + spacing * 6, btn_w, btn_h),
            "QUIT EXPEDITION",
            font_size=16,
            on_click=self.on_quit,
            sound_manager=self.sound_manager,
            accent_color=(0, 210, 245)
        )

        self.buttons = [
            self.play_btn,
            self.level_select_btn,
            self.museum_btn,
            self.challenges_btn,
            self.instructions_btn,
            self.camera_btn,
            self.quit_btn
        ]
        self.title_glow_phase = 0.0
        self.is_hand_detected: bool = False
        self.num_hands: int = 0

    def update(
        self,
        cursor_x: int,
        cursor_y: int,
        is_clicked: bool,
        dt: float,
        is_hand_detected: bool = False,
        num_hands: int = 0,
        is_pinching: bool = False
    ) -> None:
        self.is_hand_detected = is_hand_detected
        self.num_hands = num_hands
        self.title_glow_phase += 2.0 * dt
        self.scene_3d.update(dt, cursor_x, cursor_y)
        self.particles.update(dt)
        self.marine_manager.update(dt, current_active=False, cursor_pos=(cursor_x, cursor_y))

        for btn in self.buttons:
            btn.update(cursor_x, cursor_y, is_clicked or is_pinching, dt)

    def _draw_top_warning_banner(self, surface: pygame.Surface) -> None:
        """Renders top chamfered status visor showing live hand detection status."""
        banner_w, banner_h = 510, 28
        bx = SCREEN_WIDTH // 2 - banner_w // 2
        by = 24
        c = 7

        b_surf = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        pts = [
            (c, 0),
            (banner_w - c, 0),
            (banner_w, c),
            (banner_w, banner_h - c),
            (banner_w - c, banner_h),
            (c, banner_h),
            (0, banner_h - c),
            (0, c)
        ]
        # Translucent dark visor backing
        pygame.draw.polygon(b_surf, (8, 22, 38, 215), pts)

        status_pulse = math.sin(time.time() * 4.0) * 0.2 + 0.8
        if self.is_hand_detected:
            border_col = (0, 240, 180, 210)
            cam_col = (0, 240, 180)
            dot_col = (0, 255, 180)
            if self.num_hands >= 2:
                msg = "ONLINE: DUAL HANDS TRACKED — READY TO DIVE"
            else:
                msg = "ONLINE: HAND TRACKED — READY TO DIVE"
            txt_col = (140, 255, 220)
        else:
            border_col = (0, 205, 235, 175)
            cam_col = (255, 215, 60)
            dot_col = (255, 200, 40)
            msg = "STANDBY: HOLD HAND IN FRONT OF WEBCAM"
            txt_col = (255, 225, 100)

        # Visor border
        pygame.draw.polygon(b_surf, border_col, pts, width=1)

        # Camera icon & glowing status LED on left
        cam_x, cam_y = 28, banner_h // 2
        pygame.draw.rect(b_surf, cam_col, (cam_x - 7, cam_y - 5, 14, 10), border_radius=2)
        pygame.draw.rect(b_surf, cam_col, (cam_x - 3, cam_y - 7, 6, 2), border_radius=1)
        pygame.draw.circle(b_surf, (15, 25, 40), (cam_x, cam_y), 3)
        pygame.draw.circle(b_surf, cam_col, (cam_x, cam_y), 3, width=1)

        # Pulsing LED dot next to camera
        led_x = cam_x + 16
        pygame.draw.circle(b_surf, (*dot_col[:3], int(80 * status_pulse)), (led_x, cam_y), 6)
        pygame.draw.circle(b_surf, dot_col, (led_x, cam_y), 3)

        # Status text
        shadow = self.font_warning.render(msg, True, (4, 10, 18))
        txt = self.font_warning.render(msg, True, txt_col)
        tx = banner_w // 2 - txt.get_width() // 2 + 10
        ty = banner_h // 2 - txt.get_height() // 2
        b_surf.blit(shadow, (tx + 1, ty + 1))
        b_surf.blit(txt, (tx, ty))

        surface.blit(b_surf, (bx, by))

    def _draw_nautical_compass(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        """Renders the golden nautical compass rose / ship wheel emblem with wave flourishes."""
        # 1. Outer golden ship wheel ring
        pygame.draw.circle(surface, (235, 195, 65), (cx, cy), 18, 3)

        # 8 golden ship wheel handles/spokes
        for deg in (0, 45, 90, 135, 180, 225, 270, 315):
            rad = math.radians(deg)
            x1 = cx + math.cos(rad) * 12
            y1 = cy + math.sin(rad) * 12
            x2 = cx + math.cos(rad) * 24
            y2 = cy + math.sin(rad) * 24
            pygame.draw.line(surface, (235, 195, 65), (int(x1), int(y1)), (int(x2), int(y2)), 2)
            pygame.draw.circle(surface, (255, 225, 90), (int(x2), int(y2)), 2)

        # 2. Inner cyan ring
        pygame.draw.circle(surface, (0, 215, 245), (cx, cy), 11, 2)

        # 3. Center golden compass star
        pts_v = [(cx, cy - 12), (cx + 4, cy), (cx, cy + 12), (cx - 4, cy)]
        pts_h = [(cx - 12, cy), (cx, cy - 4), (cx + 12, cy), (cx, cy + 4)]
        pygame.draw.polygon(surface, (255, 235, 120), pts_v)
        pygame.draw.polygon(surface, (255, 215, 70), pts_h)
        pygame.draw.circle(surface, (0, 240, 255), (cx, cy), 3)

        # 4. Symmetrical glowing cyan wave flourishes (graceful curved swooshes)
        left_pts = [(cx - 22, cy + 2), (cx - 36, cy - 3), (cx - 52, cy + 3), (cx - 70, cy - 2)]
        right_pts = [(cx + 22, cy + 2), (cx + 36, cy - 3), (cx + 52, cy + 3), (cx + 70, cy - 2)]
        pygame.draw.lines(surface, (0, 220, 250), False, left_pts, 2)
        pygame.draw.lines(surface, (0, 220, 250), False, right_pts, 2)

    def _draw_crystalline_title(self, surface: pygame.Surface) -> None:
        """Renders stacked 3D crystalline embossed title with wave ribbons and subtitle."""
        cx = SCREEN_WIDTH // 2
        pulse = math.sin(self.title_glow_phase)
        y1 = 98 + int(pulse * 1.5)
        y2 = 140 + int(pulse * 1.5)

        text_1 = "UNDERWATER"
        text_2 = "TREASURE HUNT"

        # Helper to render 3D crystalline faceted text with dynamic specular light gleam
        glint_phase = (time.time() * 0.5) % 4.0

        def draw_crystal_text(font, text, cy):
            txt_surf = font.render(text, True, (246, 252, 255))
            tw = txt_surf.get_width()
            th = txt_surf.get_height()
            tx = cx - tw // 2

            # Deep navy drop shadow with ambient soft spread
            shadow_surf = font.render(text, True, (2, 8, 20))
            for sox, soy in [(0, 3), (2, 3), (-1, 2), (1, 2), (0, 2)]:
                surface.blit(shadow_surf, (tx + sox, cy + soy))

            # Cyan crystalline bevel extrusion
            bevel_surf = font.render(text, True, (0, 195, 235))
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)]:
                surface.blit(bevel_surf, (tx + ox, cy + oy))

            # Crisp platinum face
            surface.blit(txt_surf, (tx, cy))

            # Subtle periodic crystalline light gleam sweep across letters
            if glint_phase < 1.0:
                gleam_x = tx + int(glint_phase * (tw + 80) - 40)
                if tx - 20 <= gleam_x <= tx + tw + 20:
                    gleam_surf = pygame.Surface((24, th), pygame.SRCALPHA)
                    pygame.draw.polygon(gleam_surf, (255, 255, 255, 75), [(14, 0), (24, 0), (10, th), (0, th)])
                    surface.blit(gleam_surf, (gleam_x, cy))

        draw_crystal_text(self.font_title_1, text_1, y1)
        draw_crystal_text(self.font_title_2, text_2, y2)

        # Luminous flowing cyan wave ribbons under title
        wave_y = y2 + 48
        wave_pts_1 = []
        wave_pts_2 = []
        for i in range(-190, 191, 10):
            norm = i / 190.0
            arch = (1.0 - norm * norm) * 7.0
            wave_pts_1.append((cx + i, int(wave_y - arch + math.sin(i * 0.05 + self.title_glow_phase) * 2)))
            wave_pts_2.append((cx + i, int(wave_y - arch + 4 + math.sin(i * 0.05 + self.title_glow_phase + 1.0) * 1.5)))

        pygame.draw.lines(surface, (0, 225, 255), False, wave_pts_1, 2)
        pygame.draw.lines(surface, (0, 185, 225), False, wave_pts_2, 1)

        # Subtitle
        sub_text = SUBTITLE
        sub_shadow = self.font_subtitle.render(sub_text, True, (2, 8, 18))
        sub_surf = self.font_subtitle.render(sub_text, True, (225, 248, 255))
        sx = cx - sub_surf.get_width() // 2
        sy = wave_y + 14
        surface.blit(sub_shadow, (sx + 1, sy + 1))
        surface.blit(sub_surf, (sx, sy))

    def _draw_bottom_hud(self, surface: pygame.Surface) -> None:
        """Renders sleek glass capsule touchless gesture guidance HUD above seafloor."""
        cx = SCREEN_WIDTH // 2
        cy = 662
        pill_w, pill_h = 560, 32
        px = cx - pill_w // 2
        py = cy - pill_h // 2
        c = 8

        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pts = [
            (c, 0), (pill_w - c, 0), (pill_w, c),
            (pill_w, pill_h - c), (pill_w - c, pill_h),
            (c, pill_h), (0, pill_h - c), (0, c)
        ]
        # Translucent glass backing
        pygame.draw.polygon(pill_surf, (6, 22, 40, 195), pts)
        # Glowing cyan border
        pulse = math.sin(time.time() * 2.5) * 0.2 + 0.8
        border_col = (0, int(200 * pulse), int(235 * pulse), 180)
        pygame.draw.polygon(pill_surf, border_col, pts, width=1)

        # Specular sheen
        pygame.draw.line(pill_surf, (200, 245, 255, 70), (c + 2, 1), (pill_w - c - 2, 1), 1)

        surface.blit(pill_surf, (px, py))

        # Touchless Hand Gesture Icon & Guide Text
        guide_text = "TOUCHLESS VISION: POINT TO AIM  |  DWELL OR PINCH TO DIVE"
        shadow = self.font_swim.render(guide_text, True, (2, 8, 18))
        txt = self.font_swim.render(guide_text, True, (130, 240, 255))

        # Hand icon on left inside pill
        hx = px + 24
        hy = cy
        pygame.draw.rect(surface, (0, 235, 255), (hx - 5, hy - 4, 10, 8), border_radius=1)
        pygame.draw.line(surface, (0, 235, 255), (hx - 4, hy - 4), (hx - 4, hy - 9), 1)
        pygame.draw.line(surface, (0, 235, 255), (hx - 1, hy - 4), (hx - 1, hy - 11), 1)
        pygame.draw.line(surface, (0, 235, 255), (hx + 2, hy - 4), (hx + 2, hy - 10), 1)
        pygame.draw.line(surface, (0, 235, 255), (hx + 5, hy - 4), (hx + 5, hy - 8), 1)

        # Guide text centered in pill
        tx = cx - txt.get_width() // 2 + 10
        ty = cy - txt.get_height() // 2
        surface.blit(shadow, (tx + 1, ty + 1))
        surface.blit(txt, (tx, ty))

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the realistic cinematic 3D underwater menu scene matching reference target."""
        # 1. Dynamic 3D Ocean World Simulation (Reference Backdrop, Bubbles, Caustics, Marine Snow, Parallax)
        self.scene_3d.draw(surface, show_chest=True)

        # 2. Top Warning Visor Banner
        self._draw_top_warning_banner(surface)

        # 3. Stacked 3D Crystalline Title & Subtitle
        self._draw_crystalline_title(surface)

        # 5. Interactive Holographic Chamfered Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # 6. Holographic Touchless Vision & Gesture HUD
        self._draw_bottom_hud(surface)
