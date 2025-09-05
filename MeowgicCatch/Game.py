import sys, time, math, random
from math import sin, cos, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#CONFIG 
WINDOW_TITLE = "Meowgic Catch — OpenGL MVP"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

FOV_Y = 70.0
Z_NEAR = 0.1
Z_FAR = 2000.0

#Dynamic Environment: grid/floor visuals used by time-of-day
CELL_SIZE = 60.0
GRID_HALF_CELLS = 8
SHOW_AXES = True
SHOW_GRID_LINES = True

# Cat & Dog collision
COLLISION_HEIGHT_TOL = 25.0
HIT_IFRAMES_SEC = 0.6


# Dynamic Environment: phases of day
TIME_OF_DAY_DURATION_SEC = 30.0
COLOR_MORNING_SKY = (0.65, 0.80, 1.00)
COLOR_AFTERNOON_SKY = (0.40, 0.70, 1.00)
COLOR_EVENING_SKY = (0.05, 0.05, 0.10)

COLOR_MORNING_FLOOR = (0.80, 0.90, 0.85)
COLOR_AFTERNOON_FLOOR = (0.70, 0.85, 0.80)
COLOR_EVENING_FLOOR = (0.30, 0.35, 0.40)

# Camera defaults
CAM_DISTANCE = 900.0
CAM_YAW_DEG = 35.0
CAM_PITCH_DEG = 45.0


# Cat [Player Body, Player Movement/Jump visuals]
CAT_BODY_R = 40.0
CAT_HEAD_R = 22.0
CAT_EAR_R = 6.0
CAT_EAR_H = 14.0
CAT_LEG_W = 8.0
CAT_LEG_H = 14.0
CAT_TAIL_R = 4.0
CAT_TAIL_L = 35.0
CAT_Z_OFFSET = 30.0
CAT_COLOR_BODY = (0.90, 0.70, 0.25)
CAT_COLOR_HEAD = (0.95, 0.80, 0.40)
CAT_COLOR_EAR = (0.85, 0.55, 0.25)
CAT_COLOR_LEG = (0.45, 0.30, 0.20)
CAT_COLOR_TAIL = (0.45, 0.30, 0.20)


#  Cat jump parameters [Jump Action]
CAT_JUMP_HEIGHT = 80.0
CAT_JUMP_DURATION = 0.6
CAT_JUMP_COOLDOWN = 0.2

#Fish (random spawn + behaviors/scoring types)
FISH_COUNT = 17
FISH_BODY_R = 12.0
FISH_TAIL_R = 6.0
FISH_TAIL_L = 14.0
FISH_PICKUP_RADIUS = 36.0
FISH_Z = 25.0
FISH_COLOR_BODY = (0.20, 0.75, 0.95)
FISH_COLOR_TAIL = (0.95, 0.65, 0.25)

# spawn weights
FISH_PROB_NORMAL = 0.55
FISH_PROB_FAST = 0.25
FISH_PROB_TIMED = 0.17
FISH_PROB_GOLD = 0.03


FISH_FAST_SPEED = 220.0
FISH_TIMED_TTL_S = (4.0, 7.0)

# Powerups & scoring
POWERUP_TIME_S = 10.0
POWERUP_SPEED_MULT = 1.6
SCORE_NORMAL = 1
SCORE_FAST = 2
SCORE_TIMED = 2
SCORE_GOLD = 3

# Dogs (antagonist) and their health & steal mechanics
DOG_RADIUS = 20.0
DOG_SPEED = 70.0
DOG_COLOR = (0.36, 0.25, 0.20)
START_LIVES = 5

DOG_COUNT = 6
DOG_STEAL_INTERVAL_S = (0.6, 1.5)
DOG_STEAL_RADIUS_MULT = 0.8

# Different fish type colors for body and tail
FISH_COLOR_NORMAL = (1.20, 1.60, 1.95)
FISH_COLOR_FAST = (1.10, 1.85, 1.55)
FISH_COLOR_TIMED = (2.00, 1.30, 2.30)
FISH_COLOR_GOLD = (1.00, 2.80, 3.20)

# Meow stun 
MEOW_RANGE = 140.0
MEOW_STUN_SEC = 2.0
MEOW_COOLDOWN_S = 6.0

# Decoy 
DECOY_LIFETIME = 5.0
DECOY_RADIUS = 10.0
DECOY_COLOR = (0.6, 0.9, 0.3)

#Cheat Bubble Mode (auto-collect nearby Cat while in cheat mode)
CHEAT_BUBBLE_RADIUS = 120.0
CHEAT_MAGNET_SPEED  = 240.0
CHEAT_BUBBLE_COLOR  = (0.95, 0.97, 1.00)
CHEAT_BUBBLE_LINEW  = 2.0
cheat_mode = False

# Primitive shapes like cylinder, sphere, cone, cube
def draw_cylinder(base_radius, top_radius, height, slices, stacks):
    # Drawing a cylinder using OpenGL functions (GL_QUADS for simplicity)
    angle_step = 2.0 * math.pi / slices
    stack_step = height / stacks

    # Draw the cylindrical side surface
    for i in range(slices):
        theta0 = i * angle_step
        theta1 = (i + 1) * angle_step

        x0 = base_radius * math.cos(theta0)
        y0 = base_radius * math.sin(theta0)
        x1 = base_radius * math.cos(theta1)
        y1 = base_radius * math.sin(theta1)

        glBegin(GL_QUADS)
        for j in range(stacks):
            z0 = j * stack_step
            z1 = (j + 1) * stack_step

            glVertex3f(x0, y0, z0)
            glVertex3f(x1, y1, z0)
            glVertex3f(x1, y1, z1)
            glVertex3f(x0, y0, z1)
        glEnd()

    # Draw the top and bottom circles
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, height)  # Top center
    for i in range(slices + 1):
        angle = i * angle_step
        x = top_radius * math.cos(angle)
        y = top_radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)  # Bottom center
    for i in range(slices + 1):
        angle = i * angle_step
        x = base_radius * math.cos(angle)
        y = base_radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()

def draw_sphere(radius, slices, stacks):
    for i in range(slices):
        lat0 = math.pi * (-0.5 + float(i) / slices)
        lat1 = math.pi * (-0.5 + float(i + 1) / slices)

        glBegin(GL_QUAD_STRIP)
        for j in range(stacks + 1):
            lng = 2 * math.pi * float(j) / stacks
            x0 = cos(lng) * sin(lat0)
            y0 = sin(lng) * sin(lat0)
            z0 = cos(lat0)
            x1 = cos(lng) * sin(lat1)
            y1 = sin(lng) * sin(lat1)
            z1 = cos(lat1)
            glVertex3f(x0 * radius, y0 * radius, z0 * radius)
            glVertex3f(x1 * radius, y1 * radius, z1 * radius)
        glEnd()

def draw_cone(base_radius, height, slices, stacks):
    angle_step = 2.0 * math.pi / slices
    stack_step = height / stacks

    for i in range(slices):
        angle0 = i * angle_step
        angle1 = (i + 1) * angle_step

        x0 = base_radius * cos(angle0)
        y0 = base_radius * sin(angle0)
        x1 = base_radius * cos(angle1)
        y1 = base_radius * sin(angle1)

        glBegin(GL_TRIANGLES)
        for j in range(stacks):
            z0 = j * stack_step
            z1 = (j + 1) * stack_step

            glVertex3f(x0, y0, z0)
            glVertex3f(x1, y1, z0)
            glVertex3f(0.0, 0.0, z1)
        glEnd()

def draw_cube(size):
    half_size = size / 2.0  # Half of the cube's size for easier vertex calculation

    # Draw the 6 faces of the cube
    # Front face
    glBegin(GL_QUADS)
    glVertex3f(-half_size, -half_size, half_size)  # Bottom-left
    glVertex3f( half_size, -half_size, half_size)  # Bottom-right
    glVertex3f( half_size,  half_size, half_size)  # Top-right
    glVertex3f(-half_size,  half_size, half_size)  # Top-left
    glEnd()

    # Back face
    glBegin(GL_QUADS)
    glVertex3f(-half_size, -half_size, -half_size)  # Bottom-left
    glVertex3f(-half_size,  half_size, -half_size)  # Top-left
    glVertex3f( half_size,  half_size, -half_size)  # Top-right
    glVertex3f( half_size, -half_size, -half_size)  # Bottom-right
    glEnd()

    # Left face
    glBegin(GL_QUADS)
    glVertex3f(-half_size, -half_size, -half_size)  # Bottom-front
    glVertex3f(-half_size, -half_size,  half_size)  # Bottom-back
    glVertex3f(-half_size,  half_size,  half_size)  # Top-back
    glVertex3f(-half_size,  half_size, -half_size)  # Top-front
    glEnd()

    # Right face
    glBegin(GL_QUADS)
    glVertex3f( half_size, -half_size, -half_size)  # Bottom-front
    glVertex3f( half_size,  half_size, -half_size)  # Top-front
    glVertex3f( half_size,  half_size,  half_size)  # Top-back
    glVertex3f( half_size, -half_size,  half_size)  # Bottom-back
    glEnd()

    # Top face
    glBegin(GL_QUADS)
    glVertex3f(-half_size,  half_size, -half_size)  # Back-left
    glVertex3f(-half_size,  half_size,  half_size)  # Front-left
    glVertex3f( half_size,  half_size,  half_size)  # Front-right
    glVertex3f( half_size,  half_size, -half_size)  # Back-right
    glEnd()

    # Bottom face
    glBegin(GL_QUADS)
    glVertex3f(-half_size, -half_size, -half_size)  # Back-left
    glVertex3f( half_size, -half_size, -half_size)  # Back-right
    glVertex3f( half_size, -half_size,  half_size)  # Front-right
    glVertex3f(-half_size, -half_size,  half_size)  # Front-left
    glEnd()


# Camera
class Camera:
    def __init__(self):
        self.distance = CAM_DISTANCE
        self.yaw_deg = CAM_YAW_DEG
        self.pitch_deg = CAM_PITCH_DEG
        self.aspect = WINDOW_WIDTH / max(1, WINDOW_HEIGHT)
        self.target = (0.0, 0.0, 0.0)

    def resize(self, w, h): self.aspect = (w / max(1, h))

    def apply(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV_Y, self.aspect, Z_NEAR, Z_FAR)
        x, y, z = self._eye()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(x, y, z, self.target[0], self.target[1], self.target[2], 0, 0, 1)

    def _eye(self):
        r = self.distance
        yaw = radians(self.yaw_deg)
        pitch = radians(self.pitch_deg)
        return r * math.cos(pitch) * math.cos(yaw), r * math.cos(pitch) * math.sin(yaw), r * math.sin(pitch)

# Huds
def draw_axes(length=200.0):
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.2, 0.2); glVertex3f(0, 0, 0); glVertex3f(length, 0, 0)
    glColor3f(0.2, 1.0, 0.2); glVertex3f(0, 0, 0); glVertex3f(0, length, 0)
    glColor3f(0.2, 0.4, 1.0); glVertex3f(0, 0, 0); glVertex3f(0, 0, length)
    glEnd()

def draw_grid_lines():
    if not SHOW_GRID_LINES: return
    half, s = GRID_HALF_CELLS, CELL_SIZE
    extent = (2 * half + 1) * s * 0.5
    glLineWidth(1.0)
    glColor3f(0.25, 0.35, 0.40)
    glBegin(GL_LINES)
    for i in range(-half, half + 1):
        y = i * s
        glVertex3f(-extent, y, 0.2); glVertex3f(extent, y, 0.2)
    for i in range(-half, half + 1):
        x = i * s
        glVertex3f(x, -extent, 0.2); glVertex3f(x, extent, 0.2)
    glEnd()


# Cheat Mode visualization
def draw_wire_sphere(cx, cy, cz, r, segments=64):
    glLineWidth(CHEAT_BUBBLE_LINEW)
    glColor3f(*CHEAT_BUBBLE_COLOR)

    # XY ring
    glPushMatrix(); glTranslatef(cx, cy, cz)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        th = 2.0 * math.pi * (i / segments)
        glVertex3f(r * math.cos(th), r * math.sin(th), 0.0)
    glEnd()
    glPopMatrix()

    # XZ ring
    glPushMatrix(); glTranslatef(cx, cy, cz)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        th = 2.0 * math.pi * (i / segments)
        glVertex3f(r * math.cos(th), 0.0, r * math.sin(th))
    glEnd()
    glPopMatrix()

    # YZ ring
    glPushMatrix(); glTranslatef(cx, cy, cz)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        th = 2.0 * math.pi * (i / segments)
        glVertex3f(0.0, r * math.cos(th), r * math.sin(th))
    glEnd()
    glPopMatrix()

def hud_begin(width, height):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

def hud_end():
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW); glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()

def hud_text(x, y, text, r=1.0, g=1.0, b=1.0):
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in text: glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))


class World:
    def __init__(self):
        self.phase = "AM"
        self._t = 0.0
        self.weather = "clear"
        self._last_roll = time.time()
        self._rain = [(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(160, 260))
                      for _ in range(160)]

    def update(self, dt):
        self._t += dt
        p = int((self._t // TIME_OF_DAY_DURATION_SEC) % 3)
        self.phase = ("AM", "PM", "EVE")[p]
        if time.time() - self._last_roll > 20.0:
            self._last_roll = time.time()
            if random.random() < 0.25:
                self.weather = random.choice(["clear", "fog", "rain"])

    def apply_clear(self):
        if self.phase == "AM":
            glClearColor(*COLOR_MORNING_SKY, 1.0)
        elif self.phase == "PM":
            glClearColor(*COLOR_AFTERNOON_SKY, 1.0)
        else:
            glClearColor(*COLOR_EVENING_SKY, 1.0)

    def _set_fog(self, on):
        return

    def draw(self):
        half, s = GRID_HALF_CELLS, CELL_SIZE
        base = {"AM": COLOR_MORNING_FLOOR, "PM": COLOR_AFTERNOON_FLOOR, "EVE": COLOR_EVENING_FLOOR}[self.phase]

        glBegin(GL_QUADS)
        for ix in range(-half, half + 1):
            for iy in range(-half, half + 1):
                x0 = ix * s; y0 = iy * s; x1 = x0 + s; y1 = y0 + s
                odd = (ix + iy) & 1
                c = (base[0] * (0.95 if odd else 1.05),
                     base[1] * (0.95 if odd else 1.05),
                     base[2] * (0.95 if odd else 1.05))
                glColor3f(*c)
                glVertex3f(x0, y0, 0); glVertex3f(x1, y0, 0); glVertex3f(x1, y1, 0); glVertex3f(x0, y1, 0)
        glEnd()

        draw_grid_lines()
        if SHOW_AXES: draw_axes(200.0)

        self._set_fog(self.weather == "fog")
        if self.weather == "rain": self._draw_rain(half, s)

    def _draw_rain(self, half, s):
        size = (2 * half + 1) * s
        glLineWidth(1.0)
        glColor3f(0.85, 0.90, 0.95)
        glBegin(GL_LINES)
        for i, (rx, ry, rz) in enumerate(self._rain):
            x = rx * size * 0.5; y = ry * size * 0.5
            glVertex3f(x, y, rz); glVertex3f(x, y, rz - 14.0)
            rz -= 12.0
            if rz < 6.0:
                rz = random.uniform(160.0, 260.0)
                rx = random.uniform(-1, 1); ry = random.uniform(-1, 1)
            self._rain[i] = (rx, ry, rz)
        glEnd()

class Cat:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.yaw_deg = 0.0
        self.base_z = CAT_Z_OFFSET; self.jump_t = -1.0; self.jump_cd = 0.0
        self.step_mult = 1.0
        half, s = GRID_HALF_CELLS, CELL_SIZE
        self.max_extent = (2 * half + 1) * s * 0.5 - s * 0.5

    def rotate_left(self):  self.yaw_deg = (self.yaw_deg + 90.0) % 360.0
    def rotate_right(self): self.yaw_deg = (self.yaw_deg - 90.0) % 360.0
    def move_forward(self):
        step = CELL_SIZE * self.step_mult; yaw = radians(self.yaw_deg)
        self._try_move(self.x + math.cos(yaw) * step, self.y + math.sin(yaw) * step)
    def move_backward(self):
        step = CELL_SIZE * self.step_mult; yaw = radians(self.yaw_deg)
        self._try_move(self.x - math.cos(yaw) * step, self.y - math.sin(yaw) * step)
    def start_jump(self):
        if self.jump_t < 0 and self.jump_cd <= 0: self.jump_t = 0.0
    def update(self, dt):
        if self.jump_cd > 0: self.jump_cd = max(0.0, self.jump_cd - dt)
        if self.jump_t >= 0.0:
            self.jump_t += dt / max(1e-6, CAT_JUMP_DURATION)
            if self.jump_t >= 1.0: self.jump_t = -1.0; self.jump_cd = CAT_JUMP_COOLDOWN
    def current_z(self):
        if self.jump_t < 0: return self.base_z
        t = self.jump_t
        return self.base_z + 4.0 * CAT_JUMP_HEIGHT * t * (1.0 - t)
    def _try_move(self, nx, ny):
        nx = max(-self.max_extent, min(self.max_extent, nx))
        ny = max(-self.max_extent, min(self.max_extent, ny))
        self.x, self.y = nx, ny
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.current_z())
        glRotatef(self.yaw_deg, 0, 0, 1)
        glColor3f(*CAT_COLOR_BODY);
        draw_sphere(CAT_BODY_R, 18, 18)
        glPushMatrix()
        glTranslatef(CAT_BODY_R + CAT_HEAD_R * 0.9, 0.0, CAT_BODY_R * 0.4)
        glColor3f(*CAT_COLOR_HEAD);
        draw_sphere(CAT_HEAD_R, 18, 18)
        #ears
        glPushMatrix()
        glTranslatef(CAT_HEAD_R * 0.3, CAT_HEAD_R * 0.4, CAT_HEAD_R * 0.8)
        glRotatef(-90, 1, 0, 0);
        glColor3f(*CAT_COLOR_EAR);
        draw_cone(CAT_EAR_R, CAT_EAR_H, 10, 2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(CAT_HEAD_R * 0.3, -CAT_HEAD_R * 0.4, CAT_HEAD_R * 0.8)
        glRotatef(-90, 1, 0, 0);
        glColor3f(*CAT_COLOR_EAR);
        draw_cone(CAT_EAR_R, CAT_EAR_H, 10, 2)
        glPopMatrix()
        glPopMatrix()
        # legs
        glColor3f(*CAT_COLOR_LEG)
        for sx in (-1, 1):
            for sy in (-1, 1):
                glPushMatrix()
                glTranslatef(sx * CAT_BODY_R * 0.5, sy * CAT_BODY_R * 0.5, -CAT_BODY_R * 0.8)
                glScalef(CAT_LEG_W, CAT_LEG_W, CAT_LEG_H);
                draw_cube(1.0)
                glPopMatrix()
        # tail
        glPushMatrix()
        glTranslatef(-CAT_BODY_R * 0.8, 0.0, CAT_BODY_R * 0.5)
        glRotatef(30, 0, 1, 0); glColor3f(*CAT_COLOR_TAIL)
        draw_cylinder(CAT_TAIL_R, CAT_TAIL_R * 0.6, CAT_TAIL_L, 8, 1)
        glPopMatrix()
        glPopMatrix()


class Fish:
    def __init__(self, x, y, kind="normal"):
        self.x, self.y = x, y
        self.z = FISH_Z
        self.kind = kind
        self.alive = True
        self.tail_angle = 0
        self.timer = None
        self.vx = 0.0; self.vy = 0.0
        self.size = 1.0
        self.color = (0.20, 0.75, 0.95)
        if kind == "fast":
            ang = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(ang) * FISH_FAST_SPEED
            self.vy = math.sin(ang) * FISH_FAST_SPEED
        elif kind == "gold":
            self.color = (1.0, 0.84, 0.0); self.size = 1.8

        else:
            self.color = (0.20, 0.75, 0.95); self.size = 1.0
        self.die_at = time.time() + random.uniform(*FISH_TIMED_TTL_S) if kind == "timed" else 1e12

    def activate_powerup(self):
        if random.choice([True, False]): print("Fish activated: Speed boost!")
        else: print("Fish activated: Double score!")

    def update(self, dt, extent):
        if not self.alive: return
        if time.time() >= self.die_at and self.kind == "timed":
            self.alive = False; print(f"Timed fish expired at ({self.x}, {self.y})"); return
        if self.kind in ("fast", "gold"):
            self.x += self.vx * dt; self.y += self.vy * dt
            if self.x < -extent or self.x > extent:
                self.vx *= -1; self.x = max(-extent, min(extent, self.x))
            if self.y < -extent or self.y > extent:
                self.vy *= -1; self.y = max(-extent, min(extent, self.y))
        if self.kind == "timed" and time.time() > self.die_at:
            self.alive = False

    def draw(self):
        if not self.alive: return
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)

        # body
        body_col = FISH_COLOR_BODY if self.kind != "gold" else FISH_COLOR_GOLD
        glPushMatrix()
        glColor3f(*body_col); glScalef(1.6, 1.0, 0.7);
        draw_sphere(FISH_BODY_R, 24, 18)
        glPopMatrix()

        # tail
        tail_col = FISH_COLOR_TAIL if self.kind != "gold" else FISH_COLOR_GOLD
        glPushMatrix()
        glDisable(GL_CULL_FACE)
        glColor3f(*tail_col); glTranslatef(-16.0, 0.0, 0.0); glRotatef(self.tail_angle, 0, 1, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(-15.0, 9.0, 0.0); glVertex3f(-15.0, -9.0, 0.0)
        glEnd()
        glEnable(GL_CULL_FACE)
        glPopMatrix()


        glPushMatrix()
        glDisable(GL_CULL_FACE)
        glColor3f(*tail_col); glTranslatef(-2.0, 0.0, 7.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(10.0, 0.0, 0.0); glVertex3f(5.0, 0.0, 6.0)
        glEnd()
        glEnable(GL_CULL_FACE)
        glPopMatrix()

        # pectorals
        glPushMatrix()
        glTranslatef(4.0, 7.0, -1.0); glRotatef(90, 0, 1, 0); glRotatef(30, 1, 0, 0)
        draw_cone(5.0, 10.0, 12, 1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(4.0, -7.0, -1.0); glRotatef(90, 0, 1, 0); glRotatef(-30, 1, 0, 0)
        draw_cone(5.0, 10.0, 12, 1)
        glPopMatrix()

        def _eye(px, py, pz):
            glPushMatrix()
            glTranslatef(px, py, pz)
            glColor3f(1.0, 1.0, 1.0);
            draw_sphere(1.5, 12, 10)
            glTranslatef(0.6, 0.0, 0.0); glColor3f(0.05, 0.05, 0.05);
            draw_sphere(0.8, 10, 8)
            glPopMatrix()
        _eye(10.0, 3.0, 3.0); _eye(10.0, -3.0, 3.0)

        glPopMatrix()
        self.tail_angle = (self.tail_angle + 5) % 360

class FishField:
    def __init__(self): self.fishes = []
    def _rand_kind(self):
        r = random.random()
        if r < FISH_PROB_GOLD: return "gold"
        if r < FISH_PROB_FAST: return "fast"
        if r < FISH_PROB_TIMED: return "timed"
        return "normal"
    def spawn_random(self, n=FISH_COUNT):
        self.fishes.clear()
        half, s = GRID_HALF_CELLS, CELL_SIZE
        extent = (2 * half + 1) * s * 0.5 - s * 0.5
        for _ in range(n):
            x = random.uniform(-extent, extent); y = random.uniform(-extent, extent)
            self.fishes.append(Fish(x, y, self._rand_kind()))
    def update(self, dt):
        half, s = GRID_HALF_CELLS, CELL_SIZE
        extent = (2 * half + 1) * s * 0.5 - s * 0.5
        for f in self.fishes: f.update(dt, extent)
    def draw(self):
        for f in self.fishes: f.draw()
    def collect_if_close(self, px, py, r):
        got = 0; r2 = r * r
        for f in self.fishes:
            if f.alive:
                dx, dy = f.x - px, f.y - py
                if dx * dx + dy * dy <= r2:
                    f.alive = False; got += 1
        return got
    def collect_and_report(self, px, py, r):
        kinds = {"normal": 0, "fast": 0, "timed": 0, "gold": 0}
        r2 = r * r
        for f in self.fishes:
            if f.alive:
                dx, dy = f.x - px, f.y - py
                if dx * dx + dy * dy <= r2:
                    f.alive = False; kinds[f.kind] += 1
        return kinds
    def remaining(self): return sum(1 for f in self.fishes if f.alive)
    def magnet_pull(self, px, py, radius, pull_speed, dt):
        r2 = radius * radius
        for f in self.fishes:
            if not f.alive: continue
            dx = px - f.x; dy = py - f.y
            d2 = dx * dx + dy * dy
            if 1e-9 < d2 <= r2:
                d = d2 ** 0.5
                strength = 1.0 - (d / radius)
                step = pull_speed * strength * dt
                if step > d: step = d
                ux, uy = dx / d, dy / d
                f.x += ux * step; f.y += uy * step

class Dog:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.z = 25.0
        self.stunned_until = 0.0
        self.steal_ready_at = time.time() + random.uniform(*DOG_STEAL_INTERVAL_S)
    def stunned(self) -> bool: return time.time() < self.stunned_until
    def update(self, dt, target_xy):
        if self.stunned(): return
        tx, ty = target_xy
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy) + 1e-6
        step = DOG_SPEED * dt
        self.x += (dx / d) * step; self.y += (dy / d) * step
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(0.45, 0.55, 0.95) if self.stunned() else glColor3f(*DOG_COLOR)
        draw_sphere(DOG_RADIUS * 1.2, 16, 16)
        glPushMatrix()
        glTranslatef(DOG_RADIUS * 1.4, 0.0, DOG_RADIUS * 0.4)
        draw_sphere(DOG_RADIUS * 0.8, 16, 16)
        glPushMatrix()
        glTranslatef(DOG_RADIUS * 0.3, DOG_RADIUS * 0.45, DOG_RADIUS * 0.7)
        glRotatef(-90, 1, 0, 0);
        draw_cone(DOG_RADIUS * 0.35, DOG_RADIUS * 0.9, 10, 2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(DOG_RADIUS * 0.3, -DOG_RADIUS * 0.45, DOG_RADIUS * 0.7)
        glRotatef(-90, 1, 0, 0);
        draw_cone(DOG_RADIUS * 0.35, DOG_RADIUS * 0.9, 10, 2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(DOG_RADIUS * 0.95, 0.0, DOG_RADIUS * 0.2)
        glRotatef(90, 0, 1, 0); glColor3f(0.05, 0.05, 0.05)
        draw_cone(DOG_RADIUS * 0.25, DOG_RADIUS * 0.6, 10, 2)
        glPopMatrix()
        glPopMatrix()
        glColor3f(DOG_COLOR[0] * 0.9, DOG_COLOR[1] * 0.9, DOG_COLOR[2] * 0.9)
        leg_w = DOG_RADIUS * 0.35; leg_h = DOG_RADIUS * 0.9
        for sx in (-1, 1):
            for sy in (-1, 1):
                glPushMatrix()
                glTranslatef(sx * DOG_RADIUS * 0.7, sy * DOG_RADIUS * 0.7, -DOG_RADIUS * 0.9)
                glScalef(leg_w, leg_w, leg_h);
                draw_cube(1.0)
                glPopMatrix()

        glPushMatrix()
        glTranslatef(-DOG_RADIUS * 1.0, 0.0, DOG_RADIUS * 0.5)
        glRotatef(35, 0, 1, 0); glColor3f(*DOG_COLOR)
        draw_cylinder(DOG_RADIUS * 0.18, DOG_RADIUS * 0.12, DOG_RADIUS * 1.2, 8, 1)
        glPopMatrix()
        glPopMatrix()


class DogPack:
    def __init__(self):
        self.dogs = []

    def ensure_count(self, n):
        while len(self.dogs) < n:
            self.spawn_random()

    def spawn_random(self):
        half, s = GRID_HALF_CELLS, CELL_SIZE
        extent = (2 * half + 1) * s * 0.5 - s * 0.5
        self.dogs.append(Dog(random.uniform(-extent, extent),
                             random.uniform(-extent, extent)))

    def update(self, dt, target):
        for d in self.dogs:
            d.update(dt, target)

    def draw(self):
        for d in self.dogs:
            d.draw()

    def separate(self, dt):
        """Push dogs apart so they don't overlap visually."""
        min_dist = DOG_RADIUS * 2.5          
        r2 = min_dist * min_dist
        push = DOG_SPEED * 0.8 * dt          
        n = len(self.dogs)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.dogs[i], self.dogs[j]
                dx, dy = b.x - a.x, b.y - a.y
                d2 = dx * dx + dy * dy
                if 1e-9 < d2 < r2:
                    d = math.sqrt(d2)
                    ux, uy = dx / d, dy / d
                    a.x -= ux * push; a.y -= uy * push
                    b.x += ux * push; b.y += uy * push

#  GLOBAL STATE 
cam = Camera()
world = World()
cat = Cat()
fish_field = FishField()
dogs = DogPack()

score = 0
lives = START_LIVES
cheat_mode = False
double_score_until = -1e9
speed_boost_until = -1e9
last_meow_at = -1e9
decoy = None  # {"x","y","expires"}

last_damage_time = -1e9
game_over = False

last_time = None
fps_accum = 0.0
fps_frames = 0
fps_value = 0.0

# NEW: 10× score power-up timer
score_x10_until = -1e9

#  GAME LOGIC 
def init_gl():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE); glCullFace(GL_BACK)
    

def reset_game():
    global score, lives, decoy, last_meow_at, double_score_until, speed_boost_until
    global last_damage_time, game_over, score_x10_until
    score = 0; lives = START_LIVES; game_over = False
    last_meow_at = -1e9; double_score_until = -1e9; speed_boost_until = -1e9
    score_x10_until = -1e9
    last_damage_time = -1e9; decoy = None
    fish_field.spawn_random()
    dogs.dogs.clear(); dogs.ensure_count(DOG_COUNT)
    cat.x = 0.0; cat.y = 0.0; cat.yaw_deg = 0.0

def _meow_ready(): return (time.time() - last_meow_at) >= MEOW_COOLDOWN_S

def do_meow():
    global last_meow_at
    if not _meow_ready(): return
    last_meow_at = time.time()
    for d in dogs.dogs:
        dx, dy = d.x - cat.x, d.y - cat.y
        if dx * dx + dy * dy <= MEOW_RANGE * MEOW_RANGE:
            d.stunned_until = time.time() + MEOW_STUN_SEC

def drop_decoy():
    global decoy
    decoy = {"x": cat.x, "y": cat.y, "expires": time.time() + DECOY_LIFETIME}

def hud_color_for_env(phase, weather):
    if phase == "AM": r, g, b = (0.0, 1.0, 1.0)
    elif phase == "PM": r, g, b = (1.0, 0.5, 0.0)
    elif phase == "EVENING": r, g, b = (1.0, 0.0, 1.0)
    else: r, g, b = (1.0, 1.0, 1.0)
    if weather == "fog": r, g, b = (0.9, 0.9, 0.9)
    elif weather == "rain": r, g, b = (0.0, 0.8, 1.0)
    return r, g, b

def display():
    world.apply_clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    cam.apply()
    world.draw()

    # Decoy visuals 
    d = decoy
    decoy_active = False
    if d is not None and d.get("expires", 0) > time.time():
        decoy_active = True
        pulse = 1.0 + 0.3 * math.sin(time.time() * 10.0)
        glLineWidth(4.0); glColor3f(0.2, 1.0, 0.2)
        draw_ring(d["x"], d["y"], 2.0, DOG_RADIUS * 2.5 * pulse)
        glPushMatrix()
        glTranslatef(d["x"], d["y"], 2.0)
        glColor3f(0.3, 1.0, 0.3)
        draw_sphere(DOG_RADIUS * 1.6, 16, 16)
        glPopMatrix()

    fish_field.draw()
    dogs.draw()
    cat.draw()

    if cheat_mode:
        draw_wire_sphere(cat.x, cat.y, cat.current_z(), CHEAT_BUBBLE_RADIUS)

    hud_begin(WINDOW_WIDTH, WINDOW_HEIGHT)
    r, g, b = hud_color_for_env(world.phase, world.weather)
    hud_text(10, WINDOW_HEIGHT - 20,
             f"Phase:{world.phase}  Weather:{world.weather}  Score:{score}  Lives:{lives}",
             r, g, b)
    cd = max(0.0, MEOW_COOLDOWN_S - (time.time() - last_meow_at))
    hud_text(10, WINDOW_HEIGHT - 40, f"Meow CD:{cd:.1f}s  Cheat:{'ON' if cheat_mode else 'OFF'}")
    hud_text(10, WINDOW_HEIGHT - 60,
             "Move:WASD  Jump:Space  Meow:M  Decoy:T  Restart:R  Zoom:+/-  Yaw:1/2  Pitch:3/4",
             0.0, 1.0, 0.0)
    hud_text(10, WINDOW_HEIGHT - 80,
             f"Cat x={cat.x:.0f} y={cat.y:.0f} yaw:{cat.yaw_deg:.0f}°  FPS:{fps_value:.1f}")
    hud_text(10, WINDOW_HEIGHT - 100, f"Fish left: {fish_field.remaining()}")
    if decoy_active:
        hud_text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 40, "DECOY ACTIVE")
    if game_over:
        hud_text(WINDOW_WIDTH * 0.5 - 60, WINDOW_HEIGHT * 0.5 + 10, "GAME OVER", 1.0, 0.0, 0.0)
        hud_text(WINDOW_WIDTH * 0.5 - 120, WINDOW_HEIGHT * 0.5 - 10, "Press R to restart", 1.0, 0.2, 0.2)
    hud_end()
    glutSwapBuffers()

def draw_ring(cx, cy, cz, r, segments=48):
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        th = 2.0 * math.pi * (i / segments)
        glVertex3f(cx + r * math.cos(th), cy + r * math.sin(th), cz)
    glEnd()

def activate_double_score():
    global double_score_until
    double_score_until = time.time() + POWERUP_TIME_S

def activate_speed_boost():
    global speed_boost_until
    speed_boost_until = time.time() + POWERUP_TIME_S

# NEW: activate 10× scoring 
def activate_score_x10():
    global score_x10_until
    score_x10_until = time.time() + POWERUP_TIME_S
    print("Score x10 activated!")

def update_timer():
    global last_time, fps_accum, fps_frames, fps_value
    global score, lives, cheat_mode, decoy, game_over, last_damage_time, double_score_until, speed_boost_until
    global score_x10_until

    now = time.time()
    if last_time is None: last_time = now
    dt = min(0.1, max(0.0, now - last_time))
    last_time = now

    if game_over:
        glutPostRedisplay()
        return

    cat.step_mult = POWERUP_SPEED_MULT if now < speed_boost_until else 1.0

    
    mult = 10 if now < score_x10_until else (2 if now < double_score_until else 1)

    world.update(dt)
    cat.update(dt)
    fish_field.update(dt)

    target = (decoy["x"], decoy["y"]) if (decoy and decoy["expires"] > now) else (cat.x, cat.y)
    dogs.ensure_count(DOG_COUNT)
    dogs.update(dt, target)
    if hasattr(dogs, "separate"): dogs.separate(dt)

    for d in dogs.dogs:
        if now >= d.steal_ready_at:
            _ = fish_field.collect_if_close(d.x, d.y, FISH_PICKUP_RADIUS * DOG_STEAL_RADIUS_MULT)
            d.steal_ready_at = now + random.uniform(*DOG_STEAL_INTERVAL_S)
        if cat.jump_t >= 0.0:  
            continue
        if abs(cat.current_z() - d.z) > COLLISION_HEIGHT_TOL:
            continue
        if ((d.x - cat.x) ** 2 + (d.y - cat.y) ** 2) <= (DOG_RADIUS + CAT_BODY_R * 0.6) ** 2:
            if (now - last_damage_time) >= HIT_IFRAMES_SEC and lives > 0:
                lives -= 1; last_damage_time = now

    if decoy and decoy["expires"] <= now:
        decoy = None

    pickup_r = FISH_PICKUP_RADIUS * (1.8 if cat.jump_t >= 0.0 else 1.0)
    kinds = fish_field.collect_and_report(cat.x, cat.y, pickup_r)

    
    if kinds["gold"] > 0:
        for _ in range(kinds["gold"]):
            activate_score_x10()

    score += mult * (
        kinds["normal"] * SCORE_NORMAL
        + kinds["fast"]   * SCORE_FAST
        + kinds["timed"]  * SCORE_TIMED
        + kinds["gold"]   * SCORE_GOLD
    )

    if cheat_mode:
        fish_field.magnet_pull(cat.x, cat.y, CHEAT_BUBBLE_RADIUS, CHEAT_MAGNET_SPEED, dt)

    if fish_field.remaining() == 0: fish_field.spawn_random()

    fps_accum += dt; fps_frames += 1
    if fps_accum >= 0.5:
        fps_value = fps_frames / fps_accum
        fps_accum = 0.0; fps_frames = 0

    if lives <= 0: game_over = True

    glutPostRedisplay()



def on_keyboard(key, x, y):
    global cheat_mode, game_over
    k = key.decode("utf-8") if isinstance(key, (bytes, bytearray)) else key

    
    if game_over and k not in ('r', 'R', '\x1b'): return

    
    if k == '\x1b':  
        sys.exit(0)  

   
    elif k == '+':
        cam.distance = max(100.0, cam.distance - 30.0)
    elif k == '-':
        cam.distance = min(2000.0, cam.distance + 30.0)
    elif k == '1':
        cam.yaw_deg -= 5.0
    elif k == '2':
        cam.yaw_deg += 5.0
    elif k == '3':
        cam.pitch_deg = max(10.0, cam.pitch_deg - 3.0)
    elif k == '4':
        cam.pitch_deg = min(85.0, cam.pitch_deg + 3.0)

    # Cat movement controls
    elif k in ('w', 'W'):
        cat.move_forward()
    elif k in ('s', 'S'):
        cat.move_backward()
    elif k in ('a', 'A'):
        cat.rotate_left()
    elif k in ('d', 'D'):
        cat.rotate_right()

    # Jump and special actions
    elif k == ' ':
        cat.start_jump()
    elif k in ('c', 'C'):
        cheat_mode = not cheat_mode  
    elif k in ('m', 'M'):
        do_meow()  
    elif k in ('t', 'T'):
        drop_decoy()  # Drop a decoy
    elif k in ('r', 'R'):
        reset_game()  # Reset the game





def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(WINDOW_TITLE.encode("utf-8"))
    init_gl(); reset_game()
    glutDisplayFunc(display)
    
    glutKeyboardFunc(on_keyboard)
    glutIdleFunc(update_timer)   
    glutMainLoop()

if __name__ == "__main__":
    main()