# 🧠 tracernaut — Visualize Python Execution Like Never Before

[![PyPI Version](https://img.shields.io/pypi/v/tracernaut.svg)](https://pypi.org/project/tracernaut/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tracernaut.svg)](https://pypi.org/project/tracernaut/)
[![License](https://img.shields.io/github/license/lseman/tracernaut)](LICENSE)

> An intelligent, interactive visualizer for step-by-step Python code execution and memory tracing.  
> Built for students, educators, and curious minds.  

---

## 🚀 What is Tracernaut?

**Tracernaut** is a pedagogical tool that captures and **visually traces the execution** of Python code — including variable states, memory references, object relationships, and the call stack — using rich, annotated diagrams.

It turns abstract Python behavior into something **visible**, **intuitive**, and **beautifully structured**.

---

## 📸 Example

```python
from tracernaut import tracernaut

@tracernaut
def example():
    a = [1, 2, 3]
    b = {'x': a, 'y': 4}
    a.append(5)
    return b

example()
```

This opens an interactive widget (in Jupyter) that lets you step through each line and visualize changes in memory, objects, variables, and control flow.