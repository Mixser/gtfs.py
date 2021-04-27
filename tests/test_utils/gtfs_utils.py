import csv
import chardet
import io
from zipfile import ZipFile
import unittest


ignored_keys = []


def decode_file(stream):
    content = stream.read()
    encoding = chardet.detect(content)['encoding']
    content = content.decode(encoding)
    return io.StringIO(content)


def compare_gtfs_files(gtfs_file1, gtfs_file2, test_case):
    """
    :type gtfs_file1: str | ZipFile
    :type gtfs_file2: str | ZipFile
    :type test_case: unittest.TestCase
    """

    if not isinstance(gtfs_file1, ZipFile):
        with ZipFile(gtfs_file1) as gtfs_file1:
            return compare_gtfs_files(gtfs_file1, gtfs_file2, test_case)
    if not isinstance(gtfs_file2, ZipFile):
        with ZipFile(gtfs_file2) as gtfs_file2:
            return compare_gtfs_files(gtfs_file1, gtfs_file2, test_case)

    files_list1 = gtfs_file1.namelist()
    files_list2 = gtfs_file2.namelist()

    for i, file_name in enumerate(files_list1):
        if file_name not in files_list2:
            print('File "%s" only on left' % (file_name,))
            del files_list1[i]

    for i, file_name in enumerate(files_list2):
        if file_name not in files_list1:
            print('File "%s" only on right' % (file_name,))

    for file_name in files_list1:
        print('\nFile: "%s"' % (file_name,))
        with gtfs_file1.open(file_name, "r") as f:
            fio = decode_file(f)
            reader = csv.DictReader(fio)
            lines = {tuple(sorted(row.items())) for row in reader}

        with gtfs_file2.open(file_name, "r") as f:
            fio = decode_file(f)
            reader = csv.DictReader(fio)
            for row in reader:
                row = tuple(sorted(row.items()))
                test_case.assertIn(row, lines)
                lines.remove(row)

        test_case.assertEqual(len(lines), 0)

        print("OK")
