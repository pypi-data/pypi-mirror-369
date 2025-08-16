## tux-gpt

`tux-gpt` is an interactive command-line tool that leverages GPT-based language models to provide intelligent, conversational assistance directly within your terminal. It enables on-the-fly code generation, debugging help, technical explanations, and more—all without leaving the command-line environment.

Designed for developers and tech enthusiasts, **tux-gpt** streamlines workflows by integrating AI assistance seamlessly into terminal sessions, making complex tasks easier and faster to accomplish via intuitive, context-aware command-line interactions.

---

## Prerequisites

- Python 3.7+
- Pip (Python package manager)
- An OpenAI API key (see next section)

---

## Setup and Configuration

1. **Install**:
   From PyPI:
   ```bash
   pip install tux-gpt
   ```
   From source:
   ```bash
   git clone https://github.com/fberbert/tux-gpt.git
   cd tux-gpt
   pip install -r requirements.txt
   pip install .
   ```

2. **Get your OpenAI API key**:
   - Sign up or log in at [https://platform.openai.com](https://platform.openai.com).
   - Navigate to **API Keys** and create a new key.
   - Copy the generated key.

3. **Configure** your environment variable:
   - **Linux/macOS (bash/zsh)**:
     ```bash
     echo 'export OPENAI_API_KEY="<your_api_key>"' >> ~/.bashrc
     source ~/.bashrc
     ```
   - **Windows (PowerShell)**:
     ```powershell
     [Environment]::SetEnvironmentVariable('OPENAI_API_KEY', '<your_api_key>', 'User')
     ```

  *Note:* On first run, tux-gpt will create the directory `~/.tux-gpt/` containing:
  - `config.json`: CLI configuration (e.g., default model);
  - `history.json`: persistence of the last 20 messages (user + assistant);
  - `input_history`: command history for navigation with ↑/↓ arrow keys.

---

## Usage

### Start the interactive session:
```bash
tux-gpt
```

<div align="center">
  <img src="https://raw.githubusercontent.com/fberbert/tux-gpt/master/assets/img/sample.gif" alt="Demonstração de uso" width="600">
</div>


### Example commands

- **Search the web for current news:**
  ```
  > Find the latest headlines about OpenAI
  ```

- **Look up technical documentation:**
  ```
  > What is the syntax for Python's list comprehensions?
  ```

- **Fetch real-time data (e.g., stock price):**
  ```
  > What's the current stock price of AAPL?
  ```

- **Summarize a web article:**
  ```
  > Summarize the top result for "machine learning trends 2025"
  ```

---

## Memory & Command History

tux-gpt now persists your conversation and command history locally in the `~/.tux-gpt/` directory. The files created are:
- `config.json`: CLI configuration, such as the default model.
- `history.json`: stores the last 20 messages (user + assistant) to maintain context between sessions and limit token usage.
- `input_history`: command history used by `readline` for navigation with ↑/↓ arrow keys.

Features:
- On startup, the conversation history is automatically reloaded from `history.json`, limited to the last 20 messages to prevent token overload.
- You can navigate previous commands using the ↑ and ↓ arrow keys at the prompt.
- To reset the conversation or command history, simply remove the corresponding files in `~/.tux-gpt/`.

---

## Customization

You can configure the default model or terminal spinner settings by editing the configuration file at `~/.tux-gpt/config.json`. Example:
```json
{
  "model": "gpt-4o-mini"
}
```

---

## Troubleshooting

- **"OPENAI_API_KEY not set"**: Ensure you exported the variable correctly and restarted your shell.
- **Slow responses**: Check your internet connection or change to a faster model in the config.

---

## License

MIT © 2025 tux-gpt contributors



---

## Configuration File (~/.tux-gpt/config.json)

In the first run, **tux-gpt** will create a configuration file at `~/.tux-gpt/config.json`. This file contains settings for the default model. You can customize the behavior of **tux-gpt** by editing the configuration file located at `~/.tux-gpt/config.json`. This file allows you to set the default model and other preferences.

Example config file to set the model:

```json
{
  "model": "gpt-5-mini"
}
```

The default model is gpt-5-mini.

# Model Compatibility

**Important:** The model you choose must support web search capability.
Currently, only the following models support the web search tool:

- gpt-5-mini
- gpt-4.1
- gpt-4.1-mini

For more details, see the official OpenAI documentation on web search tools and limitations:

https://platform.openai.com/docs/guides/tools-web-search?api-mode=responses#limitations

---

## Author

**Fábio Berbert de Paula**

- Email: <fberbert@gmail.com>
- Website: [https://fabio.automatizando.dev](https://fabio.automatizando.dev)
- Founder of [www.vivaolinux.com.br](https://www.vivaolinux.com.br)
- Over 25 years of experience as a developer

## Official Repository

- [https://github.com/fberbert/tux-gpt](https://github.com/fberbert/tux-gpt)

