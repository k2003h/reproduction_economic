# ver 1.0.1

## 一、修复bug

1.  在对话识别中，新增对只有一段对话的检验

```python
# spyder.py
def get_interaction(emulator, paddleocr):        `
···
if len(interaction_log) == 0:
	interaction_log.append(item)
	print("\t\t\t", interaction_log[-1])
···
```
# ver 1.0.2
## 一、修复bug

1. 在数据库增加了对表情符号的适配

   ```sql
   ALTER DATABASE reproduction_economic CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
   ```


2. 对于单个对话过长而爆内存->新增截断机制

```python
 def extract_paragraphs(img_array, blank_height=30, threshold=5, bg_threshold=253, scaling=1):
    if i - start_idx > 1000:
                paragraph = img_array[start_idx:i - blank_count, :]
                paragraphs.append(scaling_image(paragraph,scaling))
                start_idx = i
```
3. 对于病例没有内容的新增判断机制

![[PixPin_2025-07-05_19-10-44 1.png]]

4. 修复了ADB 调试时间过长产生多个设备的bug（指定操作的某个设备）
```python
	self.id="127.0.0.1"
	subprocess.run(f"adb -s {self.id} ····")
```

## 二、程序优化

1. 在段落分割函数使用图像缩放以节省后续识图时间。

2. 在图片识别时加入等待机制避免过热关机
![[Pasted image 20250705202238.png]]![[Pasted image 20250705202248.png]]
3. 新增云存储

# ver 1.0.3-1.0.4
## 一、新增内容
commit一些未进行包管理的文件

# ver 1.0.5
## 一、修复
1. 新增上传云数据库(增加对是否是云端)
```python
def database_insert_dict(table_name, data_dict, is_local=False):  
    if is_local:  
        database = MySQLDatabase("reproduction_economic")  
    else:  
        database = MySQLDatabase("reproduction", "106.13.72.195", "k2003h", "Qwas1234!")
```
2. 修复了提取对话无法提取最后一段的bug（同步更新了其他分段的算法）
```python
if start_idx < len(horizontal_proj):  
    last_region = img_array[start_idx:, :]  
    last_gray = cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY)  
    last_proj = np.sum(last_gray < bg_threshold, axis=1)  # 更合理的投影计算  
    # last_proj = np.sum(cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY) > 252, axis=1) # 原计算方式
    if np.sum(last_proj) > threshold * last_region.shape[1] * 0.1: 
        paragraphs.append(scaling_image(last_region, scaling))
```
3. 更新了gitignore，新增对tempt文件夹的ignore


## ver 1.0.6
## 一、新增内容
1. 从笔记本中本地数据库导出信息
2. 新增数据预处理文件（data_preprocessing）
## 二、优化
1. 优化代码注释
2. 优化更新文件中格式


## ver 1.0.7
一、优化

1. 实用 os.path.abspath(__file__)来表示路径

2. 新增断点继续的功能（通过设置inquiry_holding=True使程序暂停)