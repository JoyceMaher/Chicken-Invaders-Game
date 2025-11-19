import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

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
bullet_speed = 0.2
bullet_width = 0.1
bullet_height = 0.3

# --- Helper functions ---
def draw_sphere(x, y, z, radius, r, g, b):
    glColor3f(r, g, b)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    gluSphere(quadric, radius, 32, 32)
    glPopMatrix()

def draw_cube(x, y, z, size, r, g, b):
    vertices = [
        [1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],
        [1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]
    ]
    vertices = [[v[0]*size + x, v[1]*size + y, v[2]*size + z] for v in vertices]
    surfaces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glColor3f(0,0,0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_chicken_3d(x, y, z, scale=1.0, type="white"):
    if type == "white":
        body_color = (1,1,1)
    elif type == "black":
        body_color = (0.1,0.1,0.1)
    elif type == "gold":
        body_color = (1,0.84,0)
    
    # Body
    draw_sphere(x, y, z, 0.5*scale, *body_color)
    draw_sphere(x, y+0.7*scale, z, 0.3*scale, *body_color)
    
    # Beak
    draw_sphere(x+0.35*scale, y+0.7*scale, z, 0.1*scale, 1,0.5,0)
    
    # Comb
    draw_sphere(x-0.15*scale, y+1.0*scale, z, 0.1*scale, 1,0,0)
    draw_sphere(x, y+1.05*scale, z, 0.1*scale, 1,0,0)
    draw_sphere(x+0.15*scale, y+1.0*scale, z, 0.1*scale, 1,0,0)
    
    # Wings
    draw_sphere(x-0.45*scale, y+0.2*scale, z, 0.25*scale, *body_color)
    draw_sphere(x+0.45*scale, y+0.2*scale, z, 0.25*scale, *body_color)
    
    # Legs
    draw_cube(x-0.15*scale, y-0.7*scale, z, 0.1*scale, 1,0.7,0)
    draw_cube(x+0.15*scale, y-0.7*scale, z, 0.1*scale, 1,0.7,0)

def generate_chickens(n):
    num_black = int(n*0.6)
    num_white = int(n*0.3)
    num_gold = n - num_black - num_white
    types_list = ["black"]*num_black + ["white"]*num_white + ["gold"]*num_gold
    random.shuffle(types_list)
    
    chickens = []
    for idx, t in enumerate(types_list):
        chickens.append({
            'base_x': 0,
            'base_y': -6,
            'target_x': 0,
            'target_y': 0,
            'type': t,
            'angle': 0,
            'arrived': False,
            'drop_delay': idx*0.5,
            'last_drop': time.time(),
            'offset_x': 0,
            'offset_y': 0,
            'rand_phase': random.uniform(0, 2*math.pi),
            'rand_speed_x': random.uniform(0.5,1.5),
            'rand_speed_y': random.uniform(0.5,1.5),
            'rand_amp_x': random.uniform(0.2,0.5),
            'rand_amp_y': random.uniform(0.1,0.3),
            'direction': random.choice([-1,1]),
            'alive': True
        })
    return chickens

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    light_pos = [2.0,4.0,2.0,1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    
    ambient = [0.3,0.3,0.3,1.0]
    diffuse = [0.8,0.8,0.8,1.0]
    specular = [1.0,1.0,1.0,1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMateriali(GL_FRONT, GL_SHININESS, 64)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_player(x, y):
    glColor3f(0,1,0)
    glBegin(GL_QUADS)
    glVertex3f(x - player_width/2, y - player_height/2, 0)
    glVertex3f(x + player_width/2, y - player_height/2, 0)
    glVertex3f(x + player_width/2, y + player_height/2, 0)
    glVertex3f(x - player_width/2, y + player_height/2, 0)
    glEnd()

def draw_bullet(bullet):
    glColor3f(1,1,0)
    glBegin(GL_QUADS)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glEnd()

def draw_heart_shape(x, y, z=0, size=0.35, rotation=0):
    glPushMatrix()
    glTranslatef(x,y,z)
    glRotatef(rotation,0,1,0)
    glScalef(size,size,size)
    glColor3f(1,0,0)
    
    glBegin(GL_TRIANGLES)
    glVertex3f(0,-0.5,0)
    glVertex3f(0.3,0,0)
    glVertex3f(-0.3,0,0)
    glEnd()
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(-0.15,0,0)
    rad = 0.15
    for angle in range(0,181,5):
        glVertex3f(-0.15 + rad*math.cos(math.radians(angle)),
                   0 + rad*math.sin(math.radians(angle)),0)
    glEnd()
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.15,0,0)
    for angle in range(0,181,5):
        glVertex3f(0.15 + rad*math.cos(math.radians(angle)),
                   0 + rad*math.sin(math.radians(angle)),0)
    glEnd()
    
    glPopMatrix()

def draw_score(score_value):
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1,1,0)
    glRasterPos3f(-4.8,4.8,-9.9)
    for ch in f"Score: {score_value}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopAttrib()

def draw_hearts(lives, score):
    rotation_angle = pygame.time.get_ticks() * 0.05
    total_hearts = min(max_lives, lives)
    for i in range(total_hearts):
        draw_heart_shape(-2 + i*0.6, 4, rotation=rotation_angle)

def show_message(text):
    """Show a message for 3 seconds"""
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(0,1,0)
    glRasterPos3f(-1.0,0,-9.9)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopAttrib()
    pygame.display.flip()
    pygame.time.wait(3000)

def check_win(last_chicken_time):
    if last_chicken_time is not None:
        if pygame.time.get_ticks() - last_chicken_time >= 1000:
            return True
    return False


def main():
    global player_x, lives, score

    can_shoot = True
    last_chicken_time = None

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0,0,-15)
    setup_lighting()

    clock = pygame.time.Clock()

    n = 15
    chicken_size = 0.5
    egg_size = 0.3
    chickens = generate_chickens(n)
    bullets = []
    eggs = []
    fixed_speed = 0.08
    start_time = time.time()
    
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    spacing_x = 12 / (cols - 1)
    top_y = 4
    bottom_y = 2
    spacing_y = (top_y - bottom_y) / max(rows-1,1)
    
    k = 0
    for r in range(rows):
        for c_idx in range(cols):
            if k >= n:
                break
            chickens[k]['target_x'] = -6 + c_idx*spacing_x + random.uniform(-0.3,0.3)
            chickens[k]['target_y'] = top_y - r*spacing_y + random.uniform(-0.2,0.2)
            k += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                can_shoot = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_x -= player_speed
        if keys[pygame.K_RIGHT]: player_x += player_speed
        player_x = max(min(player_x,7),-7)

        if keys[pygame.K_SPACE] and can_shoot:
            bullets.append({"x":player_x,"y":player_y+player_height/2})
            can_shoot = False

        glClearColor(0.2,0.6,1.0,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # --- Update bullets ---
        for bullet in bullets: bullet["y"] += bullet_speed
        bullets = [b for b in bullets if b["y"] < 6]

        current_time = time.time()
        for c in chickens:
            if not c['alive']:
                continue
                
            if not c['arrived']:
                if abs(c['base_x'] - c['target_x']) > fixed_speed:
                    c['base_x'] += fixed_speed if c['base_x'] < c['target_x'] else -fixed_speed
                else:
                    c['base_x'] = c['target_x']

                if abs(c['base_y'] - c['target_y']) > fixed_speed:
                    c['base_y'] += fixed_speed if c['base_y'] < c['target_y'] else -fixed_speed
                else:
                    c['base_y'] = c['target_y']

                if c['base_x'] == c['target_x'] and c['base_y'] == c['target_y']:
                    c['arrived'] = True
            else:
                t = time.time()
                c['offset_x'] = math.sin(t*c['rand_speed_x'] + c['rand_phase']) * c['rand_amp_x']
                c['offset_y'] = math.sin(t*c['rand_speed_y'] + c['rand_phase']) * c['rand_amp_y']

                c['base_x'] += c['direction'] * 0.02
                if c['base_x'] >= 6 or c['base_x'] <= -6:
                    c['direction'] *= -1

        # --- Draw chickens & drop eggs ---
        for c in chickens:
            if not c['alive']:
                continue
                
            c['angle'] += 2
            draw_x = c['base_x'] + (c['offset_x'] if c['arrived'] else 0)
            draw_y = c['base_y'] + (c['offset_y'] if c['arrived'] else 0)
            
            glPushMatrix()
            glTranslatef(draw_x, draw_y, 0)
            glRotatef(c['angle'], 0, 1, 0)
            draw_chicken_3d(0, 0, 0, 0.3, c['type'])
            glPopMatrix()

            if c['arrived'] and current_time - start_time >= c['drop_delay']:
                drop_interval = {'black':4,'white':3,'gold':5}[c['type']]
                if current_time - c['last_drop'] >= drop_interval:
                    eggs.append({'x':c['base_x'],'y':c['base_y']-0.7,'type':c['type']})
                    c['last_drop'] = current_time

        # --- Update eggs ---
        eggs_to_remove = []
        for egg in eggs:
            egg['y'] -= 0.1
            if abs(egg['x']-player_x)<(egg_size/2+player_width/2) and abs(egg['y']-player_y)<(egg_size/2+player_height/2):
                if egg['type']=="white":
                    score += 10
                    extra_lives = min(score//score_for_extra_life, max_lives-3)
                    lives = max(lives, 3+extra_lives)
                elif egg['type']=="black":
                    lives -= 1
                elif egg['type']=="gold":
                    score += 50
                eggs_to_remove.append(egg)
            elif egg['y'] < -6:
                eggs_to_remove.append(egg)
        for e in eggs_to_remove: 
            if e in eggs: eggs.remove(e)

        # --- Bullet-chicken collisions ---
        bullets_to_remove = []
        for bullet in bullets:
            for ch in chickens:
                if ch['alive']:
                    # Calculate the actual position including offsets
                    actual_x = ch['base_x'] + (ch['offset_x'] if ch['arrived'] else 0)
                    actual_y = ch['base_y'] + (ch['offset_y'] if ch['arrived'] else 0)
                    
                    # Use actual position for collision detection
                    if abs(bullet["x"] - actual_x) < (bullet_width/2 + chicken_size/2) and abs(bullet["y"] - actual_y) < (bullet_height/2 + chicken_size/2):
                        bullets_to_remove.append(bullet)
                        ch['alive'] = False
                        break
        for b in bullets_to_remove:
            if b in bullets: bullets.remove(b)

        # --- Set last_chicken_time if all chickens dead ---
        if all(not c['alive'] for c in chickens) and last_chicken_time is None:
            last_chicken_time = pygame.time.get_ticks()

        # --- Check win/lose ---
        if check_win(last_chicken_time):
           show_message("YOU WIN")
           pygame.quit()
           quit()
    
        if lives <= 0:
           show_message("GAME OVER")
           pygame.quit()
           quit()

        # --- Draw everything ---
        draw_player(player_x,player_y)
        for bullet in bullets: draw_bullet(bullet)
        draw_hearts(lives,score)
        draw_score(score)
        for egg in eggs:
            color = {'black':(0,0,0),'white':(1,1,1),'gold':(1,0.84,0)}[egg['type']]
            draw_sphere(egg['x'],egg['y'],0,0.15,*color)

        pygame.display.flip()
        clock.tick(60)


main()