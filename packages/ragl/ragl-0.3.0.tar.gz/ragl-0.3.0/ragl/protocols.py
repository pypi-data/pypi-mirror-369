"""
Protocol definitions for ragl components.

This module defines the core protocols that establish contracts
for different components in the ragl system, including text
embedding, vector storage, text retrieval, and tokenization
operations.

Classes:
    EmbedderProtocol:
        Protocol for text embedding operations.
    VectorStoreProtocol:
        Protocol for vector storage operations.
    RAGStoreProtocol:
        Protocol for text retrieval and storage.
    TokenizerProtocol:
        Protocol for text tokenization operations.
"""

from typing import (
    Any,
    Protocol,
    runtime_checkable,
)

import numpy as np

from ragl.textunit import TextUnit

__all__ = (
    'EmbedderProtocol',
    'RAGStoreProtocol',
    'TokenizerProtocol',
    'VectorStoreProtocol',
)


@runtime_checkable
class EmbedderProtocol(Protocol):
    """
    Protocol for text embedding.

    Defines methods for embedding text into vectors.
    """

    @property
    def dimensions(self) -> int:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def embed(self, text: str) -> np.ndarray:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover


@runtime_checkable
class VectorStoreProtocol(Protocol):
    """
    Protocol for vector store operations.

    Defines methods for storing and retrieving vectors.
    """

    def clear(self) -> None:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def delete_text(self, text_id: str) -> bool:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def get_relevant(
            self,
            embedding: np.ndarray,
            top_k: int,
            *,
            min_time: int | None,
            max_time: int | None,
    ) -> list[TextUnit]:  # noqa: D102
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def health_check(self) -> dict[str, Any]:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def list_texts(self) -> list[str]:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def store_text(self, text_unit: TextUnit, embedding: np.ndarray) -> str:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover


@runtime_checkable
class RAGStoreProtocol(Protocol):
    """
    Protocol for text retrieval.

    Defines methods for storing and retrieving text.
    """

    embedder: EmbedderProtocol
    storage: VectorStoreProtocol

    def clear(self) -> None:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def delete_text(self, text_id: str) -> bool:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def get_relevant(
            self,
            query: str,
            top_k: int,
            *,
            min_time: int | None,
            max_time: int | None,
    ) -> list[TextUnit]:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def list_texts(self) -> list[str]:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def store_text(self, text_unit: TextUnit) -> TextUnit:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover


@runtime_checkable
class TokenizerProtocol(Protocol):
    """
    Protocol for text tokenization.

    Defines methods for encoding and decoding text.
    """

    def decode(self, tokens: list[int]) -> str:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover

    def encode(self, text: str) -> list[int]:
        # pylint: disable=missing-function-docstring
        ...  # pragma: no cover
