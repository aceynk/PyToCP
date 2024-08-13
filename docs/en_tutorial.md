# PyToCP Documentation

The documentation here should hopefully provide all the information you need to create a mod with this module.

## Help

This is a personal project first, so I may not respond to all requests. Feel free to write up a github issue or dm me on discord (@aceynk).

## Introduction

PyToCP uses three separate classes; Mod, Entry, and ContentFile.

These docs will also use some type aliases. Here are their definitions:

```py
JsonTypes = type["str|int|list[Any]|dict[Any]"]
"""Types that json supports."""
EntryDict = type["dict[str, list[JsonTypes]]"]
"""Type for the Entry Content Patcher field."""```
```

## The Mod class

### Initialization

First, an introduction to the Mod class. This class is initialized with 5 positional arguments and 4 optional arguments.

(See: https://stardewmodding.wiki.gg/wiki/Tutorial:_How_to_create_a_manifest)

* ``name`` (str, positional): The name of the mod.
* ``author`` (str, positional): The author's name.
* ``version`` (str, positional): The version of the mod.
* ``description`` (str, positional): A brief description of the mod.
* ``uid`` (str, positional) The unique id of the mod.
* ``update_key_nexus`` (int, optional) The update key (mod number) for the mod if hosted on nexusmods.com.
* ``update_key_github`` (str, optional) The update key (name/repo) for the mod if hosted on github.com.
* ``contentpack_for`` (str, optional) Which mod the content pack is for. Defaults to ``"Pathoschild.ContentPatcher"``.
* ``dependencies`` (list[dict[str, str]], optional) The list of dependency objects for the mod.

As an example, let's try making a new mod.

```py
import pytocp as ptc

my_new_mod: Mod = ptc.Mod(
    name = "My New Mod",
    author = "aceynk",
    version = "1.0.0",
    description = "My new test mod!",
    uid = "aceynk.mynewmod"
)
```

The ``my_new_mod`` variable is now assigned to the new Mod object. It is important to store this object in a variable, as you will see later.

The information set here on initialization can be edited later by accessing ``Mod.manifest``.

### Fields

There are a few additional fields that are important to know about.

* ``Mod.unpacked_content_fp`` (str) : Using XnbHack or another XNB converter of your choice, you can extract SDV's assets into another folder. Set this field to the directory of said folder for debugging tools in the future. Currently not in use.
* ``Mod.output_fp`` (list[str]) : A list of directories in which to compile your mod. Defaults to ``[ "" ]``.
* ``Mod.dirname`` (str) : This value is either set automatically to your mod's name, or set manually by editing this field. Defaults to ``"NewMod"``.
* ``Mod.files`` (list[ContentFile]) : A list of content files to save. See the section on the ContentFile class.
* ``Mod.i18n_internal`` (dict[str, dict[str, str]]) : Set this dictionary to set and use i18n language keys. See the section on ``Mod.i18n``
* ``Mod.PREFIX_WITH_MODID`` (bool) : Whether or not to prefix ``entry_id`` values in the Entry class with "{{ModID}}". See the section on the Entry class. Defaults to True.
* ``Mod.AUTO_REGISTER`` (bool) : Whether or not to automatically register new Entry objects with the mod. Defaults to True.

Here's an example of some of these fields in use:

```py
my_new_mod.unpacked_content_fp = "~/.local/share/Steam/steamapps/common/Stardew Valley/Content (unpacked)"
my_new_mod.output_fp = [ "~/.local/share/Steam/steamapps/common/Stardew Valley/Mods" ]
my_new_mod.dirname = "MyNewMod"

my_new_mod.i18n_internal["default"] = {
    "MyDefaultName": "Hello!",
    "MyDefaultText": "Bye!"
}
my_new_mod.i18n_internal["es"] = {
    "MyDefaultName": "¡Hola!",
    "MyDefaultText": "¡Adios!"
}

my_new_mod.AUTO_REGISTER = False
```

### Methods

Now, we can get into the methods of this class.

#### Mod.i18n

This method is used to return a string that Content Patcher recognizes as an i18n reference.

``Mod.i18n`` takes one argument:

* ``key`` (str) : The key for the i18n lookup.

``Mod.i18n`` returns a string that will reference the i18n.

Example:

```py
i18n = my_new_mod.i18n

i18n("MyDefaultName")
# returns "{{i18n:MyDefaultName}}"
```

#### Mod.Register

This method is used to register Entry objects with the mod. Registering Entry objects is not necessary if ``Mod.AUTO_REGISTER`` is ``True``.

``Mod.Register`` takes one* argument:

* ``*entries`` (Entry) : Entries to register into the mod.

``Mod.Register`` does not return anything.

Example:

```py
MyNewEntry = ptc.Entry(
    action = "EditData",
    target = "Data/Objects",
    entry_id = "_my_new_entry", # will be prefixed with {{ModID}}
    entry = {
        "Name": "Weird Carrot",
        # ...
    }
)

my_new_mod.Register(MyNewEntry)
```

#### Mod.Create

This method compiles the mod to every directory listed in ``Mod.output_fp``.

``Mod.Create`` takes one argument:

* ``dirname`` (str, optional) : Override for the mod directory name.

``Mod.Create`` does not return anything.

#### Mod.Destroy

This method attempts to remove the mod at every directory listed in ``Mod.output_fp``.

``Mod.Destroy`` takes no arguments.

``Mod.Destroy`` does not return anything.

#### Mod.FetchImage

This method fetches an image (or file in general?) and adds it to the assets folder of the mod. If given a relative file path, it evaluates from the location of the file; if given an absolute file path, it should work as expected.

``Mod.FetchImage`` takes two arguments:

* ``fp`` (str) : The file path of the asset.
* ``fpid`` (str) : The content patcher id of the asset. Typically of the format "{{ModID}}/[file name]"

``Mod.FetchImage`` returns an Entry object representing the asset.

#### Mod.RegisterContentFile

This method adds a ContentFile object to ``Mod.files``. Equivalent to:

```py
MyContentFile = ptc.ContentFile(
    # ...
)
my_new_mod.files.append(MyContentFile)
```

``Mod.RegisterContentFile`` takes one argument:

* ``file`` (ContentFile) : The ContentFile object to register.

``Mod.RegisterContentFile`` does not return anything.


## The Entry class

### Initialization

This class is initialized with 8 optional arguments:

(See: https://github.com/Pathoschild/StardewMods/blob/develop/ContentPatcher/docs/author-guide.md)

* ``entry_id`` (str) : The entry id (or, really, the entry key [when accessing a dictionary])
* ``entry`` (EntryDict|JsonTypes) : The data necessary for the edit. Usually is a dictionary of some sort, but can be any Json serializable value.
* ``action`` (str) : The action is the type of edit for Content Patcher to perform.
* ``target`` (str|list[str]) : The target data file.
* ``targetfield`` (list[str]) : The fields to target within the specified data file.
* ``fromfile`` (str|list[str]) : Usually paired with some sort of loading action. Points to a file.
* ``priority`` (str) : Specifies a patch priority.
* ``moveentries`` (list[dict[str, JsonTypes]]) : Pass move entries information to move entries around in data files.

As an example, let's make an entry:

```py
ExampleEntry = ptc.Entry(
    action = "EditData",
    target = "Data/Buffs",
    entry_id = "_MyNewBuff", # prefixed with {{ModID}}
    entry = {
        "DisplayName": "My New Buff",
        "Duration": 300,
        "IconTexture": "TileSheets\\BuffsIcons",
        "IconSpriteIndex": 9,
        "Effects": {
            "Speed": 2
        }
    }
)
```

When registered, compiled, and loaded into the game, this will create a new buff type that can be used by other Entry objects or SMAPI mods.

### Fields

All fields that may be necessary to edit have the same name as the arguments to the class initialization and represent the same values.

This mod has no methods.

## The ContentFile class

The ContentFile class represents separate json files that also hold Content Patcher entries. This is used to organize similar entries together.

### Initialization

This class is initialized with 1 positional argument and 1 optional argument:

* ``file_name`` (str) : The name of the file (prepended to ".json")
* ``entries`` (list[Entry]) : List of entries to include in the file.

Example:

```py
EntryOne = ptc.Entry(
    # ...
)
EntryTwo = ptc.Entry(
    # ...
)

GenericFile = ContentFile("generic_file", [EntryOne, EntryTwo])

my_new_mod.RegisterContentFile(GenericFile)
```

### Fields

There are two accessible fields:

* ``name`` (str) : The name of the file.
* ``entries`` (list[Entry]) : List of entries included in the file.

### Methods

#### ContentFile.Register

This method registers Entry objects with the file.

``ContentFile.Register`` takes one argument:

* ``entries`` (Entry|list[Entry]) : A list (or single) of Entry objects to register.

``ContentFile.Register`` does not return anything.

## Supplementary Functions

### pytocp.Entry_Curry

"Curries" Entry objects and allows for reusing argument values across multiple objects. 

``pytocp.Entry_Curry`` takes 9 arguments:

* ``entry_id`` (str) : The entry id (or, really, the entry key [when accessing a dictionary])
* ``entry`` (EntryDict|JsonTypes) : The data necessary for the edit. Usually is a dictionary of some sort, but can be any Json serializable value.
* ``action`` (str) : The action is the type of edit for Content Patcher to perform.
* ``target`` (str|list[str]) : The target data file.
* ``targetfield`` (list[str]) : The fields to target within the specified data file.
* ``fromfile`` (str|list[str]) : Usually paired with some sort of loading action. Points to a file.
* ``priority`` (str) : Specifies a patch priority.
* ``moveentries`` (list[dict[str, JsonTypes]]) : Pass move entries information to move entries around in data files.
* ``to_curry`` (Any) : The object to curry the inputs to. Defaults to the Entry class, but can also curry already curried instances of the class.

``pytocp.Entry_Curry`` returns a function that returns the curried class object.

Example:

```py
Vegetable = Entry_Curry(
    action = "EditData",
    target = "Data/Objects",
    entry = {
        "Type": "Vegetable",
        "Category": -75,
        "Texture": "Data\\Objects",
        "Price": 200,
        "Edibility": 15,
    }
)

MyNewVegetable = Vegetable(
    entry_id = "_MyNewVegetable", # prefixed with {{ModID}}
    entry = {
        "Name": "MyNewVegetable",
        "DisplayName": i18n("MyDefaultName"),
        "Description": i18n("MyDefaultText"),
        "SpriteIndex": 0
    }
)

MySecondNewVegetable = Vegetable(
    entry_id = "_MySecondNewVegetable", # prefixed with {{ModID}}
    entry = {
        "Name": "MySecondNewVegetable",
        "DisplayName": i18n("MyDefaultName"),
        "Description": i18n("MyDefaultText"),
        "SpriteIndex": 1
    }
)

my_new_mod.Register(MyNewVegetable, MySecondNewVegetable)
```