from random import randrange, choice # generate and place new tile
from collections import defaultdict
import msvcrt
import os


actions_num = [ord(ch) for ch in 'WASDRQwasdrq']
command = ['Up', 'Left', 'Down', 'Right', 'Reset', 'Quit']
actions = dict(zip(actions_num, command * 2))


def transpose(field):
    return [list(row) for row in zip(*field)]


def invert(field):
    return [row[::-1] for row in field]


def getUserAction():
    char = 'N'
    while char not in actions_num:
        Char = msvcrt.getch()
    return actions[char]


class GameField(object):
    def __init__(self, width = 4, height = 4, winScore = 2048):
        self.width = width
        self.height = height
        self.winScore = winScore
        self.legend = 0
        self.score = 0
        self.reset()

    def reset(self):
        if self.score > self.legend:
            self.legend = self.score
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.score = 0
        self.spawn()
        self.spawn()

    def spawn(self):
        element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = element

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))
        check = {}
        check['Left'] = lambda field :\
            any(row_is_left_movable(row) for row in field)
        check['Up'] = lambda field:\
            check['Left'](transpose(field))
        check['Down'] = lambda field :\
            check['Right'](transpose(field))
        check['Right'] = lambda field :\
            check['Left'](invert(field))
        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def is_win(self):
        return any(any(i >= self.winScore for i in row) for row in self.field)

    def is_over(self):
        return not any(self.move_is_possible(i) for i in command)

    def move(self, direction):
        def moveLeft(row):
            def tighten(row): # squeese non-zero elements together
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                new_row = []
                pair = False
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))
        check = {}
        check['Left'] = lambda field:\
            [moveLeft(row) for row in field]
        check['Right'] = lambda field:\
            invert(check['Left'](invert(field)))
        check['Up'] = lambda field:\
            transpose(check['Left'](transpose(field)))
        check['Down'] = lambda field:\
            transpose(check['Right'](transpose(field)))
        if direction in command:
            if self.move_is_possible(direction):
                self.field = check[direction](self.field)
                self.spawn()
                return True
        return False
    def draw(self):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            print(string + '\n')

        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, "counter"):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1

        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        issssssss = os.system('cls')
        cast('SCORE: ' + str(self.score))
        if 0 != self.legend:
            cast('HGHSCORE: ' + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_over():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)


if __name__ == '__main__':
    def init():
        game_field.reset()
        return 'Game'

    def not_game(state):
        game_field.draw()
        action = getUserAction()
        responses = defaultdict(lambda: state) #默认是当前状态，没有行为就会一直在当前界面循环
        responses['Restart'], responses['Exit'] = 'Init', 'Exit' #对应不同的行为转换到不同的状态
        return responses[action]

    def game():

        game_field.draw()

        action = getUserAction()

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action): # move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_over():
                return 'Gameover'
        return 'Game'


    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
        }

    game_field = GameField()

    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()
