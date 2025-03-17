from PyQt5.QtWidgets import (
    QApplication, QLabel, QDialog, QDialogButtonBox,QTextEdit,QComboBox, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import sys
import cv2
import pytesseract
import os
import pandas as pd
from difflib import get_close_matches
import json 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = '--psm 6 --oem 3 -l tel'

base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
previewfiles_folder = os.path.join(base_dir, 'previewfiles')
csv_path = os.path.join(base_dir, 'book_meta_data.csv')


def detect_cameras(max_cameras=5):
    available_cameras = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

class CameraSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Camera")
        self.layout = QVBoxLayout()
        self.combo_box = QComboBox()
        cameras = detect_cameras()

        if cameras:
            for cam in cameras:
                self.combo_box.addItem(f"Camera {cam}", cam)
        else:
            self.combo_box.addItem("No Cameras Found", -1)

        self.layout.addWidget(QLabel("Choose a camera:"))
        self.layout.addWidget(self.combo_box)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_selected_camera(self):
        return self.combo_box.currentData() if self.combo_box.currentData() != -1 else None


class BookDetectorApp(QWidget):
    def __init__(self):
        super().__init__()

        dialog = CameraSelectionDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.selected_camera = dialog.get_selected_camera()
            if self.selected_camera is None:
                print("No camera selected. Exiting...")
                sys.exit()
        else:
            print("Camera selection canceled. Exiting...")
            sys.exit()

        self.initUI()
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.df = self.load_or_create_csv()

    def initUI(self):
        self.setWindowTitle("Book Detector")
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.text_edit = QTextEdit(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        capture_button = QPushButton("Capture and Process", self)
        capture_button.clicked.connect(self.process_frame)
        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.search_matches)
        quit_button = QPushButton("Quit", self)
        quit_button.clicked.connect(self.close)

        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_label)

        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Detected Text:"))
        text_layout.addWidget(self.text_edit)
        text_layout.addWidget(search_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(capture_button)
        button_layout.addWidget(quit_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(video_layout)
        main_layout.addLayout(text_layout)

        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        final_layout.addWidget(QLabel("Matches:"))
        final_layout.addWidget(self.scroll_area)
        final_layout.addLayout(button_layout)

        self.setLayout(final_layout)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qimg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def process_frame(self):
        ret, frame = self.cap.read()
        if ret:
            detected_text = pytesseract.image_to_string(frame, config=custom_config).strip()
            self.text_edit.setText(detected_text)
            self.display_matches(detected_text)

    def search_matches(self):
        detected_text = self.text_edit.toPlainText()
        self.display_matches(detected_text)

    # def load_or_create_csv(self):
    #     if os.path.exists(csv_path):
    #         return pd.read_csv(csv_path, encoding="utf-8", dtype=str)
    #     else:
    #         data = []
    #         with os.scandir(previewfiles_folder) as entries:
    #             for entry in entries:
    #                 if entry.is_file():
    #                     filename = entry.name
    #                     filepath = os.path.join(previewfiles_folder, filename)
    #                     parts = filename.split('_')
    #                     if len(parts) >= 5:
    #                         book_title = parts[0]
    #                         author = parts[1]
    #                         year = parts[2]
    #                         page_count = parts[3]
    #                         book_id = parts[4].split('.')[0]
    #                         if author != 'తెలియదు':
    #                             data.append([book_title, author, year, page_count, book_id, filepath])
    #                         else:
    #                             data.append([book_title, '', year, page_count, book_id, filepath])
    #         df = pd.DataFrame(data, columns=['book_title', 'author', 'year', 'page_count', 'book_id', 'filepath'])
    #         df.to_csv(csv_path, index=False, encoding="utf-8")
    #         return df
    
    def load_preview_folders(self):
        config_path = os.path.join(base_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                print(f"Loaded preview folders: {config.get('preview_folders', [])}")  # Debug output
                return config.get('preview_folders', [])
        print("Config file not found or empty")  # Debug output
        return [previewfiles_folder]


    def load_or_create_csv(self):
        preview_folders = self.load_preview_folders()
        data = []
        for folder in preview_folders:
            if os.path.exists(folder):
                with os.scandir(folder) as entries:
                    for entry in entries:
                        if entry.is_file():
                            filename = entry.name
                            filepath = os.path.join(folder, filename)
                            parts = filename.split('_')
                            if len(parts) >= 5:
                                book_title = parts[0]
                                author = parts[1]
                                year = parts[2]
                                page_count = parts[3]
                                book_id = parts[4].split('.')[0]
                                if author != 'తెలియదు':
                                    data.append([book_title, author, year, page_count, book_id, filepath])
                                else:
                                    data.append([book_title, '', year, page_count, book_id, filepath])
            else:
                print(f"Folder not found: {folder}")  # Debug output

        df = pd.DataFrame(data, columns=['book_title', 'author', 'year', 'page_count', 'book_id', 'filepath'])
        df.to_csv(csv_path, index=False, encoding="utf-8")
        return df

    def display_matches(self, detected_text):
        # Clear existing widgets from the grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        if not self.df.empty:
            potential_matches = get_close_matches(detected_text, self.df['book_title'].tolist(), n=5, cutoff=0.6)
            if potential_matches:
                matched_rows = self.df[self.df['book_title'].isin(potential_matches)]
            
                # Track row and column manually
                row, col = 0, 0
                max_cols = 4  # Number of columns per row
            
                for _, row_data in matched_rows.iterrows():
                    book_widget = self.create_book_widget(row_data)
                    self.grid_layout.addWidget(book_widget, row, col)

                    col += 1
                    if col >= max_cols:  # Move to next row after max_cols
                        col = 0
                        row += 1
    def create_book_widget(self, row):
        container = QWidget()
        container_layout = QHBoxLayout()

        full_page = QLabel()
        full_page.setAlignment(Qt.AlignCenter)
        full_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        try:
            import fitz
            doc = fitz.open(row['filepath'])
            page = doc.load_page(0)

            # Scale the image to display the full page
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Adjust scale if necessary
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            full_page.setPixmap(QPixmap.fromImage(img).scaled(300, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Adjust size if needed

        except Exception as e:
            full_page.setText("No Preview")

        full_page.mousePressEvent = lambda event: self.open_pdf(row['filepath'])

        details = QLabel(f"""
        <b>{row['book_title']}</b><br>
        <i>Author:</i> {row['author']}<br>
        <i>Year:</i> {row['year']}<br>
        <i>Pages:</i> {row['page_count']}<br>
        <i>ID:</i> {row['book_id']}
        """)
        details.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        details.setWordWrap(True)
        details.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        container_layout.addWidget(full_page)
        container_layout.addWidget(details)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(0, 5, 0, 5)

        container.setLayout(container_layout)
        return container


    
    def open_pdf(self, filepath):
        # Open the PDF file using the default application
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            os.system(f"open '{filepath}'")
        else:
            os.system(f"xdg-open '{filepath}'")

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookDetectorApp()
    window.show()
    sys.exit(app.exec_())