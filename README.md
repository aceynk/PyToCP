# PyToCP

PyToCP is a python module aiming to simplify Content Patcher content pack creation.

# Info

This started as and, as of writing this, continues to be a personal project. It will be maintained to my needs. 
That being said, feel free to write up issues and pull requests! I'll likely see them.

This module writes mods for Content Patcher, which is for the game Stardew Valley. You should probably have both if you choose to use this.

Content Patcher (CP) is a Mod for Stardew Valley that allows editing of game data with json files.

CP can be found here: https://www.nexusmods.com/stardewvalley/mods/1915

CP is open source: https://github.com/Pathoschild/StardewMods/tree/stable/ContentPatcher



Stardew Valley (SDV) is a video game made by Concerned Ape.

Information can be found here: https://www.stardewvalley.net/

# Install

Git clone into the repo.

You can either build the module with:

```
pip3 install -e path/to/module
```

Or try adding the src folder to PYTHONPATH. The method for this differs based on OS. I use Linux, so I'll post that command below:

**Linux:**

```sh
export PYTHONPATH=path/to/module/src:$PYTHONPATH
```

# Documentation

Module documentation can be found here:

https://github.com/aceynk/PyToCP/blob/main/docs/en_tutorial.md

# Resources

The Stardew Valley Wiki is a great resource for learning how to mod.

https://stardewvalleywiki.com/Modding:Index

XnbHack is useful for extracting game data.

https://github.com/Pathoschild/StardewXnbHack/releases

ILSpy is useful for decompiling the base game in order to better mod with SMAPI.

https://github.com/icsharpcode/ILSpy

Personally, I use this cross-platform fork:

https://github.com/icsharpcode/AvaloniaILSpy/releases