# =============================================================
# FILE: iqore/__init__.py
# Purpose: Clean import interface for iQore SDK
# =============================================================

from .service import iQoreRuntimeService
# from .iQD import api as iQD  # We’ll enable this once injection logic is ready

__all__ = ["iQoreRuntimeService"]

