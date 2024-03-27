import os
from pathlib import Path
from uuid import uuid4

import mercadopago
import qrcode
from telebot import TeleBot
from telebot.util import quick_markup

from telegram_session_bot.config import config
from telegram_session_bot.database import Session
from telegram_session_bot.models import Payment

bot = TeleBot(config['BOT_TOKEN'])
mercado_pago_sdk = mercadopago.SDK(config['MERCADO_PAGO_ACCESS_TOKEN'])


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Bem vindo a Leadsstore, um dos melhores fornecedores de sessões para telegram do Brasil. Por favor, se tiver dúvidas, contate o suporte, temos sessões novas todos os dias.\n\nAs sessões são criadas e vendidas apenas para uma única pessoa, quando você compra, ela é removida do bot. Elas também são criadas utilizando API ID e HASH nossas para melhor qualidade das contas.',
        reply_markup=quick_markup(
            {
                '📊 Tabela de valores': {'callback_data': 'price_table'},
                '📦 Comprar sessão': {'callback_data': 'buy_session'},
                'Suporte': {
                    'url': 'https://api.whatsapp.com/send?phone=5584998493595'
                },
                'Canal do Youtube': {
                    'url': 'https://www.youtube.com/channel/UCuK62MxQZFulRALHMq6hS9w'
                },
            },
            row_width=1,
        ),
    )


@bot.callback_query_handler(func=lambda c: c.data == 'price_table')
def price_table(callback_query):
    bot.send_message(
        callback_query.message.chat.id,
        '📋 Tabelas de valores :\n\n📊 Todas as contas são verificadas:\n💵 O valor por unidade é: R$ 4,50\n\nBoas compras 😊',
        reply_markup=quick_markup(
            {
                'Voltar 🔙': {'callback_data': 'return'},
            }
        ),
    )


@bot.callback_query_handler(func=lambda c: c.data == 'buy_session')
def buy_session(callback_query):
    if os.listdir('sessoes-a-venda'):
        bot.send_message(
            callback_query.message.chat.id,
            f'Estamos com {len(os.listdir("sessoes-a-venda"))} sessões disponíveis',
            reply_markup=quick_markup(
                {
                    'Comprar': {'callback_data': 'buy_session_action'},
                    'Voltar 🔙': {'callback_data': 'return'},
                },
                row_width=1,
            ),
        )
    else:
        bot.send_message(
            callback_query.message.chat.id,
            'Estamos sem estoque no momento.',
            reply_markup=quick_markup(
                {
                    'Voltar 🔙': {'callback_data': 'return'},
                }
            ),
        )


@bot.callback_query_handler(func=lambda c: c.data == 'buy_session_action')
def buy_session_action(callback_query):
    bot.send_message(
        callback_query.message.chat.id,
        'Digite a quantidade de sessões que deseja',
    )
    bot.register_next_step_handler(callback_query.message, on_session_amount)


def on_session_amount(message):
    try:
        if int(message.text) > len(os.listdir('sessoes-a-venda')) or int(message.text) <= 0:
            bot.send_message(
                message.chat.id,
                f'Digite uma quantidade de 1 a {len(os.listdir("sessoes-a-venda"))}',
            )
            bot.register_next_step_handler(message, on_session_amount)
            return
        payment_data = {
            'transaction_amount': config['SESSION_PRICE'] * int(message.text),
            'description': 'Sessões Telegram',
            'payment_method_id': 'pix',
            'installments': 1,
            'payer': {
                'email': config['PAYER_EMAIL'],
            },
        }
        response = mercado_pago_sdk.payment().create(payment_data)['response']
        qr_code = response['point_of_interaction']['transaction_data'][
            'qr_code'
        ]
        bot.send_message(
            message.chat.id,
            'Realize o pagamento que iremos te enviar os arquivos de sessão',
        )
        bot.send_message(message.chat.id, 'Chave Pix abaixo:')
        bot.send_message(message.chat.id, qr_code)
        qr_code = qrcode.make(qr_code)
        qr_code_filename = f'{uuid4()}.png'
        qr_code.save(qr_code_filename)
        bot.send_photo(
            message.chat.id, open(Path(qr_code_filename).absolute(), 'rb')
        )
        os.remove(Path(qr_code_filename).absolute())
        with Session() as session:
            payment = Payment(
                session_amount=int(message.text),
                chat_id=str(message.chat.id),
                payment_id=str(response['id']),
            )
            session.add(payment)
            session.commit()
    except ValueError:
        bot.send_message(message.chat.id, 'Digite somente números')
        bot.register_next_step_handler(message, on_session_amount)


@bot.callback_query_handler(func=lambda c: c.data == 'return')
def return_to_menu(callback_query):
    start(callback_query.message)


if __name__ == '__main__':
    bot.infinity_polling()
