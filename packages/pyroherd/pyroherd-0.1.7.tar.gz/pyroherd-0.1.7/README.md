<p align="center">
    <br>
    <b>Telegram MTProto API Framework for Python</b>
    <br>
</p>

## Pyroherd

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from pyroherd import Client, filters

app = Client("my_account")


@app.on_msg(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyroherd!")


app.run()
```

**Pyroherd** is a modern, elegant and asynchronous MTProto API
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Support

If you'd like to support Pyroherd, you can consider:

- [Become a GitHub sponsor](https://github.com/sponsors/OnTheHerd).
- [Become a LiberaPay patron](https://liberapay.com/OnTheHerd).
- [Become an OpenCollective backer](https://opencollective.com/OnTheHerd).

### Installing

``` bash
pip3 install pyroherd
```