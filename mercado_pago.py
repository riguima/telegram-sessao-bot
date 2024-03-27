import os
import shutil
from pathlib import Path
from random import choice

from sqlalchemy import select

from main import bot, mercado_pago_sdk, start
from telegram_session_bot.database import Session
from telegram_session_bot.models import Payment

if __name__ == '__main__':
    with Session() as session:
        while True:
            for payment in session.scalars(select(Payment)).all():
                response = mercado_pago_sdk.payment().get(
                    int(payment.payment_id)
                )['response']
                if response['status'] == 'approved':
                    message = bot.send_message(
                        int(payment.chat_id),
                        'Pagamento confirmado, segue os arquivos de sessão:',
                    )
                    for _ in range(payment.session_amount):
                        filename = choice(os.listdir('sessoes-a-venda'))
                        os.rename(
                            Path('sessoes-a-venda') / filename,
                            Path('sessoes') / 'sessoes' / filename,
                        )
                        shutil.make_archive('sessoes', 'zip', 'sessoes')
                    message = bot.send_document(
                        int(payment.chat_id), open('sessoes.zip', 'rb')
                    )
                    os.remove('sessoes.zip')
                    for filename in os.listdir(Path('sessoes') / 'sessoes'):
                        os.rename(
                            Path('sessoes') / 'sessoes' / filename,
                            Path('sessoes-vendidas') / filename,
                        )
                    start(message)
                    session.delete(payment)
                    session.commit()
