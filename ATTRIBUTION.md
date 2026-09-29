# Attribution and provenance

This repository packages Kian-hdr's original `dvd-digitize-archive` assistant skill,
developed with AI assistance. The inspected skill contained nine files: `SKILL.md`,
`agents/openai.yaml`, five Markdown references, and two zsh monitor scripts. There
were no bundled assets, template files, third-party source files, license files,
or attribution notices in that source tree. The original unlicensed material and
new public packaging are released under MIT with the owner's authorization.

All original workflow references and both script entry-point names are retained.
The public edition replaces machine-specific instructions, supplies generic
templates, and replaces monitor internals with a shared Python implementation.
The installed source skill was preserved separately. No real archive records,
private media, credentials, or personal filesystem paths are included.

The 1.1.0 update adapts later owner-authored optical-disc workflow files and
helpers from the maintainer's installed skill. The public text omits local
workspace paths, personal media examples, device observations and locally scoped
cleanup permission. This repository's MIT license continues to cover only its
original material; the external tools and media listed below remain separate.

FFmpeg/ffprobe, MakeMKV, dvdbackup, libdvdcss, MKVToolNix, Tesseract, Whisper and
other optional tools are independent projects. They are not bundled or relicensed
by this repository. Their names acknowledge their respective projects; follow
each project's license and attribution requirements when installing or redistributing
those tools. See the official links in the README.
