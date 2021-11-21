from os import popen
import random
from datetime import datetime
from json import dump, load, loads
import certifi
import discord
from discord.ext.commands.cog import _cog_special_method
import pymongo
import requests
# import requests
from discord import RequestsWebhookAdapter, Webhook
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.webhook import WebhookMessage
from discord_slash import SlashCommand
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import (create_option,
                                                 create_permission)

intents = discord.Intents.all()
client = commands.Bot(
    command_prefix=commands.when_mentioned_or('?'), intents=intents)
slash = SlashCommand(client, sync_commands=True)

i = 0


@ client.event
async def on_ready():
    # ahoj.start()
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name='?', type=discord.ActivityType.watching))
    print('\nBot je připraven!\n')

mongoClient = pymongo.MongoClient(
    'mongodb+srv://abc:UNVO0Vy0zGSNJ7yI@abcd.qpqdf.mongodb.net/abcd?retryWrites=true&w=majority',
    tlsCAFile=certifi.where()
)
db = mongoClient.abcd

message = """**Domácí úkoly:**

{}

_Poznámka:_
Úkoly z Nj jsou vždy pouze pro Nj2, Nj1 je taky má, ale termín je většinou jiný!
Nejsou zde zaznamenány úkoly Aj2, Chc1, Fcv2 a Tvd"""

ukol = {
    'date': '1.1.',
    'subject': 'M',
    'description': 'blbost',
    'special': 0,
}

# for ukol in db.ukoly.find():
#    print(ukol)

# print(db.ukoly.find_one({'special': 0}))

guild_ids = [796689722180239370]


@ slash.slash(name='pozvánka', description='Pošle vám pozvánku na server', guild_ids=guild_ids)
async def pozvanka(ctx: Context):
    await ctx.author.send('https://discord.gg/nRXgbdDFgP')


@ slash.permission(796689722180239370, create_permission(796693226652303390, 1, True))
@ slash.subcommand(base='u',
                   name='new',
                   description='Vytvořit nový úkol',
                   guild_ids=guild_ids,
                   options=[
                       create_option(
                           'date',
                           'Datum, na který je úkol zadán',
                           option_type=3,
                           required=True
                       ),
                       create_option(
                           'subject',
                           'Předmět, vyučující, resp. Skupina, která má tento úkol zadaný',
                           option_type=3,
                           required=True
                       ),
                       create_option(
                           'description',
                           'Popis úkolu',
                           option_type=3,
                           required=True
                       ),
                   ])
async def _ukol_new(ctx: SlashContext, date, subject, description):
    webhook = Webhook.from_url(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK', adapter=RequestsWebhookAdapter())

    id = db.ukoly.find_one({'special': 1})['id']

    ukol = {
        'date': f'**{date}**',
        'subject': subject,
        'description': description,
        'special': 0,
    }

    db.ukoly.insert_one(ukol)

    l = list(db.ukoly.find({'special': 0}))
    db.ukoly.delete_many({'special': 0})
    try:
        db.ukoly.insert_many(sorted(l, key=sort))
    except TypeError:
        pass
    l = list(db.ukoly.find({'special': 0}))

    ukoly = '\n'.join([' – '.join(removeid(u).values()) for u in l])

    webhook.edit_message(id, content=message.format(ukoly))

    await ctx.send(f'Úkol "{" – ".join(removeid(ukol).values())}" vytvořen!', embeds=[])


@ slash.subcommand(base='u',
                   name='edit',
                   description='Upraví úkol',
                   guild_ids=guild_ids,
                   options=[
                       create_option(
                           'pos',
                           'Určí, který úkol se má upravit',
                           option_type=4,
                           required=True
                       ),
                       create_option(
                           'date',
                           'Datum, na který je úkol zadán',
                           option_type=3,
                           required=False
                       ),
                       create_option(
                           'subject',
                           'Předmět, vyučující, resp. skupina, která má tento úkol zadaný',
                           option_type=3,
                           required=False
                       ),
                       create_option(
                           'description',
                           'Popis úkolu',
                           option_type=3,
                           required=False
                       ),
                   ])
async def _ukol_edit(ctx: SlashContext, pos, date=None, subject=None, description=None):
    webhook = Webhook.from_url(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK', adapter=RequestsWebhookAdapter())

    id = db.ukoly.find_one({'special': 1})['id']

    l = list(db.ukoly.find({'special': 0}))

    stary_ukol = ' – '.join(removeid(l[int(pos)]).values())

    if date != None:
        l[int(pos)]['date'] = f'**{date}**'
    if subject != None:
        l[int(pos)]['subject'] = subject
    if description != None:
        l[int(pos)]['description'] = description

    ukol = ' – '.join(removeid(l[int(pos)]).values())

    db.ukoly.delete_many({'special': 0})
    try:
        db.ukoly.insert_many(sorted(l, key=sort))
    except TypeError:
        pass
    l = list(db.ukoly.find({'special': 0}))

    ukoly = '\n'.join([' – '.join(removeid(u).values()) for u in l])
    webhook.edit_message(id, content=message.format(ukoly))

    await ctx.send(f'Úkol "{stary_ukol}" upraven na "{ukol}"!', embeds=[])


@ slash.subcommand(base='u',
                   name='delete',
                   description='Odstranit úkol',
                   guild_ids=guild_ids,
                   options=[
                       create_option(
                           'pos',
                           'Určí, který úkol se odstraní',
                           option_type=4,
                           required=True
                       ),
                   ])
async def _ukol_delete(ctx: SlashContext, pos: str):
    webhook = Webhook.from_url(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK', adapter=RequestsWebhookAdapter())

    id = db.ukoly.find_one({'special': 1})['id']

    l = list(db.ukoly.find({'special': 0}))

    stary_ukol = l[int(pos)]

    l.remove(stary_ukol)

    db.ukoly.delete_many({'special': 0})
    try:
        db.ukoly.insert_many(sorted(l, key=sort))
    except TypeError:
        pass
    l = list(db.ukoly.find({'special': 0}))

    ukoly = '\n'.join([' – '.join(removeid(u).values()) for u in l])

    webhook.edit_message(id, content=message.format(ukoly))

    await ctx.send(f'Úkol "{" – ".join(removeid(stary_ukol).values())}" odstraněn!', embeds=[])


@ slash.subcommand(base='u',
                   name='update',
                   description='Aktualizovat úkoly. POZOR! Vrátí chybu!',
                   guild_ids=guild_ids,
                   )
async def _ukol_update(ctx: SlashContext):
    webhook = Webhook.from_url(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK', adapter=RequestsWebhookAdapter())

    id = db.ukoly.find_one({'special': 1})['id']

    l = list(db.ukoly.find({'special': 0}))

    ukoly = '\n'.join([' – '.join(removeid(u).values()) for u in l])

    webhook.edit_message(id, content=message.format(ukoly))


@ slash.subcommand(base='u',
                   name='create',
                   description='Vytvořit novou zprávu s úkoly',
                   guild_ids=guild_ids,)
async def _ukol_create(ctx: SlashContext):
    webhook = Webhook.from_url(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK', adapter=RequestsWebhookAdapter())

    db.ukoly.delete_one({'special': 1})

    mes: WebhookMessage = webhook.send(
        message.format('Žádné nejsou :)'), wait=True)

    channel_id = loads(requests.get(
        'https://ptb.discord.com/api/webhooks/880521729691250729/7shHqox0wHigHCIelGou6GpImEB-UcBl34k2hlauDS2f8gcskzcnFDriPF-7xK51e4VK').text)['channel_id']

    sp_ukol = {
        'special': 1,
        'id': mes.id,
    }
    db.ukoly.insert_one(sp_ukol)

    await ctx.send(f'Zpráva vytvořena! Zde je odkaz: https://discord.com/channels/796689722180239370/{channel_id}/{mes.id}', embeds=[])

mesice = ('Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
          'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec')


def sort(it: str):
    x = it['date'].replace('*', '').split('.')
    if x[0] in mesice:
        y = (mesice.index(x[0]) + 1) * 100
    else:
        y = int(x[0]) + int(x[1]) * 100
    z = (y + 600) % 1200
    if z == 0:
        return 1200
    return z


def removeid(d):
    r = dict(d)
    del r['_id']
    del r['special']
    return r


@ client.command(aliases=['z', 'zabít'])
async def zabit(ctx):
    await ctx.send('Jsem mrtvej :expressionless:')
    quit()


@ slash.slash(name='otázka',
              description='Zeptejte se!',
              guild_ids=guild_ids,
              options=[
                  create_option(
                      'otázka',
                      'Co by sis přál vědět?',
                      option_type=3,
                      required=False,
                  )
              ],)
async def otazka(ctx, otázka='?'):
    odpovedi = [
        'Jo.',
        'Nejspíš ano.',
        'Určitě ano!',
        'Asi.',

        'Možná.',
        'Nevím.',
        'Neřeš to.',

        'Ne.',
        'Asi ne.',
        'Určitě ne!',
        'Nejspíš ne.'
    ]

    if otázka[-1] != '?':
        otázka += '?'

    if otázka == '?':
        await ctx.send(f'Špatné paranetry! Syntax je```/otázka otázka: String```')
    else:
        await ctx.send(f'{otázka}\n{random.choice(odpovedi)}')

if db.pocitani.count_documents({}) == 0:
    db.pocitani.insert_one({"id": 0, "poc": False, "cis": -1})


@ client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    doc = db.pocitani.find_one({})

    print(doc)
    if doc["poc"]:
        if doc["id"] == after.channel.id:
            await after.reply("\u2757")
            await after.delete()


@ client.event
async def on_message(message: discord.Message):
    doc = db.pocitani.find_one({})

    print(doc)
    if doc["poc"]:
        if doc["id"] == message.channel.id:
            if message.author != client.user:
                if message.content == str(doc["cis"] + 1):
                    db.pocitani.find_one_and_update({}, {"$inc": {"cis": 1}})
                    await message.add_reaction("\u2705")
                else:
                    await message.delete()

    await client.process_commands(message)


@ client.command(aliases=["pocitat", "p"])
async def pocitani(ctx):

    db.pocitani.find_one_and_update(
        {}, {"$set": {"id": ctx.channel.id, "poc": True, "cis": -1}})

    await ctx.send('0')


###################################################################
#                            EMBEDS                               #
###################################################################


odpovidat = False
id = ''
kanal = ''
krok = 0
context: discord.ext.commands.Context
embed = {
    'author': {},
    'colour': None,
    'description': None,
    'fields': [],
    'footer': {},
    'image': {},
    'thumbnail': {},
    'timestamp': None,
    'title': None,
    'type': 'rich',
    'video': {}
}


'''
0 - nic
1 - author/autor - set_author(
    1 - name
    2 - icon_url
)
3 - colour/barva - Colour.from_rgb(r, g, b)
4 - description/popisek
5 - fields - [add_field(
    6 - name
    7 - value
    8 - inline
)] - pridat / None
9 - footer/zápatí - set_footer(
    9 - text
    10 - icon_url
)
11 - image/obrázek - set_immage(
    11 - url
)
12 - thumbnail/miniatura - set_thumbnail(
    12 - url
)
13 - timestamp/datum a čas - datetime.datetime
14 - title/nadpis
     type/typ - rich
15 - video/video - set_video(
    15 - url
)
16 - channnel/kanál
'''


async def odpovedel(message: discord.Message):
    global odpovidat, context, id, kanal, krok

    w = ''
    try:
        m = message.content
    except:
        pass

    if krok == 1:
        w = 'Zadej jméno autora. `None` pro nic.'
        krok = 2

    elif krok == 2:
        if m != 'None':
            embed['author']['name'] = m
        w = 'Zadej URL ikony autora. `None` pro nic.'
        krok = 3

    elif krok == 3:
        if m != 'None':
            embed['author']['icon_url'] = m
        w = 'Zadej barvu ve formátu `R G B`.'
        krok = 18

    elif krok == 18:
        embed['colour'] = discord.Colour.from_rgb(
            *[int(i) for i in m.split()])
        w = 'Zadejte popisek.'
        krok = 4

    elif krok == 4:
        embed['description'] = m
        w = 'Chcete přidat položku? `Ne`, nebo `Ano`.'
        krok = 5

    elif krok == 5:
        if m == 'Ano':
            embed['fields'].append({})
            w = 'Zadej nadpis položky.'
            krok = 6
        elif m == 'Ne':
            w = 'Zadej text zápatí. `None` pro nic.'
            krok = 9

    elif krok == 6:
        embed['fields'][-1]['name'] = m
        w = 'Zadej hodnotu položky.'
        krok = 7

    elif krok == 7:
        embed['fields'][-1]['value'] = m
        w = 'Zadej, zda má být položka v řadě. (`True`/`False`)'
        krok = 8

    elif krok == 8:
        embed['fields'][-1]['inline'] = bool(m)
        w = 'Chcete přidat položku? `Ne`, nebo `Ano`.'
        krok = 5

    elif krok == 9:
        if m != 'None':
            embed['footer']['text'] = m
        w = 'Zadej URL ikony zápatí. `None` pro nic.'
        krok = 10

    elif krok == 10:
        if m != 'None':
            embed['footer']['icon_url'] = m
        w = 'Zadej URL obrázku. `None` pro nic.'
        krok = 11

    elif krok == 11:
        if m != 'None':
            embed['image']['url'] = m
        w = 'Zadej URL obrázku miniatury. `None` pro nic.'
        krok = 12

    elif krok == 12:
        if m != 'None':
            embed['thumbnail']['url'] = m
        w = 'Zadej datum a čas ve formátu `yyyy MM dd hh mm`. `None` pro nic.'
        krok = 13

    elif krok == 13:
        if m != 'None':
            cas = [int(i) for i in m.split()]
            embed['timestamp'] = datetime(*cas, 0, 0)
        w = 'Zadej Nadpis.'
        krok = 14

    elif krok == 14:
        embed['title'] = m
        w = 'Zadej URL videa. `None` pro nic.'
        krok = 15

    elif krok == 15:
        if m != 'None':
            embed['video']['url'] = m
        w = 'Zmiň kanál, do kterého chceš vložení poslat.'
        krok = 16

    elif krok == 16:
        await message.channel_mentions[0].send(
            embed=discord.Embed.from_dict(embed))
        odpovidat = False
        krok = 17

    if krok != 17:
        await context.send(content=w)


# @ client.event
# async def on_message(message: discord.message):
#    global odpovidat, context, id, kanal, krok
#    if odpovidat == True:
#        if kanal == message.channel_id:
#            if message.author_id == id:
#                await odpovedel(message)
#
#    await client.process_commands(message)


@ client.command(aliases=['embed', 'e'])
async def new_embed(ctx):
    global odpovidat, context, id, kanal, krok
    odpovidat = True
    context = ctx
    id = ctx.author_id
    kanal = ctx.channel_id
    krok = 1
    await odpovedel(None)


###################################################################
#////////////////////////////EMBEDS///////////////////////////////#
###################################################################

client.run('ODAxMzg4Nzg0NTg2NDU3MDk4.YAf9dw.OL8iucAymD9e9jZZ8KI2H8tsASA')
