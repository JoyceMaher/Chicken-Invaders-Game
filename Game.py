import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

glutInit()

# Player and Bullet properties / Saleh
player_x = 0
player_y = -5
player_z = 0
player_radius = 0.1
player_width = 1
player_height = 0.4
player_speed = 0.3
bullet_speed = 0.2
bullet_width = 0.1
bullet_height = 0.3

# Score properties / Jojo 
score = 0
score_for_extra_life = 100
lives = 3
max_lives = 5


# Omar functions
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

def setup_chicken_positions(chickens, n):
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    spacing_x = 12 / (cols - 1) if cols > 1 else 0
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
    return chickens

def update_chicken_movement(chickens, fixed_speed=0.08):
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
    return chickens

def draw_chickens(chickens):
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

def drop_eggs(chickens, eggs, start_time):
    current_time = time.time()
    for c in chickens:
        if c['alive'] and c['arrived'] and current_time - start_time >= c['drop_delay']:
            drop_interval = {'black':4,'white':3,'gold':5}[c['type']]
            if current_time - c['last_drop'] >= drop_interval:
                eggs.append({'x':c['base_x'],'y':c['base_y']-0.7,'type':c['type']})
                c['last_drop'] = current_time
    return eggs

def draw_eggs(eggs):
  
    for egg in eggs:
        color = {'black': (0,0,0), 'white': (1,1,1), 'gold': (1,0.84,0)}[egg['type']]
        draw_sphere(egg['x'], egg['y'], 0, 0.15, *color)


# Saleh functions
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

def draw_player(speed, height, radius, x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)   
    gluCylinder(quadric, radius, radius, height, 20, 20)
    glPopMatrix()
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(0, height, 0)   
    gluSphere(quadric, radius, 20, 20)
    glPopMatrix()
    glPushMatrix()
    window_radius = radius * 0.6     
    window_y = height * 0.5           
    glTranslatef(0, window_y, radius + 0.001) 
    glRotatef(0, 0, 0, 1) 
    glColor3f(1, 1, 1) 
    quad2 = gluNewQuadric()
    gluDisk(quad2, 0.0, window_radius, 32, 1)
    glPopMatrix()
    wing_y = height * 0.5
    wing_out = radius * 2.0
    wing_up = radius * 1.2   
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(radius, -0.2, 0)    
    glVertex3f(radius,  0.2, 0)   
    glVertex3f(radius + wing_out/2, 0, 0)
    glEnd()
    glPopMatrix()
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-radius, -0.2, 0)    
    glVertex3f(-radius,  0.2, 0)  
    glVertex3f(-(radius + wing_out/2), 0, 0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def draw_bullet(bullet):
    glColor3f(1, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glEnd()

def handle_player_input(can_shoot, bullets):
    keys = pygame.key.get_pressed()
    
    # Movement
    global player_x
    if keys[pygame.K_LEFT]: 
        player_x -= player_speed
    if keys[pygame.K_RIGHT]: 
        player_x += player_speed
    player_x = max(min(player_x, 7), -7)

    # Shooting
    if keys[pygame.K_SPACE] and can_shoot:
        bullets.append({"x": player_x, "y": player_y + player_height/2})
        can_shoot = False
    
    return can_shoot, bullets

def update_bullets(bullets):
    for bullet in bullets: 
        bullet["y"] += bullet_speed
    bullets = [b for b in bullets if b["y"] < 6]
    return bullets

def draw_bullets(bullets):
    for bullet in bullets: 
        draw_bullet(bullet)



# Jojo  functions
def draw_hearts(lives, score):
    rotation_angle = pygame.time.get_ticks() * 0.05
    total_hearts = min(max_lives, lives)
    
    for i in range(total_hearts):
        x = -2 + i * 0.6
        y = 4
        size = 0.35
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(rotation_angle, 0, 1, 0)
        glScalef(size, size, size)
        glColor3f(1, 0, 0)
        
        # Triangle part (bottom)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, -0.5, 0)
        glVertex3f(0.3, 0, 0)
        glVertex3f(-0.3, 0, 0)
        glEnd()
        
        # Left semicircle
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(-0.15, 0, 0)
        rad = 0.15
        for angle in range(0, 181, 5):
            glVertex3f(-0.15 + rad * math.cos(math.radians(angle)),
                       0 + rad * math.sin(math.radians(angle)), 0)
        glEnd()
        
        # Right semicircle
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.15, 0, 0)
        for angle in range(0, 181, 5):
            glVertex3f(0.15 + rad * math.cos(math.radians(angle)),
                       0 + rad * math.sin(math.radians(angle)), 0)
        glEnd()
        
        glPopMatrix()

def show_message(text):
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

def draw_score(score_value):
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1,1,0)
    glRasterPos3f(-4.8,4.8,-9.9)
    for ch in f"Score: {score_value}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopAttrib()

def update_eggs(eggs, chicken_size=0.5):
    eggs_to_remove = []
    global score, lives
    
    for egg in eggs:
        egg['y'] -= 0.1
        
        # Check collision with player
        if (abs(egg['x'] - player_x) < (chicken_size/2 + player_width/2) and 
            abs(egg['y'] - player_y) < (chicken_size/2 + player_height/2)):
            
            if egg['type'] == "white":
                score += 10
                extra_lives = min(score // score_for_extra_life, max_lives - 3)
                lives = max(lives, 3 + extra_lives)
            elif egg['type'] == "black":
                lives -= 1
            elif egg['type'] == "gold":
                score += 50
            eggs_to_remove.append(egg)
        elif egg['y'] < -6:  # Remove eggs that fall off screen
            eggs_to_remove.append(egg)
    
    # Remove collected/off-screen eggs
    for e in eggs_to_remove: 
        if e in eggs: 
            eggs.remove(e)
    return eggs

def check_bullet_chicken_collisions(bullets, chickens, chicken_size=0.5):
    
    bullets_to_remove = []
    
    for bullet in bullets:
        for ch in chickens:
            if ch['alive']:
                # Calculate actual chicken position
                actual_x = ch['base_x'] + (ch['offset_x'] if ch['arrived'] else 0)
                actual_y = ch['base_y'] + (ch['offset_y'] if ch['arrived'] else 0)
                
                # Check collision
                if (abs(bullet["x"] - actual_x) < (bullet_width/2 + chicken_size/2) and 
                    abs(bullet["y"] - actual_y) < (bullet_height/2 + chicken_size/2)):
                    bullets_to_remove.append(bullet)
                    ch['alive'] = False
                    break
    
    # Remove bullets that hit chickens
    for b in bullets_to_remove:
        if b in bullets: 
            bullets.remove(b)
    return bullets, chickens

def update_last_chicken_time(chickens, last_chicken_time):
    if all(not c['alive'] for c in chickens) and last_chicken_time is None:
        last_chicken_time = pygame.time.get_ticks()
    return last_chicken_time

def check_game_state(last_chicken_time):
    if check_win(last_chicken_time):
        show_message("YOU WIN")
        pygame.quit()
        quit()
    
    if lives <= 0:
        show_message("GAME OVER")
        pygame.quit()
        quit()

def initialize_game():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    glTranslatef(0, 0, -15)
    setup_lighting()
    return pygame.time.Clock()


def main():
    global player_x, lives, score
    clock = initialize_game()
    can_shoot = True
    last_chicken_time = None
    bullets = []
    eggs = []
    start_time = time.time()
    
    # Omar: Initialize chickens
    n = 15
    chickens = generate_chickens(n)
    chickens = setup_chicken_positions(chickens, n)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                can_shoot = True

        # Saleh: Handle player input and update bullets
        can_shoot, bullets = handle_player_input(can_shoot, bullets)
        bullets = update_bullets(bullets)
        
        # Clear screen
        glClearColor(0.2, 0.6, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
        # Jojo: Update game state and check collisions
        eggs = update_eggs(eggs)
        bullets, chickens = check_bullet_chicken_collisions(bullets, chickens)
        last_chicken_time = update_last_chicken_time(chickens, last_chicken_time)
        check_game_state(last_chicken_time)
        
        # Saleh 
        draw_player(player_speed,player_height,player_radius,player_x,player_y,player_z)               
        draw_bullets(bullets)         


        # Jojo 
        draw_hearts(lives, score)     
        draw_score(score)             

        # Omar
        draw_eggs(eggs)          
        chickens = update_chicken_movement(chickens)
        draw_chickens(chickens)
        eggs = drop_eggs(chickens, eggs, start_time)
        
        pygame.display.flip()
        clock.tick(60)


main()