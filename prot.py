import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPolygonItem, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF

# --- Константы стиля и геометрии ---
HEX_RADIUS = 40  # Расстояние от центра до вершины
# Внутренний радиус (апофема) для расчета позиций
HEX_WIDTH = HEX_RADIUS * math.sqrt(3) 
HEX_HEIGHT = HEX_RADIUS * 2
GAP = 2          # Визуальный отступ между ячейками

BOARD_SIZE = 3   # Сколько "колец" вокруг центра. Всего ячеек: 3*n^2 + 3*n + 1

COLOR_EMPTY = "#ffffff"
COLOR_P1 = "#000000"   # Красный
COLOR_P2 = "#808080"   # Синий
COLOR_SELECTED = "#000000" # Желтый для выделения

# --- Класс ячейки-шестиугольника ---
class HexCell(QGraphicsPolygonItem):
    def __init__(self, q, r, game_logic):
        super().__init__()
        self.q = q  # Осевая координата Q
        self.r = r  # Осевая координата R
        self.game_logic = game_logic
        self.player = 0  # 0: пусто, 1: P1, 2: P2
        self.is_selected = False

        # 1. Генерируем геометрию шестиугольника (flat-topped)
        points = []
        for i in range(6):
            # Угол 0, 60, 120... градусов. 0 градусов - это вершина справа.
            angle_rad = math.radians(60 * i)
            # Применяем GAP (отступ), немного уменьшая радиус при отрисовке
            draw_radius = HEX_RADIUS - GAP
            px = draw_radius * math.cos(angle_rad)
            py = draw_radius * math.sin(angle_rad)
            points.append(QPointF(px, py))
        
        self.setPolygon(QPolygonF(points))

        # 2. Устанавливаем позицию на сцене (конвертация axial -> pixel)
        # Используем формулу для flat-topped hex grid
        x = HEX_RADIUS * (3/2 * q)
        y = HEX_RADIUS * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        self.setPos(x, y)

        # 3. Базовая отрисовка
        self.update_visual()
        self.setAcceptHoverEvents(True) # Для будущих эффектов при наведении

    def update_visual(self):
        """Обновляет цвет заливки и обводки в зависимости от состояния."""
        # Устанавливаем цвет игрока
        if self.player == 0:
            self.setBrush(QBrush(QColor(COLOR_EMPTY)))
        elif self.player == 1:
            self.setBrush(QBrush(QColor(COLOR_P1)))
        elif self.player == 2:
            self.setBrush(QBrush(QColor(COLOR_P2)))

        # Устанавливаем обводку (толстая желтая, если выбрана)
        if self.is_selected:
            self.setPen(QPen(QColor(COLOR_SELECTED), 4, Qt.PenStyle.SolidLine))
            self.setZValue(1) # Поверх других
        else:
            self.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            self.setZValue(0)

    def mousePressEvent(self, event):
        """Обработка клика по шестиугольнику."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.game_logic.handle_cell_click(self)

# --- Основное окно игры ---
class HexxagonGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hexxagon PyQt6")
        
        # Основной виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # UI элементы
        self.status_label = QLabel("Ход Игрока 1 (Красный)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Графическая сцена
        self.scene = QGraphicsScene()
        # self.scene.setBackgroundBrush(QBrush(QColor("#2c3e50"))) # Темный фон
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.view)

        # Игровая логика
        self.cells = {}
        self.selected_cell = None
        self.current_player = 1
        self.game_over = False
        
        self.setup_board()
        
        # Центрируем камеру на поле и задаем размер окна
        self.view.centerOn(0, 0)
        self.resize(800, 700)

    def setup_board(self):
        """Генерирует гексагональное поле."""
        self.scene.clear()
        self.cells = {}

        # Генерация координат в радиусе BOARD_SIZE
        for q in range(-BOARD_SIZE, BOARD_SIZE + 1):
            r1 = max(-BOARD_SIZE, -q - BOARD_SIZE)
            r2 = min(BOARD_SIZE, -q + BOARD_SIZE)
            for r in range(r1, r2 + 1):
                cell = HexCell(q, r, self)
                self.scene.addItem(cell)
                self.cells[(q, r)] = cell

        # Расстановка начальных фишек (по углам)
        # Углы для радиуса N: (N, 0), (0, N), (-N, N), (-N, 0), (0, -N), (N, -N)
        N = BOARD_SIZE
        # P1 (Красный)
        self.set_player(N, -N, 1)
        self.set_player(-N, 0, 1)
        self.set_player(0, N, 1)
        # P2 (Синий)
        self.set_player(N, 0, 2)
        self.set_player(0, -N, 2)
        self.set_player(-N, N, 2)

    def set_player(self, q, r, player_id):
        if (q, r) in self.cells:
            self.cells[(q, r)].player = player_id
            self.cells[(q, r)].update_visual()

    # --- Математика гексагонов ---
    def get_hex_dist(self, c1, c2):
        """Возвращает расстояние между двумя ячейками."""
        return (abs(c1.q - c2.q) + abs(c1.q + c1.r - c2.q - c2.r) + abs(c1.r - c2.r)) / 2

    def get_neighbors(self, cell):
        """Возвращает список существующих соседних ячеек (расстояние 1)."""
        neighbor_coords = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in neighbor_coords:
            coord = (cell.q + dq, cell.r + dr)
            if coord in self.cells:
                neighbors.append(self.cells[coord])
        return neighbors

    # --- Игровая логика ---
    def handle_cell_click(self, clicked_cell):
        if self.game_over: return

        # Ситуация 1: Клик по своей фишке -> Выделение
        if clicked_cell.player == self.current_player:
            # Снимаем старое выделение
            if self.selected_cell:
                self.selected_cell.is_selected = False
                self.selected_cell.update_visual()
            
            # Устанавливаем новое
            self.selected_cell = clicked_cell
            clicked_cell.is_selected = True
            clicked_cell.update_visual()

        # Ситуация 2: Клик по пустой клетке, когда кто-то выбран -> Ход
        elif clicked_cell.player == 0 and self.selected_cell:
            dist = self.get_hex_dist(self.selected_cell, clicked_cell)

            if dist <= 2.1: # 2.1 чтобы избежать проблем с плавающей точкой
                move_valid = False
                
                if dist < 1.5: # Расстояние 1 -> Клонирование
                    clicked_cell.player = self.current_player
                    move_valid = True
                elif dist < 2.5: # Расстояние 2 -> Прыжок
                    clicked_cell.player = self.current_player
                    self.selected_cell.player = 0
                    self.selected_cell.update_color() # Рендерим старую пустой
                    self.selected_cell.update_visual()
                    move_valid = True
                
                if move_valid:
                    # 1. Снимаем выделение
                    self.selected_cell.is_selected = False
                    self.selected_cell.update_visual()
                    self.selected_cell = None

                    # 2. Логика захвата соседей
                    captured_something = self.capture_enemy_neighbors(clicked_cell)
                    
                    # 3. Обновляем вид походившей клетки
                    clicked_cell.update_visual()
                    
                    # 4. Передаем ход
                    self.next_turn()

    def capture_enemy_neighbors(self, cell):
        """Захватывает вражеские фишки вокруг указанной ячейки."""
        neighbors = self.get_neighbors(cell)
        enemy_id = 2 if self.current_player == 1 else 1
        captured = False
        for nb in neighbors:
            if nb.player == enemy_id:
                nb.player = self.current_player
                nb.update_visual()
                captured = True
        return captured

    def next_turn(self):
        # Подсчет очков и проверка конца игры перед сменой игрока
        s1, s2 = self.get_scores()
        
        # Проверка: есть ли пустые клетки
        empty_cells = any(c.player == 0 for c in self.cells.values())
        
        # Проверка: есть ли фишки у обоих игроков
        p1_exists = s1 > 0
        p2_exists = s2 > 0

        if not empty_cells or not p1_exists or not p2_exists:
            self.end_game(s1, s2)
            return

        # Смена игрока
        self.current_player = 2 if self.current_player == 1 else 1
        p_name = "Игрок 1 (Красный)" if self.current_player == 1 else "Игрок 2 (Синий)"
        self.status_label.setText(f"Ход: {p_name}")

    def get_scores(self):
        p1 = sum(1 for c in self.cells.values() if c.player == 1)
        p2 = sum(1 for c in self.cells.values() if c.player == 2)
        return p1, p2

    def end_game(self, s1, s2):
        self.game_over = True
        result = "Ничья!"
        if s1 > s2: result = "Победа КРАСНОГО!"
        elif s2 > s1: result = "Победа СИНЕГО!"
        
        self.status_label.setText(f"ИГРА ОКОНЧЕНА! {s1}:{s2} - {result}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HexxagonGame()
    window.show()
    sys.exit(app.exec())