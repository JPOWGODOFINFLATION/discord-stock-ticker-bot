import logging
from os import getenv

import discord
from requests import get

from util import stock, crypto, crypto_search, add_bot, add_private_bot

TICKER_TYPES = [
    'stock',
    'crypto'
]

def invite_url(client_id: str):

    return f'https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot'

class DiscordStockTickerBot(discord.Client):

    async def on_ready(self):
        logging.info('Logged in')

    async def on_message(self, message):

        if message.author.id == self.user.id:
            return

        if message.author.id == int(getenv('ADMIN_ID')):
            
            if message.content.startswith('!addbot'):

                opts = message.content.split(' ')
                logging.info(opts)

                if len(opts) < 3:
                    await message.reply('usage: !addbot <client_id> <token>', mention_author=True)
                    return
                
                if add_bot(opts[1], opts[2]):
                    await message.reply('Bot added!', mention_author=True)
                    return
                else:
                    await message.reply('Unable to add new bot.', mention_author=True)
                    return
            
            if message.content.startswith('!addprivatebot'):

                opts = message.content.split(' ')
                logging.info(opts)

                if len(opts) < 6:
                    await message.reply('usage: !addprivatebot <client> <client_id> <token> <ticker> <type>', mention_author=True)
                    return
                
                if opts[5] not in TICKER_TYPES:
                    await message.reply(f'valid types: {TICKER_TYPES}', mention_author=True)
                    return
                
                if add_private_bot(opts[1], opts[2], opts[3], opts[4], opts[5]):
                    await message.reply('Bot added!', mention_author=True)
                    return
                else:
                    await message.reply('Unable to add new bot.', mention_author=True)
                    return

        if message.content.startswith('!ticker'):

            opts = message.content.split(' ')
            logging.info(opts)

            if len(opts) < 3:
                await message.reply('usage: !ticker <stock/crypto> <ticker>', mention_author=True)
                return

            security = opts[1]
            ticker = opts[2]

            if security not in TICKER_TYPES:
                await message.reply(f'valid types: {TICKER_TYPES}', mention_author=True)
                return
            
            if security == 'stock':
                resp = stock(ticker)
            elif security == 'crypto':
                resp = crypto(ticker)

            if resp.get('error'):
                await message.reply(resp.get('error', 'unknown error'), mention_author=True)
                return
            elif resp.get('existing') and resp.get('client_id'):
                await message.reply(f'this ticker already exists! {invite_url(resp.get("client_id"))}', mention_author=True)
                return
            elif resp.get('client_id'):
                await message.reply(f'new ticker created! {invite_url(resp.get("client_id"))}', mention_author=True)
                return
        
        if message.content.startswith('!search'):

            opts = message.content.split(' ')
            logging.info(opts)

            if len(opts) < 2:
                await message.reply('usage: !search <crypto>', mention_author=True)
                return

            cryptos = opts[1]

            results = crypto_search(cryptos)

            await message.reply(f'possible coins: {", ".join(results)}', mention_author=True)
            return


if __name__ == "__main__":

    logging.basicConfig(
        filename=getenv('LOG_FILE'),
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    token = getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('DISCORD_BOT_TOKEN not set!')

    client = DiscordStockTickerBot()
    client.run(token)