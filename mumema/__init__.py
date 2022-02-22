import yaml
import os
import subprocess
import re

from doreah.control import mainfunction
from doreah.io import col
from unidecode import unidecode

paranoianames = re.compile(r"track([0-9]+).cdda.[wav/flac]")
metadata_filenames = ['metadata.yml','album.yml']

def clean_filename(filename):
	filename = unidecode(filename).replace(" - ","-").replace(" ","-").replace("/","-").strip()
	filename = ''.join(c for c in filename if (c.isalpha() or c=="_" or c=="-" or c=="."))
	return filename


def load_info_from_files(srcfile=None):
	possible_metadatafiles = [srcfile] if srcfile is not None else metadata_filenames

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
	tracks = localdata.pop('tracks')
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
	data['separator'] = data.get('separator','.')
	data['remove_artwork'] = data.get('remove_artwork',False)

	# check files
	for f in os.listdir('.'):
		ext = f.split('.')[-1].lower()



		if ext in ['flac','wav']:
			print()
			print("Found",col['orange'](f))

			match = paranoianames.match(f)

			# fresh files from cdparanoia
			if match is not None:
				paranoia = True
				idxguess_padded = match.groups()[0]
				idxguess = int(idxguess_padded)
				print(f"    Looks like a cdparanoia file...")

			# alrady named flac files
			else:
				paranoia = False
				idxguess = int(f.split(data['separator'])[0])

			# match to track info
			if idxguess not in tracks:
				print(f"    Could not be matched to a track!")
				continue

			tracktags = tracks[idxguess]
			if paranoia:
				# use the separator defined by the user
				newf = f"{idxguess_padded}{data['separator']}{clean_filename(tracktags['title'])}.flac"

				# Convert if necessary
				if ext == 'wav':
					print("    Converting",f,"to",newf)
					with open('ffmpeg.log','a') as logf:
						code = subprocess.run(["ffmpeg","-nostdin","-i",f,newf],stdout=logf,stderr=logf).returncode
					if code != 0: print(col['red']("    Error while converting. Please check ffmpeg.log."))
					ext = 'flac'
				else:
					print("    Renaming",f,"to",newf)
					os.rename(f,newf)
				f = newf

			print(f"    Tagging as: {tracktags}")

			if ext == 'flac':
				subprocess.call(["metaflac","--remove","--block-type=VORBIS_COMMENT",f])
				subprocess.call(["metaflac",f] + [f"--set-tag={key.upper()}={value}" for key,value in tracktags.items()])
				if data['remove_artwork']:
					subprocess.call(["metaflac","--remove","--block-type=PICTURE",f])


@mainfunction({'f':'srcfile'},shield=True)
def main(srcfile=None):
	info = load_info_from_files(srcfile)
	if info is not None:
		data,tracks = info
		return tag_all(data,tracks)
