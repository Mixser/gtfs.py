import csv
import io
from collections import defaultdict
from zipfile import ZipExtFile

from ..utils.parsing import decode_file


class Translator(object):
    def __init__(self, csv_file=None, data=None):
        self._words = defaultdict(dict)

        if csv_file is not None:
            self._load_file(csv_file)
        elif data is not None:
            self._load_data(data)

    def _load_data(self, data):
        for row in data:
            self.add_translate(row["lang"], row["trans_id"], row["translation"])

    def _load_file(self, csv_file):
        if isinstance(csv_file, str):
            print(type(csv_file), csv_file)
            with open(csv_file, "r", encoding='utf-8-sig') as f:
                self._load_file(f)
        elif isinstance(csv_file, ZipExtFile):
            csv_file = decode_file(csv_file)
            self._load_file(csv_file)
        else:
            print(type(csv_file))
            reader = csv.DictReader(csv_file)
            for row in reader:
                self._words[row["lang"]][row["trans_id"]] = row["translation"]
                self._load_data(reader)

    def save(self, csv_file):
        if isinstance(csv_file, str):
            with open(csv_file, "w") as f:
                self.save(f)
        else:
            fields = ["trans_id", "lang", "translation"]

            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()

            for lang_name, translations in self._words.items():
                for expression, translation in translations.items():
                    writer.writerow({"lang": lang_name, "trans_id": expression, "translation": translation})

    def translate(self, expression, language, if_not_exists=None):
        if language in self._words:
            if expression in self._words[language]:
                return self._words[language][expression]

        return if_not_exists

    def try_translate(self, expression, language):
        return self.translate(expression, language, if_not_exists=expression)

    def has_data(self):
        for lang_translates in self._words.values():
            if len(lang_translates) > 0:
                return True

        return False

    def add_translate(self, language, expression, translation):
        self._words[language][expression] = translation
