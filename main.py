Here is the exact, complete, and updated code for `simulation.py`:

```python
import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Antigravity Black Hole Simulation")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Colors (RGBA for transparency support)
SPACE_BLACK = (5, 3, 15)
NEON_CYAN = (0, 240, 255)
NEON_PINK = (255, 0, 127)
NEON_PURPLE = (180, 0, 255)
NEON_GREEN = (50, 255, 100)
NEON_YELLOW = (255, 230, 0)
NEON_ORANGE = (255, 100, 0)
WHITE = (255, 255, 255)

COLOR_PALETTE = [NEON_CYAN, NEON_PINK, NEON_PURPLE, NEON_GREEN, NEON_YELLOW, NEON_ORANGE]

# --- SPRITE GENERATOR FOR NEON GLOWS ---
# Pre-rendering glow sprites to keep performance high (60 FPS) with hundreds of glowing elements.
def create_glow_sprite(color, size, core_ratio=0.25):
    """Creates a surface with a radial neon glow and a bright core."""
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    # Draw radial glow with quadratic falloff
    for r in range(size, 0, -1):
        alpha = int(120 * (1 - r / size) ** 2.2) # Max glow alpha ~120
        c = (color[0], color[1], color[2], alpha)
        pygame.draw.circle(surf, c, (size, size), r)
    
    # Draw hot white/bright core
    core_rad = max(1, int(size * core_ratio))
    core_color = (
        min(255, color[0] + 150),
        min(255, color[1] + 150),
        min(255, color[2] + 150),
        255
    )
    pygame.draw.circle(surf, core_color, (size, size), core_rad)
    return surf

# Generate glow sprites
GLOW_SPRITES = {}
for color in COLOR_PALETTE:
    # Small sprites for accretion disk particles
    GLOW_SPRITES[(color, 'small')] = create_glow_sprite(color, 6, core_ratio=0.3)
    # Medium sprites for stars
    GLOW_SPRITES[(color, 'medium')] = create_glow_sprite(color, 12, core_ratio=0.25)
    # Large sprites for special stars
    GLOW_SPRITES[(color, 'large')] = create_glow_sprite(color, 20, core_ratio=0.2)

# Special sprites for black hole visual effects
BH_GLOW = create_glow_sprite(NEON_ORANGE, 100, core_ratio=0.0) # Pure halo
BH_GLOW_BLUE = create_glow_sprite(NEON_CYAN, 100, core_ratio=0.0) # Antigravity halo

# --- NOISE & NEBULA BACKGROUND ---
def create_nebula_surface(width, height):
    """Creates a beautiful, faint background nebula texture."""
    nebula = pygame.Surface((width, height))
    nebula.fill(SPACE_BLACK)
    
    # Create a lower-resolution surface for smooth scaling (saves performance)
    neb_low = pygame.Surface((width // 4, height // 4))
    neb_low.fill((0, 0, 0))
    
    # Draw soft colored blobs
    for _ in range(4):
        cx = random.randint(0, width // 4)
        cy = random.randint(0, height // 4)
        rad = random.randint(40, 100)
        color = random.choice([NEON_PURPLE, NEON_PINK, NEON_CYAN])
        # Draw concentric transparent circles to simulate a soft blob
        for r in range(rad, 0, -6):
            alpha = int(8 * (1 - r / rad))
            c = (color[0], color[1], color[2])
            temp_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (color[0], color[1], color[2], alpha), (r, r), r)
            neb_low.blit(temp_surf, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)

    # Scale back up with smooth scaling
    pygame.transform.smoothscale(neb_low, (width, height), nebula)
    return nebula

# --- CLASSES ---

class BlackHole:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.mass = 65000.0
        self.target_mass = 65000.0
        self.event_horizon_radius = 45
        self.target_eh_radius = 45
        self.pulse = 0.0
        
    def update(self, dt):
        # Smoothly transition mass and size updates
        self.mass += (self.target_mass - self.mass) * 0.1
        self.target_eh_radius = math.sqrt(self.mass) * 0.18
        self.event_horizon_radius += (self.target_eh_radius - self.event_horizon_radius) * 0.1
        
        # Add a subtle animation/pulsation to the event horizon
        self.pulse += dt * 3.0
        
    def draw(self, surface, antigravity):
        # Draw background gravitational lensing aura (halo)
        eh_rad = int(self.event_horizon_radius)
        pulse_val = math.sin(self.pulse) * 3.0
        
        # Choose halo color based on mode
        halo_sprite = BH_GLOW_BLUE if antigravity else BH_GLOW
        
        # Scale halo sprite to match the black hole size
        scale_size = int((eh_rad * 3.5) + pulse_val)
        if scale_size > 0:
            scaled_halo = pygame.transform.smoothscale(halo_sprite, (scale_size * 2, scale_size * 2))
            surface.blit(scaled_halo, (self.pos.x - scale_size, self.pos.y - scale_size), special_flags=pygame.BLEND_RGBA_ADD)
            
        # Draw Event Horizon (the absolute black singularity core)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), max(1, int(eh_rad)))
        
        # Add a thin neon accent ring at the boundary
        accent_color = NEON_CYAN if antigravity else NEON_ORANGE
        pygame.draw.circle(surface, accent_color, (int(self.pos.x), int(self.pos.y)), max(1, int(eh_rad)), 1)


class Star:
    def __init__(self, center_pos=None):
        self.reset(center_pos)
        
    def reset(self, center_pos=None):
        # Spawn randomly in the window or near the edges
        if center_pos:
            # Spawn at edges
            side = random.randint(0, 3)
            if side == 0: # Top
                self.pos = pygame.math.Vector2(random.randint(0, WIDTH), -20)
            elif side == 1: # Bottom
                self.pos = pygame.math.Vector2(random.randint(0, WIDTH), HEIGHT + 20)
            elif side == 2: # Left
                self.pos = pygame.math.Vector2(-20, random.randint(0, HEIGHT))
            else: # Right
                self.pos = pygame.math.Vector2(WIDTH + 20, random.randint(0, HEIGHT))
        else:
            self.pos = pygame.math.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            
        # Physics attributes
        self.vel = pygame.math.Vector2(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))
        self.color = random.choice(COLOR_PALETTE)
        self.size_type = random.choice(['medium', 'medium', 'medium', 'large']) # weight towards medium
        self.size = 12 if self.size_type == 'medium' else 20
        self.mass = random.uniform(1.0, 3.0)
        
        # Trail history for motion blur/vector lines
        self.trail = []
        self.max_trail_len = random.randint(8, 15)
        
        # Lensing distance helper (avoids dividing by zero)
        self.min_dist = 5.0
        self.hit_by_wave = False

    def update(self, black_hole, dt, antigravity, active_shockwave):
        # Save trail history (physical coordinates)
        self.trail.append(pygame.math.Vector2(self.pos))
        if len(self.trail) > self.max_trail_len:
            self.trail.pop(0)
            
        # Calculate vector to black hole
        direction = black_hole.pos - self.pos
        distance = direction.length()
        
        if distance < self.min_dist:
            distance = self.min_dist
            
        # Gravitational Acceleration calculation (F = G*M/r^2)
        # Cap distance to prevent infinite forces at singularity
        effective_dist = max(distance, black_hole.event_horizon_radius * 0.8)
        force_magnitude = (black_hole.mass * self.mass) / (effective_dist ** 2)
        force_vector = direction.normalize() * force_magnitude
        
        if antigravity:
            # Gravity reverses and repels stars
            self.vel -= force_vector * 0.7 * dt
            # Extra damping in antigravity mode to create fluid expansion
            self.vel *= 0.99
        else:
            # Standard attractive gravity
            self.vel += force_vector * dt
            # Drag coefficient (simulates a faint cosmic dust resistance)
            self.vel *= 0.995
            
        # Apply velocity
        self.pos += self.vel * dt * 60.0
        
        # Handle shockwave collision
        if active_shockwave:
            if not self.hit_by_wave and distance > 0:
                # If shockwave expands past the star's current distance
                if distance < active_shockwave.radius:
                    self.hit_by_wave = True
                    # Calculate blast impulse (stronger close to center)
                    blast_strength = 25.0 * (400.0 / (distance + 50.0))
                    # Clamp blast strength
                    blast_strength = max(5.0, min(blast_strength, 45.0))
                    # Shoot outward
                    self.vel = -direction.normalize() * blast_strength
        else:
            self.hit_by_wave = False
            
        # Boundary check: respawn if they go too far out in antigravity or get swallowed
        if distance < black_hole.event_horizon_radius:
            self.reset(center_pos=black_hole.pos)
        elif self.pos.x < -100 or self.pos.x > WIDTH + 100 or self.pos.y < -100 or self.pos.y > HEIGHT + 100:
            # Respawn at opposite side or edge under normal gravity,
            # but if antigravity is on, we let them fly out and spawn new ones at the center
            if antigravity:
                # Spawn near event horizon to blow outward
                angle = random.uniform(0, 2 * math.pi)
                spawn_dist = black_hole.event_horizon_radius + random.uniform(5, 20)
                self.pos = black_hole.pos + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * spawn_dist
                self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * random.uniform(2.0, 5.0)
                self.trail = []
            else:
                self.reset(center_pos=black_hole.pos)

    def draw(self, surface, black_hole):
        """Draws the star and its trail, warped by gravitational lensing."""
        if len(self.trail) < 2:
            return
            
        def lens_warp(pos):
            """Applies 2D Gravitational Lensing coordinates distortion."""
            offset = pos - black_hole.pos
            d = offset.length()
            if d < black_hole.event_horizon_radius:
                return None # Swallowed by event horizon, do not render
            
            # Einstein Ring simulation: warp spatial coordinates outward
            # Shift grows stronger near the event horizon
            einstein_rad = black_hole.event_horizon_radius * 1.6
            d_distorted = math.sqrt(d**2 + einstein_rad**2)
            return black_hole.pos + offset.normalize() * d_distorted

        # Draw the lensed motion trail
        warped_trail = []
        for p in self.trail:
            wp = lens_warp(p)
            if wp:
                warped_trail.append(wp)
                
        if len(warped_trail) >= 2:
            # Draw line segments for the trail with fading transparency
            for i in range(len(warped_trail) - 1):
                p1 = warped_trail[i]
                p2 = warped_trail[i+1]
                alpha = int(255 * (i / len(warped_trail)))
                color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
                
                # Draw lines on a transparent overlay
                temp_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, color_with_alpha, (p1.x, p1.y), (p2.x, p2.y), max(1, int(i * 0.25)))
                surface.blit(temp_surf, (0, 0))

        # Draw the main star body
        curr_warped = lens_warp(self.pos)
        if curr_warped:
            sprite = GLOW_SPRITES[(self.color, self.size_type)]
            sprite_rect = sprite.get_rect(center=(int(curr_warped.x), int(curr_warped.y)))
            surface.blit(sprite, sprite_rect, special_flags=pygame.BLEND_RGBA_ADD)


class DiskParticle:
    def __init__(self, black_hole, r=None):
        # Angle of orbit
        self.theta = random.uniform(0, 2 * math.pi)
        
        # Orbital radius
        if r is not None:
            self.r = r
        else:
            self.r = random.uniform(black_hole.event_horizon_radius * 1.2, black_hole.event_horizon_radius * 4.5)
            
        # Color gradient based on distance (hot yellow inside, dark orange/red outside)
        ratio = (self.r - black_hole.event_horizon_radius * 1.2) / (black_hole.event_horizon_radius * 3.3)
        ratio = max(0.0, min(1.0, ratio))
        
        if ratio < 0.2:
            self.color = NEON_YELLOW
        elif ratio < 0.6:
            self.color = NEON_ORANGE
        else:
            self.color = NEON_PINK
            
        self.base_speed = random.uniform(0.9, 1.2)
        self.noise_phase = random.uniform(0, 100)
        self.hit_by_wave = False
        self.outward_speed = 0.0

    def update(self, black_hole, dt, antigravity, active_shockwave):
        self.noise_phase += dt * 5.0
        
        # Keplerian-like orbit: angular velocity is faster at smaller radii
        # Speed ~ 1 / sqrt(r^3)
        omega = 120.0 / (max(20.0, self.r) ** 1.3) * self.base_speed
        
        # Orbit motion
        self.theta += omega * dt * 60.0
        
        # Handle radial movement (drift / gravity / shockwave)
        if antigravity:
            # Antigravity pushes accretion matter outward, expanding the disk
            self.r += (120.0 * dt) + (self.outward_speed * dt * 60.0)
            self.outward_speed *= 0.95
        else:
            # Standard gravity: matter slowly drifts inward towards event horizon
            if self.outward_speed > 0.1:
                # Settle back from shockwave blast
                self.r += self.outward_speed * dt * 60.0
                self.outward_speed *= 0.94 # Slow down outward drift
            else:
                # Normal accretion inward spiral
                drift = 0.15 * (black_hole.event_horizon_radius / max(10.0, self.r))
                self.r -= drift * dt * 60.0
                
        # Accretion turbulence (visual noise)
        radial_noise = math.sin(self.noise_phase) * 0.15
        current_r = self.r + radial_noise
        
        # Check shockwave
        if active_shockwave:
            if not self.hit_by_wave:
                # Check distance (approximation in 2D circular space)
                if current_r < active_shockwave.radius:
                    self.hit_by_wave = True
                    # Blast outward
                    self.outward_speed = random.uniform(12.0, 22.0) * (300.0 / (current_r + 50.0))
        else:
            self.hit_by_wave = False
            
        # Event horizon checks
        if self.r < black_hole.event_horizon_radius * 0.95:
            # Swallowed! Respawn at outer edge of disk
            self.r = random.uniform(black_hole.event_horizon_radius * 3.5, black_hole.event_horizon_radius * 5.0)
            self.outward_speed = 0.0
        elif self.r > WIDTH * 1.2:
            # Escaped too far in antigravity, spawn back near event horizon
            self.r = random.uniform(black_hole.event_horizon_radius * 1.1, black_hole.event_horizon_radius * 1.5)
            self.outward_speed = 0.0
            
    def get_render_info(self, black_hole):
        """Calculates 3D tilted coordinates and returns depth and pos."""
        # circular coordinate
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)
        
        # Apply simulated 3D tilt: compress Y axis
        tilt_y_factor = 0.32
        # Rotate disk plane slightly on screen (tilt angle ~ -12 degrees)
        rot_angle = -0.22 
        
        rx = x * math.cos(rot_angle) - (y * tilt_y_factor) * math.sin(rot_angle)
        ry = x * math.sin(rot_angle) + (y * tilt_y_factor) * math.cos(rot_angle)
        
        screen_pos = black_hole.pos + pygame.math.Vector2(rx, ry)
        
        # Lensing distortion on accretion disk particles
        offset = screen_pos - black_hole.pos
        d = offset.length()
        
        # Apply lensing displacement to make the accretion disk look realistically bent
        # around the event horizon. This is the hallmark of the Interstellar CGI!
        einstein_rad = black_hole.event_horizon_radius * 1.45
        if d >= black_hole.event_horizon_radius * 0.9:
            d_dist = math.sqrt(d**2 + einstein_rad**2)
            screen_pos = black_hole.pos + offset.normalize() * d_dist
            
        # Depth logic: particles with positive local y orbit in "front", negative in "back"
        is_front = (y >= 0)
        
        return screen_pos, is_front


class Shockwave:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = 0.0
        self.speed = 950.0 # pixels per second
        self.max_radius = 1200.0
        self.alpha = 255
        self.color = NEON_CYAN
        self.spark_particles = [] # Accompanying dust specs for visual flair

    def update(self, dt):
        self.radius += self.speed * dt
        
        # Fade out alpha as it approaches max radius
        alpha_ratio = max(0.0, min(1.0, 1.0 - (self.radius / self.max_radius)))
        self.alpha = int(255 * (alpha_ratio ** 1.5))
        
        # Emit sparks along the shockwave front early on
        if self.radius < 500 and random.random() < 0.6:
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                spark_pos = self.pos + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * self.radius
                spark_vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * random.uniform(2.0, 6.0)
                self.spark_particles.append({
                    'pos': spark_pos,
                    'vel': spark_vel,
                    'life': 1.0,
                    'color': random.choice([NEON_CYAN, WHITE, NEON_PURPLE])
                })
                
        # Update sparks
        for spark in self.spark_particles[:]:
            spark['pos'] += spark['vel'] * dt * 60.0
            spark['life'] -= dt * 2.0
            if spark['life'] <= 0:
                self.spark_particles.remove(spark)

    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Draw the main expanding shockwave rings
        temp_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Core ring
        pygame.draw.circle(temp_surf, (self.color[0], self.color[1], self.color[2], self.alpha), 
                           (int(self.pos.x), int(self.pos.y)), int(self.radius), max(1, int(15 * (self.alpha / 255))))
        
        # Inner secondary ripple ring
        if self.radius > 50:
            inner_alpha = int(self.alpha * 0.5)
            pygame.draw.circle(temp_surf, (self.color[0], self.color[1], self.color[2], inner_alpha), 
                               (int(self.pos.x), int(self.pos.y)), int(self.radius - 40), max(1, int(5 * (inner_alpha / 255))))
            
        surface.blit(temp_surf, (0, 0))
        
        # Draw sparks
        for spark in self.spark_particles:
            s_alpha = int(255 * spark['life'])
            s_color = (spark['color'][0], spark['color'][1], spark['color'][2], s_alpha)
            s_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, s_color, (3, 3), max(1, int(3 * spark['life'])))
            surface.blit(s_surf, (int(spark['pos'].x - 3), int(spark['pos'].y - 3)))

    def is_finished(self):
        return self.radius >= self.max_radius or self.alpha <= 0


# --- INITIALIZE SIMULATION WORLD ---
black_hole = BlackHole(WIDTH // 2, HEIGHT // 2)

# Create stars (250 background stars)
stars = [Star() for _ in range(250)]

# Create accretion disk (500 particles)
disk_particles = [DiskParticle(black_hole) for _ in range(500)]

# Simulation state
antigravity = False
active_shockwave = None
shockwave_count = 0
space_background = create_nebula_surface(WIDTH, HEIGHT)

# UI Font
font = pygame.font.SysFont("Consolas", 16)
bold_font = pygame.font.SysFont("Consolas", 20, bold=True)

# Main Loop Control
running = True
show_hud = True

while running:
    # Compute deltaTime (capped to ~60FPS equivalent dt)
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 0.1) # Prevent huge physics jumps if lag occurs

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Toggle gravity state
                antigravity = not antigravity
                
                # Trigger shockwave when switching to Antigravity
                if antigravity:
                    active_shockwave = Shockwave(black_hole.pos.x, black_hole.pos.y)
                    shockwave_count += 1
            elif event.key == pygame.K_UP:
                black_hole.target_mass = min(250000.0, black_hole.target_mass + 15000.0)
            elif event.key == pygame.K_DOWN:
                black_hole.target_mass = max(10000.0, black_hole.target_mass - 15000.0)
            elif event.key == pygame.K_r:
                # Reset simulation
                stars = [Star() for _ in range(250)]
                disk_particles = [DiskParticle(black_hole) for _ in range(500)]
                antigravity = False
                active_shockwave = None
                black_hole.target_mass = 65000.0
            elif event.key == pygame.K_h:
                show_hud = not show_hud
                
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize gracefully
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            black_hole.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
            space_background = create_nebula_surface(WIDTH, HEIGHT)

    # --- UPDATE ---
    black_hole.update(dt)
    
    if active_shockwave:
        active_shockwave.update(dt)
        if active_shockwave.is_finished():
            active_shockwave = None
            
    # Update stars
    for star in stars:
        star.update(black_hole, dt, antigravity, active_shockwave)
        
    # Update accretion disk
    for p in disk_particles:
        p.update(black_hole, dt, antigravity, active_shockwave)

    # --- RENDER ---
    # Draw dark space background with nebula
    screen.blit(space_background, (0, 0))

    # Apply additive blend overlay to make the whole screen glow slightly
    # 1. Sort accretion disk particles into back-half and front-half
    disk_draw_list = []
    for p in disk_particles:
        pos, is_front = p.get_render_info(black_hole)
        disk_draw_list.append((pos, is_front, p.color))
        
    # Draw back accretion disk (behind the singularity)
    for pos, is_front, color in disk_draw_list:
        if not is_front:
            sprite = GLOW_SPRITES[(color, 'small')]
            sprite_rect = sprite.get_rect(center=(int(pos.x), int(pos.y)))
            screen.blit(sprite, sprite_rect, special_flags=pygame.BLEND_RGBA_ADD)

    # Draw the central Black Hole core and its aura
    black_hole.draw(screen, antigravity)

    # Draw front accretion disk (in front of the singularity)
    for pos, is_front, color in disk_draw_list:
        if is_front:
            sprite = GLOW_SPRITES[(color, 'small')]
            sprite_rect = sprite.get_rect(center=(int(pos.x), int(pos.y)))
            screen.blit(sprite, sprite_rect, special_flags=pygame.BLEND_RGBA_ADD)

    # Draw lensed stars
    for star in stars:
        star.draw(screen, black_hole)

    # Draw active shockwave
    if active_shockwave:
        active_shockwave.draw(screen)

    # Draw HUD overlay
    if show_hud:
        # Create a semi-transparent HUD panel
        hud_width, hud_height = 360, 240
        hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        # Deep dark transparent slate background
        pygame.draw.rect(hud_surface, (10, 8, 22, 185), (0, 0, hud_width, hud_height), border_radius=12)
        # Neon purple border
        pygame.draw.rect(hud_surface, NEON_PURPLE, (0, 0, hud_width, hud_height), width=1, border_radius=12)
        
        # HUD Elements
        title = bold_font.render("ANTIGRAVITY SIMULATION", True, NEON_CYAN)
        hud_surface.blit(title, (20, 20))
        
        # Display gravity mode with custom neon coloring
        mode_text = "ANTIGRAVITY / EXPULSION" if antigravity else "GRAVITY / IMPLOSION"
        mode_color = NEON_CYAN if antigravity else NEON_ORANGE
        mode_label = font.render(f"Gravity Mode: {mode_text}", True, mode_color)
        hud_surface.blit(mode_label, (20, 55))
        
        # Stats
        mass_lbl = font.render(f"Black Hole Mass : {int(black_hole.mass):,}", True, WHITE)
        stars_lbl = font.render(f"Active Stars    : {len(stars)}", True, WHITE)
        disk_lbl = font.render(f"Accretion Matter: {len(disk_particles)}", True, WHITE)
        wave_lbl = font.render(f"Shockwaves      : {shockwave_count}", True, WHITE)
        fps_lbl = font.render(f"Frame Rate (FPS): {int(clock.get_fps())}", True, NEON_GREEN)
        
        hud_surface.blit(mass_lbl, (20, 85))
        hud_surface.blit(stars_lbl, (20, 105))
        hud_surface.blit(disk_lbl, (20, 125))
        hud_surface.blit(wave_lbl, (20, 145))
        hud_surface.blit(fps_lbl, (20, 165))
        
        # Help footer
        help_txt = font.render("[SPACE] Toggle Gravity | [UP/DOWN] Mass | [R] Reset | [H] HUD", True, (160, 160, 180))
        hud_surface.blit(help_txt, (20, 205))
        
        screen.blit(hud_surface, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
```
