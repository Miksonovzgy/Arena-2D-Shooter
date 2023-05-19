class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, group, shooter):
        super().__init__(group)
        self.position = pygame.math.Vector2()
        self.position.x = pos_x
        self.position.y = pos_y
        self.image_original = pygame.transform.scale(pygame.image.load('sprites/weapons/small_bullet2.png'), BULLET_SIZE)
        self.rect = self.image_original.get_rect(center = (pos_x, pos_y))
        self.bullet_speed = 40
        self.shooter = shooter

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.rect.centerx, -(mouse_y - self.rect.centery)
        angle = math.degrees(math.atan2(dy - pos_y, dx - pos_x)) - 90
        self.image = pygame.transform.rotate(self.image_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


        angle_to_move = math.atan2(mouse_y, mouse_x)
        self.dx = math.cos(angle_to_move) * self.bullet_speed
        self.dy = math.sin(angle_to_move) * self.bullet_speed

        print(f'Starting position: {self.rect.center}')

    def move(self):
        self.position.x += int(self.dx)
        self.position.y += int(self.dy)
        self.rect.center = self.position


class Weapon(pygame.sprite.Sprite): #IMPORTANT, write this thing in the brackets it is the inherentence thing you were talking about
    def __init__(self, pos, group):
        super().__init__(group) #IMPORTANT, RLY IMPORTANT without this line in the object, this implementation doesnt work
        self.image = pygame.image.load('sprites/weapons/pistol3.png')
        self.image_original = pygame.transform.scale(self.image, WEAPON_SIZE)
        self.rect = self.image.get_rect(center=pos)
        
    def rotateWeapon(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.rect.centerx, -(mouse_y - self.rect.centery)
        angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.image_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    


    def healthDisplay(self):
        healthText = get_font(30).render(f'Health:{self.health} ', True, "Red")
        healthRect = healthText.get_rect(center=(160,25))
        GAME_WINDOW.blit(healthText, healthRect)

    def ammoDisplay(self):
        ammoText = get_font(30).render(f'Ammo:{self.ammo} ', True, "White")
        ammoRect = ammoText.get_rect(center=(WIDTH - 0.1 * WIDTH, HEIGHT - 0.95 * HEIGHT))
        GAME_WINDOW.blit(ammoText, ammoRect)

    def checkIfShooting(self, events, spriteGroup):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and self.ammo > 0 and self.weapon:
                    bullet = Bullet(self.rect.centerx, self.rect.centery, spriteGroup, self.nickname)
                    BULLETS_ON_MAP.append(bullet)
                    OBJECTS.append(bullet)
                    self.ammo -= 1
                
    def checkForHits(self):
        for bullet in BULLETS_ON_MAP:
            if bullet.rect.colliderect(self.rect.centerx, self.rect.centery, self.rect.height, self.rect.width) and bullet.shooter != self.nickname:
                self.health -= 1
                BULLETS_ON_MAP.remove(bullet)
                OBJECTS.remove(bullet)
                del bullet
