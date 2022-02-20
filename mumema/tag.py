import os
import subprocess


def tag_all(data,tracks):

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
		
			if ext == 'flac':
				subprocess.call(["metaflac","--remove","--block-type=VORBIS_COMMENT",f])
				subprocess.call(["metaflac",f] + [f"--set-tag={key.upper()}={value}" for key,value in tracktags.items()])
				if data['remove_artwork']:
					subprocess.call(["metaflac","--remove","--block-type=PICTURE",f])
