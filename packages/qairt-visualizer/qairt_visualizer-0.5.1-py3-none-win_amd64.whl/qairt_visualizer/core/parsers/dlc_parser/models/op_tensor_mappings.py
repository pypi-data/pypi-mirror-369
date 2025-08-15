# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Model for op / tensor mappings data"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class MappingGroup(BaseModel):
    """
    Class defining a basic op / tensor mapping list
    """

    ops: List[str]
    tensors: List[str]


class OpTensorMappings(BaseModel):
    """
    Class defining the various op / tensor mapping relationships
    """

    dlc_ops_to_target_ops: Dict[str, MappingGroup]
    target_ops_to_dlc_ops: Dict[str, MappingGroup]
    dlc_tensors_to_target_tensors: Dict[str, MappingGroup]
    target_tensors_to_dlc_tensors: Dict[str, MappingGroup]


class DlcOpTensorMappings(BaseModel):
    """
    Class defining the top-level source and backend mappings
    """

    dlc_model_path: str
    # source_model_path and backend_model_path cannot be set until phase 2
    source_model_path: Optional[str] = None
    source_mappings: Optional[OpTensorMappings]
    backend_model_path: Optional[str] = None
    backend_mappings: Optional[OpTensorMappings]
