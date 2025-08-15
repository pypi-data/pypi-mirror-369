import configparser
import datetime as dt
import os
import shutil
import tempfile
import textwrap
from collections import OrderedDict
from unittest import TestCase
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyfakefs.fake_filesystem_unittest import Patcher

from loggertodb import ConfigurationError
from loggertodb.meteologgerstorage import TextFileMeteologgerStorage


class DummyTextFileMeteologgerStorage(TextFileMeteologgerStorage):
    def _extract_timestamp(self, line):
        result = dt.datetime.strptime(line[:16], "%Y-%m-%d %H:%M")
        result = result.replace(tzinfo=self.tzinfo)
        return result

    def _get_item_from_line(self, line, seq):
        line_items = line.strip().split(",")[1:]
        item = line_items[seq - 1]
        item_items = item.split()
        return float(item_items[0]), " ".join(item_items[1:])


class CheckParametersTestCase(TestCase):
    def test_raises_error_on_fields_missing(self):
        expected_error_message = 'Parameter "fields" is required'
        with self.assertRaisesRegex(ConfigurationError, expected_error_message):
            cfg = configparser.ConfigParser(interpolation=None)
            cfg.read_dict(
                {
                    "mystation": {
                        "station_id": 1334,
                        "path": "irrelevant",
                        "storage_format": "dummy",
                        "timezone": "Etc/GMT-2",
                    }
                }
            )
            DummyTextFileMeteologgerStorage(cfg["mystation"])

    def test_raises_error_on_invalid_parameter(self):
        expected_error_message = 'Unknown parameter "hello"'
        with self.assertRaisesRegex(ConfigurationError, expected_error_message):
            cfg = configparser.ConfigParser(interpolation=None)
            cfg.read_dict(
                {
                    "mystation": {
                        "station_id": 1334,
                        "path": "irrelevant",
                        "storage_format": "dummy",
                        "fields": "5, 6",
                        "hello": "world",
                        "timezone": "Etc/GMT-2",
                    }
                }
            )
            DummyTextFileMeteologgerStorage(cfg["mystation"])

    def test_accepts_allowed_optional_parameters(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "irrelevant",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                }
            }
        )
        DummyTextFileMeteologgerStorage(cfg["mystation"])


class TimeseriesIdsTestCase(TestCase):
    def test_timeseries_group_ids(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "irrelevant",
                    "storage_format": "dummy",
                    "fields": "0, 5, 0, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        self.assertEqual(meteologger_storage.timeseries_group_ids, set((5, 6)))


class ExtractValueAndFlagsTestCase(TestCase):
    def setUp(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                }
            }
        )
        self.meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        self.record = {
            "timestamp": dt.datetime(2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")),
            "line": "2019-02-28 17:30,42.2 MYFLAG1 MYFLAG2,24.3\n",
        }

    def test_value_with_flags(self):
        result = self.meteologger_storage._extract_value_and_flags(5, self.record)
        self.assertAlmostEqual(result[0], 42.2)
        self.assertEqual(result[1], "MYFLAG1 MYFLAG2")

    def test_value_without_flags(self):
        result = self.meteologger_storage._extract_value_and_flags(6, self.record)
        self.assertAlmostEqual(result[0], 24.3)
        self.assertEqual(result[1], "")


class GetStorageTailTestCase(TestCase):
    def setUp(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with Patcher() as patcher:
            patcher.fs.create_file(
                "/foo/bar",
                contents=textwrap.dedent(
                    """\
                    2019-02-28 17:20,42.1,24.2
                    2019-02-28 17:30,42.2,24.3
                    2019-02-28 17:40,42.3,24.4
                    """
                ),
            )
            self.result = meteologger_storage._get_storage_tail(
                dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
            )

    def test_result(self):
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 40, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:40,42.3,24.4\n",
                    "filename": "/foo/bar",
                },
            ],
        )


class GetRecentDataWithAmbiguousHourTestCase(TestCase):
    def setUp(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "null": "NULL",
                    "timezone": "Europe/Athens",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with Patcher() as patcher:
            patcher.fs.create_file(
                "/foo/bar",
                contents=textwrap.dedent(
                    """\
                    2018-10-28 02:50,42.1,24.2
                    2018-10-28 03:00,42.2,24.3
                    2018-10-28 03:10,42.3,24.4
                    2018-10-28 03:20,42.4,24.5
                    2018-10-28 03:30,42.5,24.6
                    2018-10-28 03:40,42.6,24.7
                    2018-10-28 03:50,42.7,24.8
                    2018-10-28 03:00,42.8,24.9
                    2018-10-28 03:10,42.9,25.0
                    2018-10-28 03:20,43.0,25.1
                    2018-10-28 03:30,43.1,25.2
                    2018-10-28 03:40,43.2,25.3
                    2018-10-28 03:50,43.3,25.4
                    2018-10-28 04:00,43.4,25.5
                    2018-10-28 04:10,43.5,25.6
                    2019-10-27 02:50,42.1,24.2
                    2019-10-27 03:00,42.2,24.3
                    2019-10-27 03:10,42.3,24.4
                    2019-10-27 03:20,42.4,24.5
                    2019-10-27 03:30,42.5,24.6
                    2019-10-27 03:40,42.6,24.7
                    2019-10-27 03:50,42.7,24.8
                    2019-10-27 03:00,42.8,24.9
                    2019-10-27 03:10,42.9,25.0
                    2019-10-27 03:20,43.0,25.1
                    2019-10-27 03:30,43.1,25.2
                    2019-10-27 03:40,43.2,25.3
                    2019-10-27 03:50,43.3,25.4
                    2019-10-27 04:00,43.4,25.5
                    2019-10-27 04:10,43.5,25.6
                    """
                ),
            )
            self.result = meteologger_storage.get_recent_data(
                5, dt.datetime(2018, 10, 27, 1, 0, tzinfo=ZoneInfo("Etc/GMT"))
            )

    def test_result(self):
        v = np.arange(421, 436) / 10.0
        expected_values = np.concatenate((v, v))
        expected_flags = [""] * 30
        expected_dates = pd.date_range(
            start=dt.datetime(2018, 10, 27, 23, 50, tzinfo=dt.timezone.utc),
            end=dt.datetime(2018, 10, 28, 2, 10, tzinfo=dt.timezone.utc),
            freq="10min",
        ).union(
            pd.date_range(
                start=dt.datetime(2019, 10, 26, 23, 50, tzinfo=dt.timezone.utc),
                end=dt.datetime(2019, 10, 27, 2, 10, tzinfo=dt.timezone.utc),
                freq="10min",
            )
        )
        expected_result = pd.DataFrame(
            data=OrderedDict([("value", expected_values), ("flags", expected_flags)]),
            index=expected_dates,
            dtype=object,
        )
        expected_result.index = expected_result.index.astype("datetime64[s, UTC]")
        pd.testing.assert_frame_equal(self.result, expected_result)


class IgnoreLinesTestCase(TestCase):
    def setUp(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "ignore( this)? line",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with Patcher() as patcher:
            patcher.fs.create_file(
                "/foo/bar",
                contents=textwrap.dedent(
                    """\
                    ignore line
                    2019-02-28 17:20,42.1,24.2
                    ignore this line
                    2019-02-28 17:30,42.2,24.3
                    yes, really ignore line man!
                    2019-02-28 17:40,42.3,24.4
                    """
                ),
            )
            self.result = meteologger_storage._get_storage_tail(
                dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
            )

    def test_result(self):
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 40, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:40,42.3,24.4\n",
                    "filename": "/foo/bar",
                },
            ],
        )


class EncodingTestCase(TestCase):
    def setUp(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "n' est pas",
                    "encoding": "iso-8859-1",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with Patcher() as patcher:
            patcher.fs.create_file(
                "/foo/bar",
                encoding="iso-8859-1",
                contents=textwrap.dedent(
                    """\
                    2019-02-28 17:20,42.1,24.2
                    Cette ligne n' est pas très importante
                    2019-02-28 17:30,42.2,24.3
                    2019-02-28 17:40,42.3,24.4
                    """
                ),
            )
            self.result = meteologger_storage._get_storage_tail(
                dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
            )

    def test_result(self):
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 40, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:40,42.3,24.4\n",
                    "filename": "/foo/bar",
                },
            ],
        )


class EncodingErrorsTestCase(TestCase):
    def setUp(self):
        # We use an iso-8859-1-encoded file but without declaring the encoding in the
        # parameters, so when it attempts to read it it will try utf8. It should forgive
        # the error
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": "/foo/bar",
                    "storage_format": "dummy",
                    "fields": "5, 6",
                    "timezone": "Etc/GMT-2",
                    "null": "NULL",
                    "ignore_lines": "n' est pas",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with Patcher() as patcher:
            patcher.fs.create_file(
                "/foo/bar",
                encoding="iso-8859-1",
                contents=textwrap.dedent(
                    """\
                    2019-02-28 17:20,42.1,24.2
                    Cette ligne n' est pas très importante
                    2019-02-28 17:30,42.2,24.3
                    2019-02-28 17:40,42.3,24.4
                    """
                ),
            )
            self.result = meteologger_storage._get_storage_tail(
                dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))
            )

    def test_result(self):
        self.assertEqual(
            self.result,
            [
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 30, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:30,42.2,24.3\n",
                    "filename": "/foo/bar",
                },
                {
                    "timestamp": dt.datetime(
                        2019, 2, 28, 17, 40, tzinfo=ZoneInfo("Etc/GMT-2")
                    ),
                    "line": "2019-02-28 17:40,42.3,24.4\n",
                    "filename": "/foo/bar",
                },
            ],
        )


class AllowOverlapsTestCase(TestCase):
    file_contents = textwrap.dedent(
        """\
        2019-02-28 17:20,42.1
        2019-02-28 17:30,42.2
        2019-02-28 17:40,42.3
        2019-02-28 17:30,42.2
        2019-02-28 17:40,42.3
        2019-02-28 17:50,42.4
        """
    )
    after = dt.datetime(2019, 2, 28, 17, 20, tzinfo=ZoneInfo("Etc/GMT-2"))

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datafilename = os.path.join(self.tmpdir, "foo")
        with open(self.datafilename, "w") as f:
            f.write(self.file_contents)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_get_recent_data_raises_error_without_allow_overlaps(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": self.datafilename,
                    "storage_format": "dummy",
                    "fields": "1",
                    "timezone": "Etc/GMT-2",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        with self.assertRaises(ValueError):
            meteologger_storage.get_recent_data(1, self.after)

    def test_get_recent_data_with_allow_overlaps(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_dict(
            {
                "mystation": {
                    "station_id": 1334,
                    "path": self.datafilename,
                    "storage_format": "dummy",
                    "fields": "1",
                    "timezone": "Etc/GMT-2",
                    "allow_overlaps": "yes",
                }
            }
        )
        meteologger_storage = DummyTextFileMeteologgerStorage(cfg["mystation"])
        result = meteologger_storage.get_recent_data(1, self.after)
        expected_index = [
            dt.datetime(2019, 2, 28, 15, 30, tzinfo=dt.timezone.utc),
            dt.datetime(2019, 2, 28, 15, 40, tzinfo=dt.timezone.utc),
            dt.datetime(2019, 2, 28, 15, 50, tzinfo=dt.timezone.utc),
        ]
        self.assertEqual(list(result.index), expected_index)
        self.assertTrue(
            np.allclose(result["value"].astype(float).values, [42.2, 42.3, 42.4])
        )
