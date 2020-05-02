import argparse
import os
import pyxel

import pipe_level

WIDTH = 196
HEIGHT = 128
GROUND_LEVEL = 105
BIRD_X = 32
POS_MIN = 0
POS_MAX = GROUND_LEVEL - 13
VELOCITY_UP = 5
GRAVITY = 0.2


class FlappyGame:
    def __init__(self, args):
        pyxel.init(width=WIDTH, height=HEIGHT, caption="Flappy BioBirb", fps=30)
        pyxel.load(os.path.abspath('assets.pyxres'))
        self.args = args
        self.velocity_up = args.velocity_up
        self.gravity_val = args.gravity

        self.tick = None
        self.score = None
        self.velocity = None
        self.bird_position = None
        self.gameover = None
        self.pipe_arr = None
        self.active = None

        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.active = True
        self.gameover = False
        self.tick = 0  # Current timestamp
        self.score = 0  # Achieved score
        self.velocity = 0  # Current bird velocity in y direction
        self.bird_position = 50  # Current bird y position
        self.pipe_arr = pipe_level.PipeArray()  # Class for handling obstacle pipes

    def update(self):
        if self.gameover:
            # If game is already over, check if restart key is pressed
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()

        if not self.active:
            return

        self.tick += 1  # Increase current timestamp
        # Recompute bird position, limit position by top of screen and ground
        self.bird_position = min(max(self.bird_position + self.velocity, POS_MIN), POS_MAX)
        # Update pipes (spawn a new one possibly)
        self.pipe_arr.update(self.tick)
        # Check, if bird is passed a new obstacle
        self.score += self.pipe_arr.check_update_score(self.tick, BIRD_X)

        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP):
            self.velocity -= self.velocity_up
        self.velocity += self.gravity_val

        # If any collision with obstacles is detected, then game is over. Birb died :`(
        if self.pipe_arr.check_collisions(self.tick, (BIRD_X, self.bird_position), 18, 13):
            self.active = False
            self.gameover = True

    def draw(self):
        if self.gameover:
            self.draw_gameover()
        else:
            self.draw_game()

    def draw_game(self):
        # Background color
        pyxel.cls(12)

        # Tile ground with grass
        for i in range(WIDTH // 32 + 1):
            pyxel.blt(x=32 * i - (self.tick % 32), y=GROUND_LEVEL, img=0, u=0, v=0, w=32, h=32)

        score_str = 'Score: {}'.format(self.score)
        # Draw obstacles
        self.pipe_arr.draw(self.tick)
        # Draw bird asset
        if not self.gameover:
            pyxel.blt(x=32, y=self.bird_position, img=0, u=0, v=40, w=18, h=13, colkey=0)
        else:
            pyxel.blt(x=32, y=self.bird_position, img=0, u=0, v=56, w=18, h=13, colkey=0)
        pyxel.text(x=WIDTH - len(score_str) * 4 - 5, y=8, s=score_str, col=0)

    def draw_gameover(self):
        self.draw_game()
        pyxel.blt((WIDTH - 8 * 8) // 2, (HEIGHT - 8) // 2, img=2, u=0,v=0, w=8*8, h=8)
        restart_s = 'Press R to restart'
        pyxel.text((WIDTH - len(restart_s) * 4) // 2, (HEIGHT - 8)//2 - 8, s=restart_s, col=pyxel.frame_count % 16)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gravity', type=float, default=0.2, help='Acceleration value of gravity. Default: 0.2')
    parser.add_argument('--velocity-up', type=float, default=5,
                        help='Acceleration of bird when key is pressed. Default: 5')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    game = FlappyGame(args)

