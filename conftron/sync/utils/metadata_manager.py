import datetime
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from conftron.sync.utils.cbor_b85 import CBORb85


@dataclass
class SyncMetadata:
    device_id: str
    timestamp: float
    targets: list[dict[str, str]] | None = None

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

    def to_dict(self):
        return {"device_id": self.device_id, "datetime": self.datetime.isoformat(), "timestamp": self.timestamp}


class MetadataManager:
    @staticmethod
    def generate() -> SyncMetadata:
        return SyncMetadata(
            device_id=str(uuid.uuid1(uuid.getnode(), 0))[24:], timestamp=datetime.datetime.now().timestamp()
        )

    @staticmethod
    def serialize(metadata: SyncMetadata):
        return CBORb85.dumps(asdict(metadata))

    @staticmethod
    def deserialize(data: str):
        return SyncMetadata(**CBORb85.loads(data))

    @classmethod
    def read(cls, path: Path):
        result = None

        if path.is_file():
            with open(str(path)) as f:
                result = cls.deserialize(f.read())

        return result

    @classmethod
    def write(cls, path: Path, metadata: SyncMetadata):
        data = cls.serialize(metadata)

        with open(str(path), "w+") as f:
            f.write(data)
