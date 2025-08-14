Sf2Utils
========

Sf2Utils is a soundfont 2 parsing library and companion utility.
It is meant for developers aiming to use soundfont 2 file as input,
typically for converting to another format.

Installation
------------

Sf2Utils is installable from PyPI with a single pip command::

    pip install sf2utils

Alternatively, Sf2utils can be run directly from sources after a git pull::

    git clone https://gitlab.com/zeograd/sf2utils.git
    cd sf2utils && python setup.py install


Companion script
----------------

**sf2parse** is a command line utility used to parse a sound font 2 file.
It is meant as debug companion for the **sf2utils** parser library as it shows
what is understood from its parser.

::

    usage: sf2parse [-h] [-d] sf2_filename

    LGPL v3+ 2016-2024 Olivier Jolly

    positional arguments:
      sf2_filename  input file in SoundFont2 format

    optional arguments:
      -h, --help    show this help message and exit
      -d, --debug   debug parsing [default: False]

    Parse sf2 file and display info about it


Library use
-----------

**sf2utils** can be used as a library for parsing SoundFont2 files.
There are 2 API levels, a low level and high level one.
They both open SoundFont2 file the same way::

    from sf2utils.sf2parse import Sf2File
    with open('file.sf2', 'rb') as sf2_file:
        sf2 = Sf2File(sf2_file)

Note that opening the file is up to the library user because samples
data are lazy loaded. Accessing sample data will seek and read data.
You shouldn't access sample data outside of the content in which
the file is opened, as it will fail.

Low level library API
.....................

Once sf2 is a valid Sf2File, all metadata are available via the
property **raw**, which has fields for the various sections in a
SoundFont2 file.

* **sf2.raw.info** is a dictionary with all info in the info block of the SoundFont2 file with keys as binary strings.

* **sf2.raw.smpl_offset** is the offset in the original file where the sample data are located.

* **sf2.raw.sm24_offset** is the offset in the original file where the complementary 8bits of sample data are located.

* **sf2.raw.pdta** is the main metadata structure, a dictionary with tuples named after the specification and indexed using specification structure names :
    * Pbag -> 'gen', 'mod'
    * Igen -> 'oper', 'amount'
    * Imod -> 'src_oper', 'dest_oper', 'amount', 'amount_src_oper', 'trans_oper'
    * Pmod -> 'src_oper', 'dest_oper', 'amount', 'amount_src_oper', 'trans_oper'
    * Pgen -> 'oper', 'amount'
    * Shdr -> 'sample_name', 'start', 'end', 'start_loop', 'end_loop', 'sample_rate', 'original_pitch', 'pitch_correction', 'sample_link', 'sample_type'
    * Phdr -> 'name', 'preset', 'bank', 'bag', 'library', 'genre', 'morphology'
    * Ibag -> 'gen', 'mod'
    * Inst -> 'name', 'bag'

With this API, field interpretation remains up to the library user.

High level library API
......................

With this API, info are available via the **info** property, which is a pretty printable tuple where every
field comes from the info block in the SoundFont2 file.

Samples are accessible via the **samples** property, which is a list of **Sf2Sample** from which you can
retrieve loop information and raw data.

Presets are in the **presets** property, which is a list of **Sf2Preset** from which you can list generators,
modulators, instruments and bags.

Instruments are in the **instruments** property, which is a list of **Sf2Instrument** from which you can
list bags of generators, modulators.

Bags are of class **Sf2Bag** and offer a wide range of property returning various high level info (about loop,
tuning, filters, envelopes, instruments, samples, ...) or None when no generator was found.

All those classes have a **pretty_print** returning a pretty printed string, recursing over subelements.
