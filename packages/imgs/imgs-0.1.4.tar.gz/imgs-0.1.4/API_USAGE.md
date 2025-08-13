# Utils Library - Public API Usage Guide

这是一个优雅的Python工具库，专注于图像处理和数据操作功能。

## 快速开始

### 安装和导入

```python
# 导入所有功能
from utils import *

# 或者选择性导入
from utils import load_image, save_image, ImageProcessor
from utils import ImageResource, ImageWriter
```

## 核心功能

### 1. 图像加载 (ImageResource)

```python
# 从标准测试图像加载
img = ImageResource.from_standard("chelsea")

# 从文件加载
img = ImageResource.from_file("photo.jpg")

# 从URL加载
img = ImageResource.from_url("https://example.com/image.png")

# 从base64加载
img = ImageResource.from_base64("iVBORw0KGgoAAAANSUhEUgAA...")
img = ImageResource.from_base64("data:image/png;base64,iVBORw0...")

# 从字节数据加载
with open("image.jpg", "rb") as f:
    img = ImageResource.from_bytes(f.read(), ".jpg")

# 从摄像头捕获
frame = ImageResource.from_webcam(0)  # 主摄像头

# 从屏幕截图 (Windows/Mac)
screenshot = ImageResource.from_screen()
```

### 2. 图像保存 (ImageWriter)

```python
# 保存到文件
ImageWriter.to_file(img, "output.png")
ImageWriter.to_file(img, "output.jpg", quality=95)

# 转换为base64
b64_string = ImageWriter.to_base64(img, ".png")
data_uri = ImageWriter.to_base64(img, ".jpg", include_data_uri=True)

# 转换为字节
jpg_bytes = ImageWriter.to_bytes(img, ".jpg", quality=90)

# 创建GIF动画
frames = [frame1, frame2, frame3]
ImageWriter.create_gif(frames, "animation.gif", duration=0.5)
```

### 3. 图像处理 (ImageProcessor)

```python
# 转换为灰度
gray = ImageProcessor.to_grayscale(img)

# 归一化到[0,1]范围
normalized = ImageProcessor.normalize(img)

# 批量处理
images = [img1, img2, img3]
gray_images = ImageProcessor.batch_process(images, ImageProcessor.to_grayscale)
```

### 4. 便捷函数

```python
# 统一的加载函数 - 自动检测源类型
img1 = load_image("photo.jpg")          # 文件
img2 = load_image(image_bytes)          # 字节
img3 = load_image(base64_string)        # base64
img4 = load_image("chelsea")            # 标准图像
img5 = load_image("https://...")        # URL

# 统一的保存函数
save_image(img, "output.png")

# read_image/write_image 别名也可用
img = read_image("input.jpg")
write_image(img, "output.png")
```

## 实际使用示例

### Base64图像处理流水线

```python
from utils import *

# 加载图像
original = load_image("photo.jpg")

# 处理图像
gray = ImageProcessor.to_grayscale(original)
normalized = ImageProcessor.normalize(gray)

# 转换为base64用于Web传输
b64_data = ImageWriter.to_base64(normalized, ".png")
data_uri = ImageWriter.to_base64(normalized, ".jpg", include_data_uri=True)

# 从base64恢复
restored = load_image(b64_data)  # 自动检测base64

print(f"原始: {original.shape}")
print(f"处理后: {restored.shape}")
print(f"Base64长度: {len(b64_data)} 字符")
```

### 批量图像处理

```python
from pathlib import Path
from utils import *

# 批量处理文件夹中的图像
image_folder = Path("photos")
output_folder = Path("processed")
output_folder.mkdir(exist_ok=True)

for img_path in image_folder.glob("*.jpg"):
    # 加载图像
    img = load_image(img_path)
    
    # 处理图像
    gray = ImageProcessor.to_grayscale(img)
    normalized = ImageProcessor.normalize(gray)
    
    # 保存处理后的图像
    output_path = output_folder / f"processed_{img_path.name}"
    save_image(normalized, output_path)
    
    print(f"处理完成: {img_path.name}")
```

### Web应用集成

```python
from utils import *

def process_uploaded_image(base64_data):
    """处理从Web前端上传的base64图像"""
    
    # 从base64加载图像
    img = load_image(base64_data)  # 自动检测data URI或纯base64
    
    # 应用处理
    processed = ImageProcessor.to_grayscale(img)
    processed = ImageProcessor.normalize(processed)
    
    # 返回处理后的base64数据
    return ImageWriter.to_base64(processed, ".png", include_data_uri=True)

# 使用示例
input_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
output_data = process_uploaded_image(input_data)
```

## 高级特性

### 流式处理
```python
# 摄像头流处理
for frame in ImageResource.stream_webcam(device_id=0, max_frames=100):
    processed = ImageProcessor.to_grayscale(frame)
    # 实时处理...

# 视频流处理
for frame in ImageResource.stream_video("video.mp4"):
    # 处理每一帧...
```

### 图像信息获取
```python
info = ImageResource.get_info("image.jpg")
print(f"尺寸: {info.shape}")
print(f"类型: {info.dtype}")
print(f"格式: {info.format}")
```

## 运行演示

```bash
# 运行包的演示功能
python -m utils
```

## 特点

- ✅ **优雅的API设计** - 直观易用的类和函数命名
- ✅ **全面的格式支持** - PNG, JPEG, GIF, WebP, 等等
- ✅ **Base64完整支持** - 双向转换，支持Data URI
- ✅ **自动类型检测** - 智能识别图像源类型
- ✅ **错误处理健壮** - 清晰的错误信息和异常处理
- ✅ **高性能** - 基于ImageIO和NumPy优化
- ✅ **类型安全** - 完整的类型提示支持
- ✅ **测试覆盖** - 全面的单元测试

这个工具库让图像处理变得简单而强大！🎨