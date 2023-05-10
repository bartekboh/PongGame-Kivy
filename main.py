import random

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader as SL

Builder.load_file("menu.kv")


class Boost(Widget):
    pos_x = NumericProperty(-100)
    pos_y = NumericProperty(-100)


class Player1(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            vel = Vector(-1 * vx, vy)
            ball.velocity = vel.x, vel.y + offset


class Player2(Widget):
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.sound = SL.load("ping-pong-ball.mp3")

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            try:
                self.sound.play()
            except:
                pass

            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            vel = Vector(-1 * vx, vy)
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.max_velocity_x = 12

    def move(self):
        if self.velocity_x >= self.max_velocity_x:
            self.velocity_x = self.max_velocity_x

        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    menu_widget = ObjectProperty()
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    boost = ObjectProperty()

    pressed_keys = {
        'w': False,
        's': False,
        'up': False,
        'down': False
    }

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)

        self.refresh_rate = 90

        self.menu_state = True
        self.game_over_state = False
        self.game_over_score = 10

        self.stars_count = random.randrange(30, 60)
        self.stars_list = []
        self.init_star()

        self.boost_timer = 0

        self.paddle_speed = 6

        self.avaiable_boosts = ["ball_speed", "paddle_size", "ball_size", "gravity"]

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / self.refresh_rate)

    def _keyboard_closed (self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down (self, keyboard, keycode, text, modifiers):
        #pressed_key = self._keyboard.keycode_to_string(keycode) # this does not work somehow
        pressed_key = keycode[1]
        print('You pressed the key', pressed_key, '.', sep=' ', end='\n')

        self.pressed_keys[pressed_key] = True

        if pressed_key == 'escape':
            print("ESC")
            self.change_menu_state()
        

        return True

    def _on_keyboard_up (self, keyboard, keycode):
        released_key = keycode[1]
        print('You released the key', released_key, '.', sep=' ', end='\n')
        self.pressed_keys[released_key] = False
        return True

    def on_size(self, *args):
        self.update_star()

    def init_star(self, *kwargs):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.stars_count):
                self.stars_list.append(Line())

    def update_star(self):
        for i in range(self.stars_count):
            x = random.randrange(0, 100)
            y = random.randrange(0, 100)
            w = float(random.randrange(5, 20))
            star_x = self.width/100*x
            star_y = self.height/100*y
            star_w = w/10

            if self.height * 0.9 < star_y:
                star_y = star_y * 0.5

            self.stars_list[i].points = [star_x, star_y, star_x, star_y]
            self.stars_list[i].width = star_w

    # BOOSTS
    def on_ball_speed_boost(self):
        self.ball.velocity_x *= 1.1

    def on_gravity(self):
        # for red
        self.ball.velocity_x += 0.1

        # for blue
        self.ball.velocity_x -= 0.1

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):

        

        if self.pressed_keys == 'escape':
            print("ESC")

        if self.game_over_state or self.menu_state:
            self.serve_ball(vel=(0, 0))
            # self.game_over_screen
            self.player1.center_y = self.height * 0.9 / 2
            self.player2.center_y = self.height * 0.9 / 2

            if self.game_over_state:
                print("GAME OVER")
                self.change_menu_state()

            if self.menu_state:
                pass

        else:
            self.ball.move()

            if self.boost_timer > 0:
                self.boost_timer -= dt
                print(self.boost_timer)
            
            else:
                self.remove_boost_widget()

            if random.randrange(200) == 5 and self.boost_timer == 0:
                self.boost_timer = random.randrange(20,60)
                self.boost.pos_x = random.randrange(int(self.width))
                self.boost.pos_y = random.randrange(int(self.height * 0.8))

            # bounce of paddles
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

            # bounce ball off bottom or top
            if (self.ball.y < self.y * 0.9) or (self.ball.top > self.top * 0.9):
                self.ball.velocity_y *= -1

            # went of to a side to score point?
            if self.ball.x < self.x:
                self.player2.score += 1
                if self.player2.score == self.game_over_score:
                    self.game_over_state = True
                else:
                    self.serve_ball(vel=(4, 0))
            if self.ball.right > self.width:
                self.player1.score += 1
                if self.player1.score == self.game_over_score:
                    self.game_over_state = True
                else:
                    self.serve_ball(vel=(4, 0))
                self.serve_ball(vel=(-4, 0))


            # Movements on buttons
            if self.pressed_keys['w']:
                if self.player1.center_y + self.paddle_speed < self.height * 0.9 - self.player1.height/2:
                    self.player1.y += self.paddle_speed
                elif self.player1.center_y + 1 < self.height * 0.9 - self.player1.height/2:
                    self.player1.y += 1
                    

            if self.pressed_keys['s']:
                if self.player1.center_y - self.paddle_speed > 0 + self.player1.height/2:
                    self.player1.y -= self.paddle_speed
                elif self.player1.center_y - 1 < 0 - self.player1.height/2:
                    self.player1.y -= 1

            if self.pressed_keys['up']:
                if self.player2.center_y + self.paddle_speed < self.height * 0.9 - self.player2.height/2:
                    self.player2.y += self.paddle_speed
                elif self.player2.center_y + 1 < self.height * 0.9 - self.player2.height/2:
                    self.player2.y += 1

            if self.pressed_keys['down']:
                if self.player2.center_y - self.paddle_speed > 0 + self.player2.height/2:
                    self.player2.y -= self.paddle_speed
                elif self.player2.center_y - 1 < 0 - self.player2.height/2:
                    self.player2.y -= 1

    def remove_boost_widget(self):
        self.boost_timer = 0
        self.boost.x = -100
        self.boost.y = -100

        return self.boost, self.boost_timer

    def restart_game(self):
        self.player1.score = 0
        self.player2.score = 0
        self.remove_boost_widget()
        self.serve_ball(vel=(0,4))
        self.change_menu_state()
        self.update_star()
        
    def on_menu_button_press(self):
        self.menu_widget.opacity = 0
        self.menu_state = False
        print("Closing the menu")
        print(self.menu_widget)

    def on_menu_open(self):
        self.menu_widget.opacity = 1
        self.menu_state = True
        print("Opening the Menu")
        print(self.menu_widget)

    def change_menu_state(self):
        if self.menu_widget.opacity == 0:
            self.menu_state = True
            self.menu_widget.opacity = 1
            print("Opening Menu")
        elif self.menu_widget.opacity == 1:
            self.menu_state = False
            self.menu_widget.opacity = 0
            print("Closing Menu")
            self.serve_ball(vel=(4,0))

        return

    def close_window(self):
        Window.close()


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()

        return game


if __name__ == '__main__':
    PongApp().run()