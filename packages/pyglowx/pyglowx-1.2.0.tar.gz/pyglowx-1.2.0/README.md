# pyglowx

![GitHub Repo stars](https://img.shields.io/github/stars/BirukBelihu/pyglowx)
![GitHub forks](https://img.shields.io/github/forks/BirukBelihu/pyglowx)
![GitHub issues](https://img.shields.io/github/issues/BirukBelihu/pyglowx)
[![PyPI Downloads](https://static.pepy.tech/badge/pyglowx)](https://pepy.tech/projects/pyglowx)<br>
![Python](https://img.shields.io/pypi/pyversions/pyglowx)

**pyglowx** is a lightweight, cross-platform, markdown-style console text formatter library for python.

---
GitHub: [pyglowx](https://github.com/BirukBelihu/pyglowx)
---

## ✨ Features

- 💻Cross platform (**Windows**, **Linux**, **macOS**)
- ✅ **Markdown-style tags**: `[red]`, `[green bold]`, `[italic underline]`
- 🎨 **Foreground & background colors with support for custom rgb(235, 64, 52) & hexadecimal colors(#eb4034) along with some predefined ANSI
  colors**
- 🪄 **Text styles**: `bold`, `dim`, `italic`, `underline`, `blink`, `strike` & more
- 🔄 **Nested tag support**

---

### Sample

![PyGlow Sample](images/sample_1.png)

## 📦 Installation

```
pip install pyglowx
```

You can also install pyglowx from source code. source code may not be stable, but it will have the latest features and
bug fixes.

Clone the repository:

```
git clone https://github.com/birukbelihu/pyglowx.git
```

Go inside the project directory:

```bash
cd pyglowx
```

Install pyglow:

```
pip install -e .
```

---

## 🧠 Example Usage

```python
from pyglowx.pyglowx import PyGlowx

PyGlowx.print("[cyan bold]pyglowx[/] is a lightweight, [bold]markdown-style console text formatter[/] library for Python. \nIt enables developers to output styled text in the terminal using simple and readable tags like `[red bold]Error[/]`.")
```

### Output

![PyGlowX Output](images/sample_2.png)

---

## 📦 Library Overview

| Function                              | Description                                               |
|---------------------------------------|-----------------------------------------------------------|
| `PyGlowx.parse(str text)`             | Converts your markdown-style tags to ANSI-coded string    |
| `PyGlowx.print(str text)`             | Prints the text with the provided style tags              |
| `PyGlowx.prints(str text, str style)` | Prints the text with a provided style for the entire text |

---

## 📄 Demo & Documentation

Check out [main.py](https://github.com/birukbelihu/pyglowx/blob/master/main.py) for:

- ✅ Full usage examples
- ✅ Tag reference documentation
- ✅ Quickstart code snippets

---

## 🙌 Contribute

Want to improve `pyglowx`? Contributions are welcome!

---

Shine bright in your terminal! 🚀
Made with ❤️ by **[BirukBelihu](https://github.com/birukbelihu)**

---

## 📢 Social Media

- 📺 [YouTube: @pythondevs](https://youtube.com/@pythondevs?si=_CZxaEBwDkQEj4je)

---

## 📄 License

This project is licensed under the **Apache License 2.0**. See
the [LICENSE](https://github.com/birukbelihu/pyglowx/blob/master/LICENSE) file for details.