# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""DLC Parser class"""

import os
from typing import Any, Dict, Optional, Set

from qairt_visualizer.core.errors import ArgumentError
from qairt_visualizer.core.parsers.dlc_parser.models.op_tensor_mappings import (  # type: ignore
    DlcOpTensorMappings,
    MappingGroup,
    OpTensorMappings,
)

# pylint: disable=no-name-in-module
from . import libDlModelToolsPy as modeltools  # type: ignore
from . import libPyIrGraph as ir_graph  # type: ignore

# pylint: enable=no-name-in-module

# This import is not directly referenced but must
# still be imported for modeltools to work
_ = ir_graph

OP = 1
OPS_KEY = "ops"
TENSOR = 0
TENSOR_KEY = "tensors"


class DlcParser:
    """DLC Parser and Utility Functions"""

    def __init__(self, dlc_path: str):
        self.validate_dlc_file(dlc_path)
        self.dlc_path = dlc_path
        self.model_reader = modeltools.IrDlcReader()
        self.model_reader.open(dlc_path)

    def validate_dlc_file(self, dlc_file_path: str) -> None:
        """
        Validates that an input file is a DLC file
        :param dlc_file_path: Path to the desired DLC file to open
        """

        if not dlc_file_path:
            raise ArgumentError("A valid DLC file argument is required")
        if not os.path.isfile(dlc_file_path):
            raise FileNotFoundError(f"The input file path {dlc_file_path} does not exist")
        if not os.path.splitext(dlc_file_path)[1] == ".dlc":
            raise ValueError(f"The specified file {dlc_file_path} is not a DLC file")

    def extract_onnx_mappings(self) -> DlcOpTensorMappings:
        """
        Creates a JSON serializable map of DLC ops and tensors to source,
        and source model ops and tensors back to DLC
        :param op_trace: The list of DLC trace objects containing the source ops
        :param tensor_trace: The list of DLC tensor trace objects containing the source tensors
        :return: Two dictionaries containing the map of DLC to source ops/tensors and source to
        DLC ops/tensors
        """

        graph = self.get_ir_graph(self.model_reader)
        op_source = graph.get_trace_info().get_op_trace_info()
        tensor_source = graph.get_trace_info().get_tensor_trace_info()

        return DlcOpTensorMappings(
            dlc_model_path=self.dlc_path,
            source_mappings=self._extract_onnx_mappings(op_source, tensor_source),
            # Add backend parsing here for phase 2
            backend_mappings=None,
        )

    # pylint: disable=too-many-locals
    def _extract_onnx_mappings(self, dlc_op_map, dlc_tensor_map) -> Optional[OpTensorMappings]:
        """
        Takes op and tensor traces and returns four maps:
        1. DLC op -> ONNX op/tensor
        2. ONNX op -> DLC op/tensor
        3. DLC tensor -> ONNX op/tensor
        4. ONNX tensor -> DLC op/tensor
        """
        dlc_ops_to_target_ops: Dict[str, Dict[str, Set[str]]] = {}
        target_ops_to_dlc_ops: Dict[str, Dict[str, Set[str]]] = {}
        dlc_tensors_to_target_tensors: Dict[str, Dict[str, Set[str]]] = {}
        target_tensors_to_dlc_tensors: Dict[str, Dict[str, Set[str]]] = {}

        for category, dlc_items in zip([OPS_KEY, TENSOR_KEY], [dlc_op_map, dlc_tensor_map]):
            for dlc_item in dlc_items:
                dlc_item_name = dlc_item.get_name()
                source_items = dlc_item.get_trace_pair()

                for source_item in source_items:
                    source_name = source_item.get_name()
                    source_type = OPS_KEY if source_item.get_type() == OP else TENSOR_KEY

                    # DLC -> ONNX
                    self.update_mapping(dlc_ops_to_target_ops, dlc_item_name, source_type, source_name)

                    # ONNX -> DLC
                    self.update_mapping(target_ops_to_dlc_ops, source_name, category, dlc_item_name)

                    # DLC tensor -> ONNX
                    if category == TENSOR_KEY:
                        self.update_mapping(
                            dlc_tensors_to_target_tensors, dlc_item_name, source_type, source_name
                        )

                    # ONNX tensor -> DLC
                    if source_type == TENSOR_KEY:
                        self.update_mapping(
                            target_tensors_to_dlc_tensors, source_name, category, dlc_item_name
                        )

        def convert_sets(d: Dict[str, Dict[str, Set[str]]]) -> Dict[str, MappingGroup]:
            return {
                k: MappingGroup(ops=sorted(v.get(OPS_KEY, [])), tensors=sorted(v.get(TENSOR_KEY, [])))
                for k, v in d.items()
            }

        return (
            OpTensorMappings(
                dlc_ops_to_target_ops=convert_sets(dlc_ops_to_target_ops),
                target_ops_to_dlc_ops=convert_sets(target_ops_to_dlc_ops),
                dlc_tensors_to_target_tensors=convert_sets(dlc_tensors_to_target_tensors),
                target_tensors_to_dlc_tensors=convert_sets(target_tensors_to_dlc_tensors),
            )
            if len(dlc_ops_to_target_ops)
            or len(target_ops_to_dlc_ops)
            or len(dlc_tensors_to_target_tensors)
            or len(target_tensors_to_dlc_tensors)
            else None
        )

    def update_mapping(
        self, map_obj: Dict[str, Dict[str, Set[str]]], name: str, category: str, value: str
    ) -> None:
        """Simple helper function for setting dictionary objects"""
        group: Dict[str, Set[str]] = {OPS_KEY: set(), TENSOR_KEY: set()}
        map_obj.setdefault(name, group)
        map_obj[name][category].add(value)

    def get_ir_graph(self, model_reader: Any):
        """
        Gets an IR graph object from the model_reader object
        :param model_reader: The model reader object
        :return: An IR graph object
        """
        graph_names: set = model_reader.get_ir_graph_names()
        # We only support single IR graph, so there's no need to iterate
        # It also might make sense to make 'graph' a member variable in the future
        if len(graph_names) > 1:
            raise NotImplementedError("DLC's with multiple IR graphs not currently supported")
        return self.model_reader.get_ir_graph(next(iter(graph_names)))

    def close_file(self):
        """
        Closes the model_reader file
        """
        self.model_reader.close()
