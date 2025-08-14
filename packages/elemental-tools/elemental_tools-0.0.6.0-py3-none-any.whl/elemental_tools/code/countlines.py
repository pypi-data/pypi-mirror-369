import argparse
import os
import pandas as pd

from elemental_tools.logger import Logger

logger = Logger(app_name='count-lines', owner='counter').log


def count_lines(file_path):
	with open(file_path, 'r', encoding='utf-8') as file:
		return sum(1 for line in file)


def beautify_path(path: str) -> os.path:
	folders = []
	parent_folder = path
	for _ in range(3):
		parent_folder, folder = os.path.split(parent_folder)
		if not folder:
			break
		folders.insert(0, folder)

	return os.path.join(*folders)


def count_lines_in_directory(directory, ext):
	total_lines = 0

	specs = []

	for root, dirs, files in os.walk(directory):
		for file_name in files:
			if file_name.endswith(ext):
				file_path = os.path.join(root, file_name)
				lines = count_lines(file_path)
				specs.append({'File Name': file_path, 'Total Count': lines})
				total_lines += lines

	df = pd.DataFrame(specs)
	df.sort_values('Total Count', ascending=False, inplace=True)
	df['File Name'] = df['File Name'].apply(lambda x: beautify_path(x))
	df.reset_index(drop=True, inplace=True)
	return total_lines, df.iloc[:10]


def main():
	reproved = False

	parser = argparse.ArgumentParser(description='It will iterate over a certain folder in order to count lines of a specific extension.')
	parser.add_argument('-p', '-path', '--path', '--p', help='Extension to find and count lines')
	parser.add_argument('-e', '-ext', '--extension', '--ext', '-extension', help='Extension to find and count lines')

	arguments = parser.parse_args()

	if os.path.isdir(os.path.abspath(arguments.path)):
		if os.listdir(os.path.abspath(arguments.path)):

			try:
				logger('info', f"Counting...\n\tPath:{arguments.path}\n\tExtension:{arguments.extension}\n")
				total_lines, top_five = count_lines_in_directory(os.path.abspath(arguments.path), arguments.extension)
				logger('success', f"\nDirectory Path: {os.path.abspath(arguments.path)}\nExtension: {arguments.extension}\nTotal Line Count: {total_lines}\nTop 5 Largest Files:\n{str(top_five)}\n")
			except:
				reproved = True
				pass
		else:
			logger('error', "Selected Path is Empty")
	else:
		logger('error', "Provide a Valid Path. The Current Doesn't Exist")

