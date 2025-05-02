import time
import discord
from .instance import db

coll = db.get_collection("afk")

def afk_get_user(member: discord.Member, guild: discord.Guild):
    return coll.find_one({"member": member.id, "guild": guild.id})

def afk_add_user(member: discord.Member, guild: discord.Guild, reason: str):
    if afk_get_user(member, guild):
        return False
    else:
        coll.insert({
            "member": member.id,
            "guild": guild.id,
            "reason": reason,
            "since": int(time.time())
        })
        return True
    
def afk_remove_user(member: discord.Member, guild: discord.Guild):
    result = afk_get_user(member, guild)
    if not result:
        return None
    
    coll.delete({
        "member": member.id,
        "guild": guild.id
    })

    return result
