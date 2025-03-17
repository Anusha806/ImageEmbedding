from PyQt5.QtWidgets import (
    QApplication, QLabel, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import sys
import cv2
import pytesseract
import os
import pandas as pd
from difflib import get_close_matches

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = '--psm 6 --oem 3 -l tel'

previewfiles_folder = 'previewfiles'
csv_path = 'book_meta_data.csv'

class BookDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
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

    def load_or_create_csv(self):
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        else:
            data = []
            with os.scandir(previewfiles_folder) as entries:
                for entry in entries:
                    if entry.is_file():
                        filename = entry.name
                        filepath = os.path.join(previewfiles_folder, filename)
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
            df = pd.DataFrame(data, columns=['book_title', 'author', 'year', 'page_count', 'book_id', 'filepath'])
            df.to_csv(csv_path, index=False)
            return df

    def display_matches(self, detected_text):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        if not self.df.empty:
            potential_matches = get_close_matches(detected_text, self.df['book_title'].tolist(), n=5, cutoff=0.6)
            if potential_matches:
                matched_rows = self.df[self.df['book_title'].isin(potential_matches)]
                for index, row in matched_rows.iterrows():
                    book_widget = self.create_book_widget(row)
                    self.grid_layout.addWidget(book_widget, index // 4, index % 4)

    def create_book_widget(self, row):
        container = QWidget()
        container_layout = QHBoxLayout()

        thumbnail = QLabel()
        thumbnail.setFixedSize(150, 225)
        thumbnail.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        thumbnail.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        try:
            from pdf2image import convert_from_path
            images = convert_from_path(row['filepath'], first_page=1, last_page=1)
            if images:
                image = images[0].resize((150, 225))
                image.save("temp_thumbnail.jpg")
                thumbnail.setPixmap(QPixmap("temp_thumbnail.jpg"))
                os.remove("temp_thumbnail.jpg")
        except ImportError:
            thumbnail.setText("No Preview")
        thumbnail.mousePressEvent = lambda event: self.open_pdf(row['filepath'])

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

        container_layout.addWidget(thumbnail)
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