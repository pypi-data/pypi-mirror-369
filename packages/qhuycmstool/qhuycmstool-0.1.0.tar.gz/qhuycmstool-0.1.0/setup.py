from setuptools import setup, find_packages

setup(
    name="qhuycmstool",             # tên package trên PyPI
    version="0.1.0",           # version đầu tiên
    packages=find_packages(),
    py_modules=["qhuycmstool"],      # tên file chính
    install_requires=[
        "numpy",
        "pydub"
    ],
    entry_points={
        "console_scripts": [
            "mstool = mstool:main"
        ]
    },
    author="Huy",
    author_email="wuocwee@gmail.com",  # thay bằng email của ông
    description="Mini tool để nhập melody + bass và xuất MP3",
    url="https://github.com/username/mstool",  # repo nếu có
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
