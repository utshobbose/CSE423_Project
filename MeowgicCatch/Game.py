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
