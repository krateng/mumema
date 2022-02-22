# mumema

mumema (**mu**sic **me**tadata **ma**nager) is a simple script for people who like to have information in an authorative text file to then write it to the individual audio files. As a little bonus, it also deals with the output files of [cdparanoia](https://xiph.org/paranoia/).

## Install

```sh
	pip install mumema
```

## How to use

You should have an album folder that either has filenames leading with numbers (e.g. `01_As-If-Its-Your-Last.flac`) or the output files of cdparanoia.

Create a file `metadata.yml` in this folder according to the example in the repository. Then simply run `mumema`. The script will convert and rename your cdparanoia files if present, then properly tag all files in the folder.
