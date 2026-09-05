"""ta5py: SGB V TA5/EDIFACT encode, decode, and syntactic KK validation."""

from ta5py.decode import decode
from ta5py.encode import encode, encode_slga_wire
from ta5py.kostentraeger import ingest_kostentraeger_file, load_store
from ta5py.spec_loader import DEFAULT_VERSION, get_default_version, load_package
from ta5py.validate_syntax import validate_slga, validate_syntax, validate_wire_segment_order

__all__ = [
    "DEFAULT_VERSION",
    "decode",
    "encode",
    "encode_slga_wire",
    "get_default_version",
    "ingest_kostentraeger_file",
    "load_package",
    "load_store",
    "validate_slga",
    "validate_syntax",
    "validate_wire_segment_order",
]
