import subprocess
import itertools


handlers = {}

class FormatHandler:
	def __init_subclass__(cls):
		for ext in cls.extensions:
			handlers[ext] = cls()

class Vorbis(FormatHandler):
	extensions = ('flac','opus')

	tagnames = {
		# https://xiph.org/vorbis/doc/v-comment.html
		"title":"TITLE",
		"artist":"ARTIST",
		"albumartist":"ALBUMARTIST",
		"album":"ALBUM",
		"genre":"GENRE",
		"date":"DATE",
		"tracknumber":"TRACKNUMBER"
	}

	def tag(self,file,tags,data):

		subprocess.call(["metaflac","--remove","--block-type=VORBIS_COMMENT",file])
		subprocess.call(["metaflac",file] + [f"--set-tag={self.tagnames[key]}={value}" for key,value in tags.items()])
		if data['remove_artwork']:
			subprocess.call(["metaflac","--remove","--block-type=PICTURE",file])


class ID3(FormatHandler):
	extensions = ('mp3',)

	tagnames = {
		# https://id3.org/id3v2.3.0#Text_information_frames
		"title":"TIT2",
		"artist":"TPE1",
		"albumartist":"TPE2", # not to specs, but commonly used,
		"album":"TALB",
		"genre":"TCON", # :/
		"date":"TYER",
		"tracknumber":"TRCK"
	}

	def tag(self,file,tags,data):
		subprocess.call(["id3v2"] + list(itertools.chain(*[[f"--{self.tagnames[key]}",str(value)] for key,value in tags.items()])) + [file])
