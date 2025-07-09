import paddle
from paddleocr import PaddleOCR


class OCR:
    def __init__(self,model_path=None):
        paddle.set_device('cpu')
        if model_path is None:
            self.paddleocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                ocr_version="PP-OCRv5",
                device="cpu"
            )
        else:
            self.paddleocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                text_recognition_model_dir=model_path+"\\PP-OCRv5_server_rec",
                text_detection_model_dir=model_path+"\\PP-OCRv5_server_det",
                device="cpu"
            )

    def predict(self, image_path):
        result = self.paddleocr.predict(input=image_path)
        if result:
            text = result[0]["rec_texts"]
            position_box = result[0]["rec_boxes"]
            return {"text": text, "position": position_box}
        else:
            print("!!!!!")
            return {"text": [None], "position": [None]}

    def visualize(self, image_path):
        result = self.paddleocr.predict(input=image_path)
        # 可视化结果并保存 json 结果
        for res in result:
            res.print()
            res.save_to_img("output")
            res.save_to_json("output")
