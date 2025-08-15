import configparser
import datetime as dt
import textwrap
from zoneinfo import ZoneInfo

import pandas as pd
from pyfakefs.fake_filesystem_unittest import TestCase

from loggertodb.exceptions import MeteologgerStorageReadError
from loggertodb.meteologgerstorage import (
    MeteologgerStorage_simple,
    MultiTextFileMeteologgerStorage,
)


class DummyMultiTextFileMeteologgerStorage(MultiTextFileMeteologgerStorage):
    def _extract_timestamp(self, line):
        result = dt.datetime.strptime(line[:16], "%Y-%m-%d %H:%M")
        result = result.replace(tzinfo=ZoneInfo("Etc/GMT-2"))
        return result

    def _get_item_from_line(self, line, seq):
        line_items = line.strip().split(",")[1:]
        item = line_items[seq - 1]
        item_items = item.split()
        return float(item_items[0]), " ".join(item_items[1:])


class GetStorageTailTestCase(TestCase):
    use_headers_in_files = False

    def setUp(self):
        self.setUpPyfakefs()
        self.meteologger_storage = self._get_meteologger_storage()
        self._create_files()

    def _get_meteologger_storage(self):
        parms = {
            "station_id": 1334,
            "path": "/foo/bar?",
            "storage_format": "dummy",
            "fields": "6, 6",
            "timezone": "Etc/GMT-2",
            "null": "NULL",
        }
        if self.use_headers_in_files:
            parms["ignore_lines"] = "Date"
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict({"mystation": parms})
        return DummyMultiTextFileMeteologgerStorage(cfg["mystation"])

    def _create_files(self):
        self._create_test_file("/foo/bar1", 2018)
        self._create_test_file("/foo/bar2", 2019)
        self._create_test_file("/foo/bar3", 2017)

    def _create_test_file(self, pathname, year):
        headers = "Date,value1,value2\n" if self.use_headers_in_files else ""
        self.fs.create_file(
            pathname,
            contents=textwrap.dedent(
                """\
                {}
                {}-02-28 17:20,42.1,24.2
                {}-02-28 17:30,42.2,24.3
                """.format(
                    headers, year, year
                )
            ),
        )

    def test_get_storage_tail_from_last_file(self):
        self.result = self.meteologger_storage._get_storage_tail(
            dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
        )
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar2",
                }
            ],
        )

    def test_get_storage_tail_from_last_but_one_file(self):
        self.result = self.meteologger_storage._get_storage_tail(
            dt.datetime(2018, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
        )
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2018, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2018-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar1",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:20,42.1,24.2\n",
                    "filename": "/foo/bar2",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar2",
                },
            ],
        )

    def test_get_storage_tail_from_all_files(self):
        self.result = self.meteologger_storage._get_storage_tail(
            dt.datetime(2016, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
        )
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2017, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2017-02-28 17:20,42.1,24.2\n",
                    "filename": "/foo/bar3",
                },
                {
                    "timestamp": dt.datetime(
                        2017, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2017-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar3",
                },
                {
                    "timestamp": dt.datetime(
                        2018, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2018-02-28 17:20,42.1,24.2\n",
                    "filename": "/foo/bar1",
                },
                {
                    "timestamp": dt.datetime(
                        2018, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2018-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar1",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:20,42.1,24.2\n",
                    "filename": "/foo/bar2",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar2",
                },
            ],
        )


class GetStorageTailNoFilesTestCase(TestCase):
    def setUp(self):
        self.meteologger_storage = self._get_meteologger_storage()

    def _get_meteologger_storage(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar?",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                }
            }
        )
        return DummyMultiTextFileMeteologgerStorage(cfg["mystation"])

    def test_get_storage_tail_returns_empty_list(self):
        result = self.meteologger_storage._get_storage_tail(
            dt.datetime(2016, 2, 28, 17, 20)
        )
        self.assertEqual(len(result), 0)


class GetStorageTailWithHeadersTestCase(GetStorageTailTestCase):
    use_headers_in_files = True


class GetStorageTailEmptyFileTestCase(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.meteologger_storage = self._get_meteologger_storage()
        self._create_files()

    def _get_meteologger_storage(self):
        parms = {
            "station_id": 1334,
            "path": "/foo/bar?",
            "storage_format": "dummy",
            "timezone": "Etc/GMT-2",
            "fields": "5, 6",
            "null": "NULL",
            "ignore_lines": "Date",
        }
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict({"mystation": parms})
        return DummyMultiTextFileMeteologgerStorage(cfg["mystation"])

    def _create_files(self):
        self._create_test_file("/foo/bar1", 2018)
        self._create_test_file("/foo/bar2", 2019)
        self._create_test_file("/foo/bar3", None)

    def _create_test_file(self, pathname, year):
        if year is None:
            self._create_empty_test_file(pathname)
        else:
            self._create_test_file_with_records(pathname, year)

    def _create_empty_test_file(self, pathname):
        self.fs.create_file(pathname, contents="Date,value1,value2\n")

    def _create_test_file_with_records(self, pathname, year):
        self.fs.create_file(
            pathname,
            contents=textwrap.dedent(
                """\
                Date,value1,value2
                {}-02-28 17:20,42.1,24.2
                {}-02-28 17:30,42.2,24.3
                """.format(
                    year, year
                )
            ),
        )

    def test_get_entire_storage_tail(self):
        self.result = self.meteologger_storage._get_storage_tail(
            dt.datetime(1700, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        )
        self.assertEqual(len(self.result), 4)


class BadFileOrder(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.meteologger_storage = self._get_meteologger_storage()
        self._create_file()

    def _get_meteologger_storage(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar?",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "Date",
                }
            }
        )
        return DummyMultiTextFileMeteologgerStorage(cfg["mystation"])

    def _create_file(self):
        self.fs.create_file(
            "/foo/bar1",
            contents=textwrap.dedent(
                """\
                Date,value1,value2
                2019-02-28 17:20,42.1,24.2
                2018-02-28 17:30,42.2,24.3
                """
            ),
        )

    def test_raises_value_error(self):
        msg = r"The order of timestamps in file .foo.bar1 is mixed up."
        with self.assertRaisesRegex(ValueError, msg):
            self.meteologger_storage.get_recent_data(
                5, dt.datetime(1700, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
            )


class FilesWithOverlap(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self._create_file1()
        self._create_file2()

    def _get_meteologger_storage(self, *, allow_overlaps):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar?",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "Date",
                    "allow_overlaps": f"{allow_overlaps}",
                }
            }
        )
        return DummyMultiTextFileMeteologgerStorage(cfg["mystation"])

    def _create_file1(self):
        self.fs.create_file(
            "/foo/bar1",
            contents=textwrap.dedent(
                """\
                Date,value1,value2
                2018-02-28 17:20,42.1,24.2
                2019-02-28 17:30,42.2,24.3
                """
            ),
        )

    def _create_file2(self):
        self.fs.create_file(
            "/foo/bar2",
            contents=textwrap.dedent(
                """\
                Date,value1,value2
                2019-02-28 17:20,42.1,24.2
                2020-02-28 17:30,42.2,24.3
                """
            ),
        )

    def test_raises_value_error_without_overlaps(self):
        meteologger_storage = self._get_meteologger_storage(allow_overlaps=False)
        msg = r"The timestamps in files .foo.bar1 and .foo.bar2 overlap."
        with self.assertRaisesRegex(ValueError, msg):
            meteologger_storage.get_recent_data(
                5, dt.datetime(1700, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
            )

    def test_goes_alright_with_overlaps(self):
        meteologger_storage = self._get_meteologger_storage(allow_overlaps=True)
        recent_data = meteologger_storage.get_recent_data(
            5, dt.datetime(1700, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        )
        expected_result = pd.DataFrame(
            data={
                "value": [42.1, 42.1, 42.2, 42.2],
                "flags": [""] * 4,
            },
            index=[
                dt.datetime(2018, 2, 28, 15, 20, tzinfo=dt.timezone.utc),
                dt.datetime(2019, 2, 28, 15, 20, tzinfo=dt.timezone.utc),
                dt.datetime(2019, 2, 28, 15, 30, tzinfo=dt.timezone.utc),
                dt.datetime(2020, 2, 28, 15, 30, tzinfo=dt.timezone.utc),
            ],
        )
        pd.testing.assert_frame_equal(
            recent_data, expected_result, check_dtype=False, check_index_type=False
        )


class FileWithBadLine(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.meteologger_storage = self._get_meteologger_storage()
        self._create_file()

    def _get_meteologger_storage(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar?",
                    "storage_format": "simple",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "Date",
                    "nfields_to_ignore": 1,
                }
            }
        )
        return MeteologgerStorage_simple(cfg["mystation"])

    def _create_file(self):
        self.fs.create_file(
            "/foo/bar1",
            contents=(
                b"id,Date,value1,value2\n"
                b"Invalid line\n"
                b"#501,2018-02-28 17:20,42.1,24.2\n"
                b"#502,2019-02-28 17:30,42.2,24.3\n"
            ),
        )

    def test_raises_error(self):
        msg = r'.foo.bar1: "Invalid line": Malformed line'
        with self.assertRaisesRegex(MeteologgerStorageReadError, msg):
            self.meteologger_storage.get_recent_data(
                5, dt.datetime(1700, 1, 1, 0, tzinfo=dt.timezone.utc)
            )
