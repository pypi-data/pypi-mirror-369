# WB-WriteupBuilder

**WriteupBuilder** is a command-line tool for creating clean, organized CTF write-ups in Markdown — interactively or using a ready-to-fill advanced template.

Whether you want to quickly document your hacking process or prepare a professional post-CTF report, `wb` guides you through each section and saves your work in a well-structured `.md` file.

---

## ✨ Features

- **Interactive mode** – Answer prompts to build a Markdown write-up step by step  
- **Pre-written template** – Generate a detailed, advanced CTF template with `--template`  
- **Color-coded prompts** for better readability    
- **Multi-line input support**
- **Markdown formatting**


---

## 📦 Installation

### Using `pipx` (recommended):

```bash
pipx install wb-writeupbuilder
````

### Using `pip`:

```bash
pip install wb-writeupbuilder
```

### After installation, you can run:

```bash
wb
```

---

## 🚀 Usage

### **1️⃣ Interactive Mode**

Fill in each section via guided prompts.

```bash
wb
```

You’ll be asked for:

- Challenge overview (name, platform, category, etc.)
    
- Initial info
    
- Initial analysis
    
- Exploitation steps
    
- Flags
    
- Takeaways
    

The result is saved as:

```
<challenge_name>-<platform>.md
```

---

### **2️⃣ Advanced Template Mode**

Generate a **pre-written detailed Markdown template** for manual filling.

```bash
wb -t -fn MyWriteup.md
```

**Options:**

|Flag|Description|
|---|---|
|`-fn`, `--filename`|Output file name (default: `WriteupTemplate.md`)|
|`-t`, `--template`|Use the advanced pre-written template|

---

## 🧪 Example Run

Below are **two** example sessions: one for the interactive flow and one for the template flow. This shows the prompts and sample user input.

### 1) Interactive session

![Demo](gifs/demo1.gif)

**Notes**

* Filenames are sanitized to lowercase and spaces/special characters are replaced with underscores.

* For multi-line answers the tool expects you to type `END` on a new line to finish. Pressing Enter immediately at the first prompt of a multiline field skips that section.

---

### 2) Template mode (quick)

![Demo](gifs/demo.gif)

---

## 📂 Output Example

```markdown
# 📌 Challenge Overview

| 🧩 Platform / Event | picoCTF |
| ------------------- | -------- |
| 📅 Date             | 2025-08-11 |
| 🔰 Category         | Reverse Engineering |
| ⭐ Difficulty        | Medium |
| 🎯 Points           | 200 |

---

# 📋 Initial Info:
Challenge description...

---

# 🔍 Initial Analysis:
First thoughts...

---

# ⚙️ Exploitation
Steps taken...

---

# 🚩 Flag -> picoCTF{example_flag}

---

# 📚 Takeaways
Things learned...
```

---

## 🛠 Development

Clone the repo:

```bash
git clone https://github.com/yourusername/writeupbuilder.git
cd writeupbuilder
pip install -e .
```

---
## 📂 Project Structure

```
WB-WriteupBuilder/
├── gifs/
│   ├── demo.gif
│   └── demo1.gif
├── wb/
│   ├── __init__.py
│   └── cli.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── .gitignore
```

---

## 📜 Author

[Ph4nt01](https://github.com/Ph4nt01)
