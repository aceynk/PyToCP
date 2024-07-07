"""
A mod to make carrots give a persistent and long-lasting speed buff, using PyToCP
"""

from pytocp import Mod, Entry
import pytocp

m: Mod = Mod(
    name = "PersistentSpeed",
    author = "aceynk",
    version = "1.0.0",
    description = "Creates a persistent speed buff.",
    uid = "aceynk.PersistentSpeed",
    dependencies = [
        {
            
        }
    ]
)

m.output_fp = "../steamcommon/Stardew Valley/Mods"

PersistentSpeed = Entry(
    entry_id = "_PersistentSpeed",
    entry = {
        "DisplayName": "PersistentSpeed",
        "Duration": 10000 * 1000,
        "IconTexture": "TileSheets\\BuffsIcons",
        "IconSpriteIndex": 9,
        "Effects": {
            "Speed": 1
        }
    },
    action = "EditData",
    target = "Data/Buffs"
)

PB_Entry = Entry(
    entry_id = "_PersistentSpeed",
    entry = True,
    action = "EditData",
    target = "aceynk.PersistentBuffs/PersistentBuffIds"
)

pytocp.PREFIX_WITH_MODID = False

Carrot = Entry(
    entry_id = "Buffs",
    entry = [
        {
            "BuffId": PersistentSpeed.entry_id
        }
    ],
    action = "EditData",
    target = "Data/Objects",
    targetfield= ["Carrot"]

)

m.Register(PersistentSpeed, PB_Entry, Carrot)

m.Create()