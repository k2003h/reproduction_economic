# ver 1.0.1

## fix bug

1. ｓｐｙｄｅｒ．ｐｙ

​	＞新增检验对话是否只有一句

```Ｐｙｔｈｏｎ
def get_interaction(emulator, paddleocr):        `
···
if len(interaction_log) == 0:
	interaction_log.append(item)
	print("\t\t\t", interaction_log[-1])
···
```

