import logging
import os

from .bag import Sf2Bag
from .riffparser import from_cstr


class Sf2Preset(object):
    def __init__(self, hydra_header, idx, sf2parser):
        preset_header = hydra_header['Phdr'][idx]

        self.name = from_cstr(preset_header.name)

        # don't process the sentinel item
        if self.name == 'EOP':
            self.bags = []
            return

        self.hydra_header = hydra_header

        self.preset = preset_header.preset
        self.bank = preset_header.bank

        self.bag_idx = preset_header.bag
        self.bag_size = hydra_header['Phdr'][idx + 1].bag - self.bag_idx

        if self.bank > 128:
            logging.warning("Bag %s has invalid bank number (%d while expected <= 128)", self.name, self.bank)

        self.sf2parser = sf2parser

        self.bags = self.build_bags()

    def build_bags(self):
        return [Sf2Bag(self.hydra_header, idx, self.sf2parser, 'Pbag', 'Pmod', 'Pgen') for idx in
                range(self.bag_idx, self.bag_idx + self.bag_size)]

    @property
    def gens(self):
        for bag in self.bags:
            for gen in bag.gens:
                yield gen

    @property
    def instruments(self):
        if len(self.bags) <= 0:
            yield None, None, None
        else:
            for bag in self.bags:
                yield bag.instrument

    @property
    def key_range(self):
        """
        Returns a range which is either the stated key range of the Global bag,
        or a summation of the key ranges of all other bags.
        """
        combined_range = [127, 0]
        for preset_bag in self.bags:
            if preset_bag.key_range is not None:
                if preset_bag.instrument is None:
                    # Global bag overrides all others:
                    return preset_bag.key_range
                else:
                    # Other bags with defined ranges are combined together:
                    combined_range[0] = min(combined_range[0], preset_bag.key_range[0])
                    combined_range[1] = max(combined_range[1], preset_bag.key_range[1])
            elif preset_bag.instrument is not None:
                # Preset has no key range; drill down to instrument bags:
                for instrument_bag in preset_bag.instrument.bags:
                    if instrument_bag.key_range is not None:
                        # Instrument bags with defined ranges are combined together:
                        combined_range[0] = min(combined_range[0], instrument_bag.key_range[0])
                        combined_range[1] = max(combined_range[1], instrument_bag.key_range[1])
        return range(min(combined_range[0], combined_range[1]), max(combined_range[0], combined_range[1]))

    @property
    def filename(self):
        return self.sf2parser.riff_file.name

    @property
    def soundfont_name(self):
        return os.path.basename(self.filename())

    def key_bags(self, key):
        """
        Returns a list of Sf2Bag whose key_range encompasses the given key.
        Does not return the Global bag; only returning bags with instruments.
        """
        return [bag for bag in self.bags
                if bag.instrument is not None
                and (bag.key_range is None or (bag.key_range[0] <= key <= bag.key_range[1]))]

    def key_instruments(self, key):
        """
        Returns a list of Sf2Instrument used to "render" the sound of the given key.
        """
        return [bag.instrument for bag in self.key_bags(key)]

    def key_samples(self, key):
        """
        Returns a list of Sf2Sample used to "render" the sound of the given key.
        """
        return [
            bag.sample
            for instrument in self.key_instruments(key)
            for bag in instrument.bags
            if bag.sample is not None and (bag.key_range is None or (bag.key_range[0] <= key <= bag.key_range[1]))]

    def pretty_print(self, prefix=u''):
        return u"\n".join([prefix + self.__unicode__()] +
                          ["{bag}\n{prefix}\tkeys: {key}\tvels: {vel}\n{instrument}".format(
                              bag=bag.pretty_print(prefix + u'\t'),
                              prefix=prefix,
                              key=bag.key_range or "ALL",
                              vel=bag.velocity_range or "ALL",
                              instrument=bag.instrument.pretty_print(
                                  prefix + u'\t') if bag.instrument else prefix + "\tNo Instrument / Global") for bag in
                              self.bags if self.bags])

    def __unicode__(self):
        if self.name == "EOP":
            return "Preset EOP"

        return u"Preset[{0.bank:03}:{0.preset:03}] {0.name} {0.bag_size} bag(s) from #{0.bag_idx}".format(self)

    def __repr__(self):
        return self.__unicode__()
