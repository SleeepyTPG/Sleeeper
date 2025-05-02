import time
import discord
from .instance import db

warns = db.get_collection("warns")
warnChannels = db.get_collection("warnChannels")
warnIds = db.get_collection("warnIds")

def warns_get_id(guild: discord.Guild):
    return warnIds.find_one({"guild": guild.id})

def warns_increase_id(guild: discord.Guild):
    if result := warns_get_id(guild):
        warnIds.update({
            "guild": guild.id
        }, 
        {
            "id": result["id"] + 1
        })
    else:
        warnIds.insert({"guild": guild.id, "id": 0})

def warns_get_channel(guild: discord.Guild):
    return warnChannels.find_one({"guild": guild.id})

def warns_set_channel(channel: discord.TextChannel, guild: discord.Guild):
    if warns_get_channel(guild):
        warnChannels.update({"guild": guild.id}, {"channel": channel.id})
    else:
        warnChannels.insert({"channel": channel.id, "guild": guild.id})

def warns_get_user(member: discord.Member, guild: discord.Guild):
    return warns.find_one({"member": member.id, "guild": guild.id})

def warns_add_user(member: discord.Member, guild: discord.Guild, reason: str):
    if warns_get_user(member, guild):
        return False
    else:
        warns.insert({
            "member": member.id,
            "guild": guild.id,
            "reason": reason,
            "since": int(time.time())
        })
        return True
