import discord
from .instance import db

coll = db.get_collection("logger")

def logging_get_channel(guild: discord.Guild):
    return coll.find_one({"guild": guild.id})

def logging_set_channel(channel: discord.TextChannel, guild: discord.Guild):
    if logging_get_channel(guild):
        coll.update({"guild": guild.id}, {"channel": channel.id})
    else:
        coll.insert({"channel": channel.id, "guild": guild.id})
