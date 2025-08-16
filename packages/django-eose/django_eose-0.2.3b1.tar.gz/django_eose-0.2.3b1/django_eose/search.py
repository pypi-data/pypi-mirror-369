from functools import partial
from multiprocessing import cpu_count
import pickle
import sys

from django.core.cache import cache
from django.utils.text import slugify

try:
    import psutil # Optional
except Exception:
    psutil = None

from .executors import get_executor
from .settings import DEFAULTS
from .utils import build_proc_qs, resolve_related_field, make_cache_key


def _estimate_avg_obj_size(sample, fallback: int) -> int:
    """
    Returns the average object size in bytes based on an average of 10 samples + a 50% safety margin.
    """
    sample_size = 10
    safety_margin = 1.5

    try:
        objs = list(sample[:sample_size])
        total_size = sum(sys.getsizeof(pickle.dumps(o, protocol=pickle.HIGHEST_PROTOCOL)) for o in objs)
        avg_size = total_size / len(objs)
        return int(avg_size * safety_margin)
    except Exception:
        return fallback

def _compute_batch_size(available_bytes: int, avg_obj_size: int, max_batch_size: int) -> int:
    """
    Calculate the batch size based on the available memory and the size of each object.
    """
    if avg_obj_size <= 0:
        return DEFAULTS.MIN_BATCH_SIZE
    batch = int(available_bytes // avg_obj_size)
    batch = max(batch, DEFAULTS.MIN_BATCH_SIZE)
    batch = min(batch, max_batch_size or DEFAULTS.MAX_BATCH_SIZE)
    return batch

def _process_obj(obj, *, search: str, related_field: str | None, fields: tuple[str, ...]):
    """
    Returns obj.pk if any of the fields contain the term; otherwise, None.
    """
    try:
        client_obj = resolve_related_field(obj, related_field)
        if client_obj is None:
            return None
        values = []
        for field in fields:
            try:
                values.append(getattr(client_obj, field, None))
            except Exception:
                values.append(None)
        if any(search in (str(v or "").lower()) for v in values):
            return obj.pk
    except Exception:
        pass
    return None

def search_queryset(
    search: str,
    queryset,
    *,
    related_field: str | None = None,
    fields: tuple[str, ...] | None = None,
    only_fields: tuple[str, ...] | None = None,
    executor: str = DEFAULTS.EXECUTOR,        # "processes" | "threads" | "sync"
    cache_timeout: int = DEFAULTS.CACHE_TIMEOUT,
    imap_chunksize: int = DEFAULTS.IMAP_CHUNKSIZE,
    memory_fraction: float = DEFAULTS.MEMORY_FRACTION,
    avg_obj_size_bytes: int | None = None,
    max_workers: int | None = None,
    max_batch_size: int = None
):
    """
    Parallel search over a queryset, checking if `search` (lowercase) appears in the `fields`.

    - related_field: relation path (e.g., "order__client") or None to use the object itself.
    - fields: list of fields to inspect in the final object (decrypted/derived).
    - only_fields: list of fields to load via .only(...) to optimize I/O.
    - executor: "processes" (CPU-bound), "threads" (I/O-bound), or "sync".
    - cache_timeout: seconds to cache the found IDs.
    - imap_chunksize: chunk size per worker.
    - memory_fraction: fraction of memory available for batch sizing.
    - avg_obj_size_bytes: estimated average size per object; if None, it will be inferred with fallback.
    - max_workers: number of workers; if None, use cpu_count().
    - max_batch_size: number of objects per batch.
    """
    if not search:
        return queryset.none()

    search_lc = search.lower()

    # Sign the queryset for the cache key
    model = queryset.model
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    qs_signature = str(queryset.query)
    cache_key = make_cache_key(model_label, qs_signature, slugify(search_lc), tuple(fields), related_field)

    cached_ids = cache.get(cache_key)
    if cached_ids:
        return queryset.filter(pk__in=cached_ids)

    # Estimates available memory and batch size
    if psutil and memory_fraction > 0:
        try:
            mem = psutil.virtual_memory()
            available_bytes = int(mem.available * memory_fraction)
        except Exception:
            available_bytes = DEFAULTS.AVG_OBJ_SIZE_FALLBACK * DEFAULTS.MIN_BATCH_SIZE
    else:
        available_bytes = DEFAULTS.AVG_OBJ_SIZE_FALLBACK * DEFAULTS.MIN_BATCH_SIZE
    
    # Build optimized queryset BEFORE sampling and iteration
    proc_qs = build_proc_qs(queryset, related_field, only_fields)

    # Sample to estimate size
    avg_size = avg_obj_size_bytes or _estimate_avg_obj_size(proc_qs, DEFAULTS.AVG_OBJ_SIZE_FALLBACK)
    batch_size = _compute_batch_size(available_bytes, avg_size, max_batch_size=max_batch_size)

    # Batch iteration
    total = queryset.count()
    matched_ids: set[int] = set()

    run = get_executor(executor)
    max_workers = max_workers or cpu_count()
    total_chunk = imap_chunksize * max_workers

    func = partial(_process_obj, search=search_lc, related_field=related_field, fields=tuple(fields))

    # Traverse the queryset in batches and parallelize per item
    for start in range(0, total, batch_size):
        batch_qs = proc_qs[start:start + batch_size]
        batch_iter = batch_qs.iterator(chunk_size=total_chunk)
        
        for result in run(batch_iter, func, chunksize=imap_chunksize, max_workers=max_workers):
            if result:
                matched_ids.add(result)

    cache.set(cache_key, list(matched_ids), timeout=cache_timeout)
    return queryset.filter(pk__in=matched_ids)
