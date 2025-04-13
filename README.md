# 🗂️ EXDS
🔍 **EXDS** is a lightweight yet powerful tool to exploit publicly exposed `.DS_Store` files on websites. It automatically **parses the content** and **recursively downloads all hidden files and folders**.

> Built for red teamers, bug bounty hunters, and OSINT researchers who want to reveal hidden web content.  
> 🌍 Open-source, 100% free, beginner-welcoming.

---

## 🚀 Features

- 🔁 Recursive file & folder extraction
- 🧠 Automatic `.DS_Store` parsing
- 🛡️ Handles errors and keyboard interrupts gracefully
- 📂 Downloads organized inside `output/your-target.com/`

---

## 📦 Installation

```bash
git clone https://github.com/williamlaurent/exds.git
cd exds
pip install -r requirements.txt
