# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""Adapter implementations for Thoth Qdrant."""

from .qdrant_native import QdrantNativeAdapter

__all__ = ["QdrantNativeAdapter"]