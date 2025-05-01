
import discord
from .instance import db

channels = db.get_collection("levelChannels")
levels = db.get_collection("levels")
