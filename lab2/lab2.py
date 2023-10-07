from PySide6.QtWidgets import QHBoxLayout, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QApplication, QMainWindow, QFileDialog, QMainWindow, QPushButton, QLineEdit, QListWidget
from combined_file_dialog import *
from PySide6.QtGui import QIcon
import sys
from PIL import Image
from PIL import ImageCms
import io
from pathlib import Path
from typing import Dict
from  typing import List
from time import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata reader")
        self.setGeometry(100, 100, 1000, 800)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.dir_browser = CombinedFileDialog()
        self.dir_browser.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.dir_browser.selected.connect(self.initMetadata)
        main_layout.addWidget(self.dir_browser)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(4)
        self.tree_widget.setHeaderLabels(['Name', 'Pixel size', 'Resolution', 'Bit depth'])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.setColumnWidth(1, 300)
        self.tree_widget.setColumnWidth(2, 100)
        self.tree_widget.setColumnWidth(3, 50)
        main_layout.addWidget(self.tree_widget)

    def initMetadata(self, folder):
        mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, "I": 32, "F": 32}
        
        start = time()
        top_items : List[QTreeWidgetItem] = []
        files = [p for p in Path(folder).glob("**/*") if p.suffix in {".jpeg", ".jpg", ".png", ".gif", ".tiff", ".bmp",".pcx"}]
        for file in files:
            img = Image.open(file)
            
            w,h = img.width, img.height
            depth = mode_to_bpp.get(img.mode, None)
            try:
                resX, resY = round(img.info['dpi'][0]), round(img.info['dpi'][1])
            except:
                resX, resY = 0, 0

            item = QTreeWidgetItem(None)
            item.setIcon(0, QIcon(str(file)))
            item.setText(0, file.name)
            item.setText(1, f"{w}x{h}")
            item.setText(2, f"{resX}x{resY}")
            item.setText(3, str(depth))
            top_items.append(item)

            self.exif(img, item)
            if file.suffix == ".gif":
                self.gif_func(img, item)
            elif file.suffix == ".bmp":
                self.bmp_func(img, item)
            elif file.suffix in {".jpeg", ".jpg"}:
                self.jpeg_func(img, item)
            
        self.tree_widget.clear()
        self.tree_widget.insertTopLevelItems(0, top_items)
        end = time()
        print(F"Time elapsed {end-start} for {len(files)} images. Avg: {(end-start) / len(files)}")

    def jpeg_func(self, img : Image.Image, item : QTreeWidgetItem):
        try:
            quant_table = img.quantization
            QTreeWidgetItem(item, ['Quantization table', str(quant_table)])
        except:
            pass

        try:
            profile = img.info['icc_profile']
            f = io.BytesIO(profile)
            icc_profile = ImageCms.ImageCmsProfile(f).profile.profile_description
            QTreeWidgetItem(item, ['ICC profile', icc_profile])
        except:
            pass
            

    def gif_func(self, img : Image.Image, item : QTreeWidgetItem):
        palette = img.getpalette(None)
        if palette is not None:
            QTreeWidgetItem(item, ['Palette', str(palette)])

        try:
            duration = img.info['duration']
            QTreeWidgetItem(item, ['Duration', str(duration)])
        except:
            pass

    def bmp_func(self, img : Image.Image, item : QTreeWidgetItem):
        info = img.info
        try:
            compression = info['compression']
            comp_dict : Dict[str, int] = img.COMPRESSIONS
            key_list = list(comp_dict.keys())
            compression_str = key_list[compression]
            QTreeWidgetItem(item, ['Compression', compression_str])
        except:
            pass

    def exif(self, img : Image.Image, item : QTreeWidgetItem):
        from PIL.ExifTags import TAGS

        exif = img.getexif()
        for exif_tag in exif.items():
            tag = str(TAGS[exif_tag[0]])
            value = exif_tag[1]
            try:
                value = round(value)
            except:
                pass
            QTreeWidgetItem(item, [tag, str(value)])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
