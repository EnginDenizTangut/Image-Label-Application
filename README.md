# YOLO Format Image Annotation Tool (labelme.py)

This is a **simple single-file PyQt5 application** for labeling objects in images in **YOLO format**. It allows users to draw bounding boxes and assign either numerical or string-based class identifiers (e.g., `0`, `1`, or `car`, `tree`). All annotations are saved in YOLO text format and can be used for training object detection models.

---

## ✨ Features

- [x] Draw bounding boxes with mouse  
- [x] Save annotations in YOLO format (`class_id center_x center_y width height`)  
- [x] Supports **string or numeric class IDs**  
- [x] Automatically loads existing annotations  
- [x] Browse through multiple images  
- [x] Clean and simple interface  
- [x] Single-file app (`labelme.py`)  

---

## 📦 Requirements

- Python 3.6+  
- PyQt5  

Install with:

```bash
pip install PyQt5
```

---

## 🚀 How to Use

1. Run the script:

```bash
python labelme.py
```

2. Click `Resim Seç` to choose one or more images (they will be copied to the `output/` folder).

3. Enter a class ID in the text box (e.g., `0`, `1`, or `car`) before drawing boxes.

4. Draw bounding boxes by clicking and dragging on the image.

5. Use the buttons:
   - `Temizle`: Clear boxes on current image  
   - `Önceki Resim`: Go to previous image  
   - `Sonraki Resim`: Go to next image  

6. Annotations are saved automatically to `output/*.txt` alongside the images.

---

## 📁 Output Format

Each annotation file (e.g., `image1.txt`) is saved as:

```
class_id center_x center_y width height
```

All values are **normalized (between 0 and 1)**.

Example:

```
car 0.452000 0.331000 0.120000 0.150000
tree 0.682000 0.421000 0.100000 0.200000
```

---

## 🛠️ Customization

- You can customize the label colors and formats in `paintEvent()` method.
- Class labels can be either numeric or descriptive (e.g., `cat`, `dog`).

---

## 📸 Screenshot

*Feel free to add a screenshot here of your application in use.*

---

## 📝 Notes

- All selected images and annotations are stored inside the `output/` folder.  
- If an image has already been annotated, its boxes will be reloaded when opened again.  
- It supports drawing multiple boxes with different class IDs on each image.

---

## 📄 License

This project is open source and free to use under the MIT License.
