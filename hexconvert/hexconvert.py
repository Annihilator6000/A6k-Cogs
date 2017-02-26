import discord
import os
import binascii

from discord.ext import commands
from cogs.utils.dataIO import fileIO
from cogs.utils.chat_formatting import *
from __main__ import send_cmd_help

class Convert(object):
    # Conversion code from http://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa#7397689
    def text_to_bits(self, text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    def text_from_bits(self, bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits.replace(" ", ""), 2)
        hex_string = '%x' % n
        nlen = len(hex_string)
        return binascii.unhexlify(hex_string.zfill(nlen + (nlen & 1))).decode(encoding, errors)
    
class hexconvert(object):
    def __init__(self, bot):
        self.bot = bot
        self.convert = Convert()
    
    @commands.group(pass_context=True)
    async def hexconvert(self, ctx):
        """Convert Hex to ASCII, or ASCII to Hex"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @hexconvert.command(pass_context=True, name="toascii")
    async def _toascii(self, ctx, hexadecimal: str, user : discord.Member=None):
        """Convert an appended Hex string to ASCII. If there are spaces in the Hex string it must be encased in quotes."""

        await self.bot.say("{}:\n{}".format(user.mention, self.convert.text_from_bits(hexadecimal)) if user else self.convert.text_from_bits(hexadecimal))
        
        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        has_permissions = channel.permissions_for(server.me).manage_messages
        
        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return
        
        await self.bot.delete_message(ctx.message)
    
    @hexconvert.command(pass_context=True, name="tohex")
    async def _tohex(self, ctx, ascii: str, user : discord.Member=None):
        """Convert an appended ASCII string to Hex. If there are spaces in the ASCII string it must be encased in quotes."""

        await self.bot.say("{}:\n{}".format(user.mention, self.convert.text_to_bits(ascii)) if user else self.convert.text_to_bits(ascii))
        
        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        has_permissions = channel.permissions_for(server.me).manage_messages
        
        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return
        
        await self.bot.delete_message(ctx.message)
    
def setup(bot):
    n = hexconvert(bot)
    bot.add_cog(n)
    