# 調整標記框
調整 BEVHeight 檢測出來的物件框。
標記框格式：kitti

## 使用說明
執行後如下圖
![image](https://github.com/user-attachments/assets/42f8bbc4-5e34-4c48-aa78-48d911ee5de3)
- 先按 "打開資料夾" 讀取圖片與標注，資料夾的格式如下。(直接選cal6)
```
├── cal6
│   ├── calib.txt
│   ├── denorm.txt
│   ├── det_txt
│   │   ├── cal6_000000.txt
│   │   ├── cal6_000001.txt
│   │   ├── cal6_000002.txt
│   │   ├── cal6_000003.txt
│   │   ├── cal6_000004.txt
│   │   ├── cal6_000005.txt
|   |   |   ...
│   ├── det_png
│   │   ├── cal6_000000.jpg
│   │   ├── cal6_000001.jpg
│   │   ├── cal6_000002.jpg
│   │   ├── cal6_000003.jpg
│   │   ├── cal6_000004.jpg
│   │   ├── cal6_000005.jpg
│   └── original_png
│       ├── cal6_000000.jpg
│       ├── cal6_000001.jpg
│       ├── cal6_000002.jpg
│       ├── cal6_000003.jpg
│       ├── cal6_000004.jpg
│       ├── cal6_000005.jpg

```
- cal6：資料夾本人
- calib.txt：相機內參，只包含一個P2矩陣
- denorm.txt：相機座標中的道路平面方程式(用外參算的)
- det_png：原始的標注產生的圖片
- det_txt：標注資料
- original_png：原始沒有標注的圖片。
讀取正確會到以下畫面
![image](https://github.com/user-attachments/assets/62daab53-dc25-43b4-849b-b31849c432df)

## 功能
- 恢復預設：讀取原始的標注檔，並將目前狀態清除，還原回標注檔中的狀態。**所以建議複製一個det_txt，以免玩壞了沒得恢復**
- 上一張、下一張：移動到上、下一張照片。
- 儲存標注：將目前的表格寫入檔案。**所以在儲存之前都不會動到原始檔**
- Offset：每次調整的大小，直接打想要的offset在框框內就可以調整
- +、-：調整選定的欄位，每按一次就是把框框內的數值+/-一個offset
- 新增標注：新增一個Row，欄位內的值是選定的Row。Ex:如果選擇上面範例圖的第二行，[Car, 1.4867, 1.6319...]的任意一欄，就會新增一欄一模一樣的數值在最底下。
- 刪除標注：刪除所選的Row。
