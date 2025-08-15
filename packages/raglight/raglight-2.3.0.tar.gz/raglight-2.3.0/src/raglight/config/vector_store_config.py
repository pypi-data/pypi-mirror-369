from dataclasses import dataclass, field

from ..config.settings import Settings


@dataclass(kw_only=True)
class VectorStoreConfig:
    embedding_model: str
    persist_directory: str
    api_base: str = field(default=Settings.DEFAULT_OLLAMA_CLIENT)
    provider: str = field(default=Settings.HUGGINGFACE)
    database: str = field(default=Settings.CHROMA)
    collection_name: str = field(default=Settings.DEFAULT_COLLECTION_NAME)
    ignore_folders: list = field(
        default_factory=lambda: list(Settings.DEFAULT_IGNORE_FOLDERS)
    )
