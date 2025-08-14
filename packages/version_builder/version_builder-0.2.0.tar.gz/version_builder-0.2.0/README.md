# 🚀 version_builder

🔧 **A lightweight tool for managing Git tags and versioning in CI/CD pipelines.**

---

## 📝 Features

✅ Easy to use  
✅ Works with Git tags  
✅ Simple CLI interface  
✅ Designed for CI/CD integration  
✅ Logging support  
✅ Fully testable  

---

## 🐍 Installation

```bash
pip install version_builder
```

---

## 🎮 Usage

```bash
version_builder --help
```

### Show last tag:

```bash
version_builder --last_version
```

---

## 🧪 Example Output

```bash
$ version_builder --last_version
INFO:root:v1.0.0
```

---

## 🧰 Development & Testing

```bash
pytest tests/
ruff check .
ruff format .
```

---

## 📁 Project Structure

```
version_builder/
├── cli.py     # CLI logic
├── git.py     # Git interaction
└── logger.py  # Logging setup
```

---

## 📌 License

MIT License — see [LICENSE](LICENSE)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 💌 Author

Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

---

## 🐙 GitHub

🔗 [https://gitverse.ru/dkurchigin/version_builder](https://gitverse.ru/dkurchigin/version_builder)
