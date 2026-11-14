"""Pipeline I/O: date handling, replace-day semantics, data-source policy, failure signalling."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from app import main as alpha_main
from app.database import insert_daily


class FakeQuery:
    def __init__(self, log: list, table: str, fail_on: str | None):
        self._log, self._table, self._fail_on = log, table, fail_on
        self._op: tuple | None = None

    def delete(self):
        self._op = ("delete", self._table, None)
        return self

    def like(self, column, pattern):
        assert self._op and self._op[0] == "delete"
        self._op = ("delete", self._table, (column, pattern))
        return self

    def insert(self, rows):
        self._op = ("insert", self._table, rows)
        return self

    def execute(self):
        assert self._op is not None
        if self._fail_on == self._op[0]:
            raise RuntimeError(f"simulated {self._op[0]} failure")
        self._log.append(self._op)
        return self


class FakeClient:
    def __init__(self, fail_on: str | None = None):
        self.log: list[tuple] = []
        self._fail_on = fail_on

    def table(self, name: str) -> FakeQuery:
        return FakeQuery(self.log, name, self._fail_on)


def _scored_df() -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "Ticker": "AAPL",
                "Price": 190.5,
                "Option Score": 8,
                "Band": "A",
                "Strategy Tag": "Short Put",
                "Trend (Above/Below 20/50/200 EMA)": "Above 20, 50, 200 (Bullish)",
                "Next Earnings Date": pd.NaT,
                "Sector": "Technology",
                "IV Rank (1y)": float("nan"),
            },
            {
                "Ticker": "MSFT",
                "Price": 330.0,
                "Option Score": 6,
                "Band": "B",
                "Strategy Tag": "Iron Condor",
                "Trend (Above/Below 20/50/200 EMA)": "Range",
                "Next Earnings Date": pd.Timestamp("2027-01-05"),
                "Sector": "Technology",
                "IV Rank (1y)": 55.0,
            },
        ]
    )
    return df


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> FakeClient:
    client = FakeClient()
    monkeypatch.setattr(insert_daily, "get_supabase_client", lambda: client)
    return client


# --- dates ------------------------------------------------------------------


def test_date_is_always_a_plain_day_string() -> None:
    mapped = insert_daily._map_columns(_scored_df())
    assert (mapped["date"] == insert_daily.today_str()).all()
    assert len(mapped["date"].iloc[0]) == 10  # YYYY-MM-DD, no time component


def test_existing_timestamp_dates_are_trimmed_and_day_override_wins() -> None:
    df = _scored_df().assign(date="2026-11-14T10:23:45.123456")
    assert insert_daily._map_columns(df)["date"].iloc[0] == "2026-11-14"
    assert (insert_daily._map_columns(df, day="2026-12-01")["date"] == "2026-12-01").all()


def test_nan_and_nat_become_null_not_strings() -> None:
    out = insert_daily._convert_timestamps(
        [{"a": float("nan"), "b": pd.NaT, "c": pd.Timestamp("2026-01-02"), "d": math.inf, "e": 3}]
    )[0]
    assert out == {"a": None, "b": None, "c": "2026-01-02T00:00:00", "d": None, "e": 3}


# --- replace_day ------------------------------------------------------------


def test_replace_day_deletes_all_tables_then_inserts_with_the_day(fake_client: FakeClient) -> None:
    df = _scored_df()
    weekly = df[df["Option Score"] >= 6].assign(Date=pd.Timestamp("2026-12-01"))
    counts = insert_daily.replace_day(df, weekly, day="2026-12-01")

    ops = [(op, table) for op, table, _ in fake_client.log]
    deletes = [i for i, (op, _) in enumerate(ops) if op == "delete"]
    inserts = [i for i, (op, _) in enumerate(ops) if op == "insert"]
    assert len(deletes) == 4 and deletes and inserts
    assert max(deletes) < min(inserts)  # all deletes happen before any insert

    for op, _table, arg in fake_client.log:
        if op == "delete":
            assert arg == ("date", "2026-12-01%")  # also catches legacy timestamped rows
    for op, _table, rows in fake_client.log:
        if op == "insert":
            assert {r["date"] for r in rows} == {"2026-12-01"}
    assert counts["daily_metrics"] == 2 and counts["bands"] == 2


def test_nothing_is_deleted_if_building_the_payload_fails(
    fake_client: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*a, **k):
        raise ValueError("bad data")

    monkeypatch.setattr(insert_daily, "_rows", boom)
    with pytest.raises(ValueError):
        insert_daily.replace_day(_scored_df(), _scored_df(), day="2026-12-01")
    assert fake_client.log == []  # the existing day's data is untouched


def test_supabase_errors_are_raised_not_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    for fail_on in ("delete", "insert"):
        monkeypatch.setattr(
            insert_daily, "get_supabase_client", lambda f=fail_on: FakeClient(fail_on=f)
        )
        with pytest.raises(RuntimeError, match="simulated"):
            insert_daily.replace_day(_scored_df(), _scored_df(), day="2026-12-01")


# --- data-source policy -----------------------------------------------------


def _no_real_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(alpha_main, "load_from_supabase", lambda: pd.DataFrame())
    monkeypatch.setattr(alpha_main, "load_local_csv", lambda: pd.DataFrame())


def test_no_data_fails_instead_of_inventing_data(monkeypatch: pytest.MonkeyPatch) -> None:
    _no_real_data(monkeypatch)
    with pytest.raises(alpha_main.NoDataError):
        alpha_main._load_data(allow_sample=False)


def test_sample_data_is_opt_in_and_never_written(monkeypatch: pytest.MonkeyPatch) -> None:
    _no_real_data(monkeypatch)
    source, df = alpha_main._load_data(allow_sample=True)
    assert source == "sample" and not df.empty
    # earnings dates are relative to today, so the demo never "expires"
    assert (df["Next Earnings Date"] > pd.Timestamp.today()).all()

    def must_not_write(*a, **k):
        raise AssertionError("sample data must not be written to Supabase")

    monkeypatch.setattr(alpha_main, "replace_day", must_not_write)
    alpha_main.run_system(allow_sample=True)  # completes without writing


def test_supabase_data_is_preferred_over_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(alpha_main, "load_from_supabase", lambda: _scored_df())
    monkeypatch.setattr(
        alpha_main, "load_local_csv", lambda: (_ for _ in ()).throw(AssertionError("unused"))
    )
    source, _ = alpha_main._load_data(allow_sample=False)
    assert source == "supabase"


# --- failure signalling -----------------------------------------------------


def test_main_returns_nonzero_and_alerts_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    alerts: list[str] = []
    monkeypatch.setattr(alpha_main, "send_alert", alerts.append)
    monkeypatch.setattr(
        alpha_main, "run_system", lambda: (_ for _ in ()).throw(RuntimeError("db down"))
    )
    assert alpha_main.main() == 1
    assert alerts and "db down" in alerts[0]


def test_main_returns_zero_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(alpha_main, "run_system", lambda: None)
    assert alpha_main.main() == 0
