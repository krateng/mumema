import subprocess

class FLAC_Tagger:
	extensions = ('flac',)

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



handlers = {
	'flac':FLAC_Tagger(),
}
