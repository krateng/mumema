from doreah.control import mainfunction

from . import tag, rename

commands = {
	'tag':tag.tag_all,
	'rename':rename.rename_all
}

@mainfunction({'f':'srcfile'},shield=True)
def main(command,*args,**kwargs):
	return commands[command](*args,**kwargs)
