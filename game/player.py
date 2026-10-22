"""
Underwater Treasure Hunt - Underwater Swimmer & Explorer System
The player physically controls an underwater scuba diver exploring the abyss.
Features swimming physics, fin flutter kinematics, dynamic pitch tilting,
headlight beam, carried treasure mechanics, oxygen reserves, and shield forcefields.
"""

import math
import os
import random
import time
from typing import Optional, Tuple
import pygame

from config import (
    INITIAL_OXYGEN,
    PASSIVE_OXYGEN_DEPLETION_RATE,
    SONAR_INITIAL_CHARGES,
    WATER_CURRENT_DURATION,
    SWIMMER_SPEED,
    SWIMMER_ACCEL,
    SWIMMER_FRICTION,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_DIVER_TEX: Optional[pygame.Surface] = None

def _get_diver_texture() -> Optional[pygame.Surface]:
    global _DIVER_TEX
    if _DIVER_TEX is None:
        p = os.path.join(ASSETS_DIR, "scuba_diver_hd.png")
        if os.path.isfile(p):
            try:
                _DIVER_TEX = pygame.image.load(p).convert_alpha()
            except Exception:
                _DIVER_TEX = None
    return _DIVER_TEX

class Player:
    """The underwater explorer swimmer character controlled via hand gestures."""

    def __init__(self):
        # Kinematics & Position
        self.x: float = SCREEN_WIDTH / 2.0
        self.y: float = SCREEN_HEIGHT / 2.0
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.facing_right: bool = True
        self.swim_angle: float = 0.0
        self.fin_flutter: float = 0.0
        self.speed: float = SWIMMER_SPEED

        # Vitals & Equipment
        self.oxygen: float = INITIAL_OXYGEN
        self.display_oxygen: float = INITIAL_OXYGEN
        self.lives: int = 3
        self.max_lives: int = 3
        self.invulnerability_timer: float = 0.0
        self.arm_stroke_phase: float = 0.0
        self.score: int = 0
        self.level_score: int = 0
        self.sonar_charges: int = SONAR_INITIAL_CHARGES
        
        # Action timers
        self.current_active_timer: float = 0.0
        self.screen_shake_timer: float = 0.0
        self.screen_shake_intensity: float = 0.0
        self.bubble_exhaust_timer: float = 0.0

        # Treasure Carrying State
        self.carried_treasure = None  # Reference to Treasure object being carried

        # Interaction & Swimmer Visuals
        self.is_hovering_interactable: bool = False
        self.is_hovering_danger: bool = False
        self.is_hovering_chest: bool = False
        self.is_pinching: bool = False
        self.pinch_anim_scale: float = 1.0
        self.shield_active: bool = False
        self.pulse_phase: float = 0.0

        # Dual-hand Swimming State
        self.is_dual_hand_swimming: bool = False
        self.paddle_boost: float = 1.0
        self.dual_swim_wake_phase: float = 0.0

        # Stabilized Kinematics & Tracking Filters
        self.target_filter_x: float = SCREEN_WIDTH / 2.0
        self.target_filter_y: float = SCREEN_HEIGHT / 2.0
        self.last_face_change_time: float = 0.0

    def reset_for_level(self) -> None:
        """Resets oxygen, charges, and carried items when embarking on a level."""
        self.oxygen = INITIAL_OXYGEN
        self.display_oxygen = INITIAL_OXYGEN
        self.invulnerability_timer = 0.0
        self.sonar_charges = SONAR_INITIAL_CHARGES
        self.current_active_timer = 0.0
        self.level_score = 0
        self.screen_shake_timer = 0.0
        self.carried_treasure = None
        self.is_dual_hand_swimming = False
        self.paddle_boost = 1.0
        self.dual_swim_wake_phase = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.target_filter_x = self.x
        self.target_filter_y = self.y
        self.last_face_change_time = 0.0

    def add_score(self, amount: int) -> None:
        """Adjusts score by given amount (can be positive or penalty)."""
        self.score = max(0, self.score + amount)
        self.level_score = max(0, self.level_score + amount)

    def reduce_oxygen(self, penalty: float, shake_duration: float = 0.4, shake_power: float = 8.0) -> None:
        """Drains oxygen and triggers screen shake feedback."""
        self.oxygen = max(0.0, self.oxygen - penalty)
        self.trigger_screen_shake(shake_duration, shake_power)

    def lose_life(self) -> bool:
        """
        Drains 1 life upon major hazard collision (Shark, Trap, Guardian).
        Returns True if player is still alive, False if all 3 lives lost.
        """
        if self.invulnerability_timer > 0.0:
            return True

        self.lives = max(0, self.lives - 1)
        self.invulnerability_timer = 2.2  # 2.2 seconds grace period
        self.trigger_screen_shake(0.65, 14.0)
        self.reduce_oxygen(15.0)

        # Drop carried treasure on impact
        if self.carried_treasure:
            self.carried_treasure.drop(self.x, self.y)
            self.carried_treasure = None

        return self.lives > 0

    def trigger_screen_shake(self, duration: float = 0.4, intensity: float = 8.0) -> None:
        """Triggers an underwater rumble screen shake."""
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity

    def activate_sonar(self) -> bool:
        """Attempts to consume a sonar charge. Returns True if successful."""
        if self.sonar_charges > 0:
            self.sonar_charges -= 1
            return True
        return False

    def activate_water_current(self) -> bool:
        """Activates directional water current if not already active."""
        if self.current_active_timer <= 0:
            self.current_active_timer = WATER_CURRENT_DURATION
            return True
        return False

    def grab_treasure(self, treasure) -> None:
        """Attaches a treasure to the swimmer's hands."""
        self.carried_treasure = treasure
        treasure.is_carried = True

    def release_carried_treasure(self):
        """Releases the carried treasure. Returns the released treasure object."""
        treasure = self.carried_treasure
        if treasure:
            treasure.is_carried = False
            self.carried_treasure = None
        return treasure

    def update(
        self,
        dt: float,
        target_x: float,
        target_y: float,
        is_pinching: bool,
        shield_active: bool,
        current_force_x: float = 0.0,
        is_dual_hand_swimming: bool = False,
        paddle_boost: float = 1.0,
    ) -> bool:
        """
        Updates swimmer kinematics, smooth acceleration, orientation, and vitals.
        Supports both single-hand guiding and high-propulsion dual-hand swimming.
        Returns True if a regulator bubble should be emitted.
        """
        self.is_pinching = is_pinching
        self.shield_active = shield_active
        self.is_dual_hand_swimming = is_dual_hand_swimming
        self.paddle_boost = paddle_boost
        self.pulse_phase += 4.5 * dt
        if self.invulnerability_timer > 0.0:
            self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)
        if is_dual_hand_swimming:
            self.dual_swim_wake_phase += 11.0 * dt
            self.arm_stroke_phase += 12.0 * dt
        else:
            self.arm_stroke_phase += 5.5 * dt

        # 1. Stable Hand Target Filtering: Absorbs high-frequency webcam tremor
        filter_alpha = min(1.0, 18.0 * dt)
        self.target_filter_x += (target_x - self.target_filter_x) * filter_alpha
        self.target_filter_y += (target_y - self.target_filter_y) * filter_alpha

        # Swimming Physics: Highly stable, fluid, and responsive navigation
        dx = self.target_filter_x - self.x
        dy = self.target_filter_y - self.y
        dist = math.hypot(dx, dy)

        DEADZONE = 10.0    # Pixels - micro-tremor deadzone where diver rests with zero shaking
        ARRIVE_RAD = 110.0 # Pixels - smooth deceleration envelope towards hand

        now = time.time()

        if dist > DEADZONE:
            dir_x = dx / dist
            dir_y = dy / dist

            # Smoothly ramp speed based on distance:
            # - Near arrival: smooth cubic ease-out so diver decelerates gracefully without oscillation
            # - At distance: smoothly reaches cruise speed, boosted by dual-hand paddle if active
            if dist < ARRIVE_RAD:
                ratio = (dist - DEADZONE) / (ARRIVE_RAD - DEADZONE)
                smooth_factor = ratio * ratio * (3.0 - 2.0 * ratio)
                target_speed = self.speed * smooth_factor
            else:
                dist_boost = min(1.5, 1.0 + (dist - ARRIVE_RAD) / 350.0)
                target_speed = self.speed * dist_boost

            if is_dual_hand_swimming:
                target_speed *= self.paddle_boost

            target_vx = dir_x * target_speed
            target_vy = dir_y * target_speed

            # Fluid hydrodynamic acceleration (smooth, critically damped transition towards target velocity)
            accel_rate = min(1.0, 11.0 * dt)
            self.vx += (target_vx - self.vx) * accel_rate
            self.vy += (target_vy - self.vy) * accel_rate

            # Hysteresis for facing direction: prevents nervous stroboscopic flipping
            if (now - self.last_face_change_time) > 0.20:
                if dx > 35.0 and self.vx > 25.0:
                    if not self.facing_right:
                        self.facing_right = True
                        self.last_face_change_time = now
                elif dx < -35.0 and self.vx < -25.0:
                    if self.facing_right:
                        self.facing_right = False
                        self.last_face_change_time = now

            # Smooth pitch tilt based on vertical swimming velocity
            current_speed = math.hypot(self.vx, self.vy)
            if current_speed > 35.0:
                desired_tilt = max(-0.42, min(0.42, math.atan2(self.vy, abs(self.vx) + 75.0) * 0.50))
            else:
                desired_tilt = 0.0
            self.swim_angle += (desired_tilt - self.swim_angle) * min(1.0, 7.5 * dt)

            # Fin kick flutter speed scales smoothly with current swimming speed
            flutter_mult = 1.4 if is_dual_hand_swimming else 1.0
            self.fin_flutter += max(1.5, current_speed * 0.035 * flutter_mult) * dt
        else:
            # Idle glide deceleration: diver glides gently to a stable halt inside the deadzone
            friction = 0.82 ** (dt * 60.0)
            self.vx *= friction
            self.vy *= friction
            self.swim_angle *= (0.78 ** (dt * 60.0))
            self.fin_flutter += 2.0 * dt

        # Water Current displacement
        if current_force_x != 0.0:
            self.vx += current_force_x * 0.5 * dt

        # Integrate velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Boundary clamping within playable screen area
        self.x = max(45.0, min(SCREEN_WIDTH - 45.0, self.x))
        self.y = max(85.0, min(SCREEN_HEIGHT - 65.0, self.y))

        # 2. Update Carried Treasure position to follow swimmer's hands
        if self.carried_treasure:
            hand_offset_x = 54.0 if self.facing_right else -54.0
            hand_offset_y = 14.0
            self.carried_treasure.x = self.x + hand_offset_x
            self.carried_treasure.y = self.y + hand_offset_y

        # 3. Passive Oxygen Depletion
        self.oxygen = max(0.0, self.oxygen - (PASSIVE_OXYGEN_DEPLETION_RATE * dt))

        # Smooth Display Oxygen Bar Interpolation
        diff = self.oxygen - self.display_oxygen
        self.display_oxygen += diff * min(1.0, 8.0 * dt)

        # Active Water Current Timer
        if self.current_active_timer > 0:
            self.current_active_timer -= dt

        # Screen Shake Decay
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt

        # Pinch visual animation spring
        target_scale = 0.65 if is_pinching else 1.0
        self.pinch_anim_scale += (target_scale - self.pinch_anim_scale) * min(1.0, 16.0 * dt)

        # Scuba Regulator Bubble Exhaust Timer
        self.bubble_exhaust_timer += dt * (1.6 if is_dual_hand_swimming else 1.0)
        emit_bubble = False
        threshold = 0.45 if is_dual_hand_swimming else 0.75
        if self.bubble_exhaust_timer >= threshold:
            self.bubble_exhaust_timer = random.uniform(0.0, 0.15)
            emit_bubble = True

        return emit_bubble

    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """Returns current (dx, dy) screen shake offset."""
        if self.screen_shake_timer <= 0:
            return (0, 0)
        decay = self.screen_shake_timer / 0.4
        power = self.screen_shake_intensity * decay
        return (int(random.uniform(-power, power)), int(random.uniform(-power, power)))

    def draw_swimmer(self, surface: pygame.Surface) -> None:
        """
        Renders the photorealistic underwater scuba explorer character with real
        neoprene wetsuit textures, flutter-kick kinematics, volumetric LED torch,
        dynamic underwater caustics, and carried relics.
        """
        cx, cy = int(self.x), int(self.y)
        d = 1 if self.facing_right else -1
        tilt_deg = math.degrees(self.swim_angle) * (1 if self.facing_right else -1)
        fin_kick = math.sin(self.fin_flutter) * 10.0

        # 1. Volumetric Headlamp Torch Beam (Realistic Ocean Illumination)
        head_x = cx + d * 48
        head_y = cy - 10
        light_len = 220
        light_w = 95
        torch_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        torch_origin = (head_x, head_y)
        for step, a in [(1.0, 10), (0.75, 16), (0.50, 24), (0.25, 36)]:
            lw = int(light_w * step)
            torch_poly = [
                torch_origin,
                (head_x + d * int(light_len * step), head_y - lw // 2 + int(self.swim_angle * 60)),
                (head_x + d * int(light_len * step), head_y + lw // 2 + int(self.swim_angle * 60)),
            ]
            pygame.draw.polygon(torch_surf, (225, 248, 255, a), torch_poly)
        # Central intense LED core
        pygame.draw.circle(torch_surf, (255, 255, 255, 140), torch_origin, 5)
        surface.blit(torch_surf, (0, 0))

        # 2. Forcefield Shield Dome (when Fist ✊ or 'S' key is held)
        if self.shield_active:
            shield_r = 58
            shield_surf = pygame.Surface((shield_r * 2 + 16, shield_r * 2 + 16), pygame.SRCALPHA)
            alpha = int(140 + 65 * math.sin(self.pulse_phase * 2.5))
            pygame.draw.circle(shield_surf, (*COLOR_NEON_TEAL[:3], alpha), (shield_r + 8, shield_r + 8), shield_r, 4)
            pygame.draw.circle(shield_surf, (*COLOR_OCEAN_CYAN[:3], int(alpha * 0.5)), (shield_r + 8, shield_r + 8), shield_r - 4, 2)
            pygame.draw.circle(shield_surf, (*COLOR_WHITE[:3], int(alpha * 0.35)), (shield_r + 8, shield_r + 8), shield_r - 8, 1)
            surface.blit(shield_surf, (cx - shield_r - 8, cy - shield_r - 8))

        # 3. Photorealistic Scuba Diver Character Sprite
        diver_tex = _get_diver_texture()
        if diver_tex is not None:
            base_w = 145
            base_h = 80
            flutter_ratio = math.sin(self.fin_flutter) * 0.07
            draw_h = max(20, int(base_h * (1.0 + flutter_ratio)))

            scaled_diver = pygame.transform.smoothscale(diver_tex, (base_w, draw_h))

            # Shimmering water caustics overlay on wetsuit
            caust_overlay = pygame.Surface(scaled_diver.get_size(), pygame.SRCALPHA)
            caust_a = int(32 + 18 * math.sin(self.pulse_phase * 1.6))
            pygame.draw.ellipse(caust_overlay, (200, 245, 255, caust_a), (base_w // 4, draw_h // 4, base_w // 2, draw_h // 3))
            scaled_diver.blit(caust_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Flip horizontally if swimming left
            if not self.facing_right:
                scaled_diver = pygame.transform.flip(scaled_diver, True, False)

            # Invulnerability damage flash
            if self.invulnerability_timer > 0.0 and (int(self.invulnerability_timer * 14) % 2 == 0):
                dmg_surf = scaled_diver.copy()
                dmg_surf.fill((255, 60, 60, 130), special_flags=pygame.BLEND_RGBA_MULT)
                scaled_diver = dmg_surf

            # Smooth pitch tilting along swimming trajectory
            rotated_diver = pygame.transform.rotate(scaled_diver, -tilt_deg)
            rect = rotated_diver.get_rect(center=(cx, cy))
            surface.blit(rotated_diver, rect.topleft)
        else:
            # Fallback procedural geometry
            swimmer_surf = pygame.Surface((90, 70), pygame.SRCALPHA)
            scx, scy = 45, 35
            suit_dark = (18, 32, 54)
            suit_accent = COLOR_NEON_TEAL
            tank_color = (240, 200, 30)
            mask_glow = (80, 230, 255)
            skin_tone = (235, 185, 145)

            fin_top_y = scy + 8 + int(fin_kick)
            fin_bot_y = scy + 16 - int(fin_kick)
            fin_poly_1 = [(scx - 22, scy + 10), (scx - 38, fin_top_y), (scx - 36, fin_top_y + 6), (scx - 20, scy + 12)]
            fin_poly_2 = [(scx - 20, scy + 12), (scx - 38, fin_bot_y), (scx - 36, fin_bot_y + 6), (scx - 18, scy + 14)]
            pygame.draw.polygon(swimmer_surf, (10, 80, 140), fin_poly_1)
            pygame.draw.polygon(swimmer_surf, (15, 105, 180), fin_poly_2)

            pygame.draw.line(swimmer_surf, suit_dark, (scx, scy + 6), (scx - 20, scy + 11), 7)
            body_rect = pygame.Rect(scx - 14, scy - 8, 30, 18)
            pygame.draw.ellipse(swimmer_surf, suit_dark, body_rect)
            pygame.draw.ellipse(swimmer_surf, suit_accent, body_rect, width=2)

            tank_rect = pygame.Rect(scx - 10, scy - 15, 20, 8)
            pygame.draw.rect(swimmer_surf, tank_color, tank_rect, border_radius=4)
            pygame.draw.circle(swimmer_surf, suit_dark, (scx + 15, scy - 2), 10)
            mask_rect = pygame.Rect(scx + 17, scy - 6, 8, 7)
            pygame.draw.ellipse(swimmer_surf, mask_glow, mask_rect)

            if not self.facing_right:
                swimmer_surf = pygame.transform.flip(swimmer_surf, True, False)
            rotated_surf = pygame.transform.rotate(swimmer_surf, -tilt_deg)
            surface.blit(rotated_surf, rotated_surf.get_rect(center=(cx, cy)).topleft)

        # 4. Precision Interaction Reticle (At the diver's hands)
        hand_x = cx + d * 52
        hand_y = cy + 14
        reticle_r = int(14 * self.pinch_anim_scale)

        if self.is_hovering_chest:
            cursor_col = COLOR_EMERALD
        elif self.is_hovering_danger:
            cursor_col = COLOR_CORAL_RED
        elif self.is_hovering_interactable or self.carried_treasure:
            cursor_col = COLOR_GOLD
        elif self.is_pinching:
            cursor_col = (255, 240, 120)
        else:
            cursor_col = COLOR_NEON_TEAL

        # Sleek glowing targeting ring with corner bracket accents
        pygame.draw.circle(surface, cursor_col, (hand_x, hand_y), reticle_r, 2)
        pygame.draw.circle(surface, COLOR_WHITE, (hand_x, hand_y), 3)

        # Dual-hand Swimming Hydrodynamic Wake visual
        if self.is_dual_hand_swimming:
            wake_surf = pygame.Surface((120, 50), pygame.SRCALPHA)
            wake_alpha = int(120 + 50 * math.sin(self.dual_swim_wake_phase))
            wake_col = (*COLOR_OCEAN_CYAN[:3], wake_alpha)
            pygame.draw.arc(wake_surf, wake_col, pygame.Rect(10, 10, 50, 30), 0.5, 2.6, 2)
            pygame.draw.arc(wake_surf, wake_col, pygame.Rect(60, 10, 50, 30), 0.5, 2.6, 2)
            surface.blit(wake_surf, (cx - 60, cy - 25))
