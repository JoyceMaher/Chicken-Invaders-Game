import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
from OpenGL.GLUT import *

glutInit()

# --- Player properties ---
player_x = 0
player_y = -4
player_width = 1
player_height = 0.5
player_speed = 0.1
lives = 3
max_lives = 5

# --- Score ---
score = 0
score_for_extra_life = 100

# --- Bullet properties ---
bullets = []
bullet_speed = 0.2
bullet_width = 0.1
bullet_height = 0.3

# --- Chicken properties ---
chicken_size = 0.8
chickens = [
    {"x": -4, "y": 3},
    {"x": -2, "y": 3},
    {"x": 0, "y": 3},
    {"x": 2, "y": 3},
    {"x": 4, "y": 3},
]

# --- Egg properties ---
eggs = []
egg_speed = 0.05
egg_size = 0.2

# Shooting control
can_shoot = True

# Track last chicken disappearance
last_chicken_time = None

# --- Lighting setup ---
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    light_pos = [2.0, 4.0, 2.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    ambient = [0.3, 0.3, 0.3, 1.0]
    diffuse = [0.8, 0.8, 0.8, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMateriali(GL_FRONT, GL_SHININESS, 64)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# --- Drawing functions ---
def draw_player(x, y):
    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(x - player_width/2, y - player_height/2, 0)
    glVertex3f(x + player_width/2, y - player_height/2, 0)
    glVertex3f(x + player_width/2, y + player_height/2, 0)
    glVertex3f(x - player_width/2, y + player_height/2, 0)
    glEnd()

def draw_bullet(bullet):
    glColor3f(1, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glEnd()

def draw_chicken(ch):
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(ch["x"] - chicken_size/2, ch["y"] - chicken_size/2, 0)
    glVertex3f(ch["x"] + chicken_size/2, ch["y"] - chicken_size/2, 0)
    glVertex3f(ch["x"] + chicken_size/2, ch["y"] + chicken_size/2, 0)
    glVertex3f(ch["x"] - chicken_size/2, ch["y"] + chicken_size/2, 0)
    glEnd()

def draw_egg(egg):
    if egg["color"] == "white":
        glColor3f(1, 1, 1)
    else:
        glColor3f(0, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(egg["x"] - egg_size/2, egg["y"] - egg_size/2, 0)
    glVertex3f(egg["x"] + egg_size/2, egg["y"] - egg_size/2, 0)
    glVertex3f(egg["x"] + egg_size/2, egg["y"] + egg_size/2, 0)
    glVertex3f(egg["x"] - egg_size/2, egg["y"] + egg_size/2, 0)
    glEnd()

# --- Draw heart ---
def draw_heart_shape(x, y, z=0, size=0.35, rotation=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    glScalef(size, size, size)
    glColor3f(1, 0, 0)

    glBegin(GL_TRIANGLES)
    glVertex3f(0, -0.5, 0)
    glVertex3f(0.3, 0, 0)
    glVertex3f(-0.3, 0, 0)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(-0.15, 0, 0)
    for angle in range(0, 181, 5):
        rad = 0.15
        glVertex3f(-0.15 + rad*math.cos(math.radians(angle)),
                   0 + rad*math.sin(math.radians(angle)), 0)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.15, 0, 0)
    for angle in range(0, 181, 5):
        rad = 0.15
        glVertex3f(0.15 + rad*math.cos(math.radians(angle)),
                   0 + rad*math.sin(math.radians(angle)), 0)
    glEnd()
    glPopMatrix()

# --- Score display ---
def draw_score(score_value):
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 0)
    glRasterPos3f(-4.8, 4.8, -9.9)
    for ch in f"Score: {score_value}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopAttrib()

# --- Hearts display ---
def draw_hearts(lives, score):
    rotation_angle = pygame.time.get_ticks() * 0.05
    total_hearts = min(max_lives, lives)
    for i in range(total_hearts):
        draw_heart_shape(-2 + i*0.6, 4, rotation=rotation_angle)

# --- Show message ---
def show_message(text):
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(0, 1, 0)
    glRasterPos3f(-1.0, 0, -9.9)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopAttrib()
    pygame.display.flip()
    pygame.time.wait(3000)

# --- Main game loop ---
def main():
    global player_x, can_shoot, score, lives, last_chicken_time

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

    setup_lighting()
    clock = pygame.time.Clock()

    while True:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                can_shoot = True

        # --- Movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        player_x = max(min(player_x, 5), -5)

        # --- Shooting ---
        if keys[pygame.K_SPACE] and can_shoot:
            bullets.append({"x": player_x, "y": player_y + player_height/2})
            can_shoot = False

        # --- Update bullets ---
        for bullet in bullets: bullet["y"] += bullet_speed
        bullets[:] = [b for b in bullets if b["y"] < 6]

        # --- Eggs dropping ---
        for ch in chickens:
            if random.random() < 0.01:
                color = random.choice(["white", "black"])
                eggs.append({"x": ch["x"], "y": ch["y"], "color": color})
        for egg in eggs:
            egg["y"] -= egg_speed

        # --- Collisions ---
        bullets_to_remove = []
        chickens_to_remove = []

        for bullet in bullets:
            for ch in chickens:
                if (abs(bullet["x"] - ch["x"]) < (bullet_width/2 + chicken_size/2)) and \
                   (abs(bullet["y"] - ch["y"]) < (bullet_height/2 + chicken_size/2)):
                    bullets_to_remove.append(bullet)
                    chickens_to_remove.append(ch)

        for b in bullets_to_remove:
            if b in bullets: bullets.remove(b)
        for c in chickens_to_remove:
            if c in chickens: chickens.remove(c)
            if len(chickens) == 0:
                last_chicken_time = pygame.time.get_ticks()

        eggs_to_remove = []
        for egg in eggs:
            if (abs(egg["x"] - player_x) < (egg_size/2 + player_width/2)) and \
               (abs(egg["y"] - player_y) < (egg_size/2 + player_height/2)):
                if egg["color"] == "white":
                    score += 10
                    # Add extra life every 100 points, up to max_lives
                    extra_lives = min(score // score_for_extra_life, max_lives - 3)
                    lives = max(lives, 3 + extra_lives)
                else:
                    lives -= 1
                eggs_to_remove.append(egg)
        for e in eggs_to_remove:
            if e in eggs: eggs.remove(e)
        eggs[:] = [e for e in eggs if e["y"] > -6]

        # --- Win condition (0.1 sec delay) ---
        if last_chicken_time is not None:
            if pygame.time.get_ticks() - last_chicken_time >= 100:
                show_message("YOU WIN")
                pygame.quit()
                quit()

        # --- Game over ---
        if lives <= 0:
            show_message("GAME OVER")
            pygame.quit()
            quit()

        # --- Draw everything ---
        glClearColor(0.2, 0.6, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw_player(player_x, player_y)
        for bullet in bullets: draw_bullet(bullet)
        for ch in chickens: draw_chicken(ch)
        for egg in eggs: draw_egg(egg)

        draw_hearts(lives, score)
        draw_score(score)

        pygame.display.flip()
        clock.tick(60)

main()
