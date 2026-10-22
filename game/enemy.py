"""
Underwater Treasure Hunt - Autonomous Marine Life & Predators
Implements procedural fish schools with swimming kinematics and
shark apex predator events with shield deflection mechanics.
"""

import math
import os
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    COLOR_CORAL_RED,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_WHITE,
    SHARK_OXYGEN_PENALTY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from game.collision import point_in_circle, distance

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

_CLOWN_SURF: Optional[pygame.Surface] = None
_TANG_SURF: Optional[pygame.Surface] = None
_YELLOW_TANG_SURF: Optional[pygame.Surface] = None
_TURTLE_SURF: Optional[pygame.Surface] = None
_SHARK_SURF: Optional[pygame.Surface] = None
_MANTA_SURF: Optional[pygame.Surface] = None
_JELLY_SURF: Optional[pygame.Surface] = None
_TEXTURES_LOADED: bool = False

def _get_marine_textures() -> Tuple[Optional[pygame.Surface], Optional[pygame.Surface], Optional[pygame.Surface], Optional[pygame.Surface], Optional[pygame.Surface]]:
    global _CLOWN_SURF, _TANG_SURF, _YELLOW_TANG_SURF, _TURTLE_SURF, _SHARK_SURF, _MANTA_SURF, _JELLY_SURF, _TEXTURES_LOADED
    if not _TEXTURES_LOADED:
        _TEXTURES_LOADED = True
        def load_img(name: str) -> Optional[pygame.Surface]:
            p = os.path.join(ASSETS_DIR, name)
            if os.path.isfile(p):
                try:
                    return pygame.image.load(p).convert_alpha()
                except Exception:
                    return None
            return None
        _CLOWN_SURF = load_img("clownfish.png")
        _TANG_SURF = load_img("blue_tang.png")
        _YELLOW_TANG_SURF = load_img("yellow_tang.png")
        _TURTLE_SURF = load_img("sea_turtle.png")
        _SHARK_SURF = load_img("shark.png")
        _MANTA_SURF = load_img("manta_ray.png")
        _JELLY_SURF = load_img("jellyfish.png")
    return _CLOWN_SURF, _TANG_SURF, _YELLOW_TANG_SURF, _TURTLE_SURF, _SHARK_SURF

def _get_manta_texture() -> Optional[pygame.Surface]:
    _get_marine_textures()
    return _MANTA_SURF

def _get_jelly_texture() -> Optional[pygame.Surface]:
    _get_marine_textures()
    return _JELLY_SURF

class Fish:
    """An autonomous swimming fish with realistic burst-and-coast kinematics, 3D perspective turnarounds, and schooling depth."""

    def __init__(self, x: float = None, y: float = None, species: str = None, depth_layer: float = None):
        self.direction = random.choice([-1, 1])  # 1 = moving right, -1 = moving left
        if x is None:
            self.x = random.uniform(40.0, SCREEN_WIDTH - 40.0)
        else:
            self.x = x
        self.y = y if y is not None else random.uniform(90.0, SCREEN_HEIGHT - 70.0)
        self.base_y = self.y
        self.target_y = self.y

        # Depth Layer: 0.55 (far background, hazy, smaller) to 1.15 (foreground, crisp, vibrant)
        self.depth = depth_layer if depth_layer is not None else random.uniform(0.65, 1.12)
        
        # Base speed scaled by depth
        self.cruise_speed = random.uniform(55.0, 105.0) * self.depth
        self.current_speed = self.cruise_speed
        self.size = random.uniform(16.0, 24.0) * self.depth

        # Locomotion dynamics (Burst-and-Coast swimming)
        self.swim_phase = random.uniform(0, math.pi * 2)
        self.tail_phase = random.uniform(0, math.pi * 2)
        self.tail_speed = random.uniform(7.0, 12.0)
        self.burst_timer = random.uniform(1.2, 4.0)
        self.is_bursting = False
        self.burst_duration = 0.0
        self.wander_timer = random.uniform(2.5, 6.0)
        
        # Coral grazing / hovering behavior
        self.hover_timer = random.uniform(4.0, 10.0)
        self.is_hovering = False
        self.hover_duration = 0.0

        # 3D Perspective Turnaround state
        self.is_turning = False
        self.turn_progress = 0.0  # 0.0 to 1.0
        self.turn_duration = random.uniform(0.65, 0.95)
        self.turn_from_dir = self.direction
        self.spontaneous_turn_timer = random.uniform(6.0, 16.0)

        # Velocity vectors and banking
        self.vx = self.cruise_speed * self.direction
        self.vy = 0.0
        self.pitch_deg = 0.0

        # Species & visuals
        if species:
            self.species = species
        else:
            self.species = random.choice(["clown", "blue_tang", "yellow_tang", "silver", "gold"])
        
        # Colors for procedural fallback
        if self.species == "clown":
            self.color_body = (245, 115, 35)
            self.color_accent = COLOR_WHITE
        elif self.species in ("blue_tang", "silver"):
            self.color_body = (25, 90, 225)
            self.color_accent = COLOR_GOLD
        elif self.species in ("yellow_tang", "gold"):
            self.color_body = (245, 205, 30)
            self.color_accent = (255, 130, 45)
        else:
            self.color_body = (180, 205, 220)
            self.color_accent = (95, 155, 195)

    def update(self, dt: float, current_active: bool = False, cursor_pos: Tuple[int, int] = None) -> None:
        self.swim_phase += 1.8 * dt
        self.tail_phase += self.tail_speed * dt

        # 1. Burst-and-Coast cycle (authentic fish hydrodynamic behavior)
        self.burst_timer -= dt
        if self.burst_timer <= 0:
            if not self.is_bursting:
                self.is_bursting = True
                self.burst_duration = random.uniform(0.4, 0.8)
                self.tail_speed = random.uniform(15.0, 22.0)
            else:
                self.burst_duration -= dt
                if self.burst_duration <= 0:
                    self.is_bursting = False
                    self.burst_timer = random.uniform(1.8, 4.5)
                    self.tail_speed = random.uniform(6.5, 10.5)

        # 2. Grazing / hovering near reef crevices
        self.hover_timer -= dt
        if self.hover_timer <= 0 and not self.is_turning and not self.is_bursting:
            if not self.is_hovering:
                self.is_hovering = True
                self.hover_duration = random.uniform(0.8, 1.8)
                self.tail_speed = 4.0
            else:
                self.hover_duration -= dt
                if self.hover_duration <= 0:
                    self.is_hovering = False
                    self.hover_timer = random.uniform(6.0, 14.0)
                    self.tail_speed = random.uniform(7.0, 12.0)

        # 3. Target speed interpolation (burst acceleration vs coasting drag)
        target_spd = self.cruise_speed
        if self.is_hovering:
            target_spd *= 0.18
        elif self.is_bursting:
            target_spd *= 1.45
        self.current_speed += (target_spd - self.current_speed) * min(1.0, 3.5 * dt)

        # 4. Turnaround logic (3D perspective turnaround at margins or spontaneous roaming)
        margin = 42.0
        if not self.is_turning:
            edge_trigger = (self.x < margin and self.direction == -1) or (self.x > SCREEN_WIDTH - margin and self.direction == 1)
            self.spontaneous_turn_timer -= dt
            spontaneous_trigger = self.spontaneous_turn_timer <= 0 and (140.0 < self.x < SCREEN_WIDTH - 140.0)

            if edge_trigger or spontaneous_trigger:
                self.is_turning = True
                self.turn_progress = 0.0
                self.turn_from_dir = self.direction
                self.target_y = random.uniform(100.0, SCREEN_HEIGHT - 80.0)
                self.spontaneous_turn_timer = random.uniform(8.0, 18.0)
        else:
            self.turn_progress += dt / max(0.2, self.turn_duration)
            if self.turn_progress >= 1.0:
                self.turn_progress = 1.0
                self.is_turning = False
                self.direction = -self.turn_from_dir
                self.turn_from_dir = self.direction

        # Periodic natural depth roaming across water column
        self.wander_timer -= dt
        if self.wander_timer <= 0 and not self.is_turning:
            self.wander_timer = random.uniform(3.5, 7.5)
            self.target_y = random.uniform(90.0, SCREEN_HEIGHT - 85.0)

        # 5. Base swimming velocities with realistic vertical undulation
        if self.is_turning:
            prog = min(1.0, max(0.0, self.turn_progress))
            cos_val = math.cos(prog * math.pi)
            vx = self.current_speed * self.turn_from_dir * cos_val * 0.65
            vy = (self.target_y - self.y) * 1.8
        else:
            vx = self.current_speed * self.direction
            vy = math.sin(self.swim_phase) * (16.0 * self.depth) + (self.target_y - self.y) * 0.85

        # 6. Environmental Water Current reaction
        if current_active:
            vx += 160.0 * self.depth

        # 7. Player Cursor / Hand avoidance (fright & scatter response)
        if cursor_pos:
            cx, cy = cursor_pos
            dist_to_cursor = distance(self.x, self.y, cx, cy)
            if dist_to_cursor < 85.0:
                push = (85.0 - dist_to_cursor) * 2.2
                escape_dir = -1 if self.x < cx else 1
                vx += escape_dir * push
                vy += math.sin(self.swim_phase * 2.5) * push * 0.4
                self.is_hovering = False
                self.tail_phase += 18.0 * dt

        # 8. Coordinate update and boundary safety
        self.vx = vx
        self.vy = vy
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.y = max(65.0, min(SCREEN_HEIGHT - 45.0, self.y))

        # 9. Hydrodynamic pitch banking along velocity vector (naturally tilts head into dives & climbs)
        active_facing = self.direction if not self.is_turning else (self.turn_from_dir if math.cos(self.turn_progress * math.pi) >= 0 else -self.turn_from_dir)
        target_pitch = -math.degrees(math.atan2(self.vy, max(20.0, abs(self.vx)))) * active_facing
        target_pitch = max(-25.0, min(25.0, target_pitch))
        self.pitch_deg += (target_pitch - self.pitch_deg) * min(1.0, 7.0 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        s = self.size

        # 3D Turnaround foreshortening
        if self.is_turning:
            prog = min(1.0, max(0.0, self.turn_progress))
            cos_val = math.cos(prog * math.pi)
            facing = self.turn_from_dir if cos_val >= 0 else -self.turn_from_dir
            turn_w_mult = max(0.10, abs(cos_val))
        else:
            facing = self.direction
            turn_w_mult = 1.0

        d = 1 if facing > 0 else -1

        # Check for photorealistic sprite textures
        clown_surf, tang_surf, ytang_surf, _, _ = _get_marine_textures()
        
        target_surf = None
        tint_mult = None
        
        if self.species == "clown" and clown_surf:
            target_surf = clown_surf
        elif self.species == "blue_tang" and tang_surf:
            target_surf = tang_surf
        elif self.species == "yellow_tang" and ytang_surf:
            target_surf = ytang_surf
        elif self.species == "gold" and ytang_surf:
            target_surf = ytang_surf
        elif self.species == "silver" and tang_surf:
            target_surf = tang_surf
            tint_mult = (165, 215, 245)
        elif clown_surf:
            target_surf = clown_surf

        if target_surf:
            aspect = target_surf.get_height() / max(1, target_surf.get_width())
            fw = max(10, int(s * 3.0 * turn_w_mult))
            fh = max(8, int(s * 3.0 * aspect))
            scaled = pygame.transform.smoothscale(target_surf, (fw, fh))
            
            if tint_mult:
                t_layer = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                t_layer.fill((*tint_mult, 255))
                scaled.blit(t_layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # Atmospheric depth haze for distant background fish
            if self.depth < 0.85:
                haze = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                haze_alpha = int((0.85 - self.depth) * 140)
                haze.fill((20, 95, 140, haze_alpha))
                scaled.blit(haze, (0, 0))

            facing_left = (d == -1)
            if not facing_left:
                scaled = pygame.transform.flip(scaled, True, False)

            # Realistic subcarangiform swimming wave: steady head, articulating trunk & tail
            num_slices = 16
            slice_step = fw / num_slices
            slice_w = int(math.ceil(slice_step)) + 1
            max_pad_y = 10
            bent_surf = pygame.Surface((fw + 10, fh + max_pad_y * 2), pygame.SRCALPHA)

            tail_amp = 5.5 * min(1.0, max(0.2, self.current_speed / 50.0))
            for i in range(num_slices):
                ratio = (i / (num_slices - 1)) if facing_left else (1.0 - i / (num_slices - 1))
                if ratio < 0.25:
                    amp = 0.0
                else:
                    amp = (((ratio - 0.25) / 0.75) ** 2.2) * tail_amp
                phase_lag = ratio * 3.4
                offset_y = math.sin(self.tail_phase - phase_lag) * amp

                sx = int(i * slice_step)
                cur_sw = slice_w if sx + slice_w <= fw else (fw - sx)
                if cur_sw > 0:
                    rect = pygame.Rect(sx, 0, cur_sw, fh)
                    bent_surf.blit(scaled, (sx + 5, max_pad_y + offset_y), rect)

            # Realistic pitch tilt based on vertical swimming velocity
            rotated = pygame.transform.rotate(bent_surf, self.pitch_deg)
            surface.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))
            return

        # Procedural fallback with smooth shading and 3D turn foreshortening
        tail_wag = math.sin(self.tail_phase) * (s * 0.35)

        # Elliptical fish body
        body_w = max(6, int(s * 1.6 * turn_w_mult))
        body_h = int(s * 0.9)
        body_rect = pygame.Rect(cx - body_w // 2, cy - body_h // 2, body_w, body_h)
        pygame.draw.ellipse(surface, self.color_body, body_rect)

        # Tail fin polygon
        tail_tip_x = cx - int(d * s * 1.1 * turn_w_mult)
        tail_poly = [
            (cx - int(d * s * 0.6 * turn_w_mult), cy),
            (tail_tip_x, int(cy - s * 0.5 + tail_wag)),
            (tail_tip_x, int(cy + s * 0.5 + tail_wag)),
        ]
        pygame.draw.polygon(surface, self.color_accent, tail_poly)

        # Dorsal fin
        dorsal_poly = [
            (cx - int(d * s * 0.2 * turn_w_mult), int(cy - s * 0.4)),
            (cx, int(cy - s * 0.75)),
            (cx + int(d * s * 0.3 * turn_w_mult), int(cy - s * 0.35)),
        ]
        pygame.draw.polygon(surface, self.color_accent, dorsal_poly)

        # Eye
        if turn_w_mult > 0.3:
            eye_x = cx + int(d * s * 0.45 * turn_w_mult)
            eye_y = cy - int(s * 0.1)
            pygame.draw.circle(surface, COLOR_WHITE, (eye_x, eye_y), max(2, int(s * 0.16)))
            pygame.draw.circle(surface, (20, 20, 20), (eye_x + int(d * 1), eye_y), max(1, int(s * 0.08)))


class Shark:
    """An apex predator patrolling the depth layers with realistic predatory hydrodynamics."""

    def __init__(self, direction: int = 1):
        self.direction = direction  # 1 = left-to-right, -1 = right-to-left
        self.x = -240.0 if direction == 1 else SCREEN_WIDTH + 240.0
        self.y = random.uniform(190.0, SCREEN_HEIGHT - 170.0)
        self.speed = 210.0
        self.width = 310.0   # Majestic Great White scale
        self.height = 140.0  # Anatomical 2.2:1 aspect ratio
        self.alive = True
        self.tail_phase = 0.0
        self.swim_phase = random.uniform(0.0, math.pi * 2)
        self.pitch_deg = 0.0
        self.deflected = False
        self.deflect_timer = 0.0
        self.wake_bubbles: List[dict] = []

    def update(self, dt: float) -> None:
        self.tail_phase += 5.5 * dt
        self.swim_phase += 1.4 * dt

        if self.deflected:
            self.deflect_timer -= dt
            self.y -= 160.0 * dt
            self.x += self.speed * self.direction * 1.5 * dt
            target_pitch = 22.0 * (-self.direction)
        else:
            vy = math.sin(self.swim_phase) * 32.0
            self.y += vy * dt
            self.y = max(120.0, min(SCREEN_HEIGHT - 120.0, self.y))
            self.x += self.speed * self.direction * dt
            target_pitch = -math.degrees(math.atan2(vy, max(30.0, self.speed))) * self.direction

        self.pitch_deg += (target_pitch - self.pitch_deg) * min(1.0, 4.5 * dt)

        # Caudal fin thrust wake bubbles
        if random.random() < 0.35:
            tail_ox = -self.direction * (self.width * 0.44)
            self.wake_bubbles.append({
                "x": self.x + tail_ox,
                "y": self.y + math.sin(self.tail_phase) * 14.0,
                "r": random.uniform(1.8, 3.8),
                "alpha": 180,
                "vy": random.uniform(-18.0, -6.0),
            })
        for b in self.wake_bubbles:
            b["y"] += b["vy"] * dt
            b["alpha"] -= int(190 * dt)
        self.wake_bubbles = [b for b in self.wake_bubbles if b["alpha"] > 0]

        # Check boundary exit
        if self.direction == 1 and self.x > SCREEN_WIDTH + 320:
            self.alive = False
        elif self.direction == -1 and self.x < -320:
            self.alive = False

    def check_cursor_collision(self, cursor_x: float, cursor_y: float) -> bool:
        """Checks if player cursor collides with shark body or jaws."""
        head_x = self.x + self.direction * 50.0
        return point_in_circle(cursor_x, cursor_y, head_x, self.y, 55.0) or point_in_circle(cursor_x, cursor_y, self.x, self.y, 50.0)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        cx, cy = int(self.x), int(self.y)
        d = self.direction

        # 1. Wake Bubbles trailing caudal fin
        for b in self.wake_bubbles:
            br = max(1, int(b["r"]))
            bs = pygame.Surface((br * 2 + 4, br * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(bs, (200, 240, 255, b["alpha"]), (br + 2, br + 2), br)
            pygame.draw.circle(bs, (255, 255, 255, min(255, b["alpha"] + 40)), (br + 1, br + 1), max(1, br // 2))
            surface.blit(bs, (int(b["x"] - br - 2), int(b["y"] - br - 2)))

        # 2. Photorealistic Great White Shark Rendering
        _, _, _, _, shark_surf = _get_marine_textures()
        if shark_surf:
            sw = int(self.width)
            sh = int(self.height)
            tail_wag = math.sin(self.tail_phase) * 0.08
            sh_wag = max(10, int(sh * (1.0 + tail_wag)))
            scaled = pygame.transform.smoothscale(shark_surf, (sw, sh_wag))

            # Oceanic depth atmosphere haze for realistic deep water integration
            haze = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            haze.fill((170, 215, 240, 255))
            scaled.blit(haze, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if d == 1:
                scaled = pygame.transform.flip(scaled, True, False)

            # Dynamic pitch banking along swimming vector
            rot_shark = pygame.transform.rotate(scaled, self.pitch_deg)
            surface.blit(rot_shark, (cx - rot_shark.get_width() // 2, cy - rot_shark.get_height() // 2))
            return

        tail_wag = math.sin(self.tail_phase) * 14.0

        # Shark Body (Sleek slate-gray torpedo)
        body_color = (65, 80, 95)
        
        # Upper body polygon
        body_poly = [
            (cx + int(d * 70), cy),                     # Snout tip
            (cx + int(d * 30), cy - 22),                 # Forehead
            (cx - int(d * 20), cy - 18),                 # Back
            (cx - int(d * 60), cy - 8),                  # Peduncle
            (cx - int(d * 80), int(cy - 25 + tail_wag)), # Upper caudal fin tip
            (cx - int(d * 68), int(cy + tail_wag)),      # Caudal fork
            (cx - int(d * 80), int(cy + 22 + tail_wag)), # Lower caudal fin tip
            (cx - int(d * 45), cy + 12),                 # Lower belly
            (cx + int(d * 20), cy + 14),                 # Ventral
        ]
        pygame.draw.polygon(surface, body_color, body_poly)

        # Dorsal Fin
        dorsal_poly = [
            (cx - int(d * 10), cy - 18),
            (cx - int(d * 2), cy - 44),
            (cx + int(d * 18), cy - 16),
        ]
        pygame.draw.polygon(surface, body_color, dorsal_poly)

        # Pectoral Fin
        pec_poly = [
            (cx + int(d * 15), cy + 8),
            (cx - int(d * 10), cy + 32),
            (cx - int(d * 15), cy + 10),
        ]
        pygame.draw.polygon(surface, (50, 65, 78), pec_poly)

        # Eye & Gill slits
        eye_x = cx + int(d * 48)
        eye_y = cy - 6
        pygame.draw.circle(surface, (20, 20, 20), (eye_x, eye_y), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (eye_x + d, eye_y - 1), 1)

        # Gills
        for g in range(3):
            gx = cx + int(d * (25 - g * 6))
            pygame.draw.line(surface, (40, 50, 60), (gx, cy - 8), (gx, cy + 8), 2)


class Jellyfish:
    """Bioluminescent electric jellyfish with realistic hydrodynamics and articulated tentacles."""

    def __init__(self, x: float = None, y: float = None):
        self.x = x if x is not None else random.uniform(80.0, SCREEN_WIDTH - 80.0)
        self.y = y if y is not None else random.uniform(300.0, SCREEN_HEIGHT - 130.0)
        self.radius = 36.0
        self.pulse_phase = random.uniform(0.0, math.pi * 2)
        self.sway_phase = random.uniform(0.0, math.pi * 2)
        self.pulse_speed = random.uniform(1.6, 2.2)
        self.deflected = False
        self.deflect_timer = 0.0
        self.vy = 0.0
        self.tilt_deg = 0.0

    def update(self, dt: float, current_active: bool = False) -> None:
        self.pulse_phase += self.pulse_speed * dt
        # Natural asymmetric scyphozoan contraction cycle:
        # Rapid contraction, followed by slow relaxed glide and settling
        sin_p = math.sin(self.pulse_phase)
        contract = max(0.0, sin_p) ** 2.0  # 0.0 to 1.0 peak during power pulse

        # Upward thrust surge during contraction, gentle settling during relaxation
        vy_thrust = -contract * 44.0
        self.vy = vy_thrust + 14.0

        if self.deflected:
            self.deflect_timer -= dt
            self.vy = -200.0  # Shocked recoil
            if self.deflect_timer <= 0:
                self.deflected = False

        self.y += self.vy * dt
        # Gentle boundaries
        if self.y < 160.0:
            self.y = 160.0
            self.pulse_phase = math.pi
        elif self.y > SCREEN_HEIGHT - 90.0:
            self.y = SCREEN_HEIGHT - 90.0
            self.pulse_phase = 0.0

        # Subtle horizontal current drift & bell rocking
        self.sway_phase += 1.2 * dt
        drift_x = math.sin(self.sway_phase) * 8.0
        if current_active:
            drift_x += 140.0
        self.x += drift_x * dt
        self.x = max(60.0, min(SCREEN_WIDTH - 60.0, self.x))
        self.tilt_deg = math.sin(self.sway_phase) * 6.0

    def check_collision(self, px: float, py: float) -> bool:
        return distance(px, py, self.x, self.y) <= (self.radius + 18.0)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        sin_p = math.sin(self.pulse_phase)
        contract = max(0.0, sin_p) ** 2.0

        jelly_tex = _get_jelly_texture()
        if jelly_tex:
            jw = int(self.radius * 2.3)
            aspect = jelly_tex.get_height() / jelly_tex.get_width()
            # Bell contracts narrower and taller during power stroke, expands wider during relaxation
            contraction_w = 1.0 - 0.12 * contract
            contraction_h = 1.0 + 0.16 * contract
            w_cur = max(16, int(jw * contraction_w))
            h_cur = max(24, int(jw * aspect * contraction_h))

            # 1. Soft volumetric radial glow behind bell
            glow_r = int(self.radius * 1.5)
            glow_surf = pygame.Surface((glow_r * 2 + 10, glow_r * 2 + 10), pygame.SRCALPHA)
            glow_alpha = int(32 + 28 * contract)
            pygame.draw.circle(glow_surf, (0, 210, 255, glow_alpha), (glow_r + 5, glow_r + 5), glow_r)
            pygame.draw.circle(glow_surf, (150, 240, 255, int(glow_alpha * 0.65)), (glow_r + 5, glow_r + 5), int(glow_r * 0.55))
            surface.blit(glow_surf, (cx - glow_r - 5, cy - int(h_cur * 0.35) - glow_r))

            # 2. Scaled photorealistic bioluminescent jellyfish sprite
            scaled = pygame.transform.smoothscale(jelly_tex, (w_cur, h_cur))
            tint_mult = (min(255, int(195 + 60 * contract)), 240, 255)
            tint_layer = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            tint_layer.fill((*tint_mult, 255))
            scaled.blit(tint_layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # Ethereal inner bell core luminescence
            core_surf = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            core_r = max(8, int(w_cur * 0.30))
            core_alpha = int(40 + 35 * contract)
            pygame.draw.circle(core_surf, (100, 230, 255, core_alpha), (w_cur // 2, int(h_cur * 0.22)), core_r)
            scaled.blit(core_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            if self.deflected:
                shock = scaled.copy()
                shock.fill((255, 255, 255, 140), special_flags=pygame.BLEND_RGB_ADD)
                scaled = shock

            # 3. Dynamic bell tilt
            rot_jelly = pygame.transform.rotate(scaled, self.tilt_deg)
            surface.blit(rot_jelly, (cx - rot_jelly.get_width() // 2, cy - int(h_cur * 0.35)))
            return

        # Fallback procedural neon bell surface
        r = int(self.radius + sin_p * 3.0)
        bell_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        alpha = int(170 + 50 * sin_p)
        pygame.draw.circle(bell_surf, (180, 80, 255, alpha), (r + 5, r + 5), r)
        pygame.draw.circle(bell_surf, (230, 180, 255, 230), (r + 5, r + 5), int(r * 0.65))
        pygame.draw.circle(bell_surf, (255, 255, 255, 255), (r + 5, r + 5), 3)
        surface.blit(bell_surf, (cx - r - 5, cy - r - 5))

        # Trailing electric tentacles
        for i in range(4):
            tx = cx - 12 + i * 8
            tentacle_pts = [(tx, cy + 4)]
            for s in range(1, 5):
                seg_y = cy + 4 + s * 9
                seg_x = tx + math.sin(self.pulse_phase * 1.5 + s + i) * 6.0
                tentacle_pts.append((seg_x, seg_y))
            if len(tentacle_pts) >= 2:
                pygame.draw.lines(surface, (200, 120, 255), False, tentacle_pts, 2)


class Whirlpool:
    """A swirling oceanic whirlpool that pulls the swimmer towards its center."""
    def __init__(self, x: float, y: float, radius: float = 85.0, duration: float = 14.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.life = duration
        self.angle = 0.0
        self.pull_force = 190.0
        self.swimmer_escaped = False
        self.was_in_danger = False

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.angle += 3.8 * dt
        return self.life > 0

    def apply_suction(self, px: float, py: float) -> Tuple[float, float, bool, bool]:
        """
        Calculates suction force on swimmer.
        Returns (force_x, force_y, damaged: bool, escaped_event: bool).
        """
        dist = distance(px, py, self.x, self.y)
        influence_radius = self.radius * 2.0
        damaged = False
        escaped_event = False

        if dist < influence_radius:
            self.was_in_danger = True
            dx = self.x - px
            dy = self.y - py
            ndist = max(1.0, dist)
            factor = (1.0 - dist / influence_radius)
            fx = (dx / ndist) * self.pull_force * factor
            fy = (dy / ndist) * self.pull_force * factor

            if dist < 24.0:
                damaged = True
            return fx, fy, damaged, False
        else:
            if self.was_in_danger and not self.swimmer_escaped:
                self.swimmer_escaped = True
                escaped_event = True
            return 0.0, 0.0, False, escaped_event

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)
        spiral_surf = pygame.Surface((r * 2 + 40, r * 2 + 40), pygame.SRCALPHA)
        scx, scy = r + 20, r + 20

        alpha = int(140 * min(1.0, self.life / 2.0))
        for arm in range(4):
            base_a = self.angle + arm * (math.pi / 2.0)
            points = []
            for step in range(12):
                step_r = (step / 12.0) * r
                step_a = base_a + (step * 0.35)
                ax = scx + math.cos(step_a) * step_r
                ay = scy + math.sin(step_a) * step_r
                points.append((ax, ay))
            if len(points) >= 2:
                pygame.draw.lines(spiral_surf, (*COLOR_OCEAN_CYAN[:3], alpha), False, points, 3)

        pygame.draw.circle(spiral_surf, (5, 20, 45, int(alpha * 1.2)), (scx, scy), int(r * 0.28))
        surface.blit(spiral_surf, (cx - scx, cy - scy))


class OctopusTentacle:
    """An undulating giant octopus tentacle that blocks paths and lashes out."""
    def __init__(self, base_x: float, base_y: float, target_y: float):
        self.base_x = base_x
        self.base_y = base_y
        self.target_y = target_y
        self.current_y = base_y
        self.phase = random.uniform(0, math.pi * 2)
        self.wave_speed = random.uniform(2.5, 3.8)
        self.width = random.uniform(22.0, 32.0)
        self.length = abs(base_y - target_y)

    def update(self, dt: float, extend_progress: float) -> None:
        self.phase += self.wave_speed * dt
        self.current_y = self.base_y + (self.target_y - self.base_y) * extend_progress

    def check_collision(self, px: float, py: float) -> bool:
        min_y = min(self.base_y, self.current_y)
        max_y = max(self.base_y, self.current_y)
        if min_y - 20 <= py <= max_y + 20:
            sway = math.sin(self.phase + (py * 0.02)) * 28.0
            tentacle_x = self.base_x + sway
            if abs(px - tentacle_x) < (self.width + 18.0):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        steps = 14
        points = []
        dy = (self.current_y - self.base_y) / steps
        for i in range(steps + 1):
            curr_y = self.base_y + dy * i
            sway = math.sin(self.phase + (curr_y * 0.02)) * 28.0 * (i / steps)
            points.append((int(self.base_x + sway), int(curr_y)))

        if len(points) >= 2:
            pygame.draw.lines(surface, (140, 35, 75), False, points, int(self.width))
            pygame.draw.lines(surface, (200, 70, 110), False, points, max(2, int(self.width * 0.4)))


class OctopusAmbush:
    """A surprise octopus ambush event with multiple undulating tentacles."""
    def __init__(self, duration: float = 12.0):
        self.duration = duration
        self.life = duration
        self.tentacles: List[OctopusTentacle] = [
            OctopusTentacle(base_x=220.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 320.0),
            OctopusTentacle(base_x=640.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 360.0),
            OctopusTentacle(base_x=1050.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 310.0),
        ]

    def update(self, dt: float) -> bool:
        self.life -= dt
        progress = min(1.0, (self.duration - self.life) / 1.5)
        if self.life < 1.5:
            progress = max(0.0, self.life / 1.5)

        for t in self.tentacles:
            t.update(dt, progress)
        return self.life > 0

    def check_collision(self, px: float, py: float) -> bool:
        return any(t.check_collision(px, py) for t in self.tentacles)

    def draw(self, surface: pygame.Surface) -> None:
        for t in self.tentacles:
            t.draw(surface)


class MarineLifeManager:
    """Manages swimming fish schools, occasional shark hazards, electric jellyfish, whirlpools, and octopus ambush."""

    def __init__(self, fish_count: int = 15):
        self.fish: List[Fish] = []
        species_pool = ["clown", "blue_tang", "yellow_tang", "silver", "gold"]
        for i in range(fish_count):
            spec = species_pool[i % len(species_pool)]
            d_layer = 0.62 + 0.52 * (i / max(1, fish_count - 1))
            fx = (SCREEN_WIDTH / max(1, fish_count)) * (i + 0.5) + random.uniform(-30.0, 30.0)
            fy = random.uniform(95.0, SCREEN_HEIGHT - 85.0)
            self.fish.append(Fish(x=fx, y=fy, species=spec, depth_layer=d_layer))
        
        self.jellyfish: List[Jellyfish] = []
        self.current_shark: Optional[Shark] = None
        self.active_whirlpools: List[Whirlpool] = []
        self.current_octopus: Optional[OctopusAmbush] = None
        self.shark_warning_timer: float = 0.0
        self.shark_cooldown_timer: float = 22.0

        # Ambient peaceful marine wildlife (Green Sea Turtle with realistic hydrodynamics)
        self.turtle_x = SCREEN_WIDTH * 0.78
        self.turtle_y = 140.0
        self.turtle_target_y = 140.0
        self.turtle_wander_timer = random.uniform(6.0, 12.0)
        self.turtle_dir = -1
        self.turtle_speed = 36.0
        self.turtle_stroke_phase = 0.0
        self.turtle_pitch = 0.0
        self.turtle_is_turning = False
        self.turtle_turn_prog = 0.0
        self.turtle_turn_duration = 2.2
        self.turtle_from_dir = -1

        # Manta Ray disabled per user request
        self.manta_x = -9999.0
        self.manta_y = -9999.0
        self.manta_dir = 1
        self.manta_speed = 0.0
        self.manta_wing_phase = 0.0
        self.manta_cooldown = 9999999.0
        self.manta_visible = False

    def spawn_jellyfish(self, count: int = 3) -> None:
        """Populates level with bioluminescent electric jellyfish in deeper water column."""
        self.jellyfish.clear()
        spacing = SCREEN_WIDTH // max(1, count + 1)
        for i in range(count):
            jx = spacing * (i + 1) + random.uniform(-40.0, 40.0)
            jy = random.uniform(300.0, SCREEN_HEIGHT - 130.0)
            self.jellyfish.append(Jellyfish(jx, jy))

    def trigger_shark_event(self) -> None:
        """Launches a shark warning followed by shark appearance."""
        if not self.current_shark and self.shark_warning_timer <= 0:
            self.shark_warning_timer = 2.5  # 2.5s warning banner before shark glides across

    def trigger_whirlpool(self, x: float = None, y: float = None) -> None:
        """Spawns an oceanic whirlpool pulling items and swimmer."""
        wx = x if x is not None else random.uniform(300.0, SCREEN_WIDTH - 300.0)
        wy = y if y is not None else random.uniform(220.0, SCREEN_HEIGHT - 220.0)
        self.active_whirlpools.append(Whirlpool(wx, wy))

    def trigger_octopus_ambush(self) -> None:
        """Triggers a giant octopus tentacle ambush."""
        if not self.current_octopus:
            self.current_octopus = OctopusAmbush(duration=13.0)

    def update(self, dt: float, current_active: bool = False, cursor_pos: Tuple[int, int] = None, shark_allowed: bool = False, shark_interval: float = 22.0) -> Tuple[bool, bool]:
        """
        Updates fish, jellyfish, shark, whirlpools, and octopus.
        Returns (shark_hit_player: bool, shark_deflected_by_shield: bool).
        """
        for f in self.fish:
            f.update(dt, current_active, cursor_pos)

        # Update ambient sea turtle with realistic power-stroke hydrodynamics and pitch banking
        self.turtle_stroke_phase += 1.8 * dt
        stroke = math.sin(self.turtle_stroke_phase)
        flipper_down = max(0.0, stroke)
        thrust = (flipper_down ** 1.6) * 36.0

        # Periodic depth roaming (dives down and climbs back up naturally across water column)
        self.turtle_wander_timer -= dt
        if self.turtle_wander_timer <= 0:
            self.turtle_wander_timer = random.uniform(7.0, 16.0)
            self.turtle_target_y = random.uniform(105.0, 220.0)

        if not self.turtle_is_turning:
            if (self.turtle_x < 90.0 and self.turtle_dir == -1) or (self.turtle_x > SCREEN_WIDTH - 90.0 and self.turtle_dir == 1):
                self.turtle_is_turning = True
                self.turtle_turn_prog = 0.0
                self.turtle_from_dir = self.turtle_dir
                self.turtle_target_y = random.uniform(115.0, 210.0)
        else:
            self.turtle_turn_prog += dt / max(0.3, self.turtle_turn_duration)
            if self.turtle_turn_prog >= 1.0:
                self.turtle_turn_prog = 1.0
                self.turtle_is_turning = False
                self.turtle_dir = -self.turtle_from_dir
                self.turtle_from_dir = self.turtle_dir

        if self.turtle_is_turning:
            prog = min(1.0, max(0.0, self.turtle_turn_prog))
            cos_val = math.cos(prog * math.pi)
            turtle_vx = (self.turtle_speed * 0.45) * self.turtle_from_dir * cos_val
            turtle_vy = math.sin(prog * math.pi) * 12.0
            self.turtle_x += turtle_vx * dt
            self.turtle_y += turtle_vy * dt
            target_pitch = math.sin(prog * math.pi) * 14.0 * (-self.turtle_from_dir)
        else:
            turtle_vx = (self.turtle_speed + thrust) * self.turtle_dir
            turtle_vy = (self.turtle_target_y - self.turtle_y) * 0.7 + math.sin(self.turtle_stroke_phase * 0.5) * 8.0
            self.turtle_x += turtle_vx * dt
            self.turtle_y += turtle_vy * dt
            self.turtle_y = max(80.0, min(250.0, self.turtle_y))
            # Authentic hydrodynamic pitch: tilt nose down into dive, up during climb
            traj_pitch = -math.degrees(math.atan2(turtle_vy, max(24.0, abs(turtle_vx)))) * self.turtle_dir
            stroke_heave = stroke * 4.0 * (-self.turtle_dir)
            target_pitch = max(-18.0, min(18.0, traj_pitch + stroke_heave))

        self.turtle_pitch += (target_pitch - self.turtle_pitch) * min(1.0, 4.0 * dt)

        # Manta Ray disabled per user request
        pass

        for j in self.jellyfish:
            j.update(dt, current_active)

        # Update Whirlpools
        self.active_whirlpools = [w for w in self.active_whirlpools if w.update(dt)]

        # Update Octopus Ambush
        if self.current_octopus:
            if not self.current_octopus.update(dt):
                self.current_octopus = None

        hit = False
        deflected = False

        if shark_allowed:
            self.shark_cooldown_timer -= dt
            if self.shark_cooldown_timer <= 0 and not self.current_shark and self.shark_warning_timer <= 0:
                self.trigger_shark_event()
                self.shark_cooldown_timer = shark_interval

        # Shark Warning Banner Countdown
        if self.shark_warning_timer > 0:
            self.shark_warning_timer -= dt
            if self.shark_warning_timer <= 0:
                # Spawn Shark
                direction = random.choice([-1, 1])
                self.current_shark = Shark(direction)

        # Update Active Shark
        if self.current_shark:
            self.current_shark.update(dt)
            if not self.current_shark.alive:
                self.current_shark = None

        return hit, deflected

    def check_shark_interaction(self, cursor_x: float, cursor_y: float, shield_active: bool) -> Tuple[bool, bool]:
        """
        Checks collision between player cursor and shark.
        Returns (damaged: bool, deflected: bool).
        """
        if not self.current_shark or not self.current_shark.alive:
            return False, False

        if self.current_shark.check_cursor_collision(cursor_x, cursor_y):
            if shield_active:
                if not self.current_shark.deflected:
                    self.current_shark.deflected = True
                    self.current_shark.speed *= 1.8  # Flee faster
                    return False, True
            else:
                return True, False

        return False, False

    def check_jellyfish_interaction(self, px: float, py: float, shield_active: bool) -> Tuple[bool, bool]:
        """
        Checks collision between player and electric jellyfish.
        Returns (damaged: bool, deflected: bool).
        """
        for j in self.jellyfish:
            if not j.deflected and j.check_collision(px, py):
                if shield_active:
                    j.deflected = True
                    j.deflect_timer = 1.2
                    return False, True
                else:
                    j.deflected = True
                    j.deflect_timer = 1.0
                    return True, False
        return False, False

    def apply_whirlpools(self, px: float, py: float) -> Tuple[float, float, bool, bool]:
        """
        Calculates total suction displacement from whirlpools.
        Returns (total_fx, total_fy, damaged: bool, escaped_event: bool).
        """
        tot_fx, tot_fy = 0.0, 0.0
        dmg = False
        escaped = False
        for w in self.active_whirlpools:
            fx, fy, w_dmg, w_esc = w.apply_suction(px, py)
            tot_fx += fx
            tot_fy += fy
            if w_dmg:
                dmg = True
            if w_esc:
                escaped = True
        return tot_fx, tot_fy, dmg, escaped

    def check_octopus_interaction(self, px: float, py: float) -> bool:
        """Returns True if player swimmer touches an active octopus tentacle."""
        if self.current_octopus:
            return self.current_octopus.check_collision(px, py)
        return False

    def draw(self, surface: pygame.Surface) -> None:
        # Draw Whirlpools on sea backdrop
        for w in self.active_whirlpools:
            w.draw(surface)

        # Draw Octopus Ambush Tentacles
        if self.current_octopus:
            self.current_octopus.draw(surface)

        # Draw deep pelagic Manta Ray cruising high in the sunbeams
        manta_s = _get_manta_texture()
        if manta_s and self.manta_visible:
            mw, mh = 220, 115
            wing_flex = math.sin(self.manta_wing_phase) * 0.14
            mh_mod = max(10, int(mh * (1.0 + wing_flex)))
            m_scaled = pygame.transform.smoothscale(manta_s, (mw, mh_mod))
            # Oceanic depth atmosphere haze
            haze = pygame.Surface(m_scaled.get_size(), pygame.SRCALPHA)
            haze.fill((180, 220, 245, 255))
            m_scaled.blit(haze, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            if self.manta_dir == 1:
                m_scaled = pygame.transform.flip(m_scaled, True, False)
            m_pitch = math.sin(self.manta_wing_phase * 0.4) * 3.5 * (-self.manta_dir)
            m_rot = pygame.transform.rotate(m_scaled, m_pitch)
            surface.blit(m_rot, (int(self.manta_x - m_rot.get_width() // 2), int(self.manta_y - m_rot.get_height() // 2)))

        # Draw ambient sea turtle cruising in the background with 3D turnaround
        _, _, _, turtle_s, _ = _get_marine_textures()
        if turtle_s:
            tw = 210
            aspect = turtle_s.get_height() / max(1, turtle_s.get_width())
            th = max(20, int(tw * aspect))
            if self.turtle_is_turning:
                prog = min(1.0, max(0.0, self.turtle_turn_prog))
                cos_val = math.cos(prog * math.pi)
                t_facing = self.turtle_from_dir if cos_val >= 0 else -self.turtle_from_dir
                t_w_mult = max(0.15, abs(cos_val))
            else:
                t_facing = self.turtle_dir
                t_w_mult = 1.0

            # Maintain rigid bone carapace geometry
            tw_mod = max(16, int(tw * t_w_mult))
            t_scaled = pygame.transform.smoothscale(turtle_s, (tw_mod, th))

            # Underwater depth haze & soft sunlit back lighting
            haze = pygame.Surface(t_scaled.get_size(), pygame.SRCALPHA)
            haze.fill((215, 238, 250, 255))
            t_scaled.blit(haze, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if t_facing == 1:
                t_scaled = pygame.transform.flip(t_scaled, True, False)
            t_rot = pygame.transform.rotate(t_scaled, self.turtle_pitch)
            surface.blit(t_rot, (int(self.turtle_x - t_rot.get_width() // 2), int(self.turtle_y - t_rot.get_height() // 2)))

        # Draw fish sorted by depth so distant background fish render behind near fish
        sorted_fish = sorted(self.fish, key=lambda f: getattr(f, "depth", 1.0))
        for f in sorted_fish:
            f.draw(surface)

        for j in self.jellyfish:
            j.draw(surface)

        if self.current_shark:
            self.current_shark.draw(surface)

        # Draw Warning Banner if active
        if self.shark_warning_timer > 0:
            alpha = int(180 + 75 * math.sin(time.time() * 12))
            banner_surf = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
            banner_surf.fill((160, 20, 20, max(0, min(255, alpha))))
            
            font = pygame.font.SysFont("segoeui", 22, bold=True)
            text = font.render("⚠ WARNING: APEX PREDATOR DETECTED! ACTIVATE SHIELD [FIST ✊ / 'S'] ⚠", True, COLOR_WHITE)
            banner_surf.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 12))
            surface.blit(banner_surf, (0, 100))
