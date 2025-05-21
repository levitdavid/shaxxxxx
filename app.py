
class Piece:
    def __init__(self, color: str, symbol: str, name: str):
        self.color = color
        self.symbol = symbol
        self.name = name

    def is_valid_move(self, board: 'Board', start: tuple, end: tuple) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        dr, dc = end_row - start_row, end_col - start_col

        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False
        target = board.grid[end_row][end_col]# Фигура, стоящая на конечной позиции.
        if target and target.color == self.color:# нет такого же цвета
            return False

        if self.name == "pawn":
            direction = 1 if self.color == "white" else -1
            if dc == 0 and dr == -direction and not target:# пешка двигается на одну или пусто
                return True
            if abs(dc) == 1 and dr == -direction and target:# пешка бьет если стоит противник
                return True
        elif self.name == "rook":
            return (dr == 0 or dc == 0) and board.is_path_clear(start, end)
        elif self.name == "knight":
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]
        elif self.name == "bishop":
            return abs(dr) == abs(dc) and board.is_path_clear(start, end)
        elif self.name == "queen":
            return (abs(dr) == abs(dc) or dr == 0 or dc == 0) and board.is_path_clear(start, end)
        elif self.name == "king":
            return max(abs(dr), abs(dc)) <= 1
        return False

    def get_valid_moves(self, board: 'Board', start: tuple) -> list[tuple]:
        """Возвращает список всех допустимых ходов для фигуры."""
        moves = []
        for row in range(8):#Цикл по строкам доски (от 0 до 7).
            for col in range(8):#Цикл по столбцам доски (от 0 до 7).
                if self.is_valid_move(board, start, (row, col)):
                    moves.append((row, col))
        return moves


class Archer(Piece):
    def __init__(self, color: str):
        super().__init__(color, "A" if color == "black" else "a", "archer")

    def is_valid_move(self, board: 'Board', start: tuple, end: tuple) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        dr, dc = abs(end_row - start_row), abs(end_col - start_col)
        # Проверка границ доски
        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False
        # Проверка на занятость клетки своей фигурой
        target = board.grid[end_row][end_col]
        if target and target.color == self.color:
            return False

        if dr == dc and 1 <= dr <= 2:
            if not target and board.is_path_clear(start, end):
                return True  # Обычное движение
            if target and dr == 2 and board.is_path_clear(start, end):
                return True  # "Выстрел" на 2 клетки
        return False


class Wizard(Piece):
    def __init__(self, color: str):
        super().__init__(color, "W" if color == "black" else "w", "wizard")

    def is_valid_move(self, board: 'Board', start: tuple, end: tuple) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        dr, dc = abs(end_row - start_row), abs(end_col - start_col)

        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False
        target = board.grid[end_row][end_col]
        if target and target.color == self.color:
            return False

        if max(dr, dc) == 2 and not target:
            return True  # переход на пустую клетку
        return False


class Catapult(Piece):
    def __init__(self, color: str):
        super().__init__(color, "C" if color == "black" else "c", "catapult")#Возвращает временный объект родительского класса (Piece), который позволяет вызвать его методы.


    def is_valid_move(self, board: 'Board', start: tuple, end: tuple) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        dr, dc = end_row - start_row, end_col - start_col

        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False
        target = board.grid[end_row][end_col]
        if target and target.color == self.color:
            return False

        if dr == 0 or dc == 0:
            step_r = 1 if dr > 0 else -1 if dr < 0 else 0
            step_c = 1 if dc > 0 else -1 if dc < 0 else 0
            r, c = start_row + step_r, start_col + step_c
            jumped = False
            while (r, c) != (end_row, end_col):
                if board.grid[r][c]:
                    if jumped:
                        return False
                    jumped = True
                r, c = r + step_r, c + step_c
            return jumped  # Обязателен прыжок через одну фигуру
        return False


class Move:
    def __init__(self, start: tuple, end: tuple, piece: 'Piece', captured: 'Piece'):
        self.start = start
        self.end = end
        self.piece = piece
        self.captured = captured


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.move_count = 0
        self.setup_pieces()

    def setup_pieces(self):
        self.grid[7] = [
            Piece("white", "r", "rook"), Archer("white"), Wizard("white"),
            Piece("white", "q", "queen"), Piece("white", "k", "king"),
            Catapult("white"), Archer("white"), Piece("white", "r", "rook")
        ]
        for col in range(8):
            self.grid[6][col] = Piece("white", "p", "pawn")
        self.grid[0] = [
            Piece("black", "R", "rook"), Archer("black"), Wizard("black"),
            Piece("black", "Q", "queen"), Piece("black", "K", "king"),
            Catapult("black"), Archer("black"), Piece("black", "R", "rook")
        ]
        for col in range(8):
            self.grid[1][col] = Piece("black", "P", "pawn")

    def display(self, highlight_moves=None, highlight_threats=None):
        print("\n  a b c d e f g h")
        for i in range(8):
            row = f"{8 - i} "
            for j in range(8):
                piece = self.grid[i][j]
                symbol = piece.symbol if piece else "."
                if highlight_moves and (i, j) in highlight_moves:
                    symbol = f"[{symbol}]"  # Подсветка доступных ходов
                elif highlight_threats and (i, j) in highlight_threats:
                    symbol = f"*{symbol}*"  # Подсветка угрожаемых фигур
                row += symbol + " "
            print(row + f"{8 - i}")
        print("  a b c d e f g h\n")

    def is_path_clear(self, start: tuple, end: tuple) -> bool:
        start_row, start_col = start #Извлекаются строки и столбцы начальной позиции.
        end_row, end_col = end
        dr = -1 if start_row > end_row else 1 if start_row < end_row else 0
        dc = -1 if start_col > end_col else 1 if start_col < end_col else 0
        row, col = start_row + dr, start_col + dc

        while (row, col) != (end_row, end_col):#Проверяет каждую клетку
            if self.grid[row][col]:#стоит фигура
                return False
            row, col = row + dr, col + dc
        return True

    def move(self, start: tuple, end: tuple) -> tuple[bool, 'Piece']:
        start_row, start_col = start
        end_row, end_col = end

        if not (0 <= start_row < 8 and 0 <= start_col < 8 and
                0 <= end_row < 8 and 0 <= end_col < 8):
            return False, None

        piece = self.grid[start_row][start_col]
        if not piece or not piece.is_valid_move(self, start, end):
            return False, None

        captured = self.grid[end_row][end_col]#Если на конечной позиции стоит фигура, она будет захвачена.
        self.grid[end_row][end_col] = piece#Фигура перемещается с начальной позиции на конечную.
        self.grid[start_row][start_col] = None#освобождается
        self.move_count += 1
        return True, captured


class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"
        self.move_history = []

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white" #меняет ход

    def get_position(self, prompt: str) -> tuple:
        while True:
            pos = input(prompt)
            if pos == "undo":
                return ("undo", None)
            if pos == "hint":
                return ("hint", None)
            if pos == "threat":
                return ("threat", None)
            if len(pos) != 2 or pos[0] not in "abcdefgh" or pos[1] not in "12345678":
                print("Неверный формат. Введите 'a2', 'undo', 'hint' или 'threat'")
                continue
            col = ord(pos[0]) - 97
            row = 8 - int(pos[1])
            return (row, col)

    def undo_move(self, steps: int = 1):
        steps = min(steps, len(self.move_history))
        for _ in range(steps):
            if not self.move_history:
                break
            move = self.move_history.pop()
            self.board.grid[move.start[0]][move.start[1]] = move.piece
            self.board.grid[move.end[0]][move.end[1]] = move.captured
            self.board.move_count -= 1
            self.switch_turn()
        if steps > 0:
            print(f"Откат выполнен на {steps} ход(ов) назад.")

    def show_move_hints(self, start: tuple):
        piece = self.board.grid[start[0]][start[1]]
        if not piece or piece.color != self.current_turn:
            print("Неверный выбор фигуры для подсказки")
            return
        valid_moves = piece.get_valid_moves(self.board, start)#допустимых ходов
        self.board.display(highlight_moves=valid_moves)
        print("Доступные ходы подсвечены в скобках [ ].")

    def show_threatened_pieces(self):
        threatened = []
        king_in_check = False
        opponent_color = "black" if self.current_turn == "white" else "white"

        # Проверяем все фигуры противника
        for row in range(8):#Индекс строки
            for col in range(8):# Индекс столбца
                piece = self.board.grid[row][col]
                if piece and piece.color == opponent_color:
                    moves = piece.get_valid_moves(self.board, (row, col))#допустимые ходы для фигуры
                    for move in moves:
                        target = self.board.grid[move[0]][move[1]]
                        if target and target.color == self.current_turn:# игрок пр
                            threatened.append(move)
                            if target.name == "king":
                                king_in_check = True

        self.board.display(highlight_threats=threatened)
        print("Угрожаемые фигуры подсвечены звёздочками * *.")
        if king_in_check:
            print("Внимание: король под шахом!")
        elif threatened:
            print(f"Угрожаемых фигур: {len(threatened)}")
        else:
            print("Нет угрожаемых фигур.")

    def play(self):
        while True:
            self.board.display()
            print(f"Ход {self.board.move_count + 1}. Ходят {self.current_turn}")

            start_input = self.get_position(f"Выберите фигуру ({self.current_turn}) или 'undo'/'hint'/'threat': ")
            if start_input[0] == "undo":
                try:
                    steps = int(input("Введите количество ходов для отката (1 или больше): "))
                    if steps <= 0:
                        print("Количество ходов должно быть положительным.")
                        continue
                    self.undo_move(steps)
                except ValueError:
                    print("Введите корректное число.")
                continue
            elif start_input[0] == "hint":
                start = self.get_position(f"Выберите фигуру для подсказки хода ({self.current_turn}): ")
                self.show_move_hints(start)
                continue
            elif start_input[0] == "threat":
                self.show_threatened_pieces()
                continue

            start = start_input
            piece = self.board.grid[start[0]][start[1]]

            if not piece or piece.color != self.current_turn:#Проверяет, что на выбранной клетке есть фигура.
                print("Неверный выбор фигуры")
                continue

            end = self.get_position("Выберите клетку назначения: ")

            success, captured = self.board.move(start, end)
            if success:
                self.move_history.append(Move(start, end, piece, captured))
                print(f"Ход выполнен: {chr(start[1] + 97)}{8 - start[0]} -> {chr(end[1] + 97)}{8 - end[0]}")
                self.switch_turn()
            else:
                print("Недопустимый ход")


if __name__ == "__main__":
    game = ChessGame()
    game.play()
