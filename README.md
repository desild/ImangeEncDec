# 🔐 Image Encryption & Decryption WebApp

This is a **Flask-based web application** that provides secure image encryption and decryption functionalities using advanced cryptographic methods. It ensures that sensitive images are protected for confidentiality and privacy.

---

## 📌 Features

- 🔒 **Encrypt Images**: Upload and encrypt images using a secure algorithm.
- 🔓 **Decrypt Images**: Decrypt previously encrypted images to restore them.
- 🖼️ **Image Preview**: View uploaded images before/after transformation.
- 🗃️ **SQLite3 Integration**: Encrypted data and file info are stored securely in a lightweight database.
- 🧠 **User-Friendly Interface**: Simple, clean UI built with HTML/CSS for smooth interaction.

---

## 🛠️ Tech Stack

| Layer           | Technology         |
|----------------|--------------------|
| Frontend       | HTML, CSS          |
| Backend        | Python (Flask)     |
| Database       | SQLite3            |
| Libraries Used | OpenCV, NumPy, PIL, Cryptography |

---

## 🚀 Getting Started

### 🔧 Prerequisites

- Python 3.7+
- `pip` package manager



ImangeEncDec/
├── templates/
│   ├── index.html
│   └── result.html
├── static/
├── app.py
├── encryption.py
├── decryption.py
├── database.db
└── README.md


### 📥 Installation

```bash
git clone https://github.com/desild/ImangeEncDec.git
cd ImangeEncDec
pip install -r requirements.txt
