# 調整標記框
調整 BEVHeight 檢測出來的物件框。
標記框格式：kitti

## How to run
需要載 PyQt5 及 OpenCV
```
pip install PyQt5
pip install opencv-python
```
然後直接用 VS Code 執行 annotation.py 應該就會有視窗了

## 使用說明
執行後如下圖
![image](https://github.com/user-attachments/assets/42f8bbc4-5e34-4c48-aa78-48d911ee5de3)
- 先按 "打開資料夾" 讀取圖片與標注，資料夾的格式如下。(直接選cal6)
```

├── adjusting
|   ├── calib.txt
|   ├── denorm.txt
|   ├── image
|   │   ├── 6_obj_000001.png
|   │   ├── 6_obj_000002.png
|   │   ├── 6_obj_000003.png
|   │   ├── 6_obj_000004.png
|   │   ├── 6_obj_000005.png
|   |   | ...
|   ├── label
|   │   ├── 6_obj_000001.txt
│   |   ├── 6_obj_000002.txt
|   │   ├── 6_obj_000003.txt
│   |   ├── 6_obj_000004.txt
|   │   ├── 6_obj_000005.txt

```
- adjusting：資料夾本人
- calib.txt：相機內參，只包含一個P2矩陣
- denorm.txt：相機座標中的道路平面方程式(用外參算的)
- label：標注資料
- image：原始沒有標注的圖片。
讀取正確會到以下畫面
![image](https://github.com/user-attachments/assets/62daab53-dc25-43b4-849b-b31849c432df)

## 按鈕功能介紹
- 恢復預設：讀取原始的標注檔，並將目前狀態清除，還原回標注檔中的狀態。**所以建議複製一個det_txt，以免玩壞了沒得恢復**
- 上一張、下一張：移動到上、下一張照片。
- 儲存標注：將目前的表格寫入檔案。**所以在儲存之前都不會動到原始檔**
- Offset：每次調整的大小，直接打想要的offset在框框內就可以調整
- 剪貼簿勾選框：勾選後每次點選底下表格的標註，都會把選擇的標註複製進剪貼簿。不勾選則剪貼簿不更改
- +、-：調整選定的欄位，每按一次就是把框框內的數值+/-一個offset **滑鼠移到圖片上用滾輪也可以調整**
- 新增標注：新增一個Row，欄位內的值是剪貼簿的值(剪貼簿是左上方的表格，勾選框底下)。
- 刪除標注：刪除所選的Row。


## 製作adjusting
1. Bag轉換成pcd跟png
2. 把calib.txt跟denorm.txt放進scene
3. scenes2rope.py 把scene轉換成rope3d，並產生空的標注資料
4. 用rope3kitti.py轉換成kitti。**注意** 目前的標注資料都是空的
5. 用BEVHeight產生標注資料(kitti格式)，用產生的標注資料替換掉原有的空標注資料
6. 用kitti2rope_label.py把產生的標注資料轉換成Rope3D格式
7. kitti2adjusting.py把kitti的標注資料+圖片換成adjusting格式 **adjusting格式：Rope3D的檔名+kitti的標注格式**
