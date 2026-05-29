# main.py
import sys
import math
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
    QGraphicsPolygonItem, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QPushButton, QDialog, QStackedWidget
)
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF, QTimer

from game_logic import HexGameEngine, axial_distance
from ai_bot import HexAIBot

HEX_RADIUS = 35  
GAP = 2          
BOARD_SIZE = 4   

COLOR_EMPTY = "#FFFFFF"
COLOR_P1 = "#E74C3C"         # Красный (Игрок 1)
COLOR_P2 = "#3498DB"         # Синий (Игрок 2 / Бот)
COLOR_HIGHLIGHT_1 = "#2ECC71" 
COLOR_HIGHLIGHT_2 = "#9B59B6" 


class DifficultySelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.selected_difficulty = "Средний"
        
        window_body = QWidget(self)
        window_body.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                border: 2px solid #34495E;
                border-radius: 14px;
            }
        """)
        
        layout = QVBoxLayout(window_body)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)
        
        title = QLabel("Выберите сложность")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; border: none; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        btn_easy = QPushButton("Легкий")
        btn_easy.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_easy.setStyleSheet("background-color: #2ECC71; color: white; padding: 11px; border-radius: 6px; border: none;")
        btn_easy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_easy.clicked.connect(lambda: self.select_and_close("Легкий"))
        
        btn_medium = QPushButton("Средний")
        btn_medium.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_medium.setStyleSheet("background-color: #3498DB; color: white; padding: 11px; border-radius: 6px; border: none;")
        btn_medium.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_medium.clicked.connect(lambda: self.select_and_close("Средний"))
        
        btn_hard = QPushButton("Сложный")
        btn_hard.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_hard.setStyleSheet("background-color: #E74C3C; color: white; padding: 11px; border-radius: 6px; border: none;")
        btn_hard.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hard.clicked.connect(lambda: self.select_and_close("Сложный"))
        
        layout.addWidget(btn_easy)
        layout.addWidget(btn_medium)
        layout.addWidget(btn_hard)
        
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFont(QFont("Arial", 10))
        btn_cancel.setStyleSheet("background-color: #7F8C8D; color: white; padding: 8px; border-radius: 6px; border: none; margin-top: 5px;")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(window_body)
        self.setLayout(main_layout)
        
    def select_and_close(self, level):
        self.selected_difficulty = level
        self.accept()


class GameEndDialog(QDialog):
    def __init__(self, score1, score2, mode, parent=None):
        super().__init__(parent)
        self.setFixedWidth(420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.result_choice = "menu"
        
        window_body = QWidget(self)
        window_body.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
                border-radius: 12px;
            }
        """)
        
        main_layout = QVBoxLayout(window_body)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        title = QLabel("ИГРА ОКОНЧЕНА")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; letter-spacing: 1px; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p1_card = QWidget()
        p1_card.setFixedWidth(140)
        p1_card_layout = QVBoxLayout(p1_card)
        p1_card_layout.setContentsMargins(10, 15, 10, 15)
        p1_card_layout.setSpacing(5)
        
        p1_score = QLabel(str(score1))
        p1_score.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        p1_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p1_title = QLabel("КРАСНЫЕ")
        p1_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        p1_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p1_card_layout.addWidget(p1_score)
        p1_card_layout.addWidget(p1_title)
        
        colon_label = QLabel(":")
        colon_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        colon_label.setStyleSheet("color: #7F8C8D; padding-bottom: 20px; border: none;") 
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p2_card = QWidget()
        p2_card.setFixedWidth(140)
        p2_card_layout = QVBoxLayout(p2_card)
        p2_card_layout.setContentsMargins(10, 15, 10, 15)
        p2_card_layout.setSpacing(5)
        
        p2_score = QLabel(str(score2))
        p2_score.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        p2_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p2_name = "СИНИЕ" if mode == "PvP" else "РОБОТ"
        p2_title = QLabel(p2_name)
        p2_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        p2_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p2_card_layout.addWidget(p2_score)
        p2_card_layout.addWidget(p2_title)
        
        if score1 > score2:
            p1_card.setStyleSheet("background-color: #FDEDEC; border: none; border-radius: 8px;")
            p1_title.setStyleSheet(f"color: {COLOR_P1}; border: none;")
            p1_score.setStyleSheet(f"color: {COLOR_P1}; border: none;")
            
            p2_card.setStyleSheet("background-color: #F2F4F4; border: none; border-radius: 8px;")
            p2_title.setStyleSheet("color: #7F8C8D; border: none;")
            p2_score.setStyleSheet("color: #7F8C8D; border: none;")
        elif score2 > score1:
            p1_card.setStyleSheet("background-color: #F2F4F4; border: none; border-radius: 8px;")
            p1_title.setStyleSheet("color: #7F8C8D; border: none;")
            p1_score.setStyleSheet("color: #7F8C8D; border: none;")
            
            p2_card.setStyleSheet(f"background-color: #EBF5FB; border: none; border-radius: 8px;")
            p2_title.setStyleSheet(f"color: {COLOR_P2}; border: none;")
            p2_score.setStyleSheet(f"color: {COLOR_P2}; border: none;")
        else:
            p1_card.setStyleSheet("background-color: #FDEDEC; border: none; border-radius: 8px;")
            p1_title.setStyleSheet(f"color: {COLOR_P1}; border: none;")
            p1_score.setStyleSheet(f"color: {COLOR_P1}; border: none;")
            
            p2_card.setStyleSheet(f"background-color: #EBF5FB; border: none; border-radius: 8px;")
            p2_title.setStyleSheet(f"color: {COLOR_P2}; border: none;")
            p2_score.setStyleSheet(f"color: {COLOR_P2}; border: none;")
            
        cards_layout.addWidget(p1_card)
        cards_layout.addWidget(colon_label)
        cards_layout.addWidget(p2_card)
        main_layout.addLayout(cards_layout)
        
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_restart = QPushButton("Начать заново")
        btn_restart.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_restart.setStyleSheet("background-color: #E67E22; color: white; padding: 12px; border-radius: 6px; border: none;")
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restart.clicked.connect(self.select_restart)
        
        btn_menu = QPushButton("В главное меню")
        btn_menu.setFont(QFont("Arial", 11))
        btn_menu.setStyleSheet("background-color: #7F8C8D; color: white; padding: 12px; border-radius: 6px; border: none;")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self.select_menu)
        
        btn_layout.addWidget(btn_restart)
        btn_layout.addWidget(btn_menu)
        main_layout.addLayout(btn_layout)
        
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(window_body)
        self.setLayout(dialog_layout)
        
    def select_restart(self):
        self.result_choice = "restart"
        self.accept()
        
    def select_menu(self):
        self.result_choice = "menu"
        self.accept()


class HexCellGraphics(QGraphicsPolygonItem):
    def __init__(self, q, r, ui_parent):
        super().__init__()
        self.q = q  
        self.r = r  
        self.ui_parent = ui_parent
        self.is_selected = False
        self.highlight_mode = 0  

        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i)
            draw_radius = HEX_RADIUS - GAP
            points.append(QPointF(draw_radius * math.cos(angle_rad), draw_radius * math.sin(angle_rad)))
        
        self.setPolygon(QPolygonF(points))
        x = HEX_RADIUS * (3/2 * q)
        y = HEX_RADIUS * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        self.setPos(x, y)

    def update_visual(self, player_id):
        if player_id == 0:
            self.setBrush(QBrush(QColor(COLOR_EMPTY)))
        elif player_id == 1:
            self.setBrush(QBrush(QColor(COLOR_P1)))
        elif player_id == 2:
            self.setBrush(QBrush(QColor(COLOR_P2)))

        pen = QPen(QColor("#BDC3C7"), 1)
        
        if self.is_selected:
            pen = QPen(QColor("#2C3E50"), 3, Qt.PenStyle.DashLine)
        elif player_id == 0:
            if self.highlight_mode == 1:
                self.setBrush(QBrush(QColor(COLOR_HIGHLIGHT_1)))
                pen = QPen(QColor("#27AE60"), 2)
            elif self.highlight_mode == 2:
                self.setBrush(QBrush(QColor(COLOR_HIGHLIGHT_2)))
                pen = QPen(QColor("#8E44AD"), 2)

        self.setPen(pen)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.ui_parent.handle_cell_click(self)


class HexGridGameWidget(QWidget):
    def __init__(self, main_menu_callback, mode="PvP", difficulty="Средний"):
        super().__init__()
        self.main_menu_callback = main_menu_callback
        self.mode_backup = mode
        self.diff_backup = difficulty
        
        self.engine = HexGameEngine(BOARD_SIZE)
        self.engine.mode = mode
        self.engine.difficulty = difficulty
        self.engine.reset_board()

        self.selected_graphics = None
        self.graphics_cells = {}  

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.info_panel = QHBoxLayout()
        self.info_panel.setContentsMargins(5, 5, 5, 5)
        
        # Левая часть: Статус текущего хода
        left_container = QWidget()
        left_container.setFixedWidth(280)
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #FFFFFF;")
        self.update_status_text()
        left_layout.addWidget(self.status_label)
        
        # Центральная часть: Счёт матча (БЕЗ ФОНА И С ЦВЕТОМ ТЕКСТА ПО УМОЛЧАНИЮ)
        self.score_label = QLabel("Красные: 3  :  Синие: 3")
        self.score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.score_label.setStyleSheet("color: #FFFFFF; background: transparent; padding: 6px 0px;")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Правая часть: Кнопки действий
        right_container = QWidget()
        right_container.setFixedWidth(280)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("padding: 7px 15px; background-color: #2ECC71; color: white; border-radius: 5px; border: none;")
        self.btn_save.clicked.connect(self.save_game)

        self.btn_back = QPushButton("В меню")
        self.btn_back.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.setStyleSheet("padding: 7px 15px; background-color: #7F8C8D; color: white; border-radius: 5px; border: none;")
        self.btn_back.clicked.connect(self.main_menu_callback)
        
        right_layout.addWidget(self.btn_save)
        right_layout.addWidget(self.btn_back)

        # Компоновка инфо-панели с сохранением жесткого центрирования
        self.info_panel.addWidget(left_container)
        self.info_panel.addStretch()
        self.info_panel.addWidget(self.score_label)
        self.info_panel.addStretch()
        self.info_panel.addWidget(right_container)
        
        layout.addLayout(self.info_panel)

        # Поле игры
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background: #F8F9F9; border: 1px solid #DFE3E6; border-radius: 8px;")
        layout.addWidget(self.view)

        self.setLayout(layout)
        self.build_graphics_grid()

    def build_graphics_grid(self):
        self.scene.clear()
        self.graphics_cells.clear()
        for coords in self.engine.cells_data.keys():
            cell_gfx = HexCellGraphics(coords[0], coords[1], self)
            self.scene.addItem(cell_gfx)
            self.graphics_cells[coords] = cell_gfx
        self.sync_logic_to_visual()

    def restart_match(self):
        self.selected_graphics = None
        self.engine.mode = self.mode_backup
        self.engine.difficulty = self.diff_backup
        self.engine.reset_board()
        self.update_status_text()
        self.build_graphics_grid()

    def sync_logic_to_visual(self):
        for coords, cell_gfx in self.graphics_cells.items():
            player_id = self.engine.cells_data[coords]["player"]
            cell_gfx.update_visual(player_id)
        s1, s2 = self.engine.get_scores()
        p2_title = "Синие" if self.engine.mode == "PvP" else "Бот"
        self.score_label.setText(f"Красные: {s1}   •   {p2_title}: {s2}")

    def handle_cell_click(self, cell_gfx):
        if self.engine.mode == "PvE" and self.engine.current_player == 2:
            return  

        player_at_cell = self.engine.cells_data[(cell_gfx.q, cell_gfx.r)]["player"]

        if player_at_cell == self.engine.current_player:
            self.clear_highlights()
            if self.selected_graphics == cell_gfx:
                self.selected_graphics = None
            else:
                self.selected_graphics = cell_gfx
                cell_gfx.is_selected = True
                self.highlight_moves(cell_gfx.q, cell_gfx.r)
            self.sync_logic_to_visual()

        elif player_at_cell == 0 and cell_gfx.highlight_mode > 0:
            self.engine.move_piece(self.selected_graphics.q, self.selected_graphics.r, cell_gfx.q, cell_gfx.r)
            self.clear_highlights()
            self.selected_graphics = None
            self.sync_logic_to_visual()
            
            if not self.check_end_conditions():
                self.switch_player()
                if self.engine.mode == "PvE" and self.engine.current_player == 2:
                    QTimer.singleShot(500, self.trigger_ai)

    def highlight_moves(self, sq, sr):
        for coords, gfx in self.graphics_cells.items():
            if self.engine.cells_data[coords]["player"] == 0:
                dist = axial_distance(sq, sr, coords[0], coords[1])
                if dist == 1: gfx.highlight_mode = 1
                elif dist == 2: gfx.highlight_mode = 2

    def clear_highlights(self):
        for gfx in self.graphics_cells.values():
            gfx.is_selected = False
            gfx.highlight_mode = 0

    def switch_player(self):
        self.engine.current_player = 2 if self.engine.current_player == 1 else 1
        self.update_status_text()

    def update_status_text(self):
        name = "Игрок 1 (Красный)" if self.engine.current_player == 1 else ("Игрок 2 (Синий)" if self.engine.mode == "PvP" else "Компьютер (Синий)")
        self.status_label.setText(f"Ход: {name}")

    def trigger_ai(self):
        bot = HexAIBot(self.engine.difficulty)
        decision = bot.calculate_best_move(self.engine.cells_data)
        if decision:
            from_coords, to_coords = decision
            self.engine.move_piece(from_coords[0], from_coords[1], to_coords[0], to_coords[1])
            self.sync_logic_to_visual()
            if not self.check_end_conditions():
                self.switch_player()
        else:
            self.check_end_conditions()

    def check_end_conditions(self):
        s1, s2 = self.engine.get_scores()
        empty_exists = any(c["player"] == 0 for c in self.engine.cells_data.values())
        
        if s1 == 0 or s2 == 0 or not empty_exists or not self.engine.has_valid_moves(self.engine.current_player):
            if os.path.exists("savegame.json"): 
                os.remove("savegame.json")
            
            dialog = GameEndDialog(s1, s2, self.engine.mode, self)
            dialog.exec()
            
            if dialog.result_choice == "restart":
                self.restart_match()
            else:
                self.main_menu_callback()
            return True
        return False

    def save_game(self):
        self.engine.save_to_json()


class MainMenuWidget(QWidget):
    def __init__(self, start_callback, load_callback):
        super().__init__()
        self.start_callback = start_callback
        self.load_callback = load_callback
        self.current_mode = "PvP"  
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("HEXXAGON")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.btn_start = QPushButton("Начать игру")
        self.btn_start.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_start.setStyleSheet("background-color: #E67E22; color: white; padding: 12px; border-radius: 5px;")
        self.btn_start.setFixedWidth(270) 
        self.btn_start.clicked.connect(self.handle_start_click)
        layout.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_mode_toggle = QPushButton("Режим: Против игрока")
        self.btn_mode_toggle.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_mode_toggle.setStyleSheet("background-color: #3498DB; color: white; padding: 12px; border-radius: 5px;")
        self.btn_mode_toggle.setFixedWidth(270) 
        self.btn_mode_toggle.clicked.connect(self.toggle_mode)
        layout.addWidget(self.btn_mode_toggle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_load = QPushButton("Загрузить партию")
        self.btn_load.setFont(QFont("Arial", 11))
        self.btn_load.setStyleSheet("background-color: #2ECC71; color: white; padding: 10px; border-radius: 5px;")
        self.btn_load.setFixedWidth(270) 
        self.btn_load.clicked.connect(self.load_callback)
        layout.addWidget(self.btn_load, alignment=Qt.AlignmentFlag.AlignCenter)
        
        if not os.path.exists("savegame.json"):
            self.btn_load.setEnabled(False)
            self.btn_load.setStyleSheet("background-color: #BDC3C7; color: white; padding: 10px; border-radius: 5px;")

        self.btn_exit = QPushButton("Выход")
        self.btn_exit.setFont(QFont("Arial", 11))
        self.btn_exit.setStyleSheet("background-color: #95A5A6; color: white; padding: 10px; border-radius: 5px;")
        self.btn_exit.setFixedWidth(270) 
        self.btn_exit.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def toggle_mode(self):
        if self.current_mode == "PvP":
            self.current_mode = "PvE"
            self.btn_mode_toggle.setText("Режим: Против ИИ")
            self.btn_mode_toggle.setStyleSheet("background-color: #9B59B6; color: white; padding: 12px; border-radius: 5px;")
        else:
            self.current_mode = "PvP"
            self.btn_mode_toggle.setText("Режим: Против игрока")
            self.btn_mode_toggle.setStyleSheet("background-color: #3498DB; color: white; padding: 12px; border-radius: 5px;")

    def handle_start_click(self):
        if self.current_mode == "PvP":
            self.start_callback("PvP", "Средний")
        else:
            dialog = DifficultySelectionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.start_callback("PvE", dialog.selected_difficulty)


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hexxagon Desktop System")
        self.setMinimumSize(950, 720)
        self.stacked = QStackedWidget()
        self.central_widget = QWidget()
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked)
        
        self.setCentralWidget(self.central_widget)
        self.show_menu()

    def show_menu(self):
        self.menu = MainMenuWidget(self.start_new_game, self.load_game)
        self.stacked.addWidget(self.menu)
        self.stacked.setCurrentWidget(self.menu)

    def start_new_game(self, mode, difficulty):
        self.game = HexGridGameWidget(self.show_menu, mode, difficulty)
        self.stacked.addWidget(self.game)
        self.stacked.setCurrentWidget(self.game)

    def load_game(self):
        self.game = HexGridGameWidget(self.show_menu)
        if self.game.engine.load_from_json():
            self.game.sync_logic_to_visual()
            self.stacked.addWidget(self.game)
            self.stacked.setCurrentWidget(self.game)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplicationWindow()
    window.show()
    sys.exit(app.exec())