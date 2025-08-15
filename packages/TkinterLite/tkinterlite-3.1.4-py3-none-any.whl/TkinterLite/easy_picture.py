import os
import tkinter

from PIL import Image, ImageTk


class EasyPicture:
    def __init__(self, window, img_path, size=(350, 350), side=tkinter.RIGHT, expand=False, fill=tkinter.NONE,
                 padx=0, pady=0, layout="pack", row=0, column=0, rowspan=1, columnspan=1,
                 keep_aspect_ratio=True, auto_resize=False, **kwargs):
        self._window = window
        self._img_path = img_path
        self._size = size
        self._keep_aspect_ratio = keep_aspect_ratio
        self._auto_resize = auto_resize
        self._kwargs = kwargs

        if not os.path.isfile(self._img_path):
            raise FileNotFoundError(f"Image file not found: {self._img_path}")

        # 加载原始图片
        self._orig_img = Image.open(self._img_path)
        self._photo = None  # 占位

        # 创建Label
        self._label = tkinter.Label(self._window)
        self._label.image = None  # 占位

        # 初始显示
        self._update_image(self._size)

        # 布局
        if layout == "grid":
            self._label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                             padx=padx, pady=pady, **self._kwargs)
        else:
            self._label.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, **self._kwargs)

        # 自动调整大小
        if self._auto_resize:
            # 监听容器大小变化
            self._label.bind('<Configure>', self._on_resize)

    def _update_image(self, size):
        """根据目标size和锁定比例设置图片"""
        img = self._orig_img
        if self._keep_aspect_ratio:
            img = self._resize_keep_aspect(img, size)
        else:
            img = img.resize(size, Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)
        self._label.config(image=self._photo)
        self._label.image = self._photo  # 防止被回收

    def _resize_keep_aspect(self, img, target_size):
        """按比例缩放图片到目标区域内"""
        orig_w, orig_h = img.size
        target_w, target_h = target_size
        ratio = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        return img.resize((new_w, new_h), Image.LANCZOS)

    def _on_resize(self, event):
        """容器大小变化时自动调整图片"""
        new_size = (event.width, event.height)
        self._update_image(new_size)

    def get_label(self):
        return self._label
