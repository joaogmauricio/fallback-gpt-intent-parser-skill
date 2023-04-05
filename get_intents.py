from padatious.util import expand_parentheses
import os
import sys
import re
import fnmatch

PATH = '/opt/mycroft/skills'
LANGCODE = 'en-us'
OUTPUT_FILE = '/opt/mycroft/skills/fallback-gpt-intent-parser-skill/intents.txt'

MIN_INTENT_LEN = 10
MAX_LINES_PER_INTENT = 2
MAX_LINES_PER_EXPANSION = 2


def find_intent_files(start_dir, langcode):
	"""
	Given a starting directory and a language code, find all files within its subdirectories that end with *.intent
	and have a directory structure of "locale/langcode/*.intent", and create a list where the elements are all the
	lines from these files.
	"""
	intent_lines = []
	pattern1 = os.path.join(start_dir, '**', 'locale', langcode, '*.intent')
	pattern2 = os.path.join(start_dir, '**', 'vocab', langcode, '*.intent')
	for root, dirs, files in os.walk(start_dir):
		for file in fnmatch.filter(files, '*.intent'):
			file_path = os.path.join(root, file)
			if fnmatch.fnmatch(file_path, pattern1) or fnmatch.fnmatch(file_path, pattern2):
				with open(file_path, 'r') as f:
					lines = f.readlines()
					if len(lines) > 0:
						ct = 0
						for line in lines:
							if len(line) < MIN_INTENT_LEN:
								continue
							else:
								intent_lines.append(line)
								ct += 1
							if ct == MAX_LINES_PER_INTENT:
								break
	return intent_lines


def write_list_to_file(items, filename):
	with open(filename, 'w') as f:
		f.write("Consider the following intents list: ")
		f.write(", ".join([f"\"{item.rstrip()}\"" for item in items]))


if __name__ == '__main__':
	path = PATH
	langcode = LANGCODE
	output_file = OUTPUT_FILE
	intent_lines = find_intent_files(path, langcode)

	all_expansions = []

	for intent in intent_lines:
		expansions = expand_parentheses(intent)
		ct = 0
		for expansion in expansions:
			all_expansions.append(re.sub(' +', ' ', ''.join(expansion)).strip(" "))
			ct += 1
			if ct == MAX_LINES_PER_EXPANSION:
				break

	final_expansions = list(dict.fromkeys(all_expansions))

	write_list_to_file(final_expansions, output_file)

# DEBUG
#	if len(intent_lines) > 0:
#		print(len(intent_lines), ":", len(final_expansions), ":", len(final_expansions)/len(intent_lines))

