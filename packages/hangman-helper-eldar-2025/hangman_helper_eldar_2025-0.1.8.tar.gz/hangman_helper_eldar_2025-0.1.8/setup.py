from setuptools import setup, find_packages

setup(
    name='hangman_helper_eldar_2025',               # Kitabxananın adı, PyPI-də unikal olmalıdır
    version='0.1.8',                    # Kitabxananın versiyası
    packages=find_packages(),            # Layihə içindəki bütün paketləri tapır
    install_requires=[],                 # Əgər əlavə Python kitabxanaları istifadə olunursa buraya yazılır
    description='Helper library for Hangman game',  # Qısa təsvir
    long_description=open("README.md", "r", encoding="utf-8").read(),  # Uzun təsviri README.md-dən alır
    long_description_content_type="text/markdown",  # README formatı
    author="Eldar Eliyev",              # Müəllifin adı
    author_email="liyev7773@gmail.com", # Müəllifin emaili
    url="https://github.com/eldar/neszen_helper",  # Layihənin linki (GitHub vs.)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    python_requires=">=3.12",           # Minimum Python versiyası
    keywords="hangman game helper library",  # Açar sözlər
)
