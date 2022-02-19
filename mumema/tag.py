import yaml
import os
import subprocess
import glob


def tag_all(srcfile=None):
	possible_metadatafiles = [srcfile] if srcfile is not None else ['metadata.yml','album.yml']

	### load file
	for metadatafile in possible_metadatafiles:
		if os.path.exists(metadatafile):
			print(f"Using metadata file {metadatafile}")
			with open(metadatafile) as mdf:
				data = yaml.safe_load(mdf)
				break
	else:
		print("Could not find metadata file.")
		exit()
		

	# organize data
	commontags = data.pop('album_tags')
	tracks = data.pop('tracks')

	for idx in tracks:
		if isinstance(tracks[idx],str):
			tracks[idx] = {'title':tracks[idx]}
		tracks[idx]['tracknumber'] = idx
	
	print(f"Found information about {len(tracks)} tracks.")



	# check files	
	for f in os.listdir('.'):
		ext = f.split('.')[-1].lower()
		if ext in ['flac']:
			idxguess = int(f.split(data['separator'])[0])
			if idxguess not in tracks:
				print(f"{f} could not be matched to a track!")
				continue
			tracktags = tracks[idxguess]
			print(f"Tagging {f} as: {tracktags}")
			alltags = {**commontags,**tracktags}
		
			if ext == 'flac':
				subprocess.call(["metaflac","--remove","--block-type=VORBIS_COMMENT",f])
				subprocess.call(["metaflac",f] + [f"--set-tag={key.upper()}={value}" for key,value in alltags.items()])
				if data['remove_artwork']:
					subprocess.call(["metaflac","--remove","--block-type=PICTURE",f])
