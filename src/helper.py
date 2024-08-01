from os.path import join
import json


def rec_trav(tdict: dict, keys: list[str]):
	if len(keys) == 0:
		return tdict
	if len(keys) == 1:
		return tdict[keys[0]]
	return rec_trav(tdict[keys[0]], keys[1:])


def dict_tree(keys: list[str], cur_dict: dict = {}):
	if len(keys) == 0:
		return cur_dict
	if len(keys) == 1:
		return {keys[0] : cur_dict}
	
	return dict_tree(keys[:-1], {keys[-1] : cur_dict})