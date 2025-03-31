import os
import numpy as np
from PIL import Image, ImageSequence
import torch
import folder_paths

class WebpToPngSequence:
    """
    WebPファイルをPNG連番に変換するノード
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "webp_file": ("STRING", {"default": ""}),
                "output_dir": ("STRING", {"default": "output"}),
                "prefix": ("STRING", {"default": "frame_"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert_webp_to_png_sequence"
    CATEGORY = "image/animation"
    
    def convert_webp_to_png_sequence(self, image, webp_file, output_dir, prefix):
        # ComfyUIの出力フォルダ内に指定されたディレクトリを作成
        output_path = os.path.join(folder_paths.get_output_directory(), output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # WebPファイルを開く
        try:
            if not os.path.exists(webp_file):
                print(f"Error: WebP file '{webp_file}' not found")
                return (image,)
                
            webp_image = Image.open(webp_file)
            
            # アニメーションWebPかどうかを確認
            frames = []
            for i, frame in enumerate(ImageSequence.Iterator(webp_image)):
                # フレームをRGBAモードに変換
                frame_rgba = frame.convert("RGBA")
                
                # 各フレームをPNGとして保存
                frame_path = os.path.join(output_path, f"{prefix}{i:04d}.png")
                frame_rgba.save(frame_path)
                
                # フレームをTensorに変換してリストに追加
                frame_np = np.array(frame_rgba).astype(np.float32) / 255.0
                frames.append(torch.from_numpy(frame_np)[None,...])
                
                print(f"Saved frame {i} to {frame_path}")
            
            # 全フレームを結合
            if frames:
                frames_tensor = torch.cat(frames, dim=0)
                return (frames_tensor,)
            else:
                # アニメーションではない場合、単一フレームとして処理
                frame_path = os.path.join(output_path, f"{prefix}0000.png")
                webp_image.convert("RGBA").save(frame_path)
                print(f"Saved single frame to {frame_path}")
                
                # 元の画像をそのまま返す
                return (image,)
                
        except Exception as e:
            print(f"Error processing WebP file: {e}")
            return (image,)

# ノードをComfyUIに登録するための情報
NODE_CLASS_MAPPINGS = {
    "WebpToPngSequence": WebpToPngSequence
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WebpToPngSequence": "WebP to PNG Sequence"
}
