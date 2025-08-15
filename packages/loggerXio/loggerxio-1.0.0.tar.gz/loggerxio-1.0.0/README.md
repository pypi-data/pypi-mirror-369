## 📦 loggerXio

🚀 Send your Python **logs** and **print statements** directly to **Telegram** using a bot.  
No complex setup — just **import**, set your bot token & chat ID, and start logging.  

---

## 🛠 1. Installation

```bash
pip install loggerXio
```

---

## ⚡ 2. Quick Setup

```python
from loggerXio import setup_logger

# Replace with your bot token and chat ID
logger = setup_logger("YOUR_BOT_TOKEN", 123456789)
```

✅ That's it! 🎉 Now all logs and `print()` messages will be sent to your Telegram chat.

---

## ⚙ 3. Parameters

All parameters default to `True` (except `level`, which defaults to `logging.INFO`).  
You can turn any of them off by setting them to `False` in `setup_logger()`.  

---

### 🔑 **bot_token** (str)
Your Telegram bot token (get it from [🤖 BotFather](https://t.me/BotFather)).

**Example:**
```python
setup_logger("YOUR_BOT_TOKEN", 123456789)
```

---

### 🆔 **chat_id** (int)
Your Telegram chat ID (can be a group or private chat).  

**Example:**
```python
setup_logger("YOUR_BOT_TOKEN", 987654321)
```

---

### 📊 **level** (logging level)
Controls the minimum log level sent to Telegram. Default: `logging.INFO`.  

**Example:**
```python
import logging
setup_logger("YOUR_BOT_TOKEN", 123456789, level=logging.ERROR)
```

---

### ⏰ **time** (bool)
Whether to include a timestamp in your logs. Default: `True`.  

**Example (disable time):**
```python
setup_logger("YOUR_BOT_TOKEN", 123456789, time=False)
```

---

### 🖥 **show_logs** (bool)
Also print logs to your console. Default: `True`.  

**Example (disable console output):**
```python
setup_logger("YOUR_BOT_TOKEN", 123456789, show_logs=False)
```

---

### 📝 **fetch_print** (bool)
Capture `print()` messages and send them to Telegram. Default: `True`.  

**Example (disable capturing print):**
```python
setup_logger("YOUR_BOT_TOKEN", 123456789, fetch_print=False)
```

---

### 📢 **level_info** (bool)
If `True`, uses standard logging levels (`INFO`, `WARNING`, `ERROR`).  
If `False`, only captures print messages. Default: `True`.  

**Example (capture only print statements):**
```python
setup_logger("YOUR_BOT_TOKEN", 123456789, level_info=False)
```

---

## 🧩 4. Full Setup Example (All Defaults)

```python
from loggerXio import setup_logger
import logging

# Setup with all default parameters
logger = setup_logger(
    "YOUR_BOT_TOKEN",  # bot_token
    123456789,         # chat_id
    level=logging.INFO,
    time=True,
    show_logs=True,
    fetch_print=True,
    level_info=True
)

# Test logging
logger.info("Hello from loggerXio!")
print("This is a print message.")
```

---

## 📌 Notes
- If you disable `level_info=True`, normal logging levels won't be used — only `print()` messages will be captured.
- Works in **private chats**, **groups**, **channels**.
- Uses threads to avoid blocking your main program.

---

## ✨ Credits & Rights
© 2025 All Rights Reserved.  
Developed and Created by

**─ㅤ𝐀ㅤʀㅤɪㅤꜱㅤᴇㅤﾒ**.  

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/wxxoxo)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/wxxoxo)
