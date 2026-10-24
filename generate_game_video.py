"""
==============================================================================
            AQUASENSE 3D: UNDERWATER TREASURE HUNT - WALKTHROUGH VIDEO GENERATOR
==============================================================================
Generates a complete, high-definition (1280x720 @ 30 FPS) walkthrough video of the
game with animated diver simulation, hand gesture reticles, gameplay mechanics,
and English step-by-step instruction overlays.

Output: AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4
"""

import os
import math
import random
import cv2
import numpy as np

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_VIDEO = os.path.join(BASE_DIR, "AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4")

WIDTH = 1280
HEIGHT = 720
FPS = 30.0

# Colors (BGR for OpenCV)
COLOR_BG_DARK = (15, 10, 5)
COLOR_CYAN = (235, 206, 0)       # Vibrant cyan in BGR
COLOR_GOLD = (50, 200, 255)      # Vibrant gold in BGR
COLOR_WHITE = (255, 255, 255)
COLOR_CRIMSON = (40, 40, 230)
COLOR_GREEN = (80, 220, 80)
COLOR_AMBER = (40, 160, 240)
COLOR_SHIELD = (255, 220, 100)

def load_image_fit(filename, fallback_color=(20, 40, 60)):
    """Loads an image and resizes it to 1280x720."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        img = cv2.imread(path)
        if img is not None:
            return cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
    # Fallback blank background
    blank = np.full((HEIGHT, WIDTH, 3), fallback_color, dtype=np.uint8)
    return blank

def draw_bubble_particles(frame, particles):
    """Draws rising bubbles onto frame."""
    for p in particles:
        p['y'] -= p['speed']
        p['x'] += math.sin(p['y'] * 0.05 + p['wobble']) * 0.8
        if p['y'] < -10:
            p['y'] = HEIGHT + random.randint(5, 50)
            p['x'] = random.randint(0, WIDTH)
        
        ix, iy = int(p['x']), int(p['y'])
        r = p['radius']
        cv2.circle(frame, (ix, iy), r, (220, 240, 255), 1, cv2.LINE_AA)
        cv2.circle(frame, (ix - r//3, iy - r//3), max(1, r//3), (255, 255, 255), -1, cv2.LINE_AA)

def draw_cursor_reticle(frame, x, y, state="NORMAL", pulse=0.0):
    """Draws custom glowing hand cursor reticle matching in-game ui/cursor.py."""
    ix, iy = int(x), int(y)
    
    # Outer halo color & radius based on state
    if state == "TREASURE":
        color = (40, 215, 255) # Gold
        glow_color = (20, 140, 200)
        radius = int(26 + 4 * math.sin(pulse))
        label = "TARGET: ANCIENT RELIC [PINCH TO GRAB]"
    elif state == "PINCH":
        color = (100, 255, 120) # Emerald green
        glow_color = (40, 180, 60)
        radius = 18
        label = "PINCH GRAB ACTIVE [HOLDING]"
    elif state == "DANGER":
        color = (40, 40, 240) # Crimson
        glow_color = (20, 20, 160)
        radius = int(28 + 5 * math.sin(pulse * 2))
        label = "DANGER: SEA MINE / SHARK PATROL"
    elif state == "SHIELD":
        color = (255, 220, 80) # Cyan Shield
        glow_color = (200, 160, 40)
        radius = int(32 + 3 * math.sin(pulse))
        label = "ENERGY SHIELD DEPLOYED (FIST ✊)"
    elif state == "SONAR":
        color = (240, 220, 60)
        glow_color = (180, 160, 20)
        radius = int(30 + 6 * math.sin(pulse * 1.5))
        label = "SONAR WAVE TRANSMITTING (✌️)"
    else:
        color = (240, 200, 30) # Cyan
        glow_color = (160, 120, 10)
        radius = int(22 + 2 * math.sin(pulse))
        label = "HAND VISION RETICLE (SWIM)"

    # Glow ring
    cv2.circle(frame, (ix, iy), radius + 4, glow_color, 2, cv2.LINE_AA)
    # Main ring
    cv2.circle(frame, (ix, iy), radius, color, 2, cv2.LINE_AA)
    # Inner center dot
    cv2.circle(frame, (ix, iy), 3, (255, 255, 255), -1, cv2.LINE_AA)

    # Crosshair ticks
    tick_len = 8
    cv2.line(frame, (ix - radius - tick_len, iy), (ix - radius + 2, iy), color, 1, cv2.LINE_AA)
    cv2.line(frame, (ix + radius - 2, iy), (ix + radius + tick_len, iy), color, 1, cv2.LINE_AA)
    cv2.line(frame, (ix, iy - radius - tick_len), (ix, iy - radius + 2), color, 1, cv2.LINE_AA)
    cv2.line(frame, (ix, iy + radius - 2), (ix, iy + radius + tick_len), color, 1, cv2.LINE_AA)

    # Small floating label box
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
    lx = max(10, min(WIDTH - tw - 20, ix - tw // 2))
    ly = max(30, iy - radius - 12)
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (lx - 6, ly - th - 4), (lx + tw + 6, ly + 4), (10, 15, 25), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.rectangle(frame, (lx - 6, ly - th - 4), (lx + tw + 6, ly + 4), color, 1)
    cv2.putText(frame, label, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_WHITE, 1, cv2.LINE_AA)

def draw_hud_header(frame, title="AQUASENSE 3D • VISION HAND GESTURE SYSTEM"):
    """Draws top branding and diagnostics bar."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, 52), (10, 14, 22), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    cv2.line(frame, (0, 52), (WIDTH, 52), (180, 140, 20), 1)

    # Logo / Title
    cv2.putText(frame, "AQUASENSE 3D", (24, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 210, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "|  FULL GAMEPLAY & INSTRUCTION WALKTHROUGH", (210, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1, cv2.LINE_AA)

    # Status indicators on top right
    cv2.putText(frame, "AI TRACKING: ACTIVE (30 FPS)", (WIDTH - 420, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 230, 80), 1, cv2.LINE_AA)
    cv2.putText(frame, "ENGINE: LOCKED 60 FPS", (WIDTH - 190, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 200, 40), 1, cv2.LINE_AA)

def draw_gesture_card(frame, gesture_symbol, gesture_name, description):
    """Draws active gesture visualization card on the top right."""
    cw, ch = 310, 86
    cx = WIDTH - cw - 24
    cy = 66
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (cx, cy), (cx + cw, cy + ch), (15, 20, 32), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    cv2.rectangle(frame, (cx, cy), (cx + cw, cy + ch), (220, 180, 40), 1)

    # Icon circle
    cv2.circle(frame, (cx + 36, cy + 43), 24, (40, 180, 240), 1, cv2.LINE_AA)
    # Symbol / text
    cv2.putText(frame, gesture_symbol, (cx + 20, cy + 51), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (40, 220, 255), 2, cv2.LINE_AA)

    # Gesture details
    cv2.putText(frame, "DETECTED GESTURE", (cx + 70, cy + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, gesture_name, (cx + 70, cy + 46), cv2.FONT_HERSHEY_SIMPLEX, 0.62, COLOR_WHITE, 2, cv2.LINE_AA)
    cv2.putText(frame, description, (cx + 70, cy + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 220, 240), 1, cv2.LINE_AA)

def draw_instruction_banner(frame, chapter_num, total_chapters, step_title, instruction_text, tip_text=None):
    """Draws English lower-third instruction card with glassmorphism style."""
    bh = 118
    by = HEIGHT - bh - 16
    bx = 30
    bw = WIDTH - 60

    overlay = frame.copy()
    # Gradient backdrop
    cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (12, 16, 26), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

    # Outer border & accent line
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (180, 140, 30), 1)
    cv2.line(frame, (bx + 2, by + 34), (bx + bw - 2, by + 34), (60, 50, 40), 1)

    # Chapter badge
    badge_str = f"STEP {chapter_num}/{total_chapters}"
    cv2.rectangle(frame, (bx + 14, by + 8), (bx + 115, by + 28), (200, 150, 20), -1)
    cv2.putText(frame, badge_str, (bx + 20, by + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (10, 15, 25), 2, cv2.LINE_AA)

    # Step Title
    cv2.putText(frame, step_title, (bx + 130, by + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (40, 215, 255), 2, cv2.LINE_AA)

    # Instruction Detail (English)
    cv2.putText(frame, instruction_text, (bx + 20, by + 64), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (245, 245, 245), 1, cv2.LINE_AA)

    # Pro Tip or Note
    if tip_text:
        cv2.putText(frame, f">> PRO-TIP: {tip_text}", (bx + 20, by + 94), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (90, 230, 120), 1, cv2.LINE_AA)

def draw_celebration_burst(frame, cx, cy, count, t_ratio):
    """Renders gold burst celebration particles for relic deposits."""
    for i in range(count):
        angle = (i / count) * 2 * math.pi
        dist = 20 + t_ratio * 90
        px = int(cx + math.cos(angle) * dist)
        py = int(cy + math.sin(angle) * dist - t_ratio * 30)
        size = max(1, int(4 * (1.0 - t_ratio)))
        col = (40, 210, 255) if i % 2 == 0 else (255, 255, 255)
        cv2.circle(frame, (px, py), size, col, -1, cv2.LINE_AA)

def draw_sonar_wave(frame, cx, cy, radius, alpha):
    """Renders expanding circular sonar waves."""
    overlay = frame.copy()
    cv2.circle(overlay, (int(cx), int(cy)), int(radius), (240, 220, 60), 3, cv2.LINE_AA)
    cv2.circle(overlay, (int(cx), int(cy)), max(2, int(radius - 12)), (200, 180, 40), 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

def draw_shield_dome(frame, cx, cy, radius):
    """Renders cyan energy shield dome around player."""
    overlay = frame.copy()
    cv2.circle(overlay, (int(cx), int(cy)), int(radius), (255, 220, 80), -1)
    cv2.addWeighted(overlay, 0.28, frame, 0.72, 0, frame)
    cv2.circle(frame, (int(cx), int(cy)), int(radius), (255, 240, 140), 2, cv2.LINE_AA)
    # Hexagon or pulsing rings
    cv2.circle(frame, (int(cx), int(cy)), int(radius - 6), (220, 180, 40), 1, cv2.LINE_AA)

def generate_full_walkthrough_video():
    """Builds and renders the full ~75s video."""
    print(f"[Video Generator] Target resolution: {WIDTH}x{HEIGHT} @ {FPS} FPS")
    print(f"[Video Generator] Output destination: {OUTPUT_VIDEO}")

    # Load high-res game screenshots
    img_menu = load_image_fit("menu_final_cinematic.png")
    img_level_select = load_image_fit("test_upgraded_level_select.png")
    img_l1 = load_image_fit("level1_current_view.png")
    img_l2 = load_image_fit("level2_current_view.png")
    img_l3 = load_image_fit("level3_current_view.png")
    img_l4 = load_image_fit("level4_current_view.png")
    img_l5 = load_image_fit("level5_current_view.png")
    img_mus_gallery = load_image_fit("museum_hd_gallery_preview.png")
    img_mus_inspect = load_image_fit("museum_hd_inspection_preview.png")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

    if not out.isOpened():
        print("[Error] Could not open cv2.VideoWriter!")
        return False

    # Spawn ambient bubble particles
    particles = []
    for _ in range(35):
        particles.append({
            'x': random.uniform(0, WIDTH),
            'y': random.uniform(0, HEIGHT),
            'speed': random.uniform(1.2, 3.2),
            'radius': random.randint(2, 6),
            'wobble': random.uniform(0, 6.28)
        })

    # Scenes definition: (duration_frames, bg_image, step_num, step_title, instruction, tip, gesture_sym, gesture_name, gesture_desc, cursor_start, cursor_end, cursor_state)
    scenes = [
        # Scene 1: Introduction (6.5s = 195 frames)
        {
            'frames': 195,
            'bg': img_menu,
            'step': 1,
            'title': "WELCOME TO AQUASENSE 3D • VISION DESKTOP ADVENTURE",
            'instruction': "Experience a commercial-grade underwater adventure controlled 100% via camera hand tracking.",
            'tip': "No mouse or keyboard needed! The system OS mouse is completely hidden.",
            'gesture_sym': "🖐",
            'gesture_name': "NEUTRAL HAND",
            'gesture_desc': "Ready to dive & explore",
            'cursor_mode': 'menu_roam'
        },
        # Scene 2: Gestures Overview (7.5s = 225 frames)
        {
            'frames': 225,
            'bg': img_level_select,
            'step': 2,
            'title': "FIVE INTUITIVE TACTILE HAND GESTURES",
            'instruction': "🖐 Move Hand = Swim | 🤏 Pinch = Grab / Select | ✌️ Two Fingers = Sonar | ✋ Palm = Current | ✊ Fist = Shield",
            'tip': "Both single-hand and dual-hand cooperative controls are fully supported!",
            'gesture_sym': "🤏",
            'gesture_name': "PINCH / CLICK",
            'gesture_desc': "Thumb + Index tips touch",
            'cursor_mode': 'level_select'
        },
        # Scene 3: Level 1 Grab & Carry (8.5s = 255 frames)
        {
            'frames': 255,
            'bg': img_l1,
            'step': 3,
            'title': "CORE MECHANIC: TARGET & PINCH TO GRAB (🤏)",
            'instruction': "Swim near an ancient golden relic. The reticle locks on with a gold aura (👑). Pinch to pick it up!",
            'tip': "The relic visibly attaches to the diver's hands as you navigate through deep currents.",
            'gesture_sym': "🤏",
            'gesture_name': "PINCH GRAB",
            'gesture_desc': "Relic locked in hand grip",
            'cursor_mode': 'grab_relic'
        },
        # Scene 4: Level 1 Deposit & Combo (8.0s = 240 frames)
        {
            'frames': 240,
            'bg': img_l1,
            'step': 4,
            'title': "CARRY TO SEAFLOOR VAULT & RELEASE TO DEPOSIT (🎁)",
            'instruction': "Swim to the bottom Treasure Chest Vault and release your pinch to bank the relic and trigger COMBO x2.0!",
            'tip': "Consecutive deposits advance your score multiplier up to 3.0x bonus points!",
            'gesture_sym': "🎁",
            'gesture_name': "VAULT DEPOSIT",
            'gesture_desc': "Score +100 [COMBO x2.0 🔥]",
            'cursor_mode': 'deposit_vault'
        },
        # Scene 5: Level 2 Sonar Reconnaissance (8.0s = 240 frames)
        {
            'frames': 240,
            'bg': img_l2,
            'step': 5,
            'title': "LEVEL 2: CORAL CAVERNS — SONAR RECONNAISSANCE (✌️)",
            'instruction': "Raise Index + Middle fingers to emit expanding Sonar pulses revealing hidden relics and counterfeit mimic fakes.",
            'tip': "Green pulse = Genuine Relic (+100) | Yellow pulse = Mimic Trap (-12% Oxygen penalty)!",
            'gesture_sym': "✌️",
            'gesture_name': "SONAR SCAN",
            'gesture_desc': "Concentric 360° pulse",
            'cursor_mode': 'sonar_pulse'
        },
        # Scene 6: Level 3 Flashlight & Geothermal Vents (8.0s = 240 frames)
        {
            'frames': 240,
            'bg': img_l3,
            'step': 6,
            'title': "LEVEL 3: DEEP TRENCH — FLASHLIGHT & OXYGEN STATIONS (🫧)",
            'instruction': "Dark waters restrict visibility to your diver flashlight beam. Hover over geothermal bubble vents to refill +25% Oxygen!",
            'tip': "Escape swirling vortex whirlpools by paddling firmly outward (+50 Escape Bonus).",
            'gesture_sym': "🫧",
            'gesture_name': "OXYGEN VENT",
            'gesture_desc': "+25% Oxygen Refill",
            'cursor_mode': 'flashlight_vent'
        },
        # Scene 7: Level 4 Shark Combat & Fist Shield (8.5s = 255 frames)
        {
            'frames': 255,
            'bg': img_l4,
            'step': 7,
            'title': "LEVEL 4: SHIPWRECK GRAVEYARD — DEFLECT SHARKS WITH FIST (✊)",
            'instruction': "When an apex predator shark charges, curl your hand into a tight Fist (✊) to deploy the Energy Shield dome!",
            'tip': "Deflecting shark strikes earns a +150 DEFLECTION BONUS and prevents -35% oxygen loss!",
            'gesture_sym': "✊",
            'gesture_name': "ENERGY SHIELD",
            'gesture_desc': "Forcefield active (Fist)",
            'cursor_mode': 'shark_shield'
        },
        # Scene 8: Level 5 Atlantean Gesture Puzzle (8.5s = 255 frames)
        {
            'frames': 255,
            'bg': img_l5,
            'step': 8,
            'title': "LEVEL 5: SUNKEN RUINS — ANCIENT ATLANTEAN GESTURE PUZZLE",
            'instruction': "Unlock the ancient pedestal sanctum with the 3-step sequence: ✌️ Sonar ➔ ✋ Current ➔ 🤏 Touch!",
            'tip': "Solving the puzzle unlocks the legendary Ancient Crown (+500 points) and Museum Exhibit!",
            'gesture_sym': "🏛️",
            'gesture_name': "PUZZLE SEQUENCE",
            'gesture_desc': "✌️ Sonar ➔ ✋ Current ➔ 🤏 Touch",
            'cursor_mode': 'atlantean_puzzle'
        },
        # Scene 9: Ocean Museum 3D Exhibit (7.5s = 225 frames)
        {
            'frames': 225,
            'bg': img_mus_gallery,
            'step': 9,
            'title': "UNDERWATER MUSEUM: 3D ARTIFACT ARCHIVE & LORE LOGS",
            'instruction': "Every relic deposited during your expedition is permanently unlocked in the interactive 3D Museum gallery.",
            'tip': "Pinch any showcase pedestal to inspect the 3D rotating model and read historical archaeological lore.",
            'gesture_sym': "🏛️",
            'gesture_name': "3D MUSEUM",
            'gesture_desc': "Interactive artifact gallery",
            'cursor_mode': 'museum_inspect'
        },
        # Scene 10: Summary & Quick Launch Guide (6.5s = 195 frames)
        {
            'frames': 195,
            'bg': img_menu,
            'step': 10,
            'title': "READY TO DIVE! LAUNCH QUICKLY VIA RUN_GAME.BAT",
            'instruction': "Double click run_game.bat or run 'python main.py' to launch. Position your camera in good lighting.",
            'tip': "Press 'D' anytime in-game for live CV diagnostics; press 'ESC' to pause; F11 toggles Fullscreen.",
            'gesture_sym': "🚀",
            'gesture_name': "EXPEDITION READY",
            'gesture_desc': "Launch: run_game.bat",
            'cursor_mode': 'menu_roam'
        }
    ]

    total_scenes = len(scenes)
    total_frames = sum(s['frames'] for s in scenes)
    print(f"[Video Generator] Rendering {total_scenes} scenes, total frames: {total_frames} (~{total_frames/FPS:.1f}s)...")

    frame_counter = 0

    for s_idx, s in enumerate(scenes):
        s_frames = s['frames']
        bg = s['bg']
        mode = s['cursor_mode']
        
        for f in range(s_frames):
            frame = bg.copy()
            t_ratio = f / float(s_frames)
            pulse = (frame_counter * 0.15) % (2 * math.pi)

            # Draw ambient rising bubbles
            draw_bubble_particles(frame, particles)

            # Mode specific animations
            cx, cy = 640, 360
            state = "NORMAL"

            if mode == 'menu_roam':
                cx = 640 + int(math.sin(t_ratio * 4 * math.pi) * 160)
                cy = 460 + int(math.cos(t_ratio * 4 * math.pi) * 40)
                state = "NORMAL"

            elif mode == 'level_select':
                # Move cursor over Level 1 card, then pinch
                cx = 400 + int(t_ratio * 300)
                cy = 380 + int(math.sin(t_ratio * math.pi * 3) * 30)
                state = "PINCH" if 0.4 < t_ratio < 0.7 else "NORMAL"

            elif mode == 'grab_relic':
                # Swims toward relic at (720, 480) and pinches
                start_x, start_y = 350, 300
                target_x, target_y = 720, 460
                cx = int(start_x + (target_x - start_x) * min(1.0, t_ratio * 1.5))
                cy = int(start_y + (target_y - start_y) * min(1.0, t_ratio * 1.5))
                if t_ratio < 0.5:
                    state = "TREASURE"
                else:
                    state = "PINCH"
                    # Draw attached carried relic
                    cv2.circle(frame, (cx + 15, cy + 20), 14, (40, 215, 255), -1, cv2.LINE_AA)
                    cv2.putText(frame, "HOLDING", (cx + 32, cy + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 215, 255), 1)

            elif mode == 'deposit_vault':
                # Carry relic from (600, 380) to vault at (880, 560)
                vx, vy = 880, 560
                cx = int(500 + (vx - 500) * min(1.0, t_ratio * 1.2))
                cy = int(380 + (vy - 380) * min(1.0, t_ratio * 1.2))
                if t_ratio < 0.7:
                    state = "PINCH"
                    cv2.circle(frame, (cx + 15, cy + 20), 14, (40, 215, 255), -1, cv2.LINE_AA)
                else:
                    state = "NORMAL"
                    # Trigger deposit celebration particles
                    draw_celebration_burst(frame, vx, vy, count=28, t_ratio=(t_ratio - 0.7) / 0.3)
                    # Floating text popup
                    cv2.putText(frame, "+100 DEPOSITED! [COMBO x2.0 🔥]", (vx - 140, vy - 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (40, 215, 255), 2, cv2.LINE_AA)

            elif mode == 'sonar_pulse':
                cx, cy = 620, 340
                state = "SONAR"
                wave_r = (f % 50) * 14.0
                alpha = max(0.0, 1.0 - (wave_r / 700.0))
                draw_sonar_wave(frame, cx, cy, wave_r, alpha)
                # Draw revealed green target relic
                cv2.circle(frame, (860, 420), 28, (80, 230, 80), 2, cv2.LINE_AA)
                cv2.putText(frame, "GENUINE (+100)", (810, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 230, 80), 1, cv2.LINE_AA)
                # Draw yellow mimic trap
                cv2.circle(frame, (420, 480), 28, (40, 180, 240), 2, cv2.LINE_AA)
                cv2.putText(frame, "MIMIC FAKE (-12% O2)", (350, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 180, 240), 1, cv2.LINE_AA)

            elif mode == 'flashlight_vent':
                cx, cy = 540, 420
                state = "NORMAL"
                # Vent bubbles
                vx, vy = 760, 580
                cv2.circle(frame, (vx, vy), 35, (240, 220, 80), 2, cv2.LINE_AA)
                cv2.putText(frame, "AIR VENT (+25% OXYGEN)", (vx - 110, vy - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 220, 80), 1, cv2.LINE_AA)

            elif mode == 'shark_shield':
                cx, cy = 600, 380
                state = "SHIELD"
                draw_shield_dome(frame, cx, cy, radius=75 + 4 * math.sin(pulse))
                # Shark charge deflection
                sx = int(980 - t_ratio * 240)
                sy = 380
                cv2.putText(frame, "SHARK CHARGE!", (sx - 80, sy - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 240), 2, cv2.LINE_AA)
                cv2.putText(frame, "SHIELD DEFLECTED! +150 PTS", (cx - 120, cy - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 220, 80), 2, cv2.LINE_AA)

            elif mode == 'atlantean_puzzle':
                cx, cy = 640, 400
                if t_ratio < 0.33:
                    state = "SONAR"
                    p_step = "STEP 1: ✌️ SONAR SCAN [COMPLETED]"
                elif t_ratio < 0.66:
                    state = "NORMAL"
                    p_step = "STEP 2: ✋ WATER CURRENT [COMPLETED]"
                else:
                    state = "PINCH"
                    p_step = "STEP 3: 🤏 PINCH TOUCH [SANCTUM UNLOCKED!]"
                    draw_celebration_burst(frame, 640, 480, 32, (t_ratio - 0.66) / 0.34)
                
                cv2.putText(frame, p_step, (440, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (40, 215, 255), 2, cv2.LINE_AA)

            elif mode == 'museum_inspect':
                cx = 640 + int(math.sin(t_ratio * 2 * math.pi) * 120)
                cy = 360
                state = "PINCH" if 0.4 < t_ratio < 0.8 else "NORMAL"
                cv2.putText(frame, "INSPECTING: POSEIDON SAPPHIRE RELIC [3D VIEW]", (360, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (40, 215, 255), 2, cv2.LINE_AA)

            # Draw glowing vision cursor
            draw_cursor_reticle(frame, cx, cy, state=state, pulse=pulse)

            # Draw top HUD header
            draw_hud_header(frame)

            # Draw Gesture Card on top right
            draw_gesture_card(frame, s['gesture_sym'], s['gesture_name'], s['gesture_desc'])

            # Draw English Lower-Third Instruction Banner
            draw_instruction_banner(
                frame,
                chapter_num=s['step'],
                total_chapters=total_scenes,
                step_title=s['title'],
                instruction_text=s['instruction'],
                tip_text=s['tip']
            )

            # Smooth Crossfade on scene transitions (first 10 frames of scene except first)
            if s_idx > 0 and f < 12:
                blend_alpha = f / 12.0
                prev_bg = scenes[s_idx - 1]['bg']
                # Subtly blend with previous background
                frame = cv2.addWeighted(frame, blend_alpha, cv2.resize(prev_bg, (WIDTH, HEIGHT)), 1.0 - blend_alpha, 0)

            # Write frame to video
            out.write(frame)
            frame_counter += 1

            if frame_counter % 150 == 0:
                print(f"[Video Generator] Rendered {frame_counter}/{total_frames} frames ({frame_counter/total_frames*100:.1f}%)...", flush=True)

    out.release()
    
    # Universal Web H.264 Optimization using imageio_ffmpeg if available
    try:
        import subprocess, imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        temp_h264 = os.path.join(BASE_DIR, "AQUASENSE_GAMEPLAY_WALKTHROUGH_H264.mp4")
        cmd = [
            ffmpeg_exe, '-y',
            '-i', OUTPUT_VIDEO,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            '-movflags', '+faststart',
            temp_h264
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(temp_h264):
            os.replace(temp_h264, OUTPUT_VIDEO)
            print("[Video Generator] Universal H.264 (yuv420p) encoding applied successfully!")
    except Exception as e:
        print(f"[Video Generator] Note: Standard mp4 retained ({e})")

    print(f"\n[Video Generator] SUCCESS! Video successfully generated at:\n{OUTPUT_VIDEO}")
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"[Video Generator] File Size: {file_size_mb:.2f} MB")
    return True

if __name__ == "__main__":
    generate_full_walkthrough_video()
