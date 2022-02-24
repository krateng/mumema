import yaml
import os
import subprocess
import re

from doreah.control import mainfunction
from doreah.io import col
from unidecode import unidecode

from . import formats

PARANOIA_NAMES = re.compile(r"track([0-9]+).cdda.[wav/flac]")
TRACKNUMBER_FIND = re.compile("[^0-9]*([0-9]+).*")
METADATA_FILENAMES = ['metadata.yml','album.yml']
RAW_FOLDER = 'wav_originals'

def clean_filename(filename):
	filename = unidecode(filename).replace(" - ","-").replace(" ","-").replace("/","-").strip()
	filename = ''.join(c for c in filename if (c.isalpha() or c=="_" or c=="-" or c=="."))
	return filename


def load_info_from_files(srcfile=None):
	possible_metadatafiles = [srcfile] if srcfile is not None else METADATA_FILENAMES

	# Go up the dir tree for all metadata files
	allfolders = []
	currentfolder = os.getcwd()
	while True:
		allfolders.append(currentfolder)
		if os.path.dirname(currentfolder) != currentfolder:
			currentfolder = os.path.dirname(currentfolder)
		else:
			# reached filesystem root
			break

	commontags = {}


	for folder in reversed(allfolders):
		for metadatafile in possible_metadatafiles:
			full_metadatafile = os.path.join(folder,metadatafile)
			if os.path.exists(full_metadatafile):
				print("Using metadata file",col['yellow'](full_metadatafile))
				with open(full_metadatafile,"r") as f:
					localdata = yaml.safe_load(f)
				commontags.update(localdata.pop('common_tags'))


	# use track info from last loaded file (in target folder)
	tracks = localdata.pop('tracks') if 'tracks' in localdata else []
	data = localdata

	for idx in tracks:
		if isinstance(tracks[idx],str):
			tracks[idx] = {'title':tracks[idx]}
		tracks[idx]['tracknumber'] = idx
		tracks[idx] = {**commontags,**tracks[idx]}

	print(f"Found information about {len(tracks)} tracks.")

	return data,tracks




def tag_all(data,tracks):

	# set defaults if missing
	#data['separator'] = data.get('separator','.')
	data['filename_regex'] =  data.get('filename_regex',TRACKNUMBER_FIND)
	data['remove_artwork'] = data.get('remove_artwork',False)
	data['move_raw_files'] = data.get('move_raw_files',True)

	# check files
	for f in sorted(os.listdir('.')):
		ext = f.split('.')[-1].lower()



		if ext in formats.handlers or ext == 'wav':
			print()
			print("Found",col['orange'](f))

			match = PARANOIA_NAMES.match(f)

			# fresh files from cdparanoia
			if match is not None:
				paranoia = True
				idxguess_padded = match.groups()[0]
				idxguess = int(idxguess_padded)
				print(f"    Looks like a cdparanoia file...")

			# alrady named files
			else:
				paranoia = False
				try:
					match = data['filename_regex'].match(f)
					idxguess = int(match.groups()[0])
				except:
					idxguess = None

			# match to track info
			if idxguess not in tracks:
				print(f"    Could not be matched to a track!")
				continue

			tracktags = tracks[idxguess]
			if paranoia:
				newf = f"{idxguess_padded}.{clean_filename(tracktags['title'])}.flac"

				# Convert if necessary
				if ext == 'wav':
					print("    Converting",f,"to",newf)
					with open('ffmpeg.log','a') as logf:
						code = subprocess.run(["ffmpeg","-nostdin","-i",f,newf],stdout=logf,stderr=logf).returncode
					if code != 0:
						print(col['red']("    Error while converting. Please check ffmpeg.log."))
						continue
					if data['move_raw_files']:
						print(f"    Moving wav file to {RAW_FOLDER}")
						os.makedirs(RAW_FOLDER,exist_ok=True)
						os.rename(f,os.path.join(RAW_FOLDER,f))
					ext = 'flac'
				else:
					print("    Renaming",f,"to",newf)
					os.rename(f,newf)
				f = newf

			print(col['lawngreen'](f"    Tagging as: {tracktags}"))

			# let the format handler take over
			formats.handlers[ext].tag(f,tracktags,data)

	print()
	print("All done!")


@mainfunction({'f':'srcfile'},shield=True)
def main(srcfile=None):
	info = load_info_from_files(srcfile)
	if info is not None:
		data,tracks = info
		return tag_all(data,tracks)
