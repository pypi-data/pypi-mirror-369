# B.U.R.I - Basic Universal Remote Interface

<img width="563" height="729" alt="image" src="https://github.com/user-attachments/assets/fd44ac00-cf3f-46b1-be0e-a74669280599" />

B.U.R.I (Basic Universal Remote Interface) is a **powerful, stateful, and user-friendly Python-based client** for interacting with PHP webshells. Designed for **penetration testers** and **security professionals**, B.U.R.I demonstrates the impact of file upload vulnerabilities and provides a rich command-line interface for managing remote servers.

---

## ✨ Features

- **Stateful `cd` Command**: Navigate the remote filesystem seamlessly, with the client tracking your current directory, just like a local terminal.
- **Rich User Interface**: Built with `rich` and `prompt-toolkit` libraries for a modern, colorful, and interactive terminal experience with animations.
- **Multi-Command Execution**: Execute multiple commands in a single line, separated by semicolons (`;`).
- **System Reconnaissance**: Use the built-in `sysinfo` command to quickly gather critical information about the target system.
- **Persistent Command History**: Commands are saved between sessions for easy recall.
- **Secure Webshell Generation**: Generates an advanced, JSON-based PHP webshell that communicates over POST requests for increased discretion compared to GET-based shells.

---

## ⚙️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/joelindra/buri.git
   cd buri
   ```

2. **Install Dependencies**:
   Ensure you have **Python 3.6+** installed, then install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

B.U.R.I provides two primary commands: `create` and `run`.

### 1. Creating the Webshell
Generate a PHP webshell file to upload to the target server.

**Command**:
```bash
python buri.py create <file_path> --password <your_password>
```

**Example**:
```bash
python buri.py create shell.php --password mysecretpassword
```

### 2. Running the Interactive Shell
Connect to the uploaded webshell using the `run` command to launch the interactive shell.

**Command**:
```bash
python buri.py run <url> --password <your_password>
```

**Example**:
```bash
python buri.py run https://example.com/uploads/shell.php --password mysecretpassword
```

---

## 🖥️ Client-Side Commands

Once inside the interactive shell, use these special commands. Any other command is executed on the remote server.

| Command | Description | Example |
|---------|-------------|---------|
| `sysinfo` | Displays detailed information about the remote system. | `root@example.com:/var/www$ sysinfo` |
| `upload` | Uploads a file from your local machine to the remote server. | `root@example.com:/var/www$ upload /local/path/to/file.txt /remote/path/file.txt` |
| `download` | Downloads a file from the remote server to your local machine. | `root@example.com:/var/www$ download /remote/path/config.php /local/path/to/save/config.php` |
| `cd` | Changes the current working directory on the remote server. | `root@example.com:/var/www$ cd ../tmp` |
| `clear` / `cls` | Clears the local terminal screen. | `root@example.com:/var/www$ clear` |
| `help` | Displays the help menu for client-side commands. | `root@example.com:/var/www$ help` |
| `exit` | Closes the webshell session. | `root@example.com:/var/www$ exit` |

---

## ⚠️ Disclaimer

**B.U.R.I is intended for educational purposes and authorized security testing only.** Using this tool to gain unauthorized access to computer systems is **illegal** and **unethical**. The author is not responsible for any misuse or damage caused by this program. Always ensure you have explicit permission to test systems.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. For major changes, open an issue first to discuss your ideas.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

## 📬 Contact

For questions, suggestions, or issues, please open an issue on the [GitHub repository](https://github.com/joelindra/buri).

---

## Screenshoot

<img width="1863" height="893" alt="image" src="https://github.com/user-attachments/assets/2b37588b-ff71-452f-8f2c-e70a984f2a54" />

<img width="1433" height="541" alt="image" src="https://github.com/user-attachments/assets/9acf1050-b271-4cf2-84ae-8dde1ebbfdf4" />

<img width="1498" height="847" alt="image" src="https://github.com/user-attachments/assets/217799a1-b37c-4310-988b-358b82c4d81a" />

