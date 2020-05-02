import pyxel
import collections
import random


class PipeArray:
    """
        Class for handling pipes obstacles

    Attributes:
        pipe_x_distance (int): Distance in pixels between pipes
        pipe_h_distance (int): Gap between upper and lower pipe
        n_pipes (int): Pipe buffer size
        space_height (int): Distance in pixels between ground and upper screen corner
        min_pipe_height (int): Minimal height of pipe
        ground_level (int): Ground screen position
    """

    def __init__(self, pipe_x_distance=50, pipe_h_distance=30, n_pipes=5, space_height=128-32, min_pipe_height=20,
                 ground_level=105):
        self.pipe_x_distance = pipe_x_distance
        self.pipe_h_distance = pipe_h_distance
        self.n_pipes = n_pipes
        self.space_height = space_height
        self.min_height = min_pipe_height
        self.max_height = space_height - pipe_h_distance - self.min_height
        self.ground_level = ground_level

        self.last_pipe_x = 30  # First pipe x-position
        self.pipes_deque = collections.deque(maxlen=n_pipes)  # Pipe buffer container

        for i in range(n_pipes - 1):
            self.spawn_pipe()

    def spawn_pipe(self):
        # Spawn pipe procedure. Distance between pipes always
        pipe_x = self.last_pipe_x + self.pipe_x_distance
        self.pipes_deque.append((pipe_x, random.randint(self.min_height, self.max_height)))
        self.last_pipe_x += self.pipe_x_distance

    def draw_pipe(self, x, h, type='bottom'):
        """
        Single pipe drawing on screen procedure.

        Arguments:
            x (int): Pipe x-position
            h (int): Height of pipe
            type (str): Bottom or upper pipe
        """
        assert type in ['bottom', 'upper']

        if type == 'upper':
            n = (h-10) // 16
            for i in range(n):
                pyxel.blt(x=x, y=i*16, img=1, u=0, v=0, w=18, h=16)

            if (h-10) % 16 != 0:
                pyxel.blt(x=x, y=n * 16, img=1, u=0, v=0, w=18, h=(h-10) % 16)

            pyxel.blt(x=x-1, y=h-10, img=1, u=23, v=0, w=20, h=10)
        elif type == 'bottom':
            n = (h - 10) // 16
            rem = (h-10) % 16
            for i in range(n):
                pyxel.blt(x=x, y=self.ground_level - (i+1) * 16, img=1, u=0, v=0, w=18, h=16)

            if (h - 10) % 16 != 0:
                pyxel.blt(x=x, y=self.ground_level - n * 16 - rem, img=1, u=0, v=0, w=18, h=(h - 10) % 16)

            pyxel.blt(x=x - 1, y=self.ground_level - (n+1) * 16 - rem + 9, img=1, u=23, v=11, w=20, h=10)
        else:
            raise ValueError('Not supported pipe type:' + str(type))

    def draw(self, tick):
        """
        Draw all buffered pipes according to current timestamp
        """
        for x, h in list(self.pipes_deque):
            self.draw_pipe(x - tick, h, type='upper')
            self.draw_pipe(x - tick, self.space_height - h - self.pipe_h_distance, type='bottom')

    def check_update_score(self, tick, bird_x):
        """
        Check, if a new obstacle is passed. If obstacle is passed we should update player score.
        """
        for x, h in list(self.pipes_deque):
            if x - tick == bird_x:
                return True
        return False

    @staticmethod
    def square_collision(sq1, sq2):
        """
        Method for detecting square collisions
        """
        l1 = [sq1[0], sq1[1]]
        r1 = [sq1[0] + sq1[2], sq1[1] + sq1[3]]
        l2 = [sq2[0], sq2[1]]
        r2 = [sq2[0] + sq2[2], sq2[1] + sq2[3]]

        if l1[0] >= r2[0] or l2[0] >= r1[0]:
            return False

        if l1[1] >= r2[1] or l2[1] >= r1[1]:
            return False

        return True

    def check_collisions(self, tick, bird_position, bird_w, bird_h):
        birb_square = (bird_position[0], bird_position[1], bird_w, bird_h)

        for x, h in list(self.pipes_deque):
            sq1 = (x - tick, 0, 18, h)
            sq2 = (x - tick, self.ground_level - (self.space_height - h - self.pipe_h_distance)+5, 18, self.space_height - h - self.pipe_h_distance-1)

            if self.square_collision(birb_square, sq1):
                return True

            if self.square_collision(birb_square, sq2):
                return True

        return False

    def update(self, tick):
        # If enough time is passed, then spawn new pipe
        if (tick + 50) % self.pipe_x_distance == 0:
            self.spawn_pipe()
