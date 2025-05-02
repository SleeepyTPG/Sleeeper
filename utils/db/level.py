import discord
from typing import Tuple
from .instance import db

channels = db.get_collection("levelChannels")
levels = db.get_collection("levels")

def level_get_channel(guild: discord.Guild):
    return channels.find_one({"guild": guild.id})

def level_set_channel(channel: discord.TextChannel, guild: discord.Guild):
    if not level_get_channel(guild):
        channels.insert({
            "channel": channel.id,
            "guild": guild.id
        })
    else:
        channels.update({"guild": guild.id}, {"channel": channel.id})

def level_get(member: discord.Member, guild: discord.Guild):
    return levels.find_one({"member": member.id, "guild": guild.id})

def level_set(member: discord.Member, guild: discord.Guild, level: int):
    if level_get(member, guild):
        levels.update({
            "member": member.id,
            "guild": guild.id
        },
        {
            "level": level,
            "xp": 0
        })
    else:
        levels.insert({
            "member": member.id,
            "guild": guild.id,
            "level": level,
            "xp": 0
        })

def level_add_xp(member: discord.Member, guild: discord.Guild, xp: int) -> Tuple[bool, int]:
    result = level_get(member, guild)
    if result == None:
        level_set(member, guild, 1)
        result = level_get(member, guild)

    new_xp = result["xp"] + xp
    next_level_xp = result["level"] * 100

    if new_xp >= next_level_xp:
        level_set(member, guild, result["level"] + 1)
        return True, level_get(member, guild)["level"]
    else:
        levels.update({
            "member": member.id,
            "guild": guild.id
        },
        {
            "xp": result["xp"] + xp
        })
        return False, result["level"]
    
def level_get_all(guild: discord.Guild):
    return levels.find_all({"guild": guild.id})
