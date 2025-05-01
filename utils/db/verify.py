import discord
from .instance import db

coll = db.get_collection("verify")

def verify_get_role(guild: discord.Guild):
    return coll.find_one({"guild": guild.id})

def verify_set_role(role: discord.Role, guild: discord.Guild):
    if verify_get_role(guild):
        coll.update({"guild": guild.id}, {"role": role.id})
    else:
        coll.insert({"role": role.id, "guild": guild.id})
