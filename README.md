# telegram-bot-chatgpt

My telegram bot for ChatGPT (written with the help of ChatGPT)
Bot is written in Python and is tested with the Python 3.10. 

## Preparations

1. Create Telegram bot and get bot token:
    - Bot is created using **@BotFather** in Telegram.
2. In your ChatGPT account (https://chat.openai.com) create your API key.

## Parameters

- TELEGRAM_API_TOKEN: your Telegram bot token. This parameter must be provided.
- CHATGPT_API_KEY: your ChatGPT API key. This parameter must be provided.
- GPT_MODEL: Which GPT model is going to be used for completion. Default model is "gpt-3.5-turbo".
    - To get list of models look into the documentation: [OpenAI documentation](https://platform.openai.com/docs/api-reference/models/list)
- ALLOWED_CHAT_IDS: Comma separated list of allowed account IDs.
    - When no parameter is defined, then bot operated as public.
    - When list of account IDs is given, bot communicates only with them.
    - To get ID of Telegram account, use **@userinfobot**: forward to it message from the account you want to get ID from.
- CHAT_HISTORY_SIZE: default value is 20 - it means that chat history will keep 10 messages of user and 10 answers from ChatGPT. Don't make history too large, it might not be fully processed due to exhausture of max_tokens limit. 
- MAX_TOKENS: The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. Default value is 500. Maximum possible value is 4096. If you try to set value higher, program will set it to 4096.

## Building and running

### Requirements

- Docker
- Docker-compose

### Instructions

1. Clone repository
2. Enter into the `src` directory.
3. Copy `docker-compose-template.yaml` to `docker-compose.yaml` in this directory.
4. In the `docker-compose.yaml` file set values for: TELEGRAM_API_TOKEN and CHATGPT_API_KEY. If you want private bot, also provide list of comma separated account IDs.
5. Check that your docker-compose file is correct: `docker-compose config`.
6. If no errors are found, run in the same directory: `docker-compose up -d`.

## Bot commands

- **/start**: Start the bot
- **/help**:  Show help message with commands
- **/info**: Get information about the bot
- **/status**: Check the bot's status
- **/newtopic**: Clear ChatGPT conversation history
