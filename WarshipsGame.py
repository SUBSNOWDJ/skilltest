from random import randint

print('------------------------------------------------')
print('        Приветствую в игре Морской Бой!         ')
print('------------------------------------------------')
print('              Игрок ходит первым:')
print('       Введите через пробел 2 координаты:')
print('         - номер строки и номер столбца.')
print('                    Начнем:')

#класс исключения при ошибочном вводе пользователя
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self): #Игрок стреляет за поле
        return 'Неверные координаты, повторите!'

class BoardUsedException(BoardException):
    def __str__(self): #Игрок стреляет туда, куда уже стрелял
        return 'Эта клетка уже была поражена!'

class BoardWrongShipException(BoardException):
    pass

class Board:
    def __init__(self, hid=False, size=6): #Класс игрового поля
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["О"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):  #Корабли на доске
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, sp=False): #Контур кораблей на поле
        n = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in n:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if sp:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  • 1 • 2 • 3 • 4 • 5 • 6 •"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "О")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, sp=True)
                    self.field[d.x][d.y] = "X"
                    print('Корабль потоплен!')
                    return True   #При попадании игрок продолжает стрелять
                else:
                    print('Есть пробитие!')
                    return True

        self.field[d.x][d.y] = "Т"
        print('Промах!')
        return False  #При промахе, ход переходит к другому игроку

    def begin(self):
        self.busy = []

class Game:  #установка основных параметров самой игры
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts_random = 0
        for L in lens:
            while True:
                attempts_random += 1
                if attempts_random > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), L, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def game(self):
        num = 0
        while True:
            print('-' * 27)
            print('Поле Человека:')
            print(self.us.board)
            print('-' * 27)
            print('Поле Компьютера:')
            print(self.ai.board)
            if num % 2 == 0:
                print('-' * 27)
                print('Ход человека - введите Строку и Столбец через пробел:')
                repeat = self.us.move()
            else:
                print('-' * 27)
                print('Ход Компьютера:  ')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('-' * 27)
                print('Человек победил!')
                print('Для новой игры нажмите зелёный треугольник вверху')
                break

            if self.us.board.count == 7:
                print('-' * 27)
                print('Компьютер победил!')
                print('Для новой игры нажмите зелёный треугольник вверху')
                break
            num += 1

    def start(self):
        self.game()

class Player:  #Основной класс игроков
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьюетра был такой: {d.x + 1} {d.y + 1}')
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print(' Пожалуйста, введите 2 числа! ')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(' Нет, нужны именно числа! ')
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

m = Game()
m.start()