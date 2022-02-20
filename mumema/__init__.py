from doreah.control import mainfunction

import yaml
import os

from . import tag, rename

commands = {
	'tag':tag.tag_all,
	'rename':rename.rename_all
}


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

@mainfunction({'f':'srcfile'},shield=True)
def main(command,*args,srcfile=None,**kwargs):
	info = load_info_from_file(srcfile)
	if info is not None:
		data,tracks = info
		return commands[command](data,tracks)
