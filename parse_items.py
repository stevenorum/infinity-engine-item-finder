#!/usr/bin/env python3

import binascii
from jinja2 import Environment, FileSystemLoader
import json
import os
import sys
import traceback

env = Environment(loader=FileSystemLoader("jinja_templates/"))

from ietools.shared import *

DEFAULT_ITEMS_FILE = "/Applications/Icewind Dale Enhanced Edition.app/Contents/Resources/game/IcewindDale.app/Contents/Resources/data/ITMFILE.BIF"

HEADER_ITEM_TYPES = [
    "Books/misc", # 0x0000
    "Amulets and necklaces", # 0x0001
    "Armor", # 0x0002
    "Belts and girdles", # 0x0003
    "Boots", # 0x0004
    "Arrows", # 0x0005
    "Bracers and gauntlets", # 0x0006
    "Helms, hets, and other headwear", # 0x0007
    "Keys",  # 0x0008, not in IWD?
    "Potions", # 0x0009
    "Rings", # 0x000a
    "Scrolls", # 0x000b
    "Shields", # 0x000c, not in IWD?
    "Food", # 0x000d
    "Bullets", # 0x000e
    "Bows", # 0x000f
    "Daggers", # 0x0010
    "Maces", # 0x0011
    "Slings", # 0x0012
    "Small swords", # 0x0013
    "Large swords", # 0x0014
    "Hammers", # 0x0015
    "Morning stars", # 0x0016
    "Flails", # 0x0017
    "Darts", # 0x0018
    "Axes (1-handed)", # 0x0019
    "Quarterstaff", # 0x001a
    "Crossbow", # 0x001b
    "Hand-to-hand weapons", # 0x001c
    "Spears", # 0x001d
    "Halberds", # 0x001e
    "Bolts", # 0x001f
    "Cloaks and robes", # 0x0020
    "Gold pieces", # 0x0021
    "Gems", # 0x0022
    "Wands", # 0x0023
    "Container/eye/broken armor", # 0x0024
    "Books/broken shield/bracelet", # 0x0025
    "Familiars/broken sword/earring", # 0x0026
    "Tattoos", # 0x0027, PST
    "Lenses", # 0x0028, PST
    "Buckler/teeth", # 0x0029
    "Candle", # 0x002a
    "Unknown (0x002b)", # 0x002b
    "Clubs", # 0x002c, IWD
    "Unknown (0x002d)", # 0x002d
    "Unknown (0x002e)", # 0x002e
    "Large shield", # 0x002f, IWD
    "Unknown (0x0030)", # 0x0030
    "Medium shield", # 0x0031, IWD
    "Notes", # 0x0032
    "Unknown (0x0033)", # 0x0033
    "Unknown (0x0034)", # 0x0034
    "Small shield", # 0x0035, IWD
    "Unknown (0x0036)", # 0x0036
    "Telescope", # 0x0037, IWD
    "Drink", # 0x0038, IWD
    "Great sword", # 0x0039, IWD
    "Container", # 0x003a
    "Fur/pelt", # 0x003b
    "Leather armor", # 0x003c
    "Studded leather armor", # 0x003d
    "Chain mail", # 0x003e
    "Splint mail", # 0x003f
    "Half plate", # 0x0040
    "Full plate", # 0x0041
    "Hide armor", # 0x0042
    "Robe", # 0x0043
    "Unknown (0x0044)", # 0x0044
    "Bastard sword", # 0x0045
    "Scarf", # 0x0046
    "Food", # 0x0047, IWD2
    "Hat", # 0x0048
    "Gauntlet", # 0x0049
]

HEADER_PROFICIENCY_LIST = [None] + ["<unexpected value in file>"] * 88
HEADER_PROFICIENCY_LIST += [
    "Bastard Sword", # 0x59
    "Long Sword", # 0x5a
    "Short Sword", # 0x5b
    "Axe", # 0x5c
    "Two-Handed Sword", # 0x5d
    "Katana", # 0x5e
    "Scimitar/Wakizashi/Ninja-To", # 0x5f
    "Dagger", # 0x60
    "War Hammer", # 0x61
    "Spear", # 0x62
    "Halberd", # 0x63
    "Flail/Morningstar", # 0x64
    "Mace", # 0x65
    "Quarterstaff", # 0x66
    "Crossbow", # 0x67
    "Long Bow", # 0x68
    "Short Bow", # 0x69
    "Darts", # 0x6a
    "Sling", # 0x6b
    "Blackjack", # 0x6c
    "Gun", # 0x6d
    "Martial Arts", # 0x6e
    "Two-Handed Weapon Skill", # 0x6f
    "Sword and Shield Skill", # 0x70
    "Single Weapon Skill", # 0x71
    "Two Weapon Skill", # 0x72
    "Club", # 0x73
]
HEADER_PROFICIENCY_LIST += [ "Extra Proficiency {}".format(i) for i in range(2,21) ] # 0x74-0x86

HEADER_FLAGS = [
    ["critical_item","two_handed","movable","displayable","cursed","unscribable","magical","bow"],
    ["silver","cold_iron","unsellable_stolen","conversable","force_two_handed_animation","not_usable_in_off_hand","usable_in_inventory","adamantine"],
    [None] * 8,
    ["not_dispellable_in_magical_weapon_slot","toggle_critical_hit_aversion"] + [None] * 6,
]

HEADER_USABILITY_FLAGS = [
    ["Chaotic","Evil","Good","...Neutral","Lawful","Neutral...","Bard","Cleric"],
    ["Cleric/Mage","Cleric/Thief","Cleric/Ranger","Fighter","Fighter/Druid","Fighter/Mage","Fighter/Cleric","Fighter/Mage/Cleric"],
    ["Fighter/Mage/Thief","Fighter/Thief","Mage","Mage/Thief","Paladin","Ranger","Thief","Elf"],
    ["Dwarf","Half-Elf","Halfling","Human","Gnome","Monk","Druid","Half-Orc"],
]

HEADER_KIT_USABILITY_FLAGS = [
    ["Priest of Talos (Cleric kit)","Priest of Helm (Cleric kit)","Priest of Lathlander (Cleric kit)","Totemic Druid (Druid kit)","Shapeshifter (Druid kit)","Avenger (Druid kit)","Barbarian","Wild Mage (Mage kit)"],
    ["Stalker (Ranger kit)","Beastmaster (Ranger kit)","Assassin (Thief kit)","Bounty Hunter (Thief kit)","Swashbuckler (Thief kit)","Blade (Bard kit)","Jester (Bard kit)","Skald (Bard kit)"],
    ["Diviner (Specialist Mage)","Enchanter (Specialist Mage)","Illusionist (Specialist Mage)","Invoker (Specialist Mage)","Necromancer (Specialist Mage)","Transmuter (Specialist Mage)","All","Ferlain (?)"],
    ["Berserker (Fighter kit)","Wizard Slayer (Fighter kit)","Kensai (Fighter kit)","Cavalier (Paladin kit)","Inquisitor (Paladin kit)","Undead Hunter (Paladin kit)","Abjurer (Specialist Mage)","Conjurer (Specialist Mage)"],
]

EXTENDED_HEADER_FLAGS = [
    ["add_strength_bonus","breakable"] + [None] * 6,
    [None] * 2 + ["hostile","recharges"] + [None] * 4,
    [None] * 8,
    [None] * 8,
]

_TLK = loadf('tlk.json')
_CODES = loadf('item_codes.json')
_CODES.update({_CODES[k]:k for k in _CODES})

def _parse_item_file(f, **kwargs):
    i = f.tell()
    while True:
        if "size" in kwargs:
            if i > kwargs["size"]:
                raise RuntimeError("Done")
        b = f.read(8)
        if b == "ITM V1  ".encode("utf-8"):
            break
        i += 1
        f.seek(i)
    valid = True
    attributes = {}
    attributes["unidentified_name"] = word_to_int(f.read(4))
    attributes["identified_name"] = word_to_int(f.read(4))
    if str(attributes["unidentified_name"]) not in _TLK and str(attributes["identified_name"]) not in _TLK:
        return None
    attributes["unidentified_name"] = _TLK.get(str(attributes["unidentified_name"]), str(attributes["unidentified_name"]))
    attributes["identified_name"] = _TLK.get(str(attributes["identified_name"]), str(attributes["identified_name"]))
    attributes["replacement"] = f.read(8)
    attributes["flags_bytes"] = f.read(4)
    attributes["flags"] = _parse_header_flags(attributes["flags_bytes"])
    attributes["item_type_bytes"] = word_to_int(f.read(2))
    attributes["item_type"] = _parse_header_item_type(attributes["item_type_bytes"])
    attributes["usability_bytes"] = f.read(4)
    attributes["usability"] = _parse_header_usability(attributes["usability_bytes"])
    attributes["animation"] = f.read(2)
    attributes["min_level"] = word_to_int(f.read(2))
    attributes["min_strength"] = word_to_int(f.read(2))
    attributes["min_strength_bonus"] = word_to_int(f.read(1))
    attributes["kit_usability_1"] = f.read(1)
    attributes["min_intelligence"] = word_to_int(f.read(1))
    attributes["kit_usability_2"] = f.read(1)
    attributes["min_dexterity"] = word_to_int(f.read(1))
    attributes["kit_usability_3"] = f.read(1)
    attributes["min_wisdom"] = word_to_int(f.read(1))
    attributes["kit_usability_4"] = f.read(1)
    attributes["kit_usability"] = _parse_header_kit_usability(attributes["kit_usability_1"]+attributes["kit_usability_2"]+attributes["kit_usability_3"]+attributes["kit_usability_4"])
    attributes["min_constitution"] = word_to_int(f.read(1))
    attributes["weapon_proficiency_byte"] = f.read(1)
    attributes["weapon_proficiency"] = _parse_header_proficiency(word_to_int(attributes["weapon_proficiency_byte"]))
    attributes["min_charisma"] = word_to_int(f.read(2))
    attributes["price"] = word_to_int(f.read(4))
    attributes["stack_amount"] = word_to_int(f.read(2))
    attributes["inventory_icon"] = clean_string(f.read(8))
    attributes["lore_to_id"] = word_to_int(f.read(2))
    attributes["ground_icon"] = clean_string(f.read(8))
    attributes["weight"] = word_to_int(f.read(4))
    attributes["unidentified_desc_ind"] = word_to_int(f.read(4))
    attributes["identified_desc_ind"] = word_to_int(f.read(4))

    attributes["unidentified_desc"] = _TLK.get(str(attributes["unidentified_desc_ind"]))
    attributes["identified_desc"] = _TLK.get(str(attributes["identified_desc_ind"]))
    # If an item doesn't need to be identified, the "identified_description" pointer is frequently (always?) null.
    # attributes["unidentified_desc"] = attributes["unidentified_desc"] if attributes["unidentified_desc"] else attributes["identified_desc"]
    # attributes["identified_desc"] = attributes["identified_desc"] if attributes["identified_desc"] else attributes["unidentified_desc"]
    # attributes["desc_icon"] = clean_string(f.read(8))
    attributes["desc_icon"] = f.read(8)
    attributes["enchantment"] = f.read(4)
    attributes["ext_header_offset"] = word_to_int(f.read(4)) + i
    attributes["ext_header_count"] = word_to_int(f.read(2))
    attributes["feature_block_offset"] = word_to_int(f.read(4)) + i
    attributes["equipped_feature_block_index"] = word_to_int(f.read(2))
    attributes["equipped_feature_block_count"] = word_to_int(f.read(2))
    # attributes["ext_headers"] = [] # not yet functional
    attributes["ext_headers"] = _parse_extended_headers(f, attributes["ext_header_offset"], attributes["ext_header_count"])
    attributes["feature_blocks"] = [] # not yet functional
    # attributes["feature_blocks"] = _parse_feature_blocks(f, attributes["feature_block_offset"], attributes["equipped_feature_block_count"])
    print("Returning item {} ({})".format(attributes["unidentified_name"], attributes["identified_name"]))
    return attributes

ATTACK_TYPES = [
    "None","Melee","Projectile","Magic","Launcher"
]

EXTH_TARGET_TYPES = [
    "Invalid","Creature","Crash","Character portrait","Area","Self","Crash","None (self, ignores game pause)"
]

DAMAGE_TYPES = [
    "None","Piercing/Magic","Blunt","Slashing","Ranged","Fists","Piercing/Blunt","Piercing/Slashing","Blunt/Slashing"
]

PROJECTILE_TYPES = ["None","Arrow","Bolt","Bullet"]
PROJECTILE_TYPES += [None] * 36
PROJECTILE_TYPES += ["Spear"]
PROJECTILE_TYPES += [None] * 59
PROJECTILE_TYPES += ["Throwing Axe"]

def _parse_extended_headers(f, start, count):
    here = f.tell()
    f.seek(start)
    headers = []
    for i in range(count):
        header = {}
        header["attack_type"] = ATTACK_TYPES[word_to_int(f.read(1))]
        header["id_required"] = word_to_int(f.read(1))
        header["location"] = word_to_int(f.read(1))
        header["alternative_dice_sides"] = word_to_int(f.read(1))
        header["use_icon"] = clean_string(f.read(8))
        header["target_type"] = EXTH_TARGET_TYPES[word_to_int(f.read(1))]
        header["target_count"] = word_to_int(f.read(1))
        header["range"] = word_to_int(f.read(2))
        header["projectile_type"] = PROJECTILE_TYPES[word_to_int(f.read(1))]
        header["alternative_dice_thrown"] = word_to_int(f.read(1))
        header["speed"] = word_to_int(f.read(1))
        header["alternative_damage_bonus"] = word_to_int(f.read(1))
        header["thaco_bonus"] = word_to_int(f.read(2))
        header["dice_sides"] = word_to_int(f.read(1))
        header["primary_type"] = word_to_int(f.read(1))
        header["dice_thrown"] = word_to_int(f.read(1))
        header["secondary_type"] = word_to_int(f.read(1))
        header["damage_bonus"] = word_to_int(f.read(2))
        header["damage_type"] = DAMAGE_TYPES[word_to_int(f.read(2))]
        header["feature_block_count"] = word_to_int(f.read(2))
        header["feature_block_offset"] = word_to_int(f.read(2))
        header["charges"] = word_to_int(f.read(2))
        header["charge_depletion_behavior"] = word_to_int(f.read(2))
        header["flags_bytes"] = f.read(4)
        header["flags"] = _parse_extended_header_flags(header["flags_bytes"])
        header["projectile_animation"] = f.read(2)
        header["melee_animation_1"] = word_to_int(f.read(2))
        header["melee_animation_2"] = word_to_int(f.read(2))
        header["melee_animation_3"] = word_to_int(f.read(2))
        header["melee_animation"] = _parse_extended_header_melee_animation(header["melee_animation_1"], header["melee_animation_2"], header["melee_animation_3"])
        header["bow_arrow_qualifier"] = f.read(2)
        header["crossbow_bolt_qualifier"] = f.read(2)
        header["misc_projectile_qualifier"] = f.read(2)
        headers.append(header)
    f.seek(here)
    return headers

def _parse_feature_blocks(f, start, count):
    here = f.tell()
    f.seek(start)
    blocks = []
    for i in range(count):
        block = {}
        block["opcode"] = f.read(2)
        block["target_type"] = f.read(1)
        block["power"] = f.read(1)
        block["parameter_1"] = f.read(4)
        block["parameter_2"] = f.read(4)
        block["timing_mode"] = f.read(1)
        block["resistance"] = f.read(1)
        block["duration"] = f.read(4)
        block["probability_1"] = f.read(1)
        block["probability_2"] = f.read(1)
        block["resource"] = f.read(8)
        block["dice_thrown"] = f.read(4)
        block["dice_sides"] = f.read(4)
        block["saving_throw_type"] = f.read(4)
        block["saving_throw_bonus"] = f.read(4)
        block["special"] = f.read(4)
        blocks.append(block)
        # do stuff here
        pass
    f.seek(here)
    return blocks

def _parse_flags(bs, flags):
    flag_dict = {}
    for i in range(len(bs)):
        for j in range(8):
            if flags[i][j]:
                flag_dict[flags[i][j]] = not not (bs[i] & (0x01 << j))
    return flag_dict

def _parse_header_flags(bs):
    return _parse_flags(bs, HEADER_FLAGS)

def _parse_header_item_type(bs):
    return HEADER_ITEM_TYPES[bs] if bs in range(len(HEADER_ITEM_TYPES)) else "Unknown ({})".format(bs)

def _parse_header_usability(bs):
    return _parse_flags(bs, HEADER_USABILITY_FLAGS)

def _parse_header_animation(bs):
    pass

def _parse_header_kit_usability(bs):
    return _parse_flags(bs, HEADER_KIT_USABILITY_FLAGS)

def _parse_header_proficiency(bs):
    return HEADER_PROFICIENCY_LIST[bs] if bs in range(len(HEADER_PROFICIENCY_LIST)) else "Unknown ({})".format(bs)

def _parse_extended_header_melee_animation(b1, b2, b3):
    pass

def _parse_extended_header_flags(bs):
    return _parse_flags(bs, EXTENDED_HEADER_FLAGS)

def _parse_items_file(f, size=-1, **kwargs):
    items = []
    index = 0
    try:
        while size < 0 or f.tell() < size:
            item = _parse_item_file(f, size=size)
            if item:
                item["file_index"] = str(index)
                item["item_code"] = _CODES.get(item["file_index"], "<unknown>")
                items.append(item)
            index += 1
    except:
        traceback.print_exc()
        return items

def parse_items(filename=None):
    filename = filename if filename else DEFAULT_ITEMS_FILE
    return parse_file(filename, _parse_items_file)

def main():
    items = parse_items()

    attributes = items[1]
    for item_attrs in items:
        # print("{} : {}".format(item_attrs["item_code"], item_attrs["identified_name"]))
        if "Two-Handed Sword" == item_attrs["unidentified_name"]:
            print("================================================================")
            for a in item_attrs:
                print("{} : {}".format(a, hexlify(item_attrs[a])))
    dumpf(items, "all_iwdee_items.json")
    item_code_map = {i["item_code"]:i for i in items}
    dumpf(item_code_map, "all_iwdee_items_by_id.json")
    index_contents = env.get_template("index.html").render(items=items)
    with open("html_files/index.html","w") as f:
        f.write(index_contents)
    for item in items:
        file_contents = env.get_template("item.html").render(**item)
        fname = "html_files/{item_code}.html".format(**item)
        with open(fname,"w") as f:
            f.write(file_contents)


if __name__ == "__main__":
    main()
