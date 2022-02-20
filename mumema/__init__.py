from doreah.control import mainfunction

import yaml
import os
import subprocess
import re
from unidecode import unidecode

paranoianames = re.compile(r"track([0-9]+).cdda.[wav/flac]")

def clean_filename(filename):
	filename = unidecode(filename).replace(" - ","-").replace(" ","-").replace("/","-").strip()
	filename = ''.join(c for c in filename if (c.isalpha() or c=="_" or c=="-" or c=="."))
	return filename


def load_info_from_file(srcfile=None):
	possible_metadatafiles = [srcfile] if srcfile is not None else ['metadata.yml','album.yml']

	for metadatafile in possible_metadatafiles:
		if os.path.exists(metadatafile):
			print(f"Using metadata file {metadatafile}")
			with open(metadatafile) as mdf:
				data = yaml.safe_load(mdf)

				# organize data
				commontags = data.pop('album_tags')
				tracks = data.pop('tracks')

				for idx in tracks:
					if isinstance(tracks[idx],str):
						tracks[idx] = {'title':tracks[idx]}
					tracks[idx]['tracknumber'] = idx
					tracks[idx] = {**commontags,**tracks[idx]}

				print(f"Found information about {len(tracks)} tracks.")

				return data,tracks
	else:
		print("Could not find metadata file.")
		return None



def tag_all(data,tracks):

	# check files
	for f in os.listdir('.'):
		ext = f.split('.')[-1].lower()



		if ext in ['flac','wav']:

			match = paranoianames.match(f)

			# fresh files from cdparanoia
			if match is not None:
				paranoia = True
				idxguess_padded = match.groups()[0]
				idxguess = int(idxguess_padded)
				print(f"{f} seems to be a cdparanoia file.")

			# alrady named flac files
			else:
				paranoia = False
				idxguess = int(f.split(data['separator'])[0])

			# match to track info
			if idxguess not in tracks:
				print(f"{f} could not be matched to a track!")
				continue

			tracktags = tracks[idxguess]
			if paranoia:
				# use the separator defined by the user
				newf = f"{idxguess_padded}{data['separator']}{clean_filename(tracktags['title'])}.flac"

				# Convert if necessary
				if ext == 'wav':
					print("Converting",f,"to",newf)
					subprocess.call(["ffmpeg","-i",f,newf])
					ext = 'flac'
				else:
					print("Renaming",f,"to",newf)
					os.rename(f,newf)
				f = newf

			print(f"Tagging {f} as: {tracktags}")

			if ext == 'flac':
				subprocess.call(["metaflac","--remove","--block-type=VORBIS_COMMENT",f])
				subprocess.call(["metaflac",f] + [f"--set-tag={key.upper()}={value}" for key,value in tracktags.items()])
				if data['remove_artwork']:
					subprocess.call(["metaflac","--remove","--block-type=PICTURE",f])


@mainfunction({'f':'srcfile'},shield=True)
def main(srcfile=None):
	info = load_info_from_file(srcfile)
	if info is not None:
		data,tracks = info
		return tag_all(data,tracks)
