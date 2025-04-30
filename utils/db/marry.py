import discord
from .instance import db

coll = db.get_collection("marry")

def marry_get_user(member: discord.Member):
    result = coll.find_one({"member1": member.id})
    if result == None:
        result = coll.find_one({"member2": member.id})
        if result == None:
            return None
        return result
    return result

def marry_add_user(member: discord.Member, member2: discord.Member):
    if marry_get_user(member):
        return False
    else:
        coll.insert({
            "member1": member.id,
            "member2": member2.id
        })
        return True
    
def marry_remove_user(member: discord.Member):
    result = marry_get_user(member)
    if not result:
        return False
    
    coll.delete({
        "member1": member.id
    })
    coll.delete({
        "member2": member.id
    })

    return result
