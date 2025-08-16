"""Type stubs for python-libtorrent 2.0.11

Python bindings for libtorrent - A high-performance BitTorrent library.

This module provides comprehensive Python bindings for the libtorrent C++ library,
enabling BitTorrent protocol implementation with support for both BitTorrent v1 and v2.

Key Features:
- Complete torrent session management
- Individual torrent control and monitoring
- Advanced piece picking and choking algorithms
- DHT (Distributed Hash Table) support
- Peer exchange and local service discovery
- Tracker communication and scraping
- Resume data for fast startup
- Extensive statistics and alerts
- SSL/encryption support
- Rate limiting and bandwidth management

Core Workflow:
1. Create a session with desired settings
2. Add torrents using add_torrent_params
3. Monitor progress through alerts and status updates
4. Handle peer connections and piece downloads
5. Save resume data for persistence

Example:
    import libtorrent as lt

    # Create session
    ses = lt.session()

    # Add torrent
    params = lt.add_torrent_params()
    params.ti = lt.torrent_info('file.torrent')
    params.save_path = './downloads'

    handle = ses.add_torrent(params)

    # Monitor alerts
    while True:
        alerts = ses.pop_alerts()
        for alert in alerts:
            print(alert.message())
"""

from typing import Any, Dict, List, Optional, Union, Callable, overload, Literal
import datetime

__version__: str
version: str
version_major: int
version_minor: int

class sha1_hash:
    """A 160-bit SHA-1 hash used for piece hashes and info hashes in BitTorrent v1.

    Represents a 20-byte SHA-1 hash value commonly used throughout the BitTorrent
    protocol for identifying pieces, torrents, and peers.

    Args:
        data: Optional 20-byte hash data. If None, creates a zero hash.

    Example:
        # Create from bytes
        hash_val = sha1_hash(b'\x00' * 20)

        # Convert to string representation
        print(hash_val.to_string())
    """
    def __init__(self, data: Optional[bytes] = None) -> None: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __lt__(self, other: sha1_hash) -> bool: ...
    def __hash__(self) -> int: ...
    def to_bytes(self) -> bytes: ...
    def is_all_zeros(self) -> bool: ...
    def clear(self) -> None: ...
    def to_string(self) -> str: ...

class sha256_hash:
    """A 256-bit SHA-256 hash used in BitTorrent v2 for piece hashes and merkle trees.

    Represents a 32-byte SHA-256 hash value used in the newer BitTorrent v2 protocol
    for improved security and efficiency.

    Args:
        data: Optional 32-byte hash data. If None, creates a zero hash.

    Example:
        # Create from bytes
        hash_val = sha256_hash(b'\x00' * 32)

        # Check if empty
        if hash_val.is_all_zeros():
            print("Empty hash")
    """
    def __init__(self, data: Optional[bytes] = None) -> None: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __lt__(self, other: sha256_hash) -> bool: ...
    def __hash__(self) -> int: ...
    def to_bytes(self) -> bytes: ...
    def is_all_zeros(self) -> bool: ...
    def clear(self) -> None: ...
    def to_string(self) -> str: ...

class info_hash_t:
    """Hybrid info hash supporting both BitTorrent v1 and v2 protocols.

    This class can contain either a v1 (SHA-1) hash, a v2 (SHA-256) hash, or both,
    allowing torrents to be compatible with both protocol versions.

    Args:
        v1: Optional SHA-1 hash for BitTorrent v1 compatibility.
        v2: Optional SHA-256 hash for BitTorrent v2 support.

    Example:
        # Create v1-only hash
        info_hash = info_hash_t(v1=sha1_hash(torrent_data))

        # Check which versions are available
        if info_hash.has_v1():
            print("Compatible with BitTorrent v1")
        if info_hash.has_v2():
            print("Compatible with BitTorrent v2")

        # Get the best available hash
        best_hash = info_hash.get_best()
    """
    def __init__(
        self, v1: Optional[sha1_hash] = None, v2: Optional[sha256_hash] = None
    ) -> None: ...
    def has_v1(self) -> bool: ...
    def has_v2(self) -> bool: ...
    def get_best(self) -> Union[sha1_hash, sha256_hash]: ...
    v1: sha1_hash
    v2: sha256_hash

class error_code:
    def __init__(self) -> None: ...
    def message(self) -> str: ...
    def value(self) -> int: ...
    def category(self) -> Any: ...
    def clear(self) -> None: ...
    def assign(self, val: int, cat: Any) -> None: ...
    @property
    def __safe_for_unpickling__(self) -> bool: ...

class peer_request:
    def __init__(
        self, piece: int = 0, start: int = 0, length: int = 0
    ) -> None: ...
    @property
    def piece(self) -> int: ...
    @property
    def start(self) -> int: ...
    @property
    def length(self) -> int: ...

class file_slice:
    def __init__(
        self, file_index: int = 0, offset: int = 0, size: int = 0
    ) -> None: ...
    file_index: int
    offset: int
    size: int

class file_entry:
    def __init__(
        self, path: str = "", size: int = 0, flags: int = 0, mtime: int = 0
    ) -> None: ...
    path: str
    flags: int
    mtime: int
    symlink_path: str
    @property
    def size(self) -> int: ...
    @property
    def executable_attribute(self) -> bool: ...
    @property
    def hidden_attribute(self) -> bool: ...
    @property
    def pad_file(self) -> bool: ...
    @property
    def symlink_attribute(self) -> bool: ...
    @property
    def offset(self) -> int: ...
    filehash: sha1_hash

class file_storage:
    def __init__(self) -> None: ...
    def is_valid(self) -> bool: ...
    def add_file(
        self,
        path: str,
        size: int,
        flags: int = 0,
        mtime: int = 0,
        symlink_path: str = "",
    ) -> None: ...
    def rename_file(self, index: int, new_filename: str) -> None: ...
    def num_files(self) -> int: ...
    def file_path(self, index: int) -> str: ...
    def file_size(self, index: int) -> int: ...
    def file_offset(self, index: int) -> int: ...
    def file_flags(self, index: int) -> int: ...
    def total_size(self) -> int: ...
    def piece_length(self) -> int: ...
    def num_pieces(self) -> int: ...
    def set_piece_length(self, length: int) -> None: ...
    def piece_size(self, index: int) -> int: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def at(self, index: int) -> file_entry: ...
    def file_absolute_path(self, index: int, save_path: str) -> str: ...
    def file_index_at_offset(self, offset: int) -> int: ...
    def file_index_at_piece(self, piece: int) -> int: ...
    def file_index_for_root(self, file: int) -> int: ...
    def file_name(self, index: int) -> str: ...
    def hash(self, index: int) -> sha1_hash: ...
    def name(self) -> str: ...
    def piece_index_at_file(self, file: int) -> int: ...
    def root(self, file: int) -> sha256_hash: ...
    def set_name(self, name: str) -> None: ...
    def set_num_pieces(self, num_pieces: int) -> None: ...
    def symlink(self, index: int) -> str: ...
    flag_executable: int = ...
    flag_hidden: int = ...
    flag_pad_file: int = ...
    flag_symlink: int = ...
    v2: bool = ...

class torrent_info:
    """Contains metadata and information about a torrent.

    This class represents the parsed contents of a .torrent file including
    file lists, piece hashes, tracker information, and other metadata.

    Key Information:
    - File structure and sizes
    - Piece hashes for integrity verification
    - Tracker and web seed URLs
    - Creator, comment, and creation date
    - DHT nodes and similar torrents

    Example:
        # Load from .torrent file
        ti = torrent_info('ubuntu.torrent')
        print(f"Name: {ti.name()}")
        print(f"Size: {ti.total_size()} bytes")
        print(f"Files: {ti.num_files()}")
        print(f"Pieces: {ti.num_pieces()}")

        # Iterate through files
        files = ti.files()
        for i in range(files.num_files()):
            print(f"File {i}: {files.file_path(i)} ({files.file_size(i)} bytes)")

        # Get trackers
        for tracker in ti.trackers():
            print(f"Tracker: {tracker.url}")
    """
    @overload
    def __init__(self, filename: str) -> None: ...
    @overload
    def __init__(self, buffer: bytes) -> None: ...
    @overload
    def __init__(self, dict_data: Dict[str, Any]) -> None: ...
    def info_hashes(self) -> info_hash_t: ...
    def name(self) -> str: ...
    def comment(self) -> str: ...
    def creator(self) -> str: ...
    def total_size(self) -> int: ...
    def piece_length(self) -> int: ...
    def num_pieces(self) -> int: ...
    def piece_size(self, index: int) -> int: ...
    def piece_hash(self, index: int) -> sha1_hash: ...
    def files(self) -> file_storage: ...
    def orig_files(self) -> file_storage: ...
    def rename_file(self, index: int, new_filename: str) -> None: ...
    def remap_files(self, f: file_storage) -> None: ...
    def add_tracker(self, url: str, tier: int = 0) -> None: ...
    def trackers(self) -> List[Any]: ...
    def creation_date(self) -> int: ...
    def set_creation_date(self, timestamp: int) -> None: ...
    def add_url_seed(self, url: str) -> None: ...
    def add_http_seed(self, url: str) -> None: ...
    def web_seeds(self) -> List[Dict[str, Any]]: ...
    def is_valid(self) -> bool: ...
    def priv(self) -> bool: ...
    def is_i2p(self) -> bool: ...
    def is_merkle_torrent(self) -> bool: ...
    def ssl_cert(self) -> str: ...
    def is_loaded(self) -> bool: ...
    def metadata(self) -> bytes: ...
    def metadata_size(self) -> int: ...
    def add_node(self, hostname: str, port: int) -> None: ...
    def collections(self) -> List[str]: ...
    def file_at(self, index: int) -> file_entry: ...
    def hash_for_piece(self, piece: int) -> sha1_hash: ...
    def info_hash(self) -> sha1_hash: ...
    def info_section(self) -> bytes: ...
    def map_block(
        self, piece: int, offset: int, size: int
    ) -> List[file_slice]: ...
    def map_file(self, file: int, offset: int, size: int) -> Any: ...
    def merkle_tree(self) -> List[sha1_hash]: ...
    def nodes(self) -> List[Any]: ...
    def num_files(self) -> int: ...
    def set_merkle_tree(self, tree: List[sha1_hash]) -> None: ...
    def set_web_seeds(self, seeds: List[str]) -> None: ...
    def similar_torrents(self) -> List[sha1_hash]: ...

class announce_entry:
    def __init__(self, url: str = "") -> None: ...
    url: str
    tier: int
    fail_limit: int
    @property
    def fails(self) -> int: ...
    @property
    def source(self) -> int: ...
    @property
    def verified(self) -> bool: ...
    @property
    def updating(self) -> bool: ...
    @property
    def start_sent(self) -> bool: ...
    @property
    def complete_sent(self) -> bool: ...
    @property
    def send_stats(self) -> bool: ...
    @property
    def last_error(self) -> Any: ...
    @property
    def message(self) -> str: ...
    @property
    def min_announce(self) -> int: ...
    @property
    def next_announce(self) -> int: ...
    @property
    def scrape_complete(self) -> int: ...
    @property
    def scrape_downloaded(self) -> int: ...
    @property
    def scrape_incomplete(self) -> int: ...
    @property
    def trackerid(self) -> str: ...
    can_announce: bool
    is_working: bool
    min_announce_in: int
    next_announce_in: int
    reset: Any
    trim: Any

class peer_id:
    def __init__(self, data: Optional[bytes] = None) -> None: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def to_bytes(self) -> bytes: ...
    def __lt__(self, other: "peer_id") -> bool: ...
    def clear(self) -> None: ...
    def is_all_zeros(self) -> bool: ...
    def to_string(self) -> str: ...

class peer_info:
    @property
    def flags(self) -> int: ...
    @property
    def source(self) -> int: ...
    @property
    def read_state(self) -> int: ...
    @property
    def write_state(self) -> int: ...
    @property
    def ip(self) -> Any: ...
    @property
    def up_speed(self) -> int: ...
    @property
    def down_speed(self) -> int: ...
    @property
    def payload_up_speed(self) -> int: ...
    @property
    def payload_down_speed(self) -> int: ...
    @property
    def total_download(self) -> int: ...
    @property
    def total_upload(self) -> int: ...
    @property
    def pid(self) -> peer_id: ...
    @property
    def pieces(self) -> Any: ...
    @property
    def upload_limit(self) -> int: ...
    @property
    def download_limit(self) -> int: ...
    @property
    def last_request(self) -> datetime.datetime: ...
    @property
    def last_active(self) -> datetime.datetime: ...
    @property
    def download_queue_time(self) -> datetime.datetime: ...
    @property
    def queue_bytes(self) -> int: ...
    @property
    def request_timeout(self) -> int: ...
    @property
    def send_buffer_size(self) -> int: ...
    @property
    def used_send_buffer(self) -> int: ...
    @property
    def receive_buffer_size(self) -> int: ...
    @property
    def used_receive_buffer(self) -> int: ...
    @property
    def num_hashfails(self) -> int: ...
    @property
    def country(self) -> str: ...
    @property
    def inet_as_name(self) -> str: ...
    @property
    def inet_as(self) -> int: ...
    @property
    def load_balancing(self) -> int: ...
    @property
    def requests_in_buffer(self) -> int: ...
    @property
    def target_dl_queue_length(self) -> int: ...
    @property
    def upload_queue_length(self) -> int: ...
    @property
    def download_queue_length(self) -> int: ...
    @property
    def timed_out_requests(self) -> int: ...
    @property
    def busy_requests(self) -> int: ...
    @property
    def progress(self) -> float: ...
    @property
    def progress_ppm(self) -> int: ...
    @property
    def estimated_reciprocation_rate(self) -> int: ...
    @property
    def local_endpoint(self) -> Any: ...
    @property
    def bw_disk(self) -> int: ...
    @property
    def bw_global(self) -> int: ...
    @property
    def bw_idle(self) -> int: ...
    @property
    def bw_limit(self) -> int: ...
    @property
    def bw_network(self) -> int: ...
    @property
    def bw_torrent(self) -> int: ...
    choked: bool
    @property
    def client(self) -> str: ...
    connecting: bool
    @property
    def connection_type(self) -> int: ...
    dht: bool
    @property
    def download_rate_peak(self) -> int: ...
    @property
    def downloading_block_index(self) -> int: ...
    @property
    def downloading_piece_index(self) -> int: ...
    @property
    def downloading_progress(self) -> int: ...
    @property
    def downloading_total(self) -> int: ...
    endgame_mode: bool
    @property
    def failcount(self) -> int: ...
    handshake: bool
    holepunched: bool
    http_seed: bool
    i2p_destination: str
    i2p_socket: bool
    @property
    def interesting(self) -> bool: ...
    local_connection: bool
    lsd: bool
    @property
    def num_pieces(self) -> int: ...
    on_parole: bool
    optimistic_unchoke: bool
    outgoing_connection: bool
    @property
    def pending_disk_bytes(self) -> int: ...
    pex: bool
    plaintext_encrypted: bool
    queued: bool
    rc4_encrypted: bool
    @property
    def receive_quota(self) -> int: ...
    remote_choked: bool
    @property
    def remote_dl_rate(self) -> int: ...
    remote_interested: bool
    resume_data: bool
    @property
    def rtt(self) -> int: ...
    seed: bool
    @property
    def send_quota(self) -> int: ...
    snubbed: bool
    @property
    def standard_bittorrent(self) -> bool: ...
    supports_extensions: bool
    @property
    def tracker(self) -> bool: ...
    upload_only: bool
    @property
    def upload_rate_peak(self) -> int: ...
    web_seed: bool

class torrent_status:
    """Current status and statistics for a torrent.

    Provides comprehensive information about a torrent's current state including
    download progress, transfer rates, peer connections, and various status flags.

    Key Status Information:
    - Download/upload progress and rates
    - Number of seeds and peers
    - Current state (downloading, seeding, paused, etc.)
    - Total transferred data and time statistics
    - Error information if applicable

    Example:
        status = handle.status()

        # Progress information
        print(f"Progress: {status.progress:.1%}")
        print(f"Downloaded: {status.total_done}/{status.total_wanted} bytes")

        # Speed information
        print(f"Download: {status.download_rate} B/s")
        print(f"Upload: {status.upload_rate} B/s")

        # Peer information
        print(f"Seeds: {status.num_seeds}/{status.num_complete}")
        print(f"Peers: {status.num_peers}/{status.num_incomplete}")

        # State checking
        if status.is_seeding:
            print("Currently seeding")
        elif status.paused:
            print("Paused")
        elif status.error:
            print(f"Error: {status.error}")
    """
    @property
    def state(self) -> int: ...
    @property
    def paused(self) -> bool: ...
    @property
    def auto_managed(self) -> bool: ...
    @property
    def sequential_download(self) -> bool: ...
    @property
    def is_seeding(self) -> bool: ...
    @property
    def is_finished(self) -> bool: ...
    @property
    def has_metadata(self) -> bool: ...
    @property
    def has_incoming(self) -> bool: ...
    @property
    def moving_storage(self) -> bool: ...
    @property
    def announcing_to_trackers(self) -> bool: ...
    @property
    def announcing_to_lsd(self) -> bool: ...
    @property
    def announcing_to_dht(self) -> bool: ...
    @property
    def progress(self) -> float: ...
    @property
    def progress_ppm(self) -> int: ...
    @property
    def queue_position(self) -> int: ...
    @property
    def download_rate(self) -> int: ...
    @property
    def upload_rate(self) -> int: ...
    @property
    def download_payload_rate(self) -> int: ...
    @property
    def upload_payload_rate(self) -> int: ...
    @property
    def num_seeds(self) -> int: ...
    @property
    def num_peers(self) -> int: ...
    @property
    def num_complete(self) -> int: ...
    @property
    def num_incomplete(self) -> int: ...
    @property
    def list_seeds(self) -> int: ...
    @property
    def list_peers(self) -> int: ...
    @property
    def connect_candidates(self) -> int: ...
    @property
    def num_pieces(self) -> int: ...
    @property
    def total_done(self) -> int: ...
    @property
    def total_wanted_done(self) -> int: ...
    @property
    def total_wanted(self) -> int: ...
    @property
    def total_download(self) -> int: ...
    @property
    def total_upload(self) -> int: ...
    @property
    def total_payload_download(self) -> int: ...
    @property
    def total_payload_upload(self) -> int: ...
    @property
    def total_failed_bytes(self) -> int: ...
    @property
    def total_redundant_bytes(self) -> int: ...
    @property
    def all_time_upload(self) -> int: ...
    @property
    def all_time_download(self) -> int: ...
    @property
    def added_time(self) -> int: ...
    @property
    def completed_time(self) -> int: ...
    @property
    def last_seen_complete(self) -> int: ...
    @property
    def storage_mode(self) -> int: ...
    @property
    def distributed_copies(self) -> float: ...
    @property
    def distributed_full_copies(self) -> int: ...
    @property
    def distributed_fraction(self) -> int: ...
    @property
    def pieces(self) -> Any: ...
    @property
    def verified_pieces(self) -> Any: ...
    @property
    def num_uploads(self) -> int: ...
    @property
    def uploads_limit(self) -> int: ...
    @property
    def num_connections(self) -> int: ...
    @property
    def connections_limit(self) -> int: ...
    @property
    def up_bandwidth_queue(self) -> int: ...
    @property
    def down_bandwidth_queue(self) -> int: ...
    @property
    def time_since_upload(self) -> int: ...
    @property
    def time_since_download(self) -> int: ...
    @property
    def active_time(self) -> int: ...
    @property
    def finished_time(self) -> int: ...
    @property
    def seeding_time(self) -> int: ...
    @property
    def seed_rank(self) -> int: ...
    @property
    def last_scrape(self) -> int: ...
    @property
    def sparse_regions(self) -> int: ...
    @property
    def priority(self) -> int: ...
    @property
    def save_path(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def next_announce(self) -> datetime.datetime: ...
    @property
    def current_tracker(self) -> str: ...
    @property
    def total_transferred(self) -> int: ...
    @property
    def total_size(self) -> int: ...
    @property
    def info_hashes(self) -> info_hash_t: ...
    @property
    def active_duration(self) -> int: ...
    allocating: bool
    @property
    def announce_interval(self) -> int: ...
    @property
    def block_size(self) -> int: ...
    checking_files: bool
    checking_resume_data: bool
    downloading: bool
    downloading_metadata: bool
    @property
    def errc(self) -> Any: ...
    @property
    def error(self) -> str: ...
    @property
    def error_file(self) -> int: ...
    finished: bool
    @property
    def finished_duration(self) -> int: ...
    @property
    def flags(self) -> int: ...
    @property
    def handle(self) -> Any: ...
    @property
    def info_hash(self) -> sha1_hash: ...
    @property
    def ip_filter_applies(self) -> bool: ...
    @property
    def is_loaded(self) -> bool: ...
    @property
    def last_download(self) -> int: ...
    @property
    def last_upload(self) -> int: ...
    @property
    def need_save_resume(self) -> bool: ...
    queued_for_checking: bool
    @property
    def seed_mode(self) -> bool: ...
    seeding: bool
    @property
    def seeding_duration(self) -> int: ...
    @property
    def share_mode(self) -> bool: ...
    @property
    def states(self) -> Any: ...
    @property
    def stop_when_ready(self) -> bool: ...
    @property
    def super_seeding(self) -> bool: ...
    @property
    def torrent_file(self) -> Any: ...
    @property
    def total(self) -> int: ...
    @property
    def upload_mode(self) -> bool: ...

class torrent_handle:
    """Handle for controlling and monitoring an individual torrent in a session.

    This class provides the interface to control a specific torrent including
    pausing/resuming, setting priorities, getting status information, and managing
    piece deadlines.

    Key Operations:
    - Control torrent state (pause, resume, force recheck)
    - Set file and piece priorities
    - Monitor download progress and peer information
    - Handle piece deadlines for streaming
    - Manage tracker communication
    - Save/load resume data

    Example:
        # Get torrent status
        status = handle.status()
        print(f"Progress: {status.progress * 100:.1f}%")
        print(f"Download rate: {status.download_rate} bytes/s")

        # Pause/resume torrent
        handle.pause()
        handle.resume()

        # Set file priorities (0=don't download, 1-7=priority levels)
        handle.prioritize_files([1, 0, 4])  # Download first and third file

        # Force reannounce to trackers
        handle.force_reannounce()
    """
    def __init__(self) -> None: ...
    def is_valid(self) -> bool: ...
    def pause(self, flags: int = 0) -> None: ...
    def resume(self) -> None: ...
    def clear_error(self) -> None: ...
    def status(self, flags: int = 0) -> torrent_status:
        """Get current status and statistics for this torrent.

        Args:
            flags: Optional flags to control which information is included
                  (query_distributed_copies, query_pieces, etc.)

        Returns:
            Comprehensive status object with download progress, rates, peer counts,
            and other torrent information.

        Example:
            status = handle.status()
            print(f"State: {status.state}")
            print(f"Progress: {status.progress:.2%}")
            print(f"Seeds: {status.num_seeds}, Peers: {status.num_peers}")
            print(f"Down: {status.download_rate} B/s, Up: {status.upload_rate} B/s")
        """
        ...
    def get_download_queue(self) -> List[Any]: ...
    def get_peer_info(self) -> List[peer_info]: ...
    def torrent_file(self) -> Optional[torrent_info]: ...
    def queue_position(self) -> int: ...
    def queue_position_down(self) -> None: ...
    def queue_position_top(self) -> None: ...
    def queue_position_bottom(self) -> None: ...
    def queue_position_up(self) -> None: ...
    def add_piece(self, piece: int, data: bytes, flags: int = 0) -> None: ...
    def read_piece(self, piece: int) -> None: ...
    def have_piece(self, piece: int) -> bool: ...
    def get_piece_priorities(self) -> List[int]: ...
    def get_file_priorities(self) -> List[int]: ...
    def prioritize_pieces(self, priorities: List[int]) -> None: ...
    def prioritize_files(self, priorities: List[int]) -> None: ...
    def piece_priority(self, piece: int, priority: int) -> None: ...
    def file_priority(self, file: int, priority: int) -> None: ...
    def file_status(self) -> List[Any]: ...
    def clear_piece_deadlines(self) -> None: ...
    def set_piece_deadline(
        self, piece: int, deadline: int, flags: int = 0
    ) -> None: ...
    def reset_piece_deadline(self, piece: int) -> None: ...
    def flush_cache(self) -> None: ...
    def force_lsd_announce(self) -> None: ...
    def force_dht_announce(self) -> None: ...
    def force_reannounce(
        self, seconds: int = 0, tracker_index: int = -1, flags: int = 0
    ) -> None: ...
    def scrape_tracker(self, index: int = -1) -> None: ...
    def upload_limit(self) -> int: ...
    def download_limit(self) -> int: ...
    def set_upload_limit(self, limit: int) -> None: ...
    def set_download_limit(self, limit: int) -> None: ...
    def set_sequential_download(self, sd: bool) -> None: ...
    def connect_peer(
        self, endpoint: Any, source: int = 0, flags: int = 0
    ) -> None: ...
    def save_resume_data(self, flags: int = 0) -> None: ...
    def need_save_resume_data(self) -> bool: ...
    def auto_managed(self, auto_managed: bool) -> None: ...
    def move_storage(self, save_path: str, flags: int = 0) -> None: ...
    def rename_file(self, file: int, new_name: str) -> None: ...
    def add_tracker(self, announce_entry: announce_entry) -> None: ...
    def replace_trackers(self, trackers: List[announce_entry]) -> None: ...
    def add_url_seed(self, url: str) -> None: ...
    def remove_url_seed(self, url: str) -> None: ...
    def url_seeds(self) -> List[str]: ...
    def add_http_seed(self, url: str) -> None: ...
    def remove_http_seed(self, url: str) -> None: ...
    def http_seeds(self) -> List[str]: ...
    def set_metadata(self, metadata: bytes) -> None: ...
    def set_flags(self, flags: int) -> None: ...
    def unset_flags(self, flags: int) -> None: ...
    def flags(self) -> int: ...
    def info_hash(self) -> sha1_hash: ...
    def info_hashes(self) -> info_hash_t: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __lt__(self, other: torrent_handle) -> bool: ...
    def name(self) -> str: ...
    def save_path(self) -> str: ...
    def max_uploads(self) -> int: ...
    def set_max_uploads(self, max_uploads: int) -> None: ...
    def max_connections(self) -> int: ...
    def set_max_connections(self, max_connections: int) -> None: ...
    def has_metadata(self) -> bool: ...
    def is_seed(self) -> bool: ...
    def is_finished(self) -> bool: ...
    def is_paused(self) -> bool: ...
    def is_auto_managed(self) -> bool: ...
    def force_recheck(self) -> None: ...
    @property
    def save_info_dict(self) -> bool: ...
    def get_torrent_info(self) -> torrent_info: ...
    def write_resume_data(self, flags: int = 0) -> None: ...
    def use_interface(self, net_interface: str) -> None: ...
    def set_priority(self, priority: int) -> None: ...
    def set_upload_mode(self, upload_mode: bool) -> None: ...
    def set_share_mode(self, share_mode: bool) -> None: ...
    def set_ssl_certificate(
        self,
        certificate: str,
        private_key: str,
        dh_params: str,
        passphrase: str = "",
    ) -> None: ...
    def set_ssl_certificate_buffer(
        self, certificate: bytes, private_key: bytes, dh_params: bytes
    ) -> None: ...
    def trackers(self) -> List[announce_entry]: ...
    def post_trackers(self) -> None: ...
    def post_status(self, flags: int = 0) -> None: ...
    def post_download_queue(self) -> None: ...
    def post_file_progress(self, flags: int = 0) -> None: ...
    def post_peer_info(self) -> None: ...
    def post_piece_availability(self) -> None: ...
    def file_progress(self, flags: int = 0) -> List[int]: ...
    def file_priorities(self) -> List[int]: ...
    def piece_priorities(self) -> List[int]: ...
    def piece_availability(self) -> List[int]: ...
    def stop_when_ready(self) -> bool: ...
    def super_seeding(self) -> bool: ...
    def set_ratio(self, ratio: float) -> None: ...
    def set_tracker_login(self, username: str, password: str) -> None: ...
    def set_peer_upload_limit(self, endpoint: Any, limit: int) -> None: ...
    def set_peer_download_limit(self, endpoint: Any, limit: int) -> None: ...
    @property
    def query_verified_pieces(self) -> bool: ...
    @property
    def query_pieces(self) -> bool: ...
    @property
    def query_last_seen_complete(self) -> bool: ...
    @property
    def query_distributed_copies(self) -> bool: ...
    @property
    def query_accurate_download_counters(self) -> bool: ...
    @property
    def flush_disk_cache(self) -> bool: ...
    alert_when_available: int = ...
    apply_ip_filter: int = ...
    graceful_pause: int = ...
    ignore_min_interval: int = ...
    only_if_modified: int = ...
    overwrite_existing: int = ...
    piece_granularity: int = ...

class add_torrent_params:
    """Configuration parameters for adding a torrent to a session.

    This class contains all the settings needed to add a torrent including the
    torrent metadata, save location, file priorities, and various behavioral flags.

    Key Parameters:
    - ti: torrent_info object containing torrent metadata
    - save_path: Directory where files will be saved
    - resume_data: Previously saved state for fast startup
    - file_priorities: Per-file download priorities
    - flags: Behavioral flags (paused, auto_managed, etc.)

    Example:
        # Add from .torrent file
        params = add_torrent_params()
        params.ti = torrent_info('movie.torrent')
        params.save_path = './downloads/movies'
        params.flags = torrent_flags.auto_managed

        # Add from magnet link with resume data
        params = add_torrent_params()
        params.url = 'magnet:?xt=urn:btih:...'
        params.save_path = './downloads'
        if resume_data:
            params.resume_data = resume_data

        handle = session.add_torrent(params)
    """
    def __init__(self) -> None: ...
    ti: Optional[torrent_info]
    trackers: List[str]
    tracker_tiers: List[int]
    dht_nodes: List[Any]
    name: str
    save_path: str
    resume_data: bytes
    storage_mode: int
    userdata: Any
    file_priorities: List[int]
    piece_priorities: List[int]
    url: str
    flags: int
    info_hashes: info_hash_t
    max_uploads: int
    max_connections: int
    upload_limit: int
    download_limit: int
    active_time: Any
    added_time: Any
    banned_peers: Any
    completed_time: Any
    finished_time: Any
    have_pieces: Any
    http_seeds: Any
    info_hash: Any
    last_download: Any
    last_seen_complete: Any
    last_upload: Any
    merkle_tree: Any
    num_complete: Any
    num_downloaded: Any
    num_incomplete: Any
    peers: Any
    renamed_files: Any
    seeding_time: Any
    total_downloaded: Any
    total_uploaded: Any
    trackerid: Any
    unfinished_pieces: Any
    url_seeds: Any
    verified_pieces: Any
    version: Any

class session_params:
    def __init__(self) -> None: ...
    settings: Dict[str, Any]
    dht_settings: Any
    dht_state: bytes
    alert_mask: int
    ext_state: bytes
    ip_filter: Any

class session_status:
    @property
    def has_incoming_connections(self) -> bool: ...
    @property
    def upload_rate(self) -> int: ...
    @property
    def download_rate(self) -> int: ...
    @property
    def total_download(self) -> int: ...
    @property
    def total_upload(self) -> int: ...
    @property
    def payload_upload_rate(self) -> int: ...
    @property
    def payload_download_rate(self) -> int: ...
    @property
    def total_payload_download(self) -> int: ...
    @property
    def total_payload_upload(self) -> int: ...
    @property
    def ip_overhead_upload_rate(self) -> int: ...
    @property
    def ip_overhead_download_rate(self) -> int: ...
    @property
    def total_ip_overhead_download(self) -> int: ...
    @property
    def total_ip_overhead_upload(self) -> int: ...
    @property
    def dht_upload_rate(self) -> int: ...
    @property
    def dht_download_rate(self) -> int: ...
    @property
    def total_dht_download(self) -> int: ...
    @property
    def total_dht_upload(self) -> int: ...
    @property
    def tracker_upload_rate(self) -> int: ...
    @property
    def tracker_download_rate(self) -> int: ...
    @property
    def total_tracker_download(self) -> int: ...
    @property
    def total_tracker_upload(self) -> int: ...
    @property
    def total_redundant_bytes(self) -> int: ...
    @property
    def total_failed_bytes(self) -> int: ...
    @property
    def num_peers(self) -> int: ...
    @property
    def num_unchoked(self) -> int: ...
    @property
    def allowed_upload_slots(self) -> int: ...
    @property
    def up_bandwidth_queue(self) -> int: ...
    @property
    def down_bandwidth_queue(self) -> int: ...
    @property
    def up_bandwidth_bytes_queue(self) -> int: ...
    @property
    def down_bandwidth_bytes_queue(self) -> int: ...
    @property
    def optimistic_unchoke_counter(self) -> int: ...
    @property
    def unchoke_counter(self) -> int: ...
    @property
    def disk_write_queue(self) -> int: ...
    @property
    def disk_read_queue(self) -> int: ...
    @property
    def dht_nodes(self) -> int: ...
    @property
    def dht_node_cache(self) -> int: ...
    @property
    def dht_torrents(self) -> int: ...
    @property
    def dht_global_nodes(self) -> int: ...
    @property
    def active_requests(self) -> int: ...
    @property
    def peerlist_size(self) -> int: ...
    @property
    def dht_total_allocations(self) -> int: ...
    @property
    def utp_stats(self) -> Any: ...

class alert:
    """Base class for all libtorrent alerts (events/notifications).

    Alerts are libtorrent's event system for notifying the application about
    various occurrences such as torrent completion, tracker responses, errors,
    and peer events.

    Alert Categories:
    - error_notification: Error conditions
    - peer_notification: Peer connection events
    - tracker_notification: Tracker communication
    - storage_notification: Disk I/O events
    - progress_notification: Download progress updates
    - status_notification: Torrent status changes

    Example:
        # Process alerts in main loop
        alerts = session.pop_alerts()
        for alert in alerts:
            print(f"Alert: {alert.message()}")

            # Handle specific alert types
            if isinstance(alert, torrent_finished_alert):
                print(f"Torrent completed: {alert.torrent_name()}")
            elif isinstance(alert, tracker_error_alert):
                print(f"Tracker error: {alert.error_message}")
            elif isinstance(alert, file_completed_alert):
                print(f"File completed: {alert.index}")
    """
    def __init__(self) -> None: ...
    def message(self) -> str: ...
    def what(self) -> str: ...
    def category(self) -> int: ...
    @property
    def category_t(self) -> int: ...

class torrent_alert(alert):
    @property
    def handle(self) -> torrent_handle: ...
    @property
    def torrent_name(self) -> str: ...

class peer_alert(alert):
    ip: Any
    endpoint: Any
    pid: peer_id

class tracker_alert(alert):
    @property
    def url(self) -> str: ...
    def tracker_url(self) -> str: ...
    @property
    def local_endpoint(self) -> Any: ...

class session:
    """The main BitTorrent session managing all torrents and network operations.

    The session is the core component that handles all BitTorrent functionality including
    torrent management, peer connections, DHT operations, and alert generation.

    Features:
    - Manages multiple torrents simultaneously
    - Handles peer connections and protocol negotiation
    - Implements choking/unchoking algorithms
    - Manages DHT and tracker communication
    - Provides detailed statistics and monitoring
    - Supports rate limiting and bandwidth management

    Args:
        params: Optional session configuration parameters.
        flags: Session creation flags for enabling/disabling features.

    Example:
        # Create basic session
        ses = session()

        # Configure session settings
        settings = ses.get_settings()
        settings['download_rate_limit'] = 1000000  # 1 MB/s
        ses.apply_settings(settings)

        # Add torrent
        params = add_torrent_params()
        params.save_path = './downloads'
        params.ti = torrent_info('file.torrent')
        handle = ses.add_torrent(params)

        # Process alerts
        while True:
            alerts = ses.pop_alerts()
            for alert in alerts:
                if isinstance(alert, torrent_finished_alert):
                    print(f"Torrent finished: {alert.torrent_name()}")
    """
    def __init__(
        self, params: Optional[session_params] = None, flags: int = 0
    ) -> None: ...
    def add_torrent(self, params: add_torrent_params) -> torrent_handle:
        """Add a torrent to the session for downloading/seeding.

        Args:
            params: Configuration parameters for the torrent including save path,
                   torrent info, file priorities, and various flags.

        Returns:
            A handle to control and monitor the added torrent.

        Raises:
            May generate add_torrent_alert on completion with potential errors.

        Example:
            params = add_torrent_params()
            params.ti = torrent_info('file.torrent')
            params.save_path = './downloads'
            params.flags = torrent_flags.auto_managed

            handle = session.add_torrent(params)
        """
        ...
    def async_add_torrent(self, params: add_torrent_params) -> None: ...
    def remove_torrent(
        self, handle: torrent_handle, flags: int = 0
    ) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def is_paused(self) -> bool: ...
    def status(self) -> session_status: ...
    def get_torrents(self) -> List[torrent_handle]: ...
    def find_torrent(
        self, info_hash: Union[sha1_hash, info_hash_t]
    ) -> torrent_handle: ...
    def set_alert_mask(self, mask: int) -> None: ...
    def pop_alerts(self) -> List[alert]: ...
    def wait_for_alert(self, max_wait: int) -> Optional[alert]: ...
    def post_torrent_updates(self, flags: int = 0) -> None: ...
    def post_session_stats(self) -> None: ...
    def post_dht_stats(self) -> None: ...
    def set_settings(self, settings: Dict[str, Any]) -> None: ...
    def get_settings(self) -> Dict[str, Any]: ...
    def apply_settings(self, settings: Dict[str, Any]) -> None: ...
    def set_pe_settings(self, settings: Any) -> None: ...
    def get_pe_settings(self) -> Any: ...
    def set_proxy(self, proxy_settings: Any) -> None: ...
    def proxy(self) -> Any: ...
    def set_i2p_proxy(self, proxy_settings: Any) -> None: ...
    def i2p_proxy(self) -> Any: ...
    def set_dht_settings(self, settings: Any) -> None: ...
    def get_dht_settings(self) -> Any: ...
    def is_listening(self) -> bool: ...
    def listen_port(self) -> int: ...
    def ssl_listen_port(self) -> int: ...
    def listen_on(
        self, port_range: Any, interface: str = "", flags: int = 0
    ) -> None: ...
    def is_valid(self) -> bool: ...
    def save_state(self, flags: int = 0) -> bytes: ...
    def load_state(self, data: bytes, flags: int = 0) -> None: ...
    def set_ip_filter(self, filter: Any) -> None: ...
    def get_ip_filter(self) -> Any: ...
    def set_port_filter(self, filter: Any) -> None: ...
    def get_cache_info(
        self, handle: Optional[torrent_handle] = None, flags: int = 0
    ) -> Any: ...
    def get_cache_status(self) -> Any: ...
    def start_dht(self, state: Optional[bytes] = None) -> None: ...
    def stop_dht(self) -> None: ...
    def set_dht_state(self, state: bytes) -> None: ...
    def dht_state(self) -> bytes: ...
    def add_dht_router(self, router: Any) -> None: ...
    def start_lsd(self) -> None: ...
    def stop_lsd(self) -> None: ...
    def start_upnp(self) -> None: ...
    def stop_upnp(self) -> None: ...
    def start_natpmp(self) -> None: ...
    def stop_natpmp(self) -> None: ...
    def add_extension(self, ext: Any) -> None: ...
    def add_dht_node(self, node: Any) -> None: ...
    def add_port_mapping(
        self, protocol: int, external_port: int, local_port: int
    ) -> int: ...
    def create_peer_class(self, name: str) -> int: ...
    def delete_peer_class(self, class_id: int) -> None: ...
    def delete_port_mapping(self, handle: int) -> None: ...
    @property
    def delete_files(self) -> int: ...
    @property
    def delete_partfile(self) -> bool: ...
    def dht_announce(
        self, info_hash: sha1_hash, port: int = 0, flags: int = 0
    ) -> None: ...
    def dht_get_peers(self, info_hash: sha1_hash) -> None: ...
    def dht_get_immutable_item(self, target: sha1_hash) -> None: ...
    def dht_get_mutable_item(self, key: bytes, salt: str = "") -> None: ...
    def dht_put_immutable_item(self, data: bytes) -> sha1_hash: ...
    def dht_put_mutable_item(
        self,
        key: bytes,
        value: bytes,
        signature: bytes,
        seq: int,
        salt: str = "",
    ) -> None: ...
    def dht_live_nodes(self, info_hash: sha1_hash) -> None: ...
    def dht_sample_infohashes(
        self, endpoint: Any, target: sha1_hash
    ) -> None: ...
    def download_rate_limit(self) -> int: ...
    def set_download_rate_limit(self, bytes_per_second: int) -> None: ...
    def upload_rate_limit(self) -> int: ...
    def set_upload_rate_limit(self, bytes_per_second: int) -> None: ...
    def local_download_rate_limit(self) -> int: ...
    def set_local_download_rate_limit(self, bytes_per_second: int) -> None: ...
    def local_upload_rate_limit(self) -> int: ...
    def set_local_upload_rate_limit(self, bytes_per_second: int) -> None: ...
    def max_connections(self) -> int: ...
    def set_max_connections(self, limit: int) -> None: ...
    def set_max_uploads(self, limit: int) -> None: ...
    def set_max_half_open_connections(self, limit: int) -> None: ...
    def num_connections(self) -> int: ...
    def set_peer_id(self, peer_id: peer_id) -> None: ...
    def id(self) -> int: ...
    def is_dht_running(self) -> bool: ...
    def set_dht_proxy(self, proxy_settings: Any) -> None: ...
    def dht_proxy(self) -> Any: ...
    def set_peer_proxy(self, proxy_settings: Any) -> None: ...
    def peer_proxy(self) -> Any: ...
    def set_web_seed_proxy(self, proxy_settings: Any) -> None: ...
    def web_seed_proxy(self) -> Any: ...
    def set_tracker_proxy(self, proxy_settings: Any) -> None: ...
    def tracker_proxy(self) -> Any: ...
    def set_peer_class_filter(self, filter: Any) -> None: ...
    def set_peer_class_type_filter(self, filter: Any) -> None: ...
    def set_peer_class(self, class_id: int, info: Any) -> None: ...
    def get_peer_class(self, class_id: int) -> Any: ...
    @property
    def global_peer_class_id(self) -> int: ...
    @property
    def tcp_peer_class_id(self) -> int: ...
    @property
    def local_peer_class_id(self) -> int: ...
    def set_alert_notify(self, fun: Callable[[], None]) -> None: ...
    def set_alert_fd(self, fd: int) -> None: ...
    def set_alert_queue_size_limit(self, queue_size_limit_kb: int) -> None: ...
    def reopen_network_sockets(self, options: int = 0) -> None: ...
    @property
    def reopen_map_ports(self) -> int: ...
    def get_torrent_status(
        self, pred: Any, flags: int = 0
    ) -> List[torrent_status]: ...
    def refresh_torrent_status(
        self, torrents: List[torrent_handle], flags: int = 0
    ) -> None: ...
    outgoing_ports: Any = ...
    tcp: int = ...
    udp: int = ...

def bdecode(data: bytes) -> Any:
    """Decode bencoded data into Python objects.

    Bencoding is the encoding used by the BitTorrent protocol for .torrent files
    and tracker communication.

    Args:
        data: Raw bencoded bytes to decode.

    Returns:
        Decoded Python object (dict, list, int, or bytes).

    Raises:
        bdecode_error: If the data is not valid bencoded format.

    Example:
        # Decode .torrent file
        with open('file.torrent', 'rb') as f:
            torrent_data = bdecode(f.read())

        print(f"Torrent name: {torrent_data[b'info'][b'name']}")
        print(f"Announce URL: {torrent_data[b'announce']}")
    """
    ...
def bencode(data: Any) -> bytes:
    """Encode Python objects into bencoded format.

    Converts Python data structures into the bencoded format used by BitTorrent.

    Args:
        data: Python object to encode (dict, list, int, bytes, or str).

    Returns:
        Bencoded bytes representation.

    Example:
        # Create torrent-like structure
        torrent_dict = {
            b'announce': b'http://tracker.example.com/announce',
            b'info': {
                b'name': b'example.txt',
                b'length': 12345,
                b'piece length': 262144
            }
        }

        encoded = bencode(torrent_dict)
        with open('new.torrent', 'wb') as f:
            f.write(encoded)
    """
    ...
@overload
def make_magnet_uri(handle: torrent_handle) -> str:
    """Generate a magnet link from a torrent handle.

    Creates a magnet URI that can be used to download the same torrent
    without needing the original .torrent file.

    Args:
        handle: Active torrent handle to generate magnet link for.

    Returns:
        Magnet URI string containing info hash, name, and trackers.

    Example:
        magnet = make_magnet_uri(handle)
        print(magnet)
        # Output: magnet:?xt=urn:btih:1234567890abcdef&dn=filename&tr=http://tracker...
    """
    ...
@overload
def make_magnet_uri(info: torrent_info) -> str: ...
def parse_magnet_uri(uri: str) -> Dict[str, Any]:
    """Parse a magnet URI into its components.

    Extracts information from a magnet link including info hash, display name,
    tracker URLs, and web seeds.

    Args:
        uri: Magnet URI string to parse.

    Returns:
        Dictionary containing parsed magnet link components.

    Example:
        magnet = "magnet:?xt=urn:btih:abc123&dn=file.txt&tr=http://tracker.com"
        info = parse_magnet_uri(magnet)

        print(f"Info hash: {info['info_hash']}")
        print(f"Name: {info.get('name', 'Unknown')}")
        print(f"Trackers: {info.get('trackers', [])}")
    """
    ...
def parse_magnet_uri_dict(
    uri: str, params: add_torrent_params
) -> error_code: ...
def load_torrent_file(filename: str) -> torrent_info: ...
def load_torrent_buffer(buffer: bytes) -> torrent_info: ...
def load_torrent_parsed(dict_data: Dict[str, Any]) -> torrent_info: ...
def set_piece_hashes(ct: Any, path: str) -> None: ...
def add_files(fs: file_storage, path: str, flags: int = 0) -> None: ...
def write_resume_data(params: add_torrent_params) -> bytes: ...
def write_resume_data_buf(params: add_torrent_params) -> bytes: ...
def read_resume_data(data: bytes) -> add_torrent_params: ...
def write_session_params(params: session_params) -> bytes: ...
def write_session_params_buf(params: session_params) -> bytes: ...
def read_session_params(data: bytes) -> session_params: ...
def identify_client(peer_id: peer_id) -> str: ...
def client_fingerprint(
    name: str, major: int, minor: int, revision: int, tag: int
) -> peer_id: ...
def generate_fingerprint(
    name: str, major: int, minor: int = 0, revision: int = 0, tag: int = 0
) -> peer_id: ...
def high_performance_seed(settings: Dict[str, Any]) -> Dict[str, Any]: ...
def min_memory_usage(settings: Dict[str, Any]) -> Dict[str, Any]: ...
def default_settings() -> Dict[str, Any]: ...
def add_magnet_uri(
    session: session, uri: str, params: Optional[add_torrent_params] = None
) -> torrent_handle:
    """Add a torrent to the session using a magnet URI.

    Convenience function to add a torrent from a magnet link, automatically
    parsing the URI and creating appropriate add_torrent_params.

    Args:
        session: Session to add the torrent to.
        uri: Magnet URI string.
        params: Optional additional parameters (save_path, flags, etc.).
                If None, default parameters will be used.

    Returns:
        Handle to the added torrent.

    Example:
        # Simple magnet add
        magnet = "magnet:?xt=urn:btih:abc123&dn=file.txt"
        handle = add_magnet_uri(session, magnet)

        # Add with custom save path
        params = add_torrent_params()
        params.save_path = './downloads/magnets'
        handle = add_magnet_uri(session, magnet, params)
    """
    ...
def write_torrent_file(ct: Any, filename: str) -> None: ...
def write_torrent_file_buf(ct: Any) -> bytes: ...
def operation_name(op: int) -> str: ...

class add_piece_flags_t:
    overwrite_existing: int

class add_torrent_params_flags_t:
    default_flags: int
    flag_apply_ip_filter: int
    flag_auto_managed: int
    flag_duplicate_is_error: int
    flag_merge_resume_http_seeds: int
    flag_merge_resume_trackers: int
    flag_override_resume_data: int
    flag_override_trackers: int
    flag_override_web_seeds: int
    flag_paused: int
    flag_pinned: int
    flag_seed_mode: int
    flag_sequential_download: int
    flag_share_mode: int
    flag_stop_when_ready: int
    flag_super_seeding: int
    flag_update_subscribe: int
    flag_upload_mode: int
    flag_use_resume_save_path: int

class bandwidth_mixed_algo_t:
    names: List[str]
    peer_proportional: int
    prefer_tcp: int
    values: List[int]

class choking_algorithm_t:
    auto_expand_choker: int
    bittyrant_choker: int
    fixed_slots_choker: int
    names: List[str]
    rate_based_choker: int
    values: List[int]

class create_torrent_flags_t:
    merkle: int
    modification_time: int
    optimize: int
    optimize_alignment: int
    symlinks: int
    v2_only: int

class deadline_flags_t:
    alert_when_available: int

class deprecated_move_flags_t:
    always_replace_files: int
    dont_replace: int
    fail_if_exist: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class enc_level:
    both: int
    names: List[str]
    pe_both: int
    pe_plaintext: int
    pe_rc4: int
    plaintext: int
    rc4: int
    values: List[int]

class enc_policy:
    disabled: int
    enabled: int
    forced: int
    names: List[str]
    pe_disabled: int
    pe_enabled: int
    pe_forced: int
    values: List[int]

class event_t:
    completed: int
    names: List[str]
    none: int
    paused: int
    started: int
    stopped: int
    values: List[int]

class file_flags_t:
    flag_executable: int
    flag_hidden: int
    flag_pad_file: int
    flag_symlink: int

class file_open_mode:
    locked: int
    mmapped: int
    no_atime: int
    random_access: int
    read_only: int
    read_write: int
    rw_mask: int
    sparse: int
    write_only: int

class file_progress_flags_t:
    piece_granularity: int

class fingerprint:
    def __init__(
        self, id: str, major: int, minor: int, revision: int, tag: int
    ) -> None: ...
    id: str
    major_version: int
    minor_version: int
    revision_version: int
    tag_version: int

class io_buffer_mode_t:
    disable_os_cache: int
    disable_os_cache_for_aligned_files: int
    enable_os_cache: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]
    write_through: int

class kind:
    names: List[str]
    tracker_no_anonymous: int
    values: List[int]

class listen_failed_alert_socket_type_t:
    i2p: int
    names: List[str]
    socks5: int
    tcp: int
    tcp_ssl: int
    udp: int
    utp_ssl: int
    values: List[int]

class listen_on_flags_t:
    listen_no_system_port: int
    listen_reuse_address: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class listen_succeeded_alert_socket_type_t:
    i2p: int
    names: List[str]
    socks5: int
    tcp: int
    tcp_ssl: int
    udp: int
    utp_ssl: int
    values: List[int]

class metric_type_t:
    counter: int
    gauge: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class mmap_write_mode_t:
    always_mmap_write: int
    always_pwrite: int
    auto_mmap_write: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class operation_t:
    alloc_cache_piece: int
    alloc_recvbuf: int
    alloc_sndbuf: int
    available: int
    bittorrent: int
    check_resume: int
    connect: int
    encryption: int
    enum_if: int
    exception: int
    file_copy: int
    file_fallocate: int
    file_ftruncate: int
    file_hard_link: int
    file_mmap: int
    file_move: int
    file_open: int
    file_partfile_move: int
    file_partfile_read: int
    file_partfile_write: int
    file_read: int
    file_remove: int
    file_rename: int
    file_seek: int
    file_stat: int
    file_sync: int
    file_write: int
    getname: int
    getpeername: int
    handshake: int
    hostname_lookup: int
    iocontrol: int
    mkdir: int
    partfile_move: int
    partfile_read: int
    partfile_write: int
    sock_accept: int
    sock_bind: int
    sock_iocontrol: int
    sock_listen: int
    sock_open: int
    sock_option: int
    sock_read: int
    sock_write: int
    unknown: int
    file: int
    get_interface: int
    parse_address: int
    sock_bind_to_device: int
    ssl_handshake: int
    symlink: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class options_t:
    delete_files: int
    delete_partfile: int

class pe_settings:
    def __init__(self) -> None: ...
    enc_policy: int
    in_enc_policy: int
    out_enc_policy: int
    allowed_enc_level: int
    prefer_rc4: bool

class peer_class_type_filter_socket_type_t:
    i2p_socket: int
    names: List[str]
    socks5_socket: int
    tcp_socket: int
    utp_socket: int
    values: List[int]

class portmap_protocol:
    natpmp: int
    upnp: int
    none: int
    tcp: int
    udp: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class portmap_transport:
    natpmp: int
    upnp: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class protocol_type:
    i2p: int
    socks5: int
    tcp: int
    udp: int

class protocol_version:
    V1: int
    V2: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class proxy_type_t:
    http: int
    http_pw: int
    i2p_proxy: int
    none: int
    socks4: int
    socks5: int
    socks5_pw: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class reason_t:
    fast_reconnect: int
    peer_self: int
    optimistic_unchoke: int
    tracker: int
    incoming: int
    port_forwarding: int
    peer_exchange: int
    dht: int
    lsd: int
    resume_data: int
    i2p_mixed: int
    invalid_local_interface: int
    ip_filter: int
    port_filter: int
    privileged_ports: int
    tcp_disabled: int
    utp_disabled: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class seed_choking_algorithm_t:
    anti_leech: int
    fastest_upload: int
    round_robin: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class socket_type_t:
    i2p: int
    socks5: int
    tcp: int
    tcp_ssl: int
    udp: int
    utp_ssl: int
    http: int
    http_ssl: int
    socks5_ssl: int
    utp: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class stats_channel:
    upload_ip_protocol: int
    upload_dht_protocol: int
    upload_tracker_protocol: int
    download_ip_protocol: int
    download_dht_protocol: int
    download_tracker_protocol: int
    download_payload: int
    download_protocol: int
    upload_payload: int
    upload_protocol: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class stats_metric:
    def __init__(self, name: str, value_index: int, type: int) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def value_index(self) -> int: ...
    @property
    def type(self) -> int: ...

class status_flags_t:
    query_distributed_copies: int
    query_last_seen_complete: int
    query_pieces: int
    query_verified_pieces: int
    query_torrent_file: int
    query_name: int
    query_save_path: int
    query_accurate_download_counters: int

class storage_mode_t:
    storage_mode_allocate: int
    storage_mode_sparse: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class suggest_mode_t:
    no_piece_suggestions: int
    suggest_read_cache: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class tracker_source:
    source_dht: int
    source_lsd: int
    source_pex: int
    source_router: int
    source_tracker: int
    source_client: int
    source_magnet_link: int
    source_tex: int
    source_torrent: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class write_flags:
    allow_missing_piece_layer: int
    include_dht_nodes: int
    no_http_seeds: int

class torrent_flags:
    seed_mode: int
    upload_mode: int
    share_mode: int
    apply_ip_filter: int
    paused: int
    auto_managed: int
    duplicate_is_error: int
    merge_resume_trackers: int
    update_subscribe: int
    super_seeding: int
    sequential_download: int
    pinned: int
    stop_when_ready: int
    override_trackers: int
    override_web_seeds: int
    need_save_resume: int
    disable_dht: int
    disable_lsd: int
    disable_pex: int
    default_dont_download: int
    default_flags: int
    no_verify_files: int

class session_flags_t:
    add_default_plugins: int
    start_default_features: int

class alert_category:
    error_notification: int
    peer_notification: int
    port_mapping_notification: int
    storage_notification: int
    tracker_notification: int
    debug_notification: int
    status_notification: int
    progress_notification: int
    ip_block_notification: int
    performance_warning: int
    dht_notification: int
    stats_notification: int
    session_log_notification: int
    torrent_log_notification: int
    peer_log_notification: int
    incoming_request_notification: int
    dht_log_notification: int
    dht_operation_notification: int
    port_mapping_log_notification: int
    picker_log_notification: int
    file_progress_notification: int
    piece_progress_notification: int
    upload_notification: int
    block_progress_notification: int
    all: int
    block_progress: int
    connect: int
    dht: int
    dht_log: int
    dht_operation: int
    error: int
    file_progress: int
    incoming_request: int
    ip_block: int
    peer: int
    peer_log: int
    picker_log: int
    piece_progress: int
    port_mapping: int
    port_mapping_log: int
    session_log: int
    stats: int
    status: int
    storage: int
    torrent_log: int
    tracker: int
    upload: int

class save_resume_flags_t:
    flush_disk_cache: int
    save_info_dict: int
    only_if_modified: int

class reannounce_flags_t:
    ignore_min_interval: int

class pause_flags_t:
    graceful_pause: int

class move_flags_t:
    always_replace_files: int
    fail_if_exist: int
    dont_replace: int
    names: Dict[Any, Any]
    values: Dict[Any, Any]

class add_torrent_alert(torrent_alert):
    @property
    def params(self) -> add_torrent_params: ...
    @property
    def error(self) -> error_code: ...

class torrent_added_alert(torrent_alert): ...
class torrent_removed_alert(torrent_alert): ...
class torrent_finished_alert(torrent_alert): ...
class torrent_paused_alert(torrent_alert): ...
class torrent_resumed_alert(torrent_alert): ...
class torrent_checked_alert(torrent_alert): ...

class read_piece_alert(torrent_alert):
    @property
    def piece(self) -> int: ...
    @property
    def buffer(self) -> bytes: ...
    @property
    def size(self) -> int: ...
    @property
    def error(self) -> error_code: ...

class file_completed_alert(torrent_alert):
    index: int

class file_renamed_alert(torrent_alert):
    index: int
    name: str
    new_name: str
    old_name: str

class file_rename_failed_alert(torrent_alert):
    index: int
    error: error_code

class state_changed_alert(torrent_alert):
    prev_state: int
    state: int

class tracker_error_alert(torrent_alert):
    @property
    def times_in_row(self) -> int: ...
    @property
    def status_code(self) -> int: ...
    @property
    def error(self) -> error_code: ...
    error_message: str
    @property
    def url(self) -> str: ...

class tracker_warning_alert(torrent_alert):
    url: str
    warning_message: str

class tracker_reply_alert(torrent_alert):
    num_peers: int
    url: str

class tracker_announce_alert(torrent_alert):
    url: str
    event: int

class hash_failed_alert(torrent_alert):
    piece_index: int

class invalid_request_alert(peer_alert):
    request: peer_request

class piece_finished_alert(torrent_alert):
    piece_index: int

class save_resume_data_alert(torrent_alert):
    params: add_torrent_params

class save_resume_data_failed_alert(torrent_alert):
    error: error_code

class storage_moved_alert(torrent_alert):
    storage_path: str

class storage_moved_failed_alert(torrent_alert):
    error: error_code
    file_path: str

class torrent_deleted_alert(torrent_alert):
    info_hashes: info_hash_t

class torrent_delete_failed_alert(torrent_alert):
    error: error_code
    info_hashes: info_hash_t

class metadata_failed_alert(torrent_alert):
    error: error_code

class metadata_received_alert(torrent_alert): ...

class udp_error_alert(alert):
    endpoint: Any
    error: error_code

class unwanted_block_alert(peer_alert):
    block_index: int
    piece_index: int

class url_seed_alert(torrent_alert):
    @property
    def url(self) -> str: ...
    @property
    def error(self) -> error_code: ...
    @property
    def msg(self) -> str: ...
    server_url: str

class request_dropped_alert(peer_alert):
    block_index: int
    piece_index: int

class block_downloading_alert(peer_alert):
    block_index: int
    piece_index: int
    peer_speedmsg: str

class block_finished_alert(peer_alert):
    block_index: int
    piece_index: int

class block_timeout_alert(peer_alert):
    block_index: int
    piece_index: int

class block_uploaded_alert(peer_alert):
    block_index: int
    piece_index: int

class alerts_dropped_alert(alert):
    dropped_alerts: int

class anonymous_mode_alert(torrent_alert):
    kind: int
    str: str

class cache_flushed_alert(torrent_alert): ...
class dht_bootstrap_alert(alert): ...

class dht_get_peers_alert(alert):
    info_hash: sha1_hash

class dht_get_peers_reply_alert(alert):
    info_hash: sha1_hash
    num_peers: int
    peers: List[Any]

class dht_immutable_item_alert(alert):
    target: sha1_hash
    item: bytes

class dht_live_nodes_alert(alert):
    node_id: sha1_hash
    nodes: List[Any]
    num_nodes: int

class dht_log_alert(alert):
    log_message: str
    module: str

class dht_mutable_item_alert(alert):
    @property
    def key(self) -> bytes: ...
    @property
    def signature(self) -> bytes: ...
    @property
    def seq(self) -> int: ...
    @property
    def salt(self) -> str: ...
    @property
    def item(self) -> bytes: ...
    @property
    def authoritative(self) -> bool: ...

class dht_outgoing_get_peers_alert(alert):
    @property
    def info_hash(self) -> sha1_hash: ...
    @property
    def obfuscated_info_hash(self) -> sha1_hash: ...
    @property
    def endpoint(self) -> Any: ...
    @property
    def ip(self) -> Any: ...

class dht_pkt_alert(alert):
    pkt_buf: bytes
    direction: str
    node: Any

class dht_put_alert(alert):
    @property
    def target(self) -> sha1_hash: ...
    @property
    def public_key(self) -> bytes: ...
    @property
    def signature(self) -> bytes: ...
    @property
    def salt(self) -> str: ...
    @property
    def seq(self) -> int: ...
    @property
    def num_success(self) -> int: ...

class dht_sample_infohashes_alert(alert):
    @property
    def endpoint(self) -> Any: ...
    @property
    def interval(self) -> int: ...
    @property
    def num_infohashes(self) -> int: ...
    @property
    def num_nodes(self) -> int: ...
    @property
    def samples(self) -> List[sha1_hash]: ...
    @property
    def nodes(self) -> List[Any]: ...
    @property
    def num_samples(self) -> int: ...

class dht_stats_alert(alert):
    active_requests: List[Any]
    routing_table: List[Any]

class external_ip_alert(alert):
    external_address: Any

class fastresume_rejected_alert(torrent_alert):
    @property
    def error(self) -> error_code: ...
    file_path: str
    @property
    def msg(self) -> str: ...
    @property
    def op(self) -> str: ...
    @property
    def operation(self) -> str: ...

class file_error_alert(torrent_alert):
    file: str
    error: error_code
    operation: int
    filename: str
    msg: str

class i2p_alert(alert):
    error: error_code

class incoming_connection_alert(alert):
    socket_type: int
    endpoint: Any

class listen_failed_alert(alert):
    @property
    def endpoint(self) -> Any: ...
    @property
    def error(self) -> error_code: ...
    @property
    def operation(self) -> int: ...
    @property
    def socket_type(self) -> int: ...
    @property
    def address(self) -> str: ...
    @property
    def op(self) -> str: ...
    @property
    def port(self) -> int: ...
    @property
    def sock_type(self) -> int: ...
    listen_interface: str

class listen_succeeded_alert(alert):
    @property
    def endpoint(self) -> Any: ...
    @property
    def socket_type(self) -> int: ...
    @property
    def address(self) -> str: ...
    @property
    def port(self) -> int: ...
    @property
    def sock_type(self) -> int: ...

class log_alert(alert):
    log_message: str
    msg: str

class lsd_error_alert(alert):
    error: error_code

class oversized_file_alert(torrent_alert):
    filename: str

class peer_ban_alert(peer_alert):
    banned_ip: Any

class peer_blocked_alert(torrent_alert):
    endpoint: Any
    reason: int

class peer_connect_alert(peer_alert):
    socket_type: int

class peer_disconnected_alert(peer_alert):
    error: error_code
    reason: int

class peer_error_alert(peer_alert):
    error: error_code

class peer_log_alert(peer_alert):
    direction: str
    event_type: str
    log_message: str

class peer_snubbed_alert(peer_alert): ...
class peer_unsnubbed_alert(peer_alert): ...

class performance_alert(torrent_alert):
    warning_code: int

class picker_log_alert(peer_alert):
    picker_flags: int
    blocks: List[Any]

class portmap_alert(alert):
    mapping: int
    external_port: int
    map_type: int

class portmap_error_alert(alert):
    @property
    def mapping(self) -> int: ...
    @property
    def map_type(self) -> int: ...
    @property
    def error(self) -> error_code: ...

class portmap_log_alert(alert):
    map_type: int
    log_message: str

class scrape_failed_alert(torrent_alert):
    url: str
    error: error_code
    error_message: str

class scrape_reply_alert(torrent_alert):
    @property
    def incomplete(self) -> int: ...
    @property
    def complete(self) -> int: ...
    @property
    def url(self) -> str: ...

class session_error_alert(alert):
    error: error_code

class session_stats_header_alert(alert):
    stats_header: List[str]

class socks5_alert(alert):
    error: error_code
    operation: int
    endpoint: Any

class stats_alert(torrent_alert):
    transferred: List[int]
    interval: int

class torrent_conflict_alert(torrent_alert):
    metadata: bytes

class torrent_error_alert(torrent_alert):
    error: error_code
    filename: str

class torrent_log_alert(torrent_alert):
    log_message: str

class torrent_need_cert_alert(torrent_alert):
    error: error_code

class tracker_list_alert(torrent_alert):
    trackers: List[Any]

class session_stats_alert(alert):
    values: List[int]

class state_update_alert(alert):
    status: List[torrent_status]

class dht_announce_alert(alert):
    info_hash: sha1_hash
    port: int

class dht_reply_alert(alert):
    info_hash: sha1_hash

class file_prio_alert(torrent_alert):
    file_index: int
    priority: int

class file_progress_alert(torrent_alert):
    file_index: int

class create_torrent:
    @overload
    def __init__(
        self, ti: torrent_info, piece_size: int = 0, flags: int = 0
    ) -> None: ...
    @overload
    def __init__(
        self, fs: file_storage, piece_size: int = 0, flags: int = 0
    ) -> None: ...
    def generate(self) -> Dict[str, Any]: ...
    def files(self) -> file_storage: ...
    def set_comment(self, comment: str) -> None: ...
    def set_creator(self, creator: str) -> None: ...
    def set_hash(self, piece: int, hash: sha1_hash) -> None: ...
    def set_file_hash(self, file: int, hash: sha1_hash) -> None: ...
    def add_url_seed(self, url: str) -> None: ...
    def add_http_seed(self, url: str) -> None: ...
    def add_tracker(self, url: str, tier: int = 0) -> None: ...
    def set_priv(self, priv: bool) -> None: ...
    def num_pieces(self) -> int: ...
    def piece_length(self) -> int: ...
    def piece_size(self, piece: int) -> int: ...
    def priv(self) -> bool: ...
    def add_collection(self, collection: str) -> None: ...
    def add_node(self, hostname: str, port: int) -> None: ...
    def add_similar_torrent(self, info_hash: sha1_hash) -> None: ...
    def generate_buf(self) -> bytes: ...
    def set_root_cert(self, cert: str) -> None: ...
    canonical_files: int
    canonical_files_no_tail_padding: int
    merkle: int
    modification_time: int
    no_attributes: int
    optimize_alignment: int
    symlinks: int
    v1_only: int
    v2_only: int

create_smart_ban_plugin: Any
create_ut_metadata_plugin: Any
create_ut_pex_plugin: Any

def session_stats_metrics() -> List[str]: ...
def find_metric_idx(name: str) -> int: ...

class ip_filter:
    def __init__(self) -> None: ...
    def add_rule(self, first: str, last: str, flags: int) -> None: ...
    def access(self, addr: str) -> int: ...

class dht_settings:
    def __init__(self) -> None: ...
    max_peers_reply: int
    search_branching: int
    max_fail_count: int
    max_torrents: int
    max_dht_items: int
    max_peers: int
    max_torrent_search_reply: int
    restrict_routing_ips: bool
    restrict_search_ips: bool
    extended_routing_table: bool
    aggressive_lookups: bool
    privacy_lookups: bool
    enforce_node_id: bool
    ignore_dark_internet: bool
    block_timeout: int
    block_ratelimit: int
    read_only: bool
    item_lifetime: int
    sample_infohashes_interval: int
    max_infohashes_sample_count: int

class dht_state:
    def __init__(self) -> None: ...
    nodes: List[Any]
    node_ids: List[bytes]
    nids: List[bytes]
    nodes6: List[Any]

class open_file_state:
    def __init__(self) -> None: ...
    file_index: int
    last_use: int
    open_mode: int

class error_category:
    def __init__(self) -> None: ...
    def name(self) -> str: ...
    def message(self, value: int) -> str: ...

class save_state_flags_t:
    save_settings: int
    save_dht_settings: int
    save_dht_state: int
    save_encryption_settings: int
    save_as_map: int
    save_dht_proxy: int
    save_i2p_proxy: int
    save_peer_proxy: int
    save_proxy: int
    save_tracker_proxy: int
    save_web_proxy: int

def get_libtorrent_category() -> Any: ...
def get_http_category() -> Any: ...
def get_socks_category() -> Any: ...
def get_upnp_category() -> Any: ...
def get_i2p_category() -> Any: ...
def get_bdecode_category() -> Any: ...
def system_category() -> Any: ...
def generic_category() -> Any: ...

libtorrent_category: Any
http_category: Any
socks_category: Any
upnp_category: Any
i2p_category: Any
bdecode_category: Any
