# Save highscore: https://www.youtube.com/watch?v=MFv1Ew_nGG0

from pygame import * 
from os.path import * 
import sys

# Choice: Selects a random item from a List (Randomize scoring    ): https://pynative.com/python-random-choice/
from random import choice

# pygame fonts: https://nerdparadise.com/programming/pygame/part5
# pygame fonts: https://pythonprogramming.altervista.org/pygame-4-fonts/

# Set path variables
# https://www.geeksforgeeks.org/python-os-path-abspath-method-with-example/
MIN_WIDTH = 800
MIN_HEIGHT = 600
STARTING_PATH = abspath(dirname(__file__))
FONT = STARTING_PATH + '/fonts/VT323.ttf'
IMAGE_PATH = STARTING_PATH + "/img/"
INSTRUCTOR_POSITION = 65
INSTRUCTOR_MOVE_DOWN = 35
DEFAULT_MOVE_SPEED = 5
SHIELD_BOUND_LEFT = 10 
SHIELD_BOUND_RIGHT = 740
SCREEN_SIZE = display.set_mode((MIN_WIDTH, MIN_HEIGHT)) # W x H

# Set style variables: Colors
WHITE_TEXT = (245, 245, 245)
RED_TEXT = (225, 0, 0)
BLUE_SCORING = (0, 188, 245)
GREEN_SCORING = (12, 215, 73)
PINK_SCORING = (245, 0, 220)

# Set image variables
IMAGE_NAMES = ["blue_explode", "green_explode", "pink_explode", "shield", "john", "instructor1.1", "instructor1.2",  "instructor2.1", "instructor2.2", "instructor3.1", "instructor3.2","blue_explode", "green_explode", "pink_explode", "corndog", "dry_erase_marker"]

# Map image (all must be .png files)
IMAGE = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha() 
          for name in IMAGE_NAMES}


################GAME DESIGN################

class Game_Text_Format(object):
    def __init__(self, textFont, size, message, color, x_position, y_position):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(x_position, y_position))
    
    # Pygame Draw Docs: http://www.pygame.org/docs/ref/draw.html
    def draw(self, surface):
        surface.blit(self.surface, self.rect)



################PLAYER SPRITES################

# Sprite Docs: https://www.pygame.org/docs/ref/sprite.html
# PyGame.Surface requires rect: https://pygame.readthedocs.io/en/latest/rect/rect.html
class Shield(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGE['shield']
        self.rect = self.image.get_rect(topleft=(400, 550)) #R/L (1/2 width), HEIGHT
        self.shield_speed = DEFAULT_MOVE_SPEED

    def update(self, user_keyboard_move, *args):
        if user_keyboard_move[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.shield_speed
        if user_keyboard_move[K_RIGHT] and self.rect.x < 740 :
            self.rect.x += self.shield_speed
        # Update shield placement & 'refresh' screen
        # blit() = Block Transfer
        game.screen.blit(self.image, self.rect)



class Instructor(sprite.Sprite):
    def __init__(self, row, column, idx=0):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.idx = idx
        self.images = []
        self.show_img()
        self.image = self.images[self.idx]
        self.rect = self.image.get_rect()

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

    def show_img(self):
        images = {0: ['1.2', '1.1'],
                  1: ['2.2', '2.1'],
                  2: ['2.2', '2.1'],
                  3: ['3.1', '3.2'],
                  4: ['3.1', '3.2'],
                  }
        img_one, img_two = (IMAGE['instructor{}'.format(img_num)] for img_num in
                      images[self.row])
        self.images.append(transform.scale(img_one, (37, 42)))
        self.images.append(transform.scale(img_two, (37, 42)))

    def animate_img(self):
        self.idx += 1
        if self.idx >= len(self.images):
            self.idx = 0
        self.image = self.images[self.idx] 

    
#Pygame Time docs (Do NOT import time): https://www.pygame.org/docs/ref/time.html
class Just_John(sprite.Sprite):
    def __init__(self, row=5, move_speed=20000, direction=1):
        sprite.Sprite.__init__(self)
        self.image = IMAGE['john']
        self.image = transform.scale(self.image, (90, 50))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = row
        self.move_speed = move_speed
        self.direction = direction
        self.timer = time.get_ticks()

    def update(self, keys, current_time, *args):
        reset_flag = False
        passed_time = current_time - self.timer
        if passed_time > self.move_speed:
            if self.rect.x < 840 and self.direction == 1:
                self.rect.x += 3
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.rect.x -= 3
                game.screen.blit(self.image, self.rect)
        if self.rect.x > 830:
            self.direction = -1
            reset_flag = True
        if self.rect.x < -90:
            self.direction = 1
            reset_flag = True
        if passed_time > self.move_speed and reset_flag:
            self.timer = current_time

################SPRITE GROUP################
class EducationTeam(sprite.Group):
    def __init__(self, columns, rows, total_left_moves=30, left_move_update=0, left_columns=0, total_right_moves=30,right_move_update=0, move_speed=600, move_number=15, direction=1, ):
        sprite.Group.__init__(self)
        self.columns = columns
        self.rows = rows
        self.column_list = list(range(columns))
        self.right_columns = columns - 1
        self.left_columns = left_columns
        self.direction = direction
        self.total_left_moves = total_right_moves
        self.left_move_update = left_move_update
        self.total_right_moves = total_right_moves
        self.right_move_update = right_move_update
        self.move_speed = move_speed
        self.move_number = move_number
        self.instructors = [[None] * columns for _ in range(rows)]
        self.timer = time.get_ticks()
        self.bottom = game.instructor_position + ((rows - 1) * 44) + 34

    def update(self, current_time):
        reset_flag = False
        if current_time - self.timer > self.move_speed:
            if self.direction == 1:
                move = self.total_right_moves + self.right_move_update
            else:
                move = self.total_left_moves + self.left_move_update

            if self.move_number >= move:
                self.move_number = 0
                self.bottom = 0
                self.direction *= -1
                self.total_left_moves = 30 + self.right_move_update
                self.total_right_moves = 30 + self.left_move_update
                for instructor in self:
                    instructor.rect.y += INSTRUCTOR_MOVE_DOWN
                    instructor.animate_img()
                    if self.bottom < instructor.rect.y + 35:
                        self.bottom = instructor.rect.y + 35
            else:
                if self.direction == 1:
                    speed = 10
                else: 
                    speed = -10

                # velocity = 10 if self.direction == 1 else -10
                for instructor in self:
                    instructor.rect.x += speed
                    instructor.animate_img()
                self.move_number += 1

            self.timer += self.move_speed

    def random_bottom(self):
        column = choice(self.column_list)
        instructor_column = (self.instructors[row - 1][column]
                       for row in range(self.rows, 0, -1))
        # print("instructor_column", instructor_column)
        return next((ch for ch in instructor_column if ch is not None), None)

    #Add-internal storage: https://gamedev.stackexchange.com/questions/169142/pygame-error-attributeerror-pygame-surface-object-has-no-attribute-add-inter
    def add_internal(self, *sprites):
        super(EducationTeam, self).add_internal(*sprites)
        for i in sprites:
            self.instructors[i.row][i.column] = i

    def remove_internal(self, *sprites):
        super(EducationTeam, self).remove_internal(*sprites)
        for i in sprites:
            self.kill(i)
        self.change_speed_helper()

    def column_dead_helper(self, column):
        return not any(self.instructors[row][column] for row in range(self.rows))


    def change_speed_helper(self):
        if len(self) == 1:
            self.move_speed = 200
        elif len(self) <= 10:
            self.move_speed = 400

    def kill(self, instructor):
        self.instructors[instructor.row][instructor.column] = None
        column_dead_helper = self.column_dead_helper(instructor.column)
        if column_dead_helper:
            self.column_list.remove(instructor.column)
        if instructor.column == self.right_columns:

            while self.right_columns > 0 and column_dead_helper:
                self.right_columns -= 1
                column_dead_helper = self.column_dead_helper(self.right_columns)
                self.right_move_update += 5

        elif instructor.column == self.left_columns:
            while self.left_columns < self.columns and column_dead_helper:
                self.left_columns += 1
                self.left_move_update += 5
                column_dead_helper = self.column_dead_helper(self.left_columns)

################SPRITE ACTIONS################
class Lives(sprite.Sprite):
    def __init__(self, x_position, y_position, img=IMAGE['shield']):
        sprite.Sprite.__init__(self)
        self.img = img
        self.img = transform.scale(self.img, (22, 22))
        self.rect = self.img.get_rect(topleft=(x_position, y_position))

    def update(self, *args):
        game.screen.blit(self.img, self.rect)
        
class Shoot_Laser(sprite.Sprite):
    def __init__(self, x_position, y_position, direction, speed, img_name="corndog", side="center"):
        sprite.Sprite.__init__(self)
        self.image = IMAGE[img_name]
        self.rect = self.image.get_rect(topleft=(x_position, y_position))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.img_name = img_name

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        # Get rid of 'lasers' when off screen
        if self.rect.y > 600 or self.rect.y < 15:
            self.kill()

class BadaBingBadaBoom(sprite.Sprite):
    def __init__(self, instructor, *groups):
        super(BadaBingBadaBoom, self).__init__(*groups)
        self.image = transform.scale(self.get_image(instructor.row), (37, 42))
        self.image_two = transform.scale(self.get_image(instructor.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(instructor.rect.x, instructor.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        reset_flag = False
        passed_time = current_time - self.timer
        if passed_time <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed_time <= 200:
            game.screen.blit(self.image_two, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed_time:
            self.kill()

    def get_image(self, row):
        img_colors = ['pink', 'blue', 'blue', 'green', 'green']
        return IMAGE['{}_explode'.format(img_colors[row])]

# Explode class kills/resets a round   
class InstructorExplode(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(InstructorExplode, self).__init__(*groups)
        self.image = IMAGE['shield']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        reset_flag = False
        passed_time = current_time - self.timer
        if 300 < passed_time <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed_time:
            self.kill()

class JohnExplode(sprite.Sprite):
    def __init__(self, mystery, rand_score, *groups):
        super(JohnExplode, self).__init__(*groups)
        self.text = Game_Text_Format(FONT, 20, str(rand_score), WHITE_TEXT, mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        reset_flag = False
        passed_time = current_time - self.timer
        if passed_time <= 200 or 400 < passed_time <= 600:
            self.text.draw(game.screen)
        elif 600 < passed_time:
            self.kill()

            
################GAME LOGIC################


class CodeCreeps():
    def __init__(self, start_game=False, main_screen=True, game_over=False):
        init()
        self.clock = time.Clock()
        self.screen = SCREEN_SIZE
        self.instructor_position = INSTRUCTOR_POSITION
        self.start_game = start_game
        self.main_screen = main_screen
        self.game_over = game_over
        self.caption = display.set_caption('Code Creepers')
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        
        # Position Life Counters
        self.life_one = Lives(715, 3)
        self.life_two = Lives(742, 3)
        self.life_three = Lives(769, 3)
        self.life_group = sprite.Group(self.life_one, self.life_two, self.life_three)

        #Format Text
        self.title_text = Game_Text_Format(FONT, 50, 'Code Creepers', WHITE_TEXT, 164, 155)
        self.title_subtext = Game_Text_Format(FONT, 25, 'Press any key to continue', WHITE_TEXT, 201, 225)
        self.text_game_over = Game_Text_Format(FONT, 50, 'Game Over', RED_TEXT, 250, 270)
        self.text_next_round = Game_Text_Format(FONT, 50, 'Next Round', GREEN_SCORING, 240, 270)
        self.text_instructor_one = Game_Text_Format(FONT, 25, '   =  10  pts', GREEN_SCORING, 368, 270)
        self.text_instructor_two = Game_Text_Format(FONT, 25, '   =  20 pts', BLUE_SCORING, 368, 320)
        self.text_instructor_three = Game_Text_Format(FONT, 25, '   =  30 pts', PINK_SCORING, 368, 370)
        self.text_instructor_four = Game_Text_Format(FONT, 25, '   =  ?????', RED_TEXT, 368, 420)
        self.text_score = Game_Text_Format(FONT, 20, 'Score', WHITE_TEXT, 5, 5)
        self.text_lives = Game_Text_Format(FONT, 20, 'Lives ', WHITE_TEXT, 640, 5)


    def game_logic(self):
        while True:
            if self.main_screen:
                self.screen.blit(self.background, (0, 0))
                self.title_text.draw(self.screen)
                self.title_subtext.draw(self.screen)
                self.text_instructor_one.draw(self.screen)
                self.text_instructor_two.draw(self.screen)
                self.text_instructor_three.draw(self.screen)
                self.text_instructor_four.draw(self.screen)
                self.opening_menu_helper()
                for e in event.get():
                    if self.exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        self.life_group.add(self.life_one, self.life_two, self.life_three)
                        self.reset(0)
                        self.start_game = True
                        self.main_screen = False

            elif self.start_game:
                if not self.instructors and not self.explosions_activate:
                    current_time = time.get_ticks()
                    if current_time - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.text_score_two = Game_Text_Format(FONT, 20, str(self.score), WHITE_TEXT, 85, 5)
                        self.text_score.draw(self.screen)
                        self.text_score_two.draw(self.screen)
                        self.text_next_round.draw(self.screen)
                        self.text_lives.draw(self.screen)
                        self.life_group.update()
                        self.user_input_handler()
                    if current_time - self.gameTimer > 3000:
                        self.instructor_position += INSTRUCTOR_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    current_time = time.get_ticks()
                    self.screen.blit(self.background, (0, 0))
                    self.text_score_two = Game_Text_Format(FONT, 20, str(self.score), WHITE_TEXT, 85, 5)
                    self.text_score.draw(self.screen)
                    self.text_score_two.draw(self.screen)
                    self.text_lives.draw(self.screen)
                    self.user_input_handler()
                    self.instructors.update(current_time)
                    self.all_sprite.update(self.keys, current_time)
                    self.explosions_activate.update(current_time)
                    self.collision_helper()
                    self.instructor_helper(self.new_instructor_flag, current_time)
                    self.instructor_lasers()

            elif self.game_over:
                current_time = time.get_ticks()
                self.instructor_position = INSTRUCTOR_POSITION
                self.game_over_helper(current_time)

            display.update()
            self.clock.tick(60)

    
    def keep_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }
        score = scores[row]
        self.score += score
        return score

    def instructor_generator(self):
        instructors = EducationTeam(10, 5) # C x R
        for row in range(5):
            for column in range(10):
                instructor = Instructor(row, column)
                instructor.rect.x = 157 + (column * 50)
                instructor.rect.y = self.instructor_position + (row * 45)
                instructors.add(instructor)
        self.instructors = instructors

    def instructor_lasers(self):
        if (time.get_ticks() - self.timer) > 700 and self.instructors:
            instructor = self.instructors.random_bottom()
            self.inst.add(Shoot_Laser(instructor.rect.x + 14, instructor.rect.y + 20, 1, 5, 'dry_erase_marker', 'center'))
            self.all_sprite.add(self.inst)
            self.timer = time.get_ticks()


    #################HELPER FUNCTIONS#################
    def opening_menu_helper(self):
        self.instructor_one = IMAGE['instructor3.1']
        self.instructor_one = transform.scale(self.instructor_one, (36, 45))
        self.instructor_two = IMAGE['instructor2.2']
        self.instructor_two = transform.scale(self.instructor_two, (36, 45))
        self.instructor_three = IMAGE['instructor1.2']
        self.instructor_three = transform.scale(self.instructor_three, (36, 45))
        self.instructor_four = IMAGE['john']
        self.instructor_four = transform.scale(self.instructor_four, (85, 50))
        self.screen.blit(self.instructor_one, (318, 270))
        self.screen.blit(self.instructor_two, (318, 320))
        self.screen.blit(self.instructor_three, (318, 370))
        self.screen.blit(self.instructor_four, (299, 420))
    
    def user_input_handler(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.lasers) == 0 and self.active_sprite_flag:
                        if self.score < 1000:
                            single_laser = Shoot_Laser(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, 'corndog', 'center')
                            self.lasers.add(single_laser)
                            self.all_sprite.add(self.lasers)
                        else:
                            double_laser_left = Shoot_Laser(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, 'corndog', 'left')
                            double_laser_right = Shoot_Laser(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, 'corndog', 'right')
                            self.lasers.add(double_laser_left)
                            self.lasers.add(double_laser_right)
                            self.all_sprite.add(self.lasers)
    
    def collision_helper(self):
        sprite.groupcollide(self.lasers, self.inst, True, True)
        for instructor in sprite.groupcollide(self.instructors, self.lasers, True, True).keys():
            self.keep_score(instructor.row)
            BadaBingBadaBoom(instructor, self.explosions_activate)
            self.gameTimer = time.get_ticks()
        for mystery in sprite.groupcollide(self.john_group, self.lasers, True, True).keys():
            score = self.keep_score(mystery.row)
            JohnExplode(mystery, score, self.explosions_activate)
            new_john_who_dis = Just_John()
            self.all_sprite.add(new_john_who_dis)
            self.john_group.add(new_john_who_dis)
        for player in sprite.groupcollide(self.player_group, self.inst, True, True).keys():
            if self.life_three.alive():
                self.life_three.kill()
            elif self.life_two.alive():
                self.life_two.kill()
            elif self.life_one.alive():
                self.life_one.kill()
            else:
                self.game_over = True
                self.start_game = False
            InstructorExplode(player, self.explosions_activate)
            self.new_instructor_flag = True
            self.sprite_timer = time.get_ticks()
            self.active_sprite_flag = False
        if self.instructors.bottom >= 540:
            sprite.groupcollide(self.instructors, self.player_group, True, True)
            if not self.player.alive() or self.instructors.bottom >= 600:
                self.game_over = True
                self.start_game = False


    def instructor_helper(self, ta, current_time):
        if ta and (current_time - self.sprite_timer > 900):
            reset_flag = False
            self.player = Shield()
            self.all_sprite.add(self.player)
            self.player_group.add(self.player)
            self.new_instructor_flag = False
            self.active_sprite_flag = True

    def game_over_helper(self, current_time):
        self.screen.blit(self.background, (0, 0))
        reset_flag = False
        passed_time = current_time - self.timer
        if passed_time < 750:
            self.text_game_over.draw(self.screen)
        elif 750 < passed_time < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed_time < 2250:
            self.text_game_over.draw(self.screen)
        elif 2250 < passed_time < 2750:
            self.screen.blit(self.background, (0, 0))
        elif passed_time > 3000:
            self.main_screen = True

        for e in event.get():
            if self.exit(e):
                sys.exit()

    def exit(self, event):
        return event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE)

    def reset(self, score):
        time_helper = time.get_ticks()
        self.player = Shield()
        self.john_avatar = Just_John()
        self.instructor_generator()
        self.score = score

        self.player_group = sprite.Group(self.player)
        self.john_group = sprite.Group(self.john_avatar)
        self.explosions_activate = sprite.Group()
        self.lasers = sprite.Group()
        self.inst = sprite.Group()
        self.all_sprite = sprite.Group(self.player, self.instructors, self.life_group, self.john_avatar)
        self.keys = key.get_pressed()

        self.timer = time_helper
        self.noteTimer = time_helper
        self.sprite_timer = time_helper
        self.new_instructor_flag = False
        self.active_sprite_flag = True


if __name__ == '__main__':
    game = CodeCreeps()
    game.game_logic()