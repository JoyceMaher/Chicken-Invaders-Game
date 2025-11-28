def game_over_screen(win=False):
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display)
    
    if win:
        pygame.display.set_caption("Chicken Invaders - You Win!")
        title_text = "YOU WIN!"
        title_color = (0, 255, 0)  # Green for win
    else:
        pygame.display.set_caption("Chicken Invaders - Game Over")
        title_text = "GAME OVER"
        title_color = (255, 0, 0)  # Red for loss

    try:
        # You can use the same background or a different one
        background_image = pygame.image.load(r"C:\Users\omarm\OneDrive\Desktop\222.jpg")
        background_image = pygame.transform.scale(background_image, display)
    except:
        print("Background image not found. Using black background.")
        background_image = None

    font_title = pygame.font.SysFont("Arial", 60, bold=True)
    font_option = pygame.font.SysFont("Arial", 30, bold=True)
    font_score = pygame.font.SysFont("Arial", 24)

    button_width = 250
    button_height = 60
    button_spacing = 20
    
    play_again_button = pygame.Rect((800 - button_width) // 2, 350, button_width, button_height)
    quit_button = pygame.Rect((800 - button_width) // 2, 350 + button_height + button_spacing, button_width, button_height)

    while True:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Draw title
        title_surface = font_title.render(title_text, True, title_color)
        screen.blit(title_surface, ((800 - title_surface.get_width()) // 2, 100))

        # Draw score
        score_surface = font_score.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_surface, ((800 - score_surface.get_width()) // 2, 180))

        mouse_pos = pygame.mouse.get_pos()
        
        # Play Again button
        play_again_hover = play_again_button.collidepoint(mouse_pos)
        pygame.draw