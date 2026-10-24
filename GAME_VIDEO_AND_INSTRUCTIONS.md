# 🌊 AquaSense 3D: Underwater Treasure Hunt
## Complete Video Walkthrough & English Gameplay Instruction Guide

> **Document Version:** 1.0.0  
> **Target Video File:** [`AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4`](AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4)  
> **Video Generator Script:** [`generate_game_video.py`](generate_game_video.py)  
> **Platform:** Python 3.12 • MediaPipe • OpenCV • Pygame • NumPy  

---

## 📽️ 1. Video Walkthrough Overview

The complete video walkthrough for **AquaSense 3D: Underwater Treasure Hunt** is recorded in High-Definition (1280x720 @ 30 FPS) and saved in the root directory:
* **Video File Location:** [`AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4`](AQUASENSE_GAMEPLAY_WALKTHROUGH.mp4)
* **Duration:** ~77.5 seconds (10 Full Chapters)
* **Features:** Animated scuba diver simulation, real-time hand gesture reticle overlays, live gesture indicator cards, step-by-step English instruction banners, sonar pulses, shield deflections, and treasure deposit celebrations.

### ⏱️ Video Chapter Timestamps

| Timestamp | Chapter | Scene / Mechanic | Description & English Instruction |
| :---: | :---: | :--- | :--- |
| **00:00 - 00:06** | **Step 1** | **Introduction & Overview** | Welcome to AquaSense 3D. 100% camera hand-controlled interactive adventure. Zero mouse dependency. |
| **00:06 - 00:14** | **Step 2** | **Gesture Controls & Level Select** | Demonstration of the 5 tactile hand gestures: Move, Pinch, Sonar, Current, and Fist Shield. |
| **00:14 - 00:22** | **Step 3** | **Level 1: Target & Pinch to Grab** | Diver approaches ancient relic; reticle locks with gold halo (👑). Pinch thumb + index to grab. |
| **00:22 - 00:30** | **Step 4** | **Level 1: Deposit & Combo Multiplier** | Carry relic to seafloor vault; release pinch to score +100! Combo multiplier advances to **x2.0 🔥**. |
| **00:30 - 00:38** | **Step 5** | **Level 2: Sonar Reconnaissance (✌️)** | Raise Index + Middle fingers to emit Sonar wave. Distinguish genuine relics from deadly mimic traps. |
| **00:38 - 00:46** | **Step 6** | **Level 3: Flashlight & Oxygen Vents** | Dark waters require diver flashlight navigation. Hover over geothermal bubble vents to refill +25% O₂. |
| **00:46 - 00:55** | **Step 7** | **Level 4: Shark Defense with Fist (✊)** | Apex predator shark charges! Curl hand into Fist (✊) to deploy Energy Shield dome (+150 bonus). |
| **00:55 - 01:03** | **Step 8** | **Level 5: Atlantean Gesture Puzzle** | Execute ancient 3-step invocation: ✌️ Sonar ➔ ✋ Current ➔ 🤏 Touch to claim the Ancient Crown (+500). |
| **01:03 - 01:11** | **Step 9** | **Underwater Museum 3D Exhibit** | All deposited relics unlock in the 3D gallery. Inspect rotating 3D models and marine archaeology logs. |
| **01:11 - 01:18** | **Step 10** | **Summary & Quick Start** | How to run the game with `run_game.bat` and tips for optimal lighting and camera setup. |

---

## 🖐️ 2. Core Hand Gesture Controls

The player's hand controls both the **animated scuba explorer** and a permanent, visible **underwater glowing hand cursor (`ui/cursor.py`)**. The operating system mouse cursor is completely hidden.

```
                    ┌───────────────────────────────┐
                    │     5 CORE HAND GESTURES      │
                    └───────────────────────────────┘
   🖐 NEUTRAL MOVE          🤏 PINCH / TAP           ✌️ TWO FINGERS
   [Swim Navigation]      [Grab & Deposit Items]     [Sonar Recon Pulse]
  Steer diver smoothly     Touch thumb + index tips   Raise Index + Middle
  across the ocean floor  Click buttons / Open chests Reveal hidden traps

                    ✋ OPEN PALM             ✊ CLOSED FIST
                 [Water Current Surge]     [Anti-Shark Forcefield]
                 Spread all 5 fingers      Curl fingers into palm
                 Push objects & fish       Deploy protective dome
```

### 1. 🖐 Hand Movement (Neutral Hand)
* **How to perform:** Hold your hand naturally in front of the webcam and move it up, down, left, or right.
* **In-Game Effect:** The custom glowing cyan reticle moves smoothly across the screen, and the scuba diver banks, flutters twin swimming fins, and follows your hand trajectory.
* **Dual-Hand Support:** If both hands are raised, the diver navigates toward the midpoint between both hands. Moving hands in a rhythmic swimming stroke activates the **Propulsion Boost (1.35x to 1.85x speed)**!

### 2. 🤏 Pinch / Index Tap
* **How to perform:** Bring the tips of your thumb and index finger together (or tap index finger downwards).
* **In-Game Effect:**
  - **Relic Collection:** When hovering near a treasure relic, pinches grab the item.
  - **Menu Selection:** Pinches click buttons on the Main Menu, Level Select, Pause, and Museum screens.
  - **Mystery Crates:** Cracks open wooden sunken crates to reveal oxygen canisters or gold.

### 3. ✌️ Two Fingers (Index + Middle)
* **How to perform:** Raise your index and middle fingers in a "V" peace sign while keeping other fingers tucked.
* **In-Game Effect:** Fires a concentric **Sonar Reconnaissance Wave** sweeping 360° across the seabed.
  - 🟢 **Green Halo:** Genuine relic (Safe to pick up!).
  - 🟡 **Yellow Halo:** Mimic counterfeit trap (-12% Oxygen penalty if grabbed).
  - 🔴 **Red Pulse:** Explosive sea mine (Deals lethal -25% Oxygen and life loss).

### 4. ✋ Open Palm
* **How to perform:** Spread all five fingers wide open.
* **In-Game Effect:** Unleashes a surging hydrodynamic **Water Current Burst** that disperses schools of fish, dislodges submerged items, and completes step 2 of the ancient Atlantean ruin puzzle.
* **Mega Tidal Current:** Opening **both hands** simultaneously triggers a double-strength ocean current!

### 5. ✊ Closed Fist
* **How to perform:** Curl all four fingers tightly into your palm into a solid fist.
* **In-Game Effect:** Deploys a bioluminescent **Energy Shield Dome** around the diver.
  - Deflects patrolling Great White Sharks (+150 Deflection Bonus).
  - Protects against electric shocks from pulsating bioluminescent jellyfish.

---

## 💎 3. The Tactile Gameplay Loop: Grab ➔ Carry ➔ Deposit

The fundamental interaction loop of the game simulates real physical underwater diving:

```
    [1. EXPLORE & AIM] ────────► [2. PINCH TO GRAB (🤏)]
           ▲                                  │
           │                                  ▼
    [4. DEPOSIT VAULT (🎁)] ◄──────── [3. SWIM & CARRY]
```

1. **Explore & Aim:** Steer your scuba diver across the seabed. When hovering near a valid treasure, the reticle transforms from cyan to a **glowing gilded gold halo (👑)**.
2. **Pinch to Grab (🤏):** Pinch your thumb and index finger together. The relic visibly snaps to the diver's hands.
3. **Carry:** While maintaining the pinch (or holding), swim through oceanic currents, dodge floating sea mines, and evade predatory creatures.
4. **Deposit into Vault (🎁):** Swim toward the seafloor **Treasure Chest Depot** (marked on your radar minimap) and release your pinch:
   - Golden celebration burst particles erupt!
   - Score is immediately credited (+50 for Common, +100 for Gold, +250 for Rare, +500 for Crown).
   - Your **Combo Multiplier advances (`🔥 COMBO x2.0`, `x2.5`, `x3.0`)**!
   - Objective counter updates (`OBJECTIVE: X / Y STORED`).
   - If released outside the vault, the treasure safely drops back to the ocean floor.

---

## 🗺️ 4. Level-by-Level Exploration Guide

The expedition spans five distinct underwater environments, each introducing new mechanics, hazards, and archaeological secrets:

### ☀️ Level 1: The Sunken Shallows
* **Environment:** Bright, sunlit coral reef with clear turquoise waters.
* **Primary Objective:** Collect and store **3 Genuine Relics** in the seafloor vault.
* **Hazards:** Occasional harmless sea urchins; learning the grab and deposit rhythm.
* **Pro Tip:** Keep an eye on your oxygen gauge in the top-left HUD. Depositing relics awards combo bonuses!

### 🪸 Level 2: Coral Caverns
* **Environment:** Deep bioluminescent cavern surrounded by undulating coral fans.
* **Primary Objective:** Collect and store **4 Relics**.
* **New Hazard — Mimic Counterfeits:** Deceptive fakes look like real gold. Grabbing them inflicts a **-12% Oxygen penalty** and resets your combo streak!
* **Pro Tip:** Use the **Two-Finger Sonar (✌️)** to reveal which relics are genuine (Green rings) before grabbing!

### 🕳️ Level 3: The Deep Trench
* **Environment:** Dark abyssal trench where daylight fades away.
* **Primary Objective:** Collect and store **4 Rare Artifacts**.
* **Key Mechanics:**
  - **Diver Flashlight Beam:** You can only see objects illuminated by your directional headlight.
  - **🫧 Geothermal Air Bubble Vents:** White bubbling vents recharge **+25% Oxygen** on a 12-second cooldown.
  - **🌀 Swirling Whirlpools:** Vortexes that pull the diver inward. Actively swim away to break free and earn a **+50 Escape Bonus**!

### 🚢 Level 4: Shipwreck Graveyard
* **Environment:** Sunken 18th-century Spanish galleon draped in kelp and sea fog.
* **Primary Objective:** Collect and store **5 Bullion Relics**.
* **Apex Predator — Great White Shark:** A ferocious shark patrols the galleon corridors.
  - If it strikes an unshielded diver, it inflicts a catastrophic **-35% Oxygen penalty**!
  - **Defense:** Curl hand into a **Fist (✊)** when the shark charges to deploy the Energy Shield and deflect it (+150 bonus)!
* **🐙 Octopus Ambush:** Giant tentacles sweep across the deck. Keep moving to dodge strikes!

### 🏛️ Level 5: Sunken Atlantean Ruins
* **Environment:** Submerged marble temples and glowing pedestals of ancient Atlantis.
* **Primary Objective:** Solve the Atlantean Sanctum Puzzle & retrieve the **Ancient Crown (+500 pts)**.
* **The Ancient Invocation Sequence:** Hover near the central pedestal and perform:
  $$\text{Step 1: ✌️ Sonar Scan} \longrightarrow \text{Step 2: ✋ Current Burst} \longrightarrow \text{Step 3: 🤏 Pinch Touch}$$
* **Reward:** Unlocks the Legendary Poseidon Relic and the Museum Guardian Seal exhibit!

---

## 🏛️ 5. The Underwater Museum 3D Exhibit

Every genuine relic, rare artifact, and legendary treasure deposited during your expeditions is permanently saved in the **Underwater Museum Archive** (`ui/museum.py` & `museum_data.json`):

1. **Accessing the Museum:**
   - From Main Menu: Hover over **MUSEUM (🏛️)** and pinch.
   - Post-Expedition: Access directly from the Level Complete victory screen.
2. **Features:**
   - **3D Rotating Pedestals:** Exhibits rendered with dynamic 3D perspective projection.
   - **Interactive Inspection Modal:** Pinch any unlocked pedestal to zoom in, view high-resolution details, and read official marine archaeology expedition logs.
   - **Vault Statistics:** Displays total discovered gold value, unlocked exhibits, and expedition ranks.

---

## ⌨️ 6. Keyboard & Mouse Fallback Controls

If a webcam is not connected or lighting conditions are dim, the application automatically enables seamless mouse and keyboard controls:

| Action | Hand Gesture Equivalent | Mouse / Keyboard Control |
| :--- | :--- | :--- |
| **Move Diver** | Move Hand (🖐) | Move Mouse Cursor |
| **Pinch Grab / Click** | Pinch Fingers (🤏) | Left Mouse Button / Spacebar |
| **Sonar Pulse** | Two Fingers (✌️) | Right Mouse Button / 'S' Key |
| **Water Current** | Open Palm (✋) | Middle Mouse Button / 'C' Key |
| **Energy Shield** | Closed Fist (✊) | Hold 'F' Key / Shift Key |
| **Pause Game** | Hand Wave | 'ESC' Key |
| **Toggle Debug Overlay** | N/A | 'D' Key |
| **Toggle Fullscreen** | N/A | 'F11' Key |

---

## 🚀 7. How to Launch the Game

To launch the game on your system:

### Option A: Quick Batch Launcher (Recommended)
Simply double-click the included batch file in the project folder:
```cmd
run_game.bat
```
*(Or `run.bat`)*

### Option B: Terminal Command
Open PowerShell or Command Prompt in the project folder and run:
```powershell
python main.py
```

### Optimal Camera Setup Tips:
* **Position:** Sit 1.5 to 2.5 feet (45–75 cm) away from your webcam.
* **Lighting:** Ensure your face and hands are clearly lit from the front. Avoid strong backlights or bright windows directly behind you.
* **Hand Visibility:** Keep your full hand and wrist within the camera frame for responsive, jitter-free tracking.

---
*Created for AquaSense 3D Interactive Project Showcase.*
