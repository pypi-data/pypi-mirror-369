# -*- coding: utf-8 -*-
"""Utility functions and classes."""
import asyncio
import datetime
import logging
import multiprocessing
import time
import warnings
from collections import defaultdict
from typing import (
    Any,
    Coroutine,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

import httpx
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from shorthand_datetime import parse_shorthand_datetime
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm

# Local imports
from . import exceptions as E
from . import version

BASE_URL = "https://api.24sea.eu/routes/v1/"
PYDANTIC_V2 = version.parse_version(version.__version__).major >= 2

if PYDANTIC_V2:
    from pydantic import BaseModel, field_validator, validate_call  # noqa: F401

else:
    from pydantic import BaseModel, validator  # noqa: F401

    # Fallback for validate_call (acts as a no-op)
    def validate_call(*args, **kwargs):
        # Remove config kwarg if present since it's not supported in v1
        if "config" in kwargs:
            del kwargs["config"]

        def decorator(func):
            return func

        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

    # Shim for field_validator to behave like validator
    def field_validator(field_name, *args, **kwargs):
        def decorator(func):
            # Convert mode='before' to pre=True for v1 compatibility
            if "mode" in kwargs:
                if kwargs["mode"] == "before":
                    kwargs["pre"] = True
                del kwargs["mode"]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return validator(field_name, *args, **kwargs)(func)

        return decorator


def handle_request(
    url: str,
    params: Dict,
    auth: Optional[httpx.BasicAuth],
    headers: Dict,
    max_retries: int = 10,
    timeout: int = 3600,
) -> httpx.Response:
    """Handle the request to the 24SEA API and manage errors using httpx.

    This function will handle the request to the 24SEA API and manage any
    errors that may arise. If the request is successful, the response object
    will be returned. Otherwise, an error will be raised.

    Parameters
    ----------
    url : str
        The URL to which to send the request.
    params : dict
        The parameters to send with the request.
    auth : httpx.BasicAuth
        The authentication object.
    headers : dict
        The headers to send with the request.

    Returns
    -------
    httpx.Response
        The response object if the request was successful, otherwise error.
    """
    if auth is None:
        auth = httpx.BasicAuth("", "")
    retry_count = 0

    while True:
        try:
            # fmt: off
            r_ = httpx.get(url, params=params, auth=auth, headers=headers,
                           timeout=timeout)
            # fmt: on
            if r_.status_code != 502 or retry_count >= max_retries:
                break
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(3)
                continue
        except httpx.RequestError as exc:
            raise exc
    # fmt: off
    if r_.status_code in [400, 401, 403, 404, 503, 504]:
        print(f"Request failed because: \033[31;1m{r_.text}\033[0m")
        r_.raise_for_status()
    elif r_.status_code in [500, 501, 502]:
        print("\033[31;1mServer-side error. Try to run again the query. If the"
              "error persists, you will need to contact support at "
              "\033[32;1;4msupport.api@24sea.eu\033[0m")
        r_.raise_for_status()
    elif r_.status_code > 400:
        print("Request failed with status code: "
              f"\033[31;1m{r_.status_code}\033[0m")
        r_.raise_for_status()
    # fmt: on
    return r_


async def handle_request_async(
    url: str,
    params: dict,
    auth: Optional[httpx.BasicAuth],
    headers: dict = {"accept": "application/json"},
    max_retries: int = 10,
    timeout: int = 1800,
) -> httpx.Response:
    """Asynchronously handle the request to the 24SEA API using httpx's
    AsyncClient."""
    retry_count = 0
    async with httpx.AsyncClient(
        auth=auth, headers=headers, timeout=timeout
    ) as client:
        while True:
            try:
                r_ = await client.get(url, params=params)
                if r_.status_code != 502 or retry_count >= max_retries:
                    break
                retry_count += 1
                if retry_count <= max_retries:
                    await asyncio.sleep(3)
                    continue
            except (httpx.NetworkError, httpx.TimeoutException) as exc:
                raise exc
        # fmt: off
        if r_.status_code in [400, 401, 403, 404, 502, 503, 504]:
            logging.error(f"Request failed because: \033[31;1m{r_.text}\033[0m")
            r_.raise_for_status()
        elif r_.status_code == 500:
            logging.error("\033[31;1mInternal server error. You will need to "
                          "contact support at \033[32;1;4msupport.api@24sea.eu"
                          "\033[0m")
            r_.raise_for_status()
        elif r_.status_code > 400:
            logging.error("Request failed with status code: "
                          f"\033[31;1m{r_.status_code}\033[0m")
            r_.raise_for_status()
        # fmt: on
        return r_


def default_to_regular_dict(d_: Union[DefaultDict, Dict]) -> Dict:
    """Convert a defaultdict to a regular dictionary."""
    if isinstance(d_, defaultdict):
        return {k: default_to_regular_dict(v) for k, v in d_.items()}
    return d_


def require_auth(func):
    """Decorator to ensure authentication before executing a method"""

    def wrapper(self, *args, **kwargs):
        """Wrapper function to check authentication."""
        if not self.authenticated:
            self._lazy_authenticate()
        if not self.authenticated:
            raise E.AuthenticationError(
                "\033[31;1mAuthentication needed before querying the metrics.\n"
                "\033[0mUse the \033[34;1mdatasignals.\033[0mauthenticate("
                "\033[32;1m<username>\033[0m, \033[32;1m<password>\033[0m) "
                "method."
            )
        return func(self, *args, **kwargs)

    return wrapper


# def require_auth_async(func):
#     """Decorator to ensure authentication before executing a method"""

#     async def wrapper(self, *args, **kwargs):
#         """Wrapper function to check authentication."""
#         if not self.authenticated:
#             await self._lazy_authenticate()
#         if not self.authenticated:
#             raise E.AuthenticationError(
#                 "\033[31;1mAuthentication needed before querying the metrics.\n"
#                 "\033[0mUse the \033[34;1mdatasignals.\033[0mauthenticate("
#                 "\033[32;1m<username>\033[0m, \033[32;1m<password>\033[0m) "
#                 "method."
#             )
#         return await func(self, *args, **kwargs)

#     return wrapper


def parse_timestamp(
    df: pd.DataFrame,
    formats: Iterable[str] = ("ISO8601", "mixed"),
    dayfirst: bool = False,
    keep_index_only: bool = True,
) -> pd.DataFrame:
    """Parse timestamp column in DataFrame using multiple format attempts.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing timestamp column or index
    formats : Iterable[str], default ('ISO8601', 'mixed')
        List of datetime format strings to try
    dayfirst : bool, default False
        Whether to interpret dates as day first

    Returns
    -------
    pandas.DataFrame
        DataFrame with parsed timestamp column

    Raises
    ------
    ValueError
        If timestamp parsing fails with all formats
    """
    series = None
    d_e = (
        f"No format matched the timestamp index/column among {formats}.\n"
        "            Try calling `parse_timestamp` manually with another "
        "format, e.g.,\n"
        "            \033[32;1m>>>\033[31;1m import\033[0m api_24sea.utils "
        "\033[31;1mas \033[0mU\n"
        "            \033[32;1m>>>\033[0m U.parse_timestamp(df,\n"
        "                                  formats=\033[32m[\033[36m"
        "'YYYY-MM-DDTHH:MM:SSZ'\033[32m]\033[0m,\n"
        "                                  dayfirst=\033[34mFalse\033[0m)"
    )

    if df.index.name == "timestamp":
        if "timestamp" in df.columns:
            # fmt: off
            logging.warning("Both index and column named 'timestamp' found. "
                            "Index takes precedence.")
            # fmt: on
            # Drop the column if it's not the index
            df.drop(columns="timestamp", inplace=True)
        series = df.index.to_series()
    else:
        if "timestamp" in df.columns:
            if df["timestamp"].isnull().all():
                # fmt: off
                raise E.DataSignalsError("`data` must include a 'timestamp' "
                                         "column or indices convertible to "
                                         "timestamps.")
                # fmt: on
            series = df["timestamp"]
    if series is None:
        raise E.DataSignalsError(d_e)
    try:
        # Try parsing with different formats
        for fmt in formats:
            try:
                df["timestamp"] = pd.to_datetime(
                    series, format=fmt, dayfirst=dayfirst, errors="raise"
                )
                if keep_index_only:
                    df.set_index("timestamp", inplace=True)
                return df
            except ValueError:
                continue
        # fmt: off
        # If all previous attempts failed, it means that pandas version
        # is not compatible with the formats provided, therefore try
        # with the following formats.
        formats = ["%Y-%m-%dT%H:%M:%S%z", "%d.%m.%YT%H:%M:%S.%f%z",
                   "%Y-%m-%dT%H:%M:%SZ", "%d.%m.%YT%H:%M:%S.%fZ"]
        # fmt: on
        df["timestamp"] = pd.NaT
        for fmt in formats:
            temp_series = pd.to_datetime(series, format=fmt, errors="coerce")
            df["timestamp"].fillna(temp_series, inplace=True)
        if keep_index_only:
            df.set_index("timestamp", inplace=True)
        return df
    except Exception as exc:
        logging.error(f"All timestamp parsing attempts failed: {str(exc)}")
        raise E.DataSignalsError("Could not parse timestamp data") from exc


def estimate_chunk_size(
    tasks: list,
    start_timestamp: Union[str, datetime.datetime],
    end_timestamp: Union[str, datetime.datetime],
    grouped_metrics: Iterable,
    selected_metrics: Union[pd.DataFrame, None] = None,
):
    """
    Estimate the optimal chunk size for processing tasks based on the expected
    data volume.
    This function calculates the estimated size of the data request in megabytes
    (MB) by considering the number of data points, the number of tasks, and the
    bytes required per metric. It then determines an appropriate chunk size for
    processing the tasks efficiently.

    Parameters
    ----------
    tasks : list
        List of tasks to be processed.
    query : object
        Query object containing at least `start_timestamp` and `end_timestamp`
        attributes.
    grouped_metrics : iterable
        Iterable of grouped metrics, where each group is a tuple (key, group),
        and group is typically a DataFrame.
    selected_metrics : pandas.DataFrame or None
        DataFrame containing selected metrics with at least a "metric" column
        and optionally a "data_group" column.

    Returns
    -------
    dict
        Dictionary with the following keys:
            - "total_mb": float, estimated total size of the request in MB.
            - "n_tasks": int, number of tasks.
            - "chunk_size": int, recommended chunk size for processing.

    Notes
    -----
    - The function assumes each data point is a float64 (8 bytes) unless
      overridden by the "data_group".
    - The number of data points is estimated as one every 10 minutes between the
      start and end timestamps.
    - Chunk size is determined based on the estimated total data size.
    """

    def parse_dt(dt):
        if isinstance(dt, str):
            try:
                return pd.to_datetime(dt)
            except pd._libs.tslibs.parsing.DateParseError:
                dt = parse_shorthand_datetime(dt).replace(tzinfo=None)
        return dt

    start_dt = parse_dt(start_timestamp)
    end_dt = parse_dt(end_timestamp)
    n_minutes = (end_dt - start_dt).total_seconds() / 60
    n_points = int(n_minutes // 10) + 1
    n_tasks = len(tasks)
    # Build a dictionary of bytes per metric
    bytes_per_metric = {}
    if selected_metrics is not None:
        for _, row in selected_metrics.iterrows():
            metric = row["metric"]
            data_group = str(row.get("data_group", "")).lower()
            if data_group == "fatigue":
                bytes_per_metric[metric] = 200
            elif data_group == "mpe":
                bytes_per_metric[metric] = 50
            elif data_group == "mdl":
                bytes_per_metric[metric] = 50
            else:
                bytes_per_metric[metric] = 8
    total_bytes = 0
    for _, group in grouped_metrics:
        if isinstance(group, pd.DataFrame):
            group_met = group["metric"].tolist()
        else:
            group_met = [group["metric"]] if hasattr(group, "metric") else []
        group_bytes = sum(bytes_per_metric.get(m, 8) for m in group_met)
        total_bytes += n_points * group_bytes

    # Check for negative or zero values (sanity check)
    if total_bytes <= 0 or n_points <= 0:
        total_bytes = 0
    total_mb = total_bytes / (1024 * 1024)

    # Determine chunk_size
    if total_mb < 40:
        chunk_size = n_tasks
    elif total_mb < 80:
        chunk_size = max(1, n_tasks // 2)
    elif total_mb < 160:
        chunk_size = max(1, n_tasks // 4)
    else:
        chunk_size = max(1, n_tasks // 8)

    logging.info(f"Estimated request size: {total_mb:.2f} MB")
    return {
        "total_mb": total_mb,
        "n_tasks": n_tasks,
        "chunk_size": chunk_size,
    }


async def gather_in_chunks(
    tasks: List[Coroutine], chunk_size: int = 5, timeout: int = 3600
) -> List:
    results = []
    chunk_results = []
    with logging_redirect_tqdm():
        total_tasks = len(tasks)

        if total_tasks == 1:
            desc = "API-24SEA get_data"
        elif chunk_size == 1:
            desc = f"API-24SEA get_data [total locations: {total_tasks}]"
        else:
            # fmt: off
            desc = (f"API-24SEA get_data in {chunk_size}-sized chunks "
                    f"[total locations: {total_tasks}]")
        for i in tqdm(
            range(0, len(tasks), max(1, chunk_size)),
            desc=desc,
            colour="#c9cfd8",
        ):
            chunk = tasks[i : i + chunk_size]
            chunk_results = await tqdm_asyncio.gather(
                *chunk,
                desc=f"Getting chunk: [{i+1}-{i+len(chunk)}]",
                timeout=timeout,
                colour="#e4e8ee",
            )
            results.extend(chunk_results)
    return results


def fetch_data_sync(
    url,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    headers: Dict[str, str],
    group: DataFrameGroupBy,
    auth: httpx.BasicAuth,
    timeout: int,
) -> Any:
    """Syncronously fetch metrics data for the datasignals API app."""
    # fmt: off
    s_ = "• " + ",".join(group["metric"].tolist()).replace(",", "\n            • ")  # noqa: E501  # pylint: disable=C0301
    logging.info(f"\033[32;1m⏳ Getting data for {site} - "
                    f"{location}...\n📊 \033[35;1mMetrics: "
                    f"\033[0;34m{s_}\n\033[0m")
    # fmt: on
    r_ = handle_request(
        url,
        {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "project": [site],
            "location": [location],
            "metrics": ",".join(group["metric"].tolist()),
        },
        auth,
        headers,
        timeout=timeout,
    )
    # Warn if empty
    if r_.json() == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - " f"{location}.\033[0m"
        )
    return r_.json()


async def fetch_data_async(
    url,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    headers: Dict[str, str],
    group: DataFrameGroupBy,
    auth: httpx.BasicAuth,
    timeout: int,
    max_retries: int,
    as_dict: bool = False,
) -> Union[pd.DataFrame, Dict[str, Any]]:
    """Asyncronously fetch metrics data for the datasignals API app."""
    s_ = "• " + ",".join(group["metric"].tolist()).replace(
        ",", "\n            • "
    )
    logging.info(
        f"\033[32;1m⏳ Getting data for {site} - {location}..."
        f"\n📊 \033[35;1mMetrics: \033[0;34m{s_}\n\033[0m"
    )
    r_ = await handle_request_async(
        url,
        {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "project": [site],
            "location": [location],
            "metrics": ",".join(group["metric"].tolist()),
        },
        auth,
        headers,
        max_retries=max_retries,
        timeout=timeout,
    )
    result_json = r_.json()
    if result_json == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - {location}.\033[0m"
        )
    if as_dict:
        return result_json
    return pd.DataFrame(result_json)


async def fetch_oldest_timestamp_async(
    url,
    site: str,
    locations: Optional[str],
    headers: Dict[str, str],
    auth: httpx.BasicAuth,
    timeout: int,
    max_retries: int,
    as_dict: bool = False,
) -> Union[pd.DataFrame, Dict[str, Any]]:
    # Format locations with bullets and newlines
    if locations:
        formatted_locations = "   • " + "\n   • ".join(locations.split(","))
        logging.info(
            f"\033[32;1m⏳ Getting oldest timestamps for {site} at the "
            f"following locations:\n{formatted_locations}\n\033[0m"
        )
    else:
        logging.info(
            f"\033[32;1m⏳ Getting oldest timestamps for {site}\n\033[0m"
        )
    r_ = await handle_request_async(
        url,
        (
            {"project": site, "locations": locations}
            if locations
            else {"project": site}
        ),
        auth,
        headers,
        max_retries=max_retries,
        timeout=timeout,
    )
    result_json = r_.json()
    if result_json == []:
        logging.warning(f"\033[33;1m⚠️ No data found for {site}.\033[0m")
    if as_dict:
        return result_json
    return pd.DataFrame(result_json)


def set_threads_nr(threads: Optional[int], thread_limit: int = 30) -> int:
    """
    Set the number of threads to use for processing.

    Parameters
    ----------
    threads : Optional[int]
        The number of threads to use. If None, the number of available CPU cores
        will be used.

    Returns
    -------
    int
        The number of threads to use.
    """
    if threads is None:
        return multiprocessing.cpu_count()
    if threads < 1:
        return 1
    return int(threads) if threads < thread_limit else thread_limit


def parse_stats_list(stats_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Parse a list of statistics dictionaries into a DataFrame.

    Parameters
    ----------
    stats_list : List[Dict[str, Any]]
        List of dictionaries containing statistics data.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the parsed statistics.
    """
    if not stats_list:
        return pd.DataFrame()

    rows = []
    for d in stats_list:
        for k, v in d.items():
            if "_" in k:
                prefix, metric = k.split("_", 1)
                rows.append({"metric": metric, "stat_type": prefix, "value": v})

    if not rows:
        return pd.DataFrame()

    # Create DataFrame and pivot in one operation
    df = pd.DataFrame(rows)
    stats_df = df.pivot_table(
        index="metric", columns="stat_type", values="value", aggfunc="first"
    ).reset_index()

    # Reorder and clean
    raw_prefixes = sorted(c_ for c_ in stats_df.columns if c_ != "metric")
    cols_order = ["metric"] + sorted(raw_prefixes)
    for c in cols_order:
        if c not in stats_df.columns:
            stats_df[c] = None
    stats_df = stats_df[cols_order]

    return stats_df.reset_index(drop=True)


def get_stats_overview_info(
    stats_df: pd.DataFrame,
    metrics_overview: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Get the overview information for statistics DataFrame.

    Parameters
    ----------
    stats_df : pd.DataFrame
        DataFrame containing statistics data.
    metrics_overview : pd.DataFrame
        DataFrame containing metrics overview information.

    Returns
    -------
    pd.DataFrame
        DataFrame with overview information merged with stats_df.
    """
    if metrics_overview is None:
        return stats_df
    if stats_df.empty or metrics_overview.empty:
        return stats_df

    stats_df_temp = stats_df.copy()
    overview_temp = metrics_overview.copy()
    stats_df_temp["metric_lower"] = stats_df_temp["metric"].str.lower()
    overview_temp["metric_lower"] = overview_temp["metric"].str.lower()
    merged = stats_df_temp.merge(
        overview_temp[
            [
                "metric",
                "metric_lower",
                "site",
                "location",
                "data_group",
                "statistic",
                "short_hand",
                "print_str",
            ]
        ],
        on="metric_lower",
        how="left",
        suffixes=("", "_overview"),
    )
    merged["metric"] = merged["metric_overview"].fillna(merged["metric"])
    return merged.drop(["metric_lower", "metric_overview"], axis=1)


def get_stats_as_dict(
    stats_df: pd.DataFrame,
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Convert the statistics DataFrame to a dictionary format.

    Parameters
    ----------
    stats_df : pd.DataFrame
        DataFrame containing statistics data.

    Returns
    -------
    Dict[str, Dict[str, pd.DataFrame]]
        Dictionary with site and location as keys and statistics as values.
    """
    result_dict: DefaultDict[str, DefaultDict[str, pd.DataFrame]] = defaultdict(
        lambda: defaultdict(pd.DataFrame)
    )
    # fmt: off
    for (s_, l_), group in stats_df.groupby(['site', 'location']):
        s_ = s_.lower()
        l_ = l_.upper()
        result_dict[s_][l_] = group.drop(['site', 'location'],
                                            axis=1).reset_index(drop=True)
    # fmt: on
    return default_to_regular_dict(result_dict)


def get_site_locations(
    sites: Union[str, List[str]],
    locations: Optional[Union[str, List[str]]],
    metrics_overview: pd.DataFrame,
) -> Tuple[List[str], List[List[str]]]:
    """
    Provided a set of sites and locations, as well as the metrics overview
    table, retrieve matching locations for each site.

    Parameters
    ----------
    sites : str or List[str]
        Site(s) to filter.
    locations : str or List[str], optional
        Location(s) to filter. If None, all locations for the site(s) are used.
    metrics_overview : pd.DataFrame
        DataFrame containing metrics overview information.

    Returns
    -------
    Tuple[List[str], List[List[str]]]
        A tuple containing a list of sites and a list of lists of locations.
    """
    if isinstance(locations, list):
        if len(locations) > 1 and any(loc is None for loc in locations):
            # fmt: off
            raise E.DataSignalsError("You cannot assign multiple sites and "
                                        "locations to a list containing None")
        # fmt: on
        if len(locations) == 1 and not locations[0]:
            locations = None
    if isinstance(sites, str):
        sites = [sites]
    if isinstance(locations, str):
        locations = [locations] if locations else None

    site_locations = []
    for site in sites:
        site = site.lower()
        filtered_overview = metrics_overview[
            metrics_overview["site"].str.lower() == site
        ]
        if locations:
            locations_lower = [loc.lower() for loc in locations]
            filtered_overview = filtered_overview[
                filtered_overview["location"].str.lower().isin(locations_lower)
            ]
        locs = filtered_overview["location"].unique().tolist()
        # print(f"Found locations for site {site}: {locs}")
        if not locs:
            raise E.DataSignalsError(
                f"No matching locations (f{locations}) "
                f"found for site: {site}"
            )
        if not locations:
            site_locations.append(locs)
        else:
            site_locations.append(
                [
                    loc
                    for loc in locs
                    if loc.lower() in map(str.lower, locations)
                ]
            )
    return sites, site_locations
