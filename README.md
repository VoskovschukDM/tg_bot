# tg_bot — Telegram Bot for Party Purchuase Management
## Project Overview

**tg_bot** is a Telegram bot designed to help users manage purchuases that was done fore friends and retur money to each others. The bot allows users to create groups, add items, split their prices manage payment directly inside Telegram. It leverages the Telegram Bot API using Python and the `aiogram` asynchronous framework to handle bot logic and communications.

This project provides a robust and scalable example of building feature-rich Telegram bots using modern Python async libraries, including command and state management for interactive user sessions.

---

## Table of Contents

- [Features](#features)  
- [Technologies](#technologies)  
- [Setup and Installation](#setup-and-installation)  
- [Project Structure](#project-structure)  
- [Key Components and Modules](#key-components-and-modules)  
- [How to Use the Bot](#how-to-use-the-bot)  

---

## Features

- **Task Creation:** Users can add new tasks with descriptions.  
- **Task Listing:** View all or filtered lists of current tasks.  
- **Task Completion:** Mark tasks as done or remove them.  
- **User Interaction:** Uses Telegram inline buttons and messages for seamless UX.  
- **Asynchronous Processing:** Bot uses async API calls for performance and responsiveness.  
- **State Management:** Supports multistep flows with user states using aiogram’s FSM.  

---

## Technologies

- **Python 3.8+**  
- **aiogram:** Asynchronous Telegram Bot API framework  
- **asyncio:** Python’s asynchronous I/O module  
- **SQLite from aiosqlite:** For task persistence (confirm in code)  
- **logging:** Tracking state of bot
- **GitHub:** Version control and project hosting  

---

## Setup and Installation

1. **Clone the Repository**
  ```bash
  git clone https://github.com/VoskovschukDM/tg_bot.git
  cd tg_bot
  ```
2. **Create Virtual Environment**
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux / Mac
  venv\Scripts\activate     # Windows
  ```
3. **Install Dependencies**
  ```bash
  pip install -r requirements.txt
  ```
4. **Set Telegram Bot Token**
  ```bash
  BOT_TOKEN='your_telegram_bot_token'
  ```
5. **Rename bot.env.example to bot.env**
  ```bash
  ren bot.env.example bot.env
  ```
6. **Run the Bot**
  ```bash
  python main.py
  ```

---

## Project Structure
  ```bash
  tg_bot/
  ├── main.py                  # Bot entry point
  ├── body.py                  # Bot backend 
  ├── databases.py             # Database related functions
  ├── keyboards.py             # Setting keyboards
  ├── bot.env.example          # Example if token file
  ├── config.py                # Configuration parameters, env variables
  ├── requirements.txt         # Required Python packages
  └── README.md                # Project overview and instructions (this doc)
  ```

---

## Key Components and Modules

### `main.py`

- The main entry point for the bot.
- Initializes the bot, sets up the asyncio event loop.
- Starts long polling to listen for Telegram updates.

### `body.py`

- Processes information transforming from database answers

### `databases.py`

- Completes commits to databases

### `keyboards.py`

- Reusable inline and reply keyboard definitions for task-related actions and menus.

### `bot.env.example`

- Contains Telegram Bot Token

### `config.py`

- Configuration file where environment variables or bot parameters are defined.

---

## How to Use the Bot

Once the bot is running and connected to Telegram:

1. Start interacting by sending `/start`.
2. Create group and invite some friends to it.
3. Add purchases to bot.
4. Use `/personal_bill` to see amount of money, you have to pay to your friends.
5. Pay this amount and the use `/pay` to close the debt

---

Thank you for checking out the **tg_bot** project! Contributions and feedback are welcome.

---

*Powered by [VoskovschukDM](https://github.com/VoskovschukDM)*
