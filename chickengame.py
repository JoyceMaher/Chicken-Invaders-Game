import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math as mm
#ajhfjkahf





# -------------------------
# Draw player (Cylinder + Sphere + Window)
# -------------------------
def draw_player(speed, height, radius, x, y, z):
    glPushMatrix()

    # Move player to world position
    glTranslatef(x, y, z)

    # ============================
    # 1) Cylinder (aligned along +Y)
    # ============================
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()

    glPushMatrix()
    glRotatef(-90, 1, 0, 0)   # Cylinder → along +Y instead of +Z
    gluCylinder(quadric, radius, radius, height, 20, 20)
    glPopMatrix()

    # ============================
    # 2) Sphere على رأس السلندر
    # ============================
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()

    glPushMatrix()
    glTranslatef(0, height, 0)   # sphere فوق السلندر مباشرة
    gluSphere(quadric, radius, 20, 20)
    glPopMatrix()

    # ============================
    # 3) Window circle (Disk) على جسم السلندر
    # ============================
    glPushMatrix()

    window_radius = radius * 0.6        # حجم النافذة
    window_y = height * 0.5             # منتصف السلندر

    glTranslatef(0, window_y, radius + 0.001)   # على السطح الأمامي للسلندر
    glRotatef(0, 0, 0, 1)  # disk already faces +Z (perfect orientation)

    glColor3f(1, 1, 1)   # white window
    quad2 = gluNewQuadric()
    gluDisk(quad2, 0.0, window_radius, 32, 1)

    glPopMatrix()
    # ============================
    # True Half Triangle Wings (one full edge attached)
    # ============================

    wing_y = height * 0.5
    wing_out = radius * 2.0
    wing_up = radius * 1.2     # ارتفاع الرأس

    # -------- Right Wing --------
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)

    glBegin(GL_TRIANGLES)

    # ضلع كامل ملزق على السلندر
    glVertex3f(radius, -0.2, 0)     # النقطة السفلى على سطح السلندر
    glVertex3f(radius,  0.2, 0)     # النقطة العليا على سطح السلندر

    # رأس الجناح للخارج
    glVertex3f(radius + wing_out/2, 0, 0)

    glEnd()
    glPopMatrix()

    # -------- Left Wing --------
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)

    glBegin(GL_TRIANGLES)

    # ضلع كامل ملزق على السلندر
    glVertex3f(-radius, -0.2, 0)    # نقطة سفلية
    glVertex3f(-radius,  0.2, 0)    # نقطة علوية

    # الرأس للخارج
    glVertex3f(-(radius + wing_out/2), 0, 0)

    glEnd()
    glPopMatrix()



    glPopMatrix()




# -------------------------
# Main Loop
# -------------------------
def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, -1.0, -5)

    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


  

        glPushMatrix()
        glRotatef(angle, 0, 1, 0)  # Optional rotating view
        draw_player(0.3, 0.4, 0.1, 0, -0.8, 0)
        glPopMatrix()

        



        angle += 1
        pygame.display.flip()
        pygame.time.wait(10)
main()
