import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
import os
import shutil

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.drawing = False
        self.start_pos = None
        self.end_pos = None
        self.rectangles = []
        self.image_file = None
        self.current_class_id = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.end_pos = event.pos()
            self.update()
            self.save_rectangle()

    def save_rectangle(self):
        if not self.start_pos or not self.end_pos:
            return

        rect = QRect(self.start_pos, self.end_pos).normalized()
        x1, y1, w, h = rect.left(), rect.top(), rect.width(), rect.height()
        self.rectangles.append((x1, y1, w, h, self.current_class_id))
        self.save_coordinates()

    def save_coordinates(self):
        if not self.image_file:
            return

        img = self.pixmap()
        if not img:
            return

        img_w, img_h = img.width(), img.height()
        file_name = os.path.splitext(os.path.basename(self.image_file))[0] + ".txt"
        save_path = os.path.join(OUTPUT_DIR, file_name)
        
        with open(save_path, 'w') as f:
            for rect in self.rectangles:
                x1, y1, w, h, class_id = rect
                center_x = (x1 + w/2) / img_w
                center_y = (y1 + h/2) / img_h
                norm_w = w / img_w
                norm_h = h / img_h
                f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {norm_w:.6f} {norm_h:.6f}\n")

    def paintEvent(self, event):
        if self.pixmap():
            super().paintEvent(event)
            painter = QPainter(self)
            for rect in self.rectangles:
                x1, y1, w, h, class_id = rect
                painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                painter.drawRect(QRect(QPoint(x1, y1), QPoint(x1 + w, y1 + h)))
                painter.drawText(QPoint(x1 + 5, y1 + 15), str(class_id))
            if self.start_pos and self.end_pos and self.drawing:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                rect = QRect(self.start_pos, self.end_pos).normalized()
                painter.drawRect(rect)
                painter.drawText(QPoint(rect.left() + 5, rect.top() + 15), str(self.current_class_id))

    def clear_rectangles(self):
        self.rectangles = []
        self.start_pos = None
        self.end_pos = None
        self.update()

    def load_existing_labels(self):
        self.clear_rectangles()
        if not self.image_file:
            return
        label_file = os.path.splitext(os.path.basename(self.image_file))[0] + ".txt"
        label_path = os.path.join(OUTPUT_DIR, label_file)
        if os.path.exists(label_path):
            img = self.pixmap()
            if not img:
                return
            img_w, img_h = img.width(), img.height()
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, cx, cy, w, h = map(float, parts)
                        x = int((cx - w / 2) * img_w)
                        y = int((cy - h / 2) * img_h)
                        w = int(w * img_w)
                        h = int(h * img_h)
                        self.rectangles.append((x, y, w, h, int(class_id)))
            self.update()

class ImageDisplayApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO Formatında Etiketleme Aracı")
        self.setGeometry(100, 100, 800, 600)
        self.create_interface()
        self.images = []
        self.current_image_index = 0
        self.load_image = False

    def create_interface(self):
        layout = QVBoxLayout()

        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class ID:"))
        self.class_input = QLineEdit("0")
        self.class_input.setMaximumWidth(50)
        class_layout.addWidget(self.class_input)
        class_layout.addStretch()
        layout.addLayout(class_layout)

        self.image_label = ImageLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        btn_layout = QHBoxLayout()
        self.select_button = QPushButton("Resim Seç")
        self.select_button.clicked.connect(self.select_images)
        btn_layout.addWidget(self.select_button)

        self.clear_button = QPushButton("Temizle")
        self.clear_button.clicked.connect(self.image_label.clear_rectangles)
        btn_layout.addWidget(self.clear_button)

        self.prev_button = QPushButton("Önceki Resim")
        self.prev_button.clicked.connect(self.load_prev_image)
        btn_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Sonraki Resim")
        self.next_button.clicked.connect(self.load_next_image)
        btn_layout.addWidget(self.next_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Resim Seç", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if files:
            try:
                self.image_label.current_class_id = int(self.class_input.text())
            except ValueError:
                self.image_label.current_class_id = 0
                self.class_input.setText("0")

            self.images = []
            for f in files:
                fname = os.path.basename(f)
                dest = os.path.join(OUTPUT_DIR, fname)
                if not os.path.exists(dest):
                    shutil.copy(f, dest)
                self.images.append(dest)

            self.current_image_index = 0
            self.load_image = True
            self.load_image_at_index()

    def load_image_at_index(self):
        if self.load_image and 0 <= self.current_image_index < len(self.images):
            current_image = self.images[self.current_image_index]
            self.image_label.image_file = current_image
            pixmap = QPixmap(current_image)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            self.image_label.load_existing_labels()
        elif self.current_image_index >= len(self.images):
            self.image_label.setText("Tüm resimler etiketlendi.")
        elif self.current_image_index < 0:
            self.current_image_index = 0

    def load_next_image(self):
        if self.load_image and self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.load_image_at_index()

    def load_prev_image(self):
        if self.load_image and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image_at_index()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDisplayApp()
    window.show()
    sys.exit(app.exec_())