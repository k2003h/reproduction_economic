# ver 1.0.1

## fix bug

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
##　fix bug

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

## 优化

1. 在段落分割函数使用图像缩放以节省后续识图时间。

2. 在图片识别时加入等待机制避免过热关机
![[Pasted image 20250705202238.png]]![[Pasted image 20250705202248.png]]
3. 新增云存储