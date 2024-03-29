# telegram-bot-chatgpt

My telegram bot for ChatGPT (written with the help of ChatGPT)
Bot is written in Python and is tested with the Python 3.10 and Python 3.11.
Dockerfile uses **Python:3.11-slim** base image.

Bot supports:
- Chat mode via GPT Chat Completion API
- Web search mode: Web search results from Duckduckgo engine are completed via GPT Compltion API

## Preparations

1. Create Telegram bot and get bot token:
    - Bot is created using **@BotFather** in Telegram.
2. In your ChatGPT account (https://chat.openai.com) create your API key.

## Parameters

- TELEGRAM_API_TOKEN: your Telegram bot token. This parameter must be provided.
- OPENAI_API_KEY: your ChatGPT API key. This parameter must be provided.
- GPT_CHAT_MODEL: Which GPT model is going to be used for chat completion.
    - To get list of models look into the documentation: [OpenAI documentation](https://platform.openai.com/docs/api-reference/models/list)
    - Default model: "gpt-3.5-turbo".
- ALLOWED_CHAT_IDS: Comma separated list of allowed account IDs.
    - When no parameter is defined, then bot operated as public.
    - When list of account IDs is given, bot communicates only with them.
    - To get ID of Telegram account, use **@userinfobot**: forward to it message from the account you want to get ID from.
- CHAT_HISTORY_SIZE: How many chat messages are going to be stored. If set to 10, it means it will keep 5 messages of user and 5 answers from ChatGPT. Don't make history too large, it might not be fully processed due to exhausture of max_tokens limit. 
    - Default value: 20
    - Max value: 50
- MAX_TOKENS: The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length.
    - Default value: 500
    - Max value: 4096
- NUM_SEARCH_RESULTS: Maximum number of Duckduckgo search results used as input for completion.
    - Default value: 3
    - Max value: 10

## Building and running

### Requirements

- Docker (or Podman, but do symlink `docker` to `podman`)
- Docker-compose (or Podman-compose, but do symlink `docker-compose` to `podman-compose`)

### Instructions

1. Clone repository
2. Enter into the `src` directory.
3. Build image using `make build` or `make build-latest` commands.
    - `make build` builds image with tag `telegram-bot:$(VERSION)`.
    - `make build-latest` builds image with tag `telegram-bot:latest` and with `telegram-bot:$(VERSION)`.
3. Copy `docker-compose-template.yaml` to `docker-compose.yaml` in this directory.
4. In the `docker-compose.yaml` file set values for: TELEGRAM_API_TOKEN and CHATGPT_API_KEY. If you want private bot, also provide list of comma separated account IDs.
5. Check that your docker-compose file is correct: `docker-compose config`.
6. If no errors are found, run in the same directory: `docker-compose up -d`.

## `make` commands

Makefile contains following commands:
- `build`: Build image with tag `telegram-bot:$(VERSION)`.
- `build-latest`: Build image with tag `telegram-bot:latest` and with `telegram-bot:$(VERSION)`.
- `install-requirments`: Creates Python virtual environment and installs requirements for running bot.
- `install-dev-requirments`: Creates Python virtual environment and installs requirements for running bot and python linter and LSP server.
- `clean-enviroment`: Removes Python virtual environment and `__pycache__` directories.
- `clean-docker`: Removes built docker images: `telegram-bot:$(VERSION)` and `telegram-bot:latest`.
- `clean-all`: `clean-enviroment` and `clean-docker` and removes source Docker image used by the Dockerfile.

## Bot commands

- **/start**: Start the bot
- **/help**:  Show help message with commands
- **/info**: Get information about the bot
- **/status**: Check the bot's status
- **/newtopic**: Clear ChatGPT conversation history
- **/regen**: Regenerate ChatGPT response on the last query
- **/web `<query>`**: Search with Duckduckgo and process results with ChatGPT using `<query>`
