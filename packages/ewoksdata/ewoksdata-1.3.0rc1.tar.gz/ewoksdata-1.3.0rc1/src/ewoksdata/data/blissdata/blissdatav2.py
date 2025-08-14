import sys
import time
import logging
from collections import Counter
from typing import List, Optional, Tuple

import numpy
from numpy.typing import ArrayLike

from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.store import DataStore
from blissdata.redis_engine.scan import ScanState
from blissdata.redis_engine.exceptions import (
    EndOfStream,
    IndexNoMoreThereError,
    IndexNotYetThereError,
    IndexWontBeThereError,
)
from blissdata.streams.base import CursorGroup


logger = logging.getLogger(__name__)

INFINITY = sys.maxsize


def _get_data_store() -> None:
    redis_url = BeaconData().get_redis_data_db()
    return DataStore(redis_url)


def iter_bliss_scan_data_from_memory(
    scan_key: str,
    lima_names: List[str],
    counter_names: List[str],
    retry_timeout: Optional[float] = None,
    retry_period: Optional[float] = None,
):
    streams = _get_streams(scan_key, lima_names, counter_names)
    if not streams:
        return

    cursor = CursorGroup(list(streams.values()))
    cursor_timeout = retry_period or 0
    buffers = {ctr_name: list() for ctr_name in lima_names + counter_names}
    ctr_names = {stream.name: ctr_name for ctr_name, stream in streams.items()}

    while True:
        try:
            views = cursor.read(timeout=cursor_timeout)
        except EndOfStream:
            break

        views = {ctr_names[stream.name]: view for stream, view in views.items()}

        nyield = min(
            len(buffer) + len(views.get(ctr_name, ()))
            for ctr_name, buffer in buffers.items()
        )
        view_positions = {ctr_name: 0 for ctr_name in buffers.keys()}
        for _ in range(nyield):
            data = {}
            for ctr_name, buffer in buffers.items():
                if buffer:
                    data_point = buffer.pop(0)
                else:
                    view = views[ctr_name]
                    start = view_positions[ctr_name]
                    data_points = view.get_data(start=start, stop=start + 1)
                    data_point = data_points[0]
                    view_positions[ctr_name] += 1
                data[ctr_name] = data_point
            yield data

        for ctr_name, view in views.items():
            start = view_positions[ctr_name]
            data_points = view.get_data(start=start, stop=None)
            buffers[ctr_name].extend(data_points)


def last_lima_image(scan_key: str, lima_name: str) -> ArrayLike:
    """Get last lima image from memory"""
    streams = _get_streams(scan_key, [lima_name], [])
    stream = list(streams.values())[0]
    return stream.get_last_live_image().array


def _get_streams(
    scan_key: str,
    lima_names: List[str],
    counter_names: List[str],
):
    data_store = _get_data_store()
    scan = data_store.load_scan(scan_key)

    while scan.state < ScanState.PREPARED:
        scan.update()

    streams = dict()

    for name, stream in scan.streams.items():
        if (
            stream.event_stream.encoding["type"] == "json"
            and "lima" in stream.info["format"]
        ):
            if name.split(":")[-2] in lima_names:
                streams[name.split(":")[-2]] = stream

        elif name.split(":")[-1] in counter_names:
            streams[name.split(":")[-1]] = stream

    nnames = len(lima_names) + len(counter_names)
    nstreams = len(streams)
    if nnames != nstreams:
        logger.warning("asked for %d names but got %s streams", nnames, nstreams)
        return dict()

    return streams


def iter_bliss_scan_data_from_memory_slice(
    scan_key: str,
    lima_names: List[str],
    counter_names: List[str],
    slice_range: Optional[Tuple[int, int]] = None,
    retry_timeout: Optional[float] = None,
    retry_period: Optional[float] = None,
    yield_timeout: Optional[float] = None,
    max_slicing_size: Optional[float] = None,
    verbose: Optional[bool] = False,
):
    """Iterates over the data from a Bliss scan, slicing the streams associated to a lima detector or a counter between specific indexes of the scan (optional)

    :param str scan_key: key of the Bliss scan (e.g. "esrf:scan:XXXX")
    :param list lima_names: names of lima detectors
    :param list counter_names: names of non-lima detectors (you need to provide at least one)
    :param tuple slice_range: two elements which define the limits of the iteration along the scan. If None, it iterates along the whole scan
    :param float retry_timeout: timeout when it cannot access the data for `retry_timeout` seconds
    :param float retry_period: interval in seconds between data access retries
    :param float yield_timeout: timeout to stop slicing the stream and yield the buffered data
    :param float max_slicing_size: maximum size of frames to be sliced out of the stream in one single iteration. If None, it will slice all the available data in the stream
    :yields dict: data
    """
    streams = _get_streams(scan_key, lima_names, counter_names)
    if not streams:
        return

    if slice_range is None:
        slice_range = (0, INFINITY)

    if yield_timeout is None:
        yield_timeout = 0.01

    buffers_count = Counter({counter: slice_range[0] for counter in streams.keys()})

    # Read and yield continuously
    stream_on = True

    incoming_buffers = {stream_name: [] for stream_name in streams.keys()}
    non_yielded_buffers = {stream_name: [] for stream_name in streams.keys()}

    restart_buffer = time.perf_counter()
    while stream_on:

        # While loop will stop unless one single stream is successfully sliced
        stream_on = False

        for stream_name, stream in streams.items():
            try:
                # Stop condition for limited slices
                if (
                    slice_range[1] is not INFINITY
                    and buffers_count[stream_name] >= slice_range[1]
                ):
                    continue

                # Test first index, (slicing between limits do not fall into Error)
                _ = stream[buffers_count[stream_name]]
                if max_slicing_size is None:
                    stream_data = stream[buffers_count[stream_name] : slice_range[1]]
                else:
                    stream_data = stream[
                        buffers_count[stream_name] : min(
                            slice_range[1],
                            buffers_count[stream_name] + max_slicing_size,
                        )
                    ]
                incoming_buffers[stream_name] = stream_data
                buffers_count[stream_name] += len(stream_data)
                stream_on = True

            except IndexNotYetThereError:
                stream_on = True
            except IndexWontBeThereError:
                pass
            except IndexNoMoreThereError:
                pass
            except EndOfStream:
                pass
            except RuntimeError:
                pass

            for stream_name in incoming_buffers.keys():
                if len(incoming_buffers[stream_name]) > 0:
                    if len(non_yielded_buffers[stream_name]) == 0:
                        non_yielded_buffers[stream_name] = numpy.array(
                            incoming_buffers[stream_name]
                        )
                    else:
                        non_yielded_buffers[stream_name] = numpy.concatenate(
                            (
                                non_yielded_buffers[stream_name],
                                incoming_buffers[stream_name],
                            )
                        )
                    incoming_buffers[stream_name] = []

        if not stream_on or ((time.perf_counter() - restart_buffer) > yield_timeout):

            frames_to_yield = min(
                [len(value) for value in non_yielded_buffers.values()]
            )

            if frames_to_yield > 0:
                if verbose:
                    for stream_name, stream_buffer in non_yielded_buffers.items():
                        print(
                            f"After slicing the stream: {stream_name} buffer contains {len(stream_buffer)} items"
                        )

                # Yield point by point
                for index in range(frames_to_yield):
                    yield {
                        stream_name: stream_buffer[index]
                        for stream_name, stream_buffer in non_yielded_buffers.items()
                    }

                # Save the non-yielded points for the next iteration
                for stream_name in non_yielded_buffers.keys():
                    non_yielded_buffers[stream_name] = non_yielded_buffers[stream_name][
                        frames_to_yield:
                    ]

                if verbose:
                    for stream_name, stream_buffer in non_yielded_buffers.items():
                        print(
                            f"After yielding: {stream_name} buffer contains {len(stream_buffer)} non-yielded items"
                        )

            restart_buffer = time.perf_counter()
