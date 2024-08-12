"""
A Python script made to provide tools for Content Patcher mod development.

Important contents:
    (class) Mod

    (class) Entry

    (class) ContentFile
    
    (function) Entry_Curry

    (global Mod) _MOD
"""

from os.path import abspath, join, basename, split
from os import mkdir, chdir
from typing import Any, NewType
from shutil import rmtree, copyfile
from copy import deepcopy
from inspect import stack
from requests import get
from helper import rec_trav, dict_tree
from time import perf_counter
import re
import json

JsonTypes = type["str|int|list[Any]|dict[Any]"]
"""Types that json supports."""
EntryDict = type["dict[str, list[JsonTypes]]"]
"""Type for the Entry Content Patcher field."""

_MOD = None
"""Internally used global mod instance. Overriden on every new mod object initialization."""


def _hash_entry(action: str, target: str, targetfield: list, fromfile: str, priority: str) -> int:
    """Internal function.

    Args:
        action (str): Action value for entry.
        target (str): Target value for entry.
        targetfield (list): TargetField value for entry.
        fromfile (str): FromFile value for entry.
        priority (str): Priority value for entry.

    Returns:
        int: A hash value for the entry target data.
    """
    def else_to_string(value: "str|list|None"):
        """Internal method
        """
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return ", ".join(value)
        if value is None:
            return ""
    
    this_hash = hash("".join([*map(else_to_string, [action, target, targetfield, fromfile])]))

    _MOD._hash_lookup[this_hash] = {
        "Action": action,
        "Target": else_to_string(target),
        "TargetField": targetfield,
        "FromFile": else_to_string(fromfile),
        "Priority": priority
    }

    return this_hash


_new_replace = lambda x, y : y if y else x


def eval_entry(entry):
    if _MOD.unpacked_content_fp is None:
        return
    
    if not entry.action == "EditData":
        return
    
    directory = re.split(r"\\|/", entry.target)
    
    fp = join(_MOD.unpacked_content_fp, *directory[:-1], directory[-1] + ".json")
	
    try:
        file = json.load(open(fp, "r"))
    except FileNotFoundError:
        print(f'Could not find data file {directory[-1] + ".json"}.')
        return
    except:
        print(f"An unknown error occurred when finding data file.")
        return
	
    if isinstance(file, list):
        return entry.entry
	
    base_dict = rec_trav(file, entry.targetfield)
	
    base_dict[entry.entry_id] = entry.entry
	
    if entry.targetfield == []:
        return {entry.entry_id : entry.entry}
    else:
        return dict_tree(entry.targetfield, base_dict)
    

def _adv_dict_merge(dict1, dict2):
    dict1 = deepcopy(dict1)
    
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return _new_replace(dict2, dict1)

    for key in dict2:
        if isinstance(dict2[key], str) or isinstance(dict2[key], int):
            dict1[key] = dict2[key]

        elif isinstance(dict2[key], list):
            if not key in dict1:
                dict1[key] = dict2[key]
                continue

            dict1[key] = dict1[key] + dict2[key]

        elif isinstance(dict2[key], dict):
            if not key in dict1:
                dict1[key] = dict2[key]
                continue

            dict1[key] = dict1[key] | dict2[key]

    return dict1


class Entry:
    """A Content patcher entry, represented as a Python class.

    Args:
        entry_id (str, optional): The unique id for the entry (also see: Mod.PREFIX_WITH_MODID). Defaults to "".
        entry (EntryDict | Any, optional): The entry data. Defaults to None.
        action (str, optional): The action key for the entry. Designates how the patch should be dealt with. Defaults to None.
        target (str | list[str], optional): The data to target. Defaults to None.
        targetfield (list[str], optional): The field to target within the ``target`` data; a path in list format. Defaults to None.
        fromfile (str | list[str], optional): The file to be recognized by Content Patcher. Defaults to None.
        priority (str, optional): How important this entry is. Defaults to None.
        moveentries (list[dict[str, JsonTypes]], optional): Describes how to move entries in the data. Defaults to None.
    """

    def __init__(
            self,
            entry_id: str = "",
            entry: "EntryDict|JsonTypes" = None,
            action: str = None,
            target: "str|list[str]" = None,
            targetfield: list[str] = [],
            fromfile: "str|list[str]" = None,
            priority: str = None,
            moveentries: list[dict[str, JsonTypes]] = []
        ):
        """A Content Patcher entry, represented as a Python object.

        Args:
            entry_id (str, optional): The unique id for the entry (also see: Mod.PREFIX_WITH_MODID). Defaults to "".
            entry (EntryDict | Any, optional): The entry data. Defaults to None.
            action (str, optional): The action key for the entry. Designates how the patch should be dealt with. Defaults to None.
            target (str | list[str], optional): The data to target. Defaults to None.
            targetfield (list[str], optional): The field to target within the ``target`` data; a path in list format. Defaults to None.
            fromfile (str | list[str], optional): The file to be recognized by Content Patcher. Defaults to None.
            priority (str, optional): How important this entry is. Defaults to None.
            moveentries (list[dict[str, JsonTypes]], optional): Describes how to move entries in the data. Defaults to None.
        """

        self.entry_id = entry_id

        if _MOD.PREFIX_WITH_MODID:
            self.entry_id = "{{ModID}}" + entry_id

        self.action = action
        self.targetfield = targetfield
        self.entry = entry
        self.priority = priority
        self.moveentries = moveentries
        
        self.file = ""

        self.file = ""

        if isinstance(target, list):
            self.target = ", ".join(target)
        else:
            self.target = target

        if isinstance(fromfile, list):
            self.fromfile = ", ".join(fromfile)
        else:
            self.fromfile = fromfile

        self.hash = _hash_entry(action, target, targetfield, fromfile, priority)

        if _MOD.AUTO_REGISTER:
            _MOD.Register(self)
            
        log = eval_entry(self)
        if not log is None:
            print(json.dumps(log, indent=4))


class ContentFile:
    def __init__(self, file_name: str, *entries: Entry):
        self.name = file_name
        self.entries = {}
        self.moveentries = {}
        self.Register(*entries)

    def Register(self, *entries: Entry):
        for entry in entries:

            if not entry.hash in self.entries:
                self.entries[entry.hash] = {}
            self.entries[entry.hash][entry.entry_id] = entry.entry
            
            if not entry.hash in self.moveentries:
                self.moveentries[entry.hash] = []
            self.moveentries[entry.hash] += entry.moveentries


def Entry_Curry(
        entry_id: str = "",
        entry: EntryDict = {},
        action: str = None,
        target: "str|list[str]" = None,
        targetfield: list[str] = [],
        fromfile: "str|list[str]" = None,
        priority: str = None,
        moveentries: list[dict[str, JsonTypes]] = [],
        to_curry: Any = Entry,
        register_with: ContentFile = None
    ):

    c_entry_id = entry_id
    c_entry = entry
    c_action = action
    c_target = target
    c_targetfield = targetfield
    c_fromfile = fromfile
    c_priority = priority
    c_moveentries = moveentries

    def _curried_entry(
            entry_id: str = "",
            entry: EntryDict = {},
            action: str = None,
            target: "str|list[str]" = None,
            targetfield: list[str] = None,
            fromfile: "str|list[str]" = None,
            priority: str = None,
            moveentries: list[dict[str, JsonTypes]] = []
        ) -> "Entry|Any":

        out = to_curry(
            entry_id = _new_replace(entry_id, c_entry_id),
            entry = _adv_dict_merge(c_entry, entry),
            action = _new_replace(action, c_action),
            target = _new_replace(target, c_target),
            targetfield = _new_replace(targetfield, c_targetfield),
            fromfile = _new_replace(fromfile, c_fromfile),
            priority = _new_replace(priority, c_priority),
            moveentries = _new_replace(moveentries, c_moveentries)
        )
        
        if not register_with is None:
            register_with.Register(out)
            
        return out

    return _curried_entry


def reload_SMAPI():
    ## only if WebServerCommands is installed and enabled. ##
    
    WebServerCommandsURL = "http://127.0.0.1:56802/execute"
    
    get(WebServerCommandsURL + f"?command=patch reload {_MOD.manifest['UniqueId']}")


def log(*string: tuple[str]):
    _MOD._log_file += "\n".join(string) + "\n"*2


class Mod:
    def __init__(
        self,
        name: str,
        author: str,
        version: str,
        description: str,
        uid: str,
        update_key_nexus: int = None,
        update_key_github: str = None,
        contentpack_for: str = "Pathoschild.ContentPatcher",
        dependencies: list[dict[str, str]] = None
        ):

        self._start = perf_counter()

        def _setattr_prefix(self, func):
            """Internal wrapping method.

            Args:
                func (function): The function to wrap
            """
            def wrapper(self, name: str, value: Any) -> None:
                """Internal wrapping method.
                Monkeypatch prefix to .__setattr__

                Args:
                    name (str): Attribute name
                    value (Any): Attribute value
                """
                if name in _extra and value:
                    func(name, _extra[name](value))
                    return
                func(name, value)

            return wrapper

        Mod.__setattr__ = _setattr_prefix(self, self.__setattr__)

        _extra: dict[str, function[Any, Any]] = {
            "unpacked_content_fp": 
            lambda v : abspath(v),
            "output_fp":
            lambda v : [abspath(x) for x in v] if v != [""] else [abspath("")]
        }
        """Internal dict for the __setattr__ monkeypatch."""
        
        self.manifest: "dict[str, str|list[str]|dict[str,str]]" = {
            "Name": name,
            "Author": author,
            "Version": version,
            "Description": description,
            "UniqueId": uid,
            "UpdateKeys": [],
            "ContentPackFor": {
                "UniqueId": contentpack_for
            }
        }
        """The mod manifest for this mod. Auto generated on class initialization"""

        if update_key_github:
            self.manifest["UpdateKeys"].append("Github:" + update_key_github)

        if update_key_nexus:
            self.manifest["UpdateKeys"].append("Nexus:" + str(update_key_nexus))

        if dependencies:
            self.manifest["Dependencies"] = dependencies;

        self.unpacked_content_fp : str = None
        """The filepath for the unpacked Stardew Valley content folder."""
        self.output_fp : list[str] = [""]
        """The list of output filepaths to create the mod in."""
        self.dirname: str = "NewMod"
        """The name of the mod folder for the mod. Defaults to the mod name in the manifest."""
        self.files: list[ContentFile] = []
        """The list of ContentFile objects registered with the mod."""

        self.entries: dict[int, dict[str, EntryDict]] = {}
        """Contains the registered entries for the mod."""
        self.moveentries: dict[int, dict[str, EntryDict]] = {}
        """Contains the MoveEntries data for the mod."""

        self.i18n_internal: dict[str, dict[str, str]] = {}
        """i18n dict. Use Mod.i18n(key) to get the i18n reference token for the given key."""

        global _MOD
        _MOD = self

        self._hash_lookup: dict[int, dict[str, str|list]] = {}
        """Internally used entry hash table."""

        self._file = stack()[1].filename
        """Used to help resolve relative imports."""

        self.PREFIX_WITH_MODID: bool = True
        """Whether or not to prefix entry_id values passed with "{{ModID}}"."""
        self.AUTO_REGISTER: bool = True
        """Whether to automatically register new Entry objects."""
        self.AUTO_RELOAD: bool = False
        """Whether or not to automatically reload the mod through SMAPI. Requires the WebServerCommands mod (and SMAPI running)."""

        self._logged = set()


    def _log_once(self, msg: str) -> None:
        if not hash(msg) in self._logged:
            print(msg)
            self._logged |= {hash(msg)}
    
    def i18n(self, key: str) -> str:
        """Returns the i18n reference token for the given key.

        Args:
            key (str): i18n key.

        Returns:
            str: The reference token for the i18n key.
        """

        return "{{i18n:" + key + "}}"


    def Register(self, *entries: Entry) -> None:
        """Registers Entry objects with the mod. (also see: pytocp.AUTO_REGISTER)
        """

        for entry in entries:

            if entry.entry is None:
                self.entries[entry.hash] = None
            elif not entry.hash in self.entries:
                self.entries[entry.hash] = {entry.entry_id: entry.entry}
            else:
                self.entries[entry.hash][entry.entry_id] = entry.entry


            if entry.moveentries is None:
                self.moveentries[entry.hash] = None
            elif not entry.hash in self.moveentries:
                self.moveentries[entry.hash] = entry.moveentries
            else:
                self.moveentries[entry.hash] += entry.moveentries


    def Create(self, dirname: str = None) -> None:
        """Compiles the mod in all directories

        Args:
            dirname (str, optional): Optional dirname override. Will default to the mod name.
        """
        if not dirname: dirname = self.manifest["Name"]
        self.dirname = dirname
        

        def trymkdir(path: str, folder_name: str) -> None:
            """Internal method.

            Args:
                path (str): Filepath for directory.
                folder_name (str): Log name for directory
            """
            try: 
                mkdir(path)
                
            except IsADirectoryError:
                self._log_once(f"Skipping creating {folder_name} folder - folder already exists.")
            except FileExistsError:
                self._log_once(f"Skipping creating {folder_name} folder - folder already exists.")
            except FileNotFoundError:
                print("Invalid filepath.")
            except Exception as e:
                print(f"Cannot create {folder_name} folder, an unknown error occurred.")


        for odir in self.output_fp:
            trymkdir(join(odir, dirname), "mod")


        def writefile(name: "str|None", subdir: str = None, fp: str = None) -> Any:
            """Internal method.

            Args:
                name (str|None): 
                subdir (str, optional): Within the main mod, the subfolder to write to. Defaults to None.
                fp (str, optional): The base file path to write to. Defaults to None.

            Returns:
                Any: Either the opened file to be written to, or a lambda currying ``subdir``.
            """
            
            return open(join(fp, dirname, "" if subdir is None else subdir, name + ".json"), "w")

        for odir in self.output_fp:
            try:
                writefile("manifest", fp=odir).write(json.dumps(self.manifest, indent=4))
                self._log_once("Successfully wrote manifest.json")
            except Exception as e:
                print(f"Couldn't write manifest.json with error: {e}")
                
        if len(self.files) > 0:
            for odir in self.output_fp:
                trymkdir(join(odir, dirname, "code"), "code")
                
        content_load_string = []
        
        for contentfile in self.files:
            content_load_string.append(f"code/{contentfile.name}.json")
            
            file_content = [
                {
                    change_data[0]: change_data[1]
                    for change_data in self._hash_lookup[hash_key].items()
                    if not change_data is None
                }
                | {"uid": hash_key}
                for hash_key in contentfile.entries.keys()
            ]
            
            for fchange in file_content:
                fcur_id = fchange["uid"]
                fchange.pop("uid")
                
                for fc_key in [*fchange.keys()]:
                    if not fchange[fc_key]:
                        fchange.pop(fc_key)
                        
                if not contentfile.entries[fcur_id] is None:
                    fchange["Entries"] = contentfile.entries[fcur_id]
                    
                if fcur_id in contentfile.moveentries.keys() and not contentfile.moveentries[fcur_id] == []:
                    fchange["MoveEntries"] = contentfile.moveentries[fcur_id]
                
            for odir in self.output_fp:
                try:
                    writefile(contentfile.name, "code", odir)\
                        .write(json.dumps({"Changes": file_content}, indent=4))
                except:
                    print(f"Couldn't write the \"{contentfile.name}\" Content File.")
                
            
        if len(self.files) > 0:
            prev_aRegister = deepcopy(self.AUTO_REGISTER)
            self.AUTO_REGISTER = True
            
            Entry(
                action = "Include",
                fromfile = content_load_string
            )
            
            self.AUTO_REGISTER = prev_aRegister

        
        if len(self.files) > 0:
            for odir in self.output_fp:
                trymkdir(join(odir, dirname, "code"), "code")


        content_load_string = []

        
        for contentfile in self.files:
            content_load_string.append(f"code/{contentfile.name}.json")

            file_content = [
                {
                    change_data[0]: change_data[1]
                    for change_data in self._hash_lookup[hash_key].items()
                    if not change_data[1] is None
                }
                | {"uid": hash_key}
                for hash_key in contentfile.entries.keys()
            ]

            for fchange in file_content:
                fcur_id = fchange["uid"]
                fchange.pop("uid")

                for fc_key in [*fchange.keys()]:
                    if not fchange[fc_key]:
                        fchange.pop(fc_key)

                if not contentfile.entries[fcur_id] is None:
                    fchange["Entries"] = contentfile.entries[fcur_id]

                if fcur_id in contentfile.moveentries.keys() and not contentfile.moveentries[fcur_id] == []:
                    fchange["MoveEntries"] = contentfile.moveentries[fcur_id]

            for odir in self.output_fp:
                try:
                    writefile(contentfile.name, "code", odir)\
                        .write(json.dumps({"Changes": file_content}, indent=4))
                except:
                    print(f"Couldn't write the \"{contentfile.name}\" Content File.")


        if len(self.files) > 0:
            prev_aRegister = deepcopy(self.AUTO_REGISTER)
            self.AUTO_REGISTER = True

            Entry(
                action = "Include",
                fromfile = content_load_string
            )

            self.AUTO_REGISTER = prev_aRegister


        content: list[dict[str: str|int]] = [
            {
                change_data[0]: change_data[1]
                for change_data in self._hash_lookup[hash_key].items()
                if not change_data[1] is None
            }
            | {"uid": hash_key}
            for hash_key in self.entries.keys()
        ]

        for change in content:
            cur_id = change["uid"]
            change.pop("uid")

            for c_key in [*change.keys()]:
                if not change[c_key]:
                    change.pop(c_key)

            if not self.entries[cur_id] is None:
                change["Entries"] = self.entries[cur_id]

            if cur_id in self.moveentries.keys() and not self.moveentries[cur_id] == []:
                change["MoveEntries"] = self.moveentries[cur_id]

        for odir in self.output_fp:
            try:
                writefile("content", fp=odir)\
                    .write(json.dumps({"Format":"2.2.0","Changes":content}, indent=4))
                self._log_once("Successfully wrote content.json")
            except Exception as e:
                print(f"Couldn't write content.json with error: {e}")


        if len(self.i18n_internal.keys()) != 0:
            for odir in self.output_fp:
                trymkdir(join(odir, dirname, "i18n"), "i18n")
            for locale in self.i18n_internal:
                for odir in self.output_fp:
                    try:
                        writefile(join("i18n", locale), fp=odir)\
                        .write(json.dumps(self.i18n_internal[locale], indent=4))
                    except Exception as e:
                        print(f"Couldn't write {locale}.json with error: {e}")


        print(f"Successfully compiled \"{self.manifest['Name']}\" at {', '.join([join(x, dirname) for x in self.output_fp])}!")
        
        if self.AUTO_RELOAD:
            try:
                reload_SMAPI()
            except Exception as e:
                print(f"Failed to reload content pack with {e.__class__.__name__}")
                


    def Destroy(self):
        """Attempts to remove every instance of the mod created by pytocp.
        """
        success = True

        def fail(_,__,___):
            nonlocal success
            success = False

        for odir in self.output_fp:
            rmtree(
                join(odir, self.dirname),
                onerror= fail
            )

        if success:
            print(f"Successfully removed \"{self.manifest['Name']}\"")
        else:
            print("Failed to remove the mod. Please do it manually.")


    def FetchImage(self, fp: str, fpid: str) -> Entry:
        """Fetches an asset for use in the content pack. Copies it to an assets folder within the mod.

        Args:
            fp (str): File path for asset.
            fpid (str): Internal Content Patcher id for fetched asset.
        """
        self.dirname = self.manifest["Name"]

        chdir(split(self._file)[0])

        for odir in self.output_fp:
            try:
                mkdir(join(odir, self.dirname, "assets"))
            except IsADirectoryError:
                self._log_once("Skipping making assets folder - already exists")
            except FileExistsError:
                print("Failed to write assets folder.")
            except FileNotFoundError:
                print("Invalid directory passed.")
            except Exception as e:
                print(f"An unknown error occured: {e}")

        for odir in self.output_fp:
            try:
                copyfile(fp, join(odir, self.dirname, "assets", basename(fp)))
            except Exception as e:
                self._log_once(f"Failed to add asset ({fp}) to mod with {e.__class__.__name__}. Using directory: {abspath(fp)}.")


        return Entry(
            action = "Load",
            target = fpid,
            fromfile = "assets/" + basename(fp)
        )


    def RegisterContentFile(self, file: ContentFile):
        self.files.append(file)