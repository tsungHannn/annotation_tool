import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
from PyQt5.QtWidgets import QTableWidget, QHBoxLayout, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox
from  vis_util import *


class ImageViewerApp(QWidget):
    def __init__(self):
        super().__init__()

        # 設定窗口標題
        self.setWindowTitle("Image Viewer with PyQt5")
        self.setGeometry(100, 100, 800, 600)  # 調整窗口大小以適應圖片顯示

        # 建立主佈局
        main_layout = QVBoxLayout()

        # 建立頂部佈局，放置 image_list 和 image_label
        top_layout = QHBoxLayout()

        # 建立界面元素
        self.open_folder_btn = QPushButton("打開資料夾")
        self.open_folder_btn.clicked.connect(self.open_folder)

        self.image_qtlist = QListWidget()
        self.image_qtlist.itemClicked.connect(self.set_current_index)

        self.data_root_label = QLabel("Data Root:")

        self.image_label = QLabel("此處顯示圖片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(640, 480)  # 設定圖片顯示區域大小

        self.restore_button = QPushButton("恢復預設")
        self.restore_button.clicked.connect(self.restore_label)
        self.save_file_btn = QPushButton("儲存標注")
        self.save_file_btn.clicked.connect(self.save_label)

        self.offset_layout = QHBoxLayout()
        self.offset = 0.1
        self.show_offset = QLabel("Offset: "+str(self.offset))
        self.input_offset = QLineEdit()
        self.input_offset.textChanged.connect(self.change_offset)

        self.offset_layout.addWidget(self.show_offset)
        self.offset_layout.addWidget(self.input_offset)
        
        

        # 表格設置
        self.label_table = QTableWidget()
        self.label_table.setColumnCount(8)
        self.label_table.setRowCount(2)
        self.label_table.setHorizontalHeaderLabels(['Class', 'Height', 'Width', 'Length', 'x', 'y', 'z', 'Rotation'])

        # 增加、減少按鈕
        self.increase_btn = QPushButton("+")
        self.increase_btn.clicked.connect(self.increase_value)

        self.decrease_btn = QPushButton("-")
        self.decrease_btn.clicked.connect(self.decrease_value)

        # 上、下一張照片
        image_button_layout = QHBoxLayout()
        self.next_image_button = QPushButton("Next")
        self.next_image_button.clicked.connect(self.next_image)
        self.previous_image_button = QPushButton("Previous")
        self.previous_image_button.clicked.connect(self.previous_image)
        image_button_layout.addWidget(self.previous_image_button)
        image_button_layout.addWidget(self.next_image_button)

        # 將按鈕放在按鈕佈局中
        offset_button_layout = QHBoxLayout()
        offset_button_layout.addWidget(self.decrease_btn)
        offset_button_layout.addWidget(self.increase_btn)


        # 將 image_list 和 image_label 加入到 top_layout 中
        top_layout.addWidget(self.image_qtlist)
        top_layout.addWidget(self.image_label)

        # 將元件添加到主佈局
        main_layout.addWidget(self.open_folder_btn) # 開啟檔案按鈕
        main_layout.addWidget(self.data_root_label) # 顯示路徑
        main_layout.addLayout(top_layout)           # image list跟顯示圖片
        main_layout.addWidget(self.save_file_btn)   # 儲存圖片
        main_layout.addLayout(self.offset_layout)   # 輸入offset
        main_layout.addWidget(self.label_table)     # label表格
        main_layout.addLayout(offset_button_layout) # + -
        main_layout.addLayout(image_button_layout)  # 上一張、下一張

        # 設置主佈局
        self.setLayout(main_layout)

        self.data_root = None
        self.image_folder = None
        self.image_list = None
        self.annotation_folder = None
        self.current_image_path = None
        self.current_index = 0

        # show picture setting
        self.denorm = None
        self.label_list = list()
        self.label_file_name = ""
        self.calib = None
    
        

        
    # 選擇資料夾
    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇圖片資料夾")
        if folder:
            self.data_root = folder
            self.annotation_folder = os.path.join(folder, "det_text")
            self.image_folder = os.path.join(folder, "original_png")
            self.load_images_from_folder()
            self.data_root_label.setText(self.image_folder)

            self.now_image_index = 0

    # 讀取資料夾裡面的圖片後顯示list
    def load_images_from_folder(self):
        self.image_qtlist.clear()
        if self.image_folder:
            self.image_list = os.listdir(self.image_folder)
            self.image_list.sort()
            images = [f for f in self.image_list if f.endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff'))]
            for image in images:
                self.image_qtlist.addItem(image)
        
        self.image_qtlist.setCurrentRow(self.current_index)
        self.select_image(self.image_qtlist.currentItem())
    


    
    def increase_value(self):
        # 獲取選中的單元格並增加其值
        selected_item = self.label_table.currentItem()
        if selected_item:
            try:
                value = float(selected_item.text())
                value += float(self.offset)
                selected_item.setText(str(round(value, 4)))
            except ValueError:
                pass  # 若無法轉換為數字，則忽略
        
        self.label_list = self.get_label_table()
        self.display_image()
        

    def decrease_value(self):
        # 獲取選中的單元格並減少其值
        selected_item = self.label_table.currentItem()
        if selected_item:
            try:
                value = float(selected_item.text())
                value -= float(self.offset)
                selected_item.setText(str(round(value, 4)))
            except ValueError:
                pass  # 若無法轉換為數字，則忽略

        self.label_list = self.get_label_table()
        self.display_image()

    def set_current_index(self, item):
        for i in range(len(self.image_list)):
            if item.text() == self.image_list[i]:
                self.current_index = i
                break
        
        self.image_qtlist.setCurrentRow(self.current_index)
        self.select_image(self.image_qtlist.currentItem())
        


    def next_image(self):
        if self.current_index == len(self.image_list) - 1:
            pass # do nothing
        else:
            self.current_index += 1
            self.image_qtlist.setCurrentRow(self.current_index)
            self.select_image(self.image_qtlist.currentItem())
    
    def previous_image(self):
        if self.current_index == 0:
            pass # do nothing
        else:
            self.current_index -= 1
            self.image_qtlist.setCurrentRow(self.current_index)
            self.select_image(self.image_qtlist.currentItem())
    

    def get_label_table(self):
        label_table = list()
        for i in range(self.label_table.rowCount()):
            temp = list()
            for j in range(self.label_table.columnCount()):
                temp.append(str(self.label_table.item(i, j).text()))
            label_table.append(temp.copy())
        return label_table

    def load_label(self, file_path):
        
        label_list = list()

        with open(file_path) as f:
            for line in f.readlines():
                temp_object = list()
                line_list = line.split('\n')[0].split(' ')
                temp_object.append(line_list[0])
                temp_object.append(line_list[8])
                temp_object.append(line_list[9])
                temp_object.append(line_list[10])
                temp_object.append(line_list[11])
                temp_object.append(line_list[12])
                temp_object.append(line_list[13])
                temp_object.append(line_list[14])
                label_list.append(temp_object.copy())

        self.label_table.setRowCount(len(label_list))

        # 填入資訊
        for i in range(len(label_list)):
            for j in range(len(label_list[i])):
                self.label_table.setItem(i, j, QTableWidgetItem(str(label_list[i][j])))
        
        return label_list
    



    # 輸入offset
    def change_offset(self):
        temp = self.input_offset.text()
        if is_number(temp):
            self.offset = temp
            self.show_offset.setText("Offset:"+str(self.offset))
        else:
            self.show_offset.setText("Input is not a number.\nOffset: "+str(self.offset))

    

    
    # 選擇圖片後，會設定calib, denorm, label等
    def select_image(self, item):
        
        image_path = os.path.join(self.image_folder, item.text())
        self.current_image_path = image_path
        
        file_prefix = item.text()[:-4]
        calib_path = os.path.join(self.data_root, "calib.txt")
        label_path = os.path.join(self.data_root, "det_txt")
        denorm_path = os.path.join(self.data_root, "denorm.txt")


        self.label_file_name= os.path.join(label_path, file_prefix + ".txt")
        self.label_list = self.load_label(self.label_file_name)


        _, self.calilb, self.denorm = load_calib(calib_path, denorm_path)

        self.display_image()
        
    # 讀取原始圖片後，劃上標記
    def display_image(self):
        image = cv2.imread(self.current_image_path)
        image = draw_3d_box_on_image(image, self.label_list, self.calilb, self.denorm) # return a opencv image

        height, width, channel = image.shape
        bytesPerline = channel * width
        image = QImage(image, width, height, bytesPerline, QImage.Format_RGB888)

        # 使用QPixmap顯示圖片
        pixmap = QPixmap(image)

        if pixmap.isNull():
            QMessageBox.warning(self, "錯誤", "無法加載圖片")
            return

        # 調整圖片大小以適應QLabel
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    
    def restore_label(self):
        self.select_image(self.image_qtlist.currentItem(self.current_index))
        

    def save_label(self):
        self.label_list = self.get_label_table()
        write_kitti_in_txt(self.label_list, self.label_file_name)
        # if self.current_image_path:
        #     save_path, _ = QFileDialog.getSaveFileName(self, "保存圖像", "", "Images (*.png *.jpg *.bmp)")
        #     if save_path:
        #         # 將當前圖片儲存到新位置
        #         pixmap = QPixmap(self.current_image_path)
        #         pixmap.save(save_path)
        #         QMessageBox.information(self, "成功", "圖像已保存！")
        # else:
        #     QMessageBox.warning(self, "錯誤", "沒有選擇圖像保存！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewerApp()
    viewer.show()
    sys.exit(app.exec_())
