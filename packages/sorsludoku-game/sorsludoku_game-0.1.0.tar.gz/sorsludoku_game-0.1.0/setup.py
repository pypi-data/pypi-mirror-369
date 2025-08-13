from setuptools import setup, find_packages
import pathlib

# README.md içeriğini uzun açıklama olarak al
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="sorsludoku",  # pip install sorsludoku
    version="1.0",
    author="Mel1h & ChatGPT(OpenAI)",
    author_email="orslumelih@gmail.com",
    description="A simple Sudoku game built with Streamlit and NumPy",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "streamlit"
    ],
    python_requires=">=3.7",
    license = "MIT",
)
