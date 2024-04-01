# Telegram Session Bot

Bot para venda de sessões do Telegram.

# Instalação

Crie um arquivo chamado `.config.toml` e defina as seguintes variáveis:

```
MERCADO_PAGO_ACCESS_TOKEN = "access_token_mercado_pago"
BOT_TOKEN = "telegram_bot_token"
DATABASE_URI = "sqlite:///database.db" # URI do banco de dados
PAYER_EMAIL = "email_do_pagador"
SESSION_PRICE = 4.5 # Valor de cada sessão
START_MESSAGE = "Mensagem quando der /start"
```

Segue script de instalação:

```
git clone https://github.com/riguima/telegram-session-bot
cd telegram-session-bot
mkdir -p sessoes/sessoes sessoes-a-venda sessoes-vendidas
pip install -r requirements.txt
```

Rode com `python main.py && python mercado_pago.py`

Na pasta `sessoes-a-venda` coloque todos os arquivos de sessão que estão disponiveis para compra, automaticamente serão movidas para a pasta `sessoes-vendidas` quando o pagamento for confirmado
