"""Regression checks for ingestion CLI exit codes without ML or network dependencies."""
from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_ingestion_cli():
    src = types.ModuleType("src")
    src.__path__ = [str(ROOT / "src")]
    tools = types.ModuleType("src.tools")
    tools.__path__ = [str(ROOT / "src" / "tools")]
    utils = types.ModuleType("src.utils")
    utils.__path__ = [str(ROOT / "src" / "utils")]
    cfg = types.ModuleType("src.utils.config")
    cfg.PROCESSED_DATA_DIR = ROOT / "data" / "processed"
    utils.config = cfg
    rag = types.ModuleType("src.tools.rag_pipeline")
    rag.IngestionPipeline = Mock()
    logger_module = types.ModuleType("src.utils.logger_config")
    logger_module.logger = Mock()
    modules = {
        "src": src, "src.tools": tools, "src.utils": utils,
        "src.utils.config": cfg, "src.tools.rag_pipeline": rag,
        "src.utils.logger_config": logger_module,
    }
    spec = importlib.util.spec_from_file_location(
        "alpha_ingestion_cli_under_test", ROOT / "scripts" / "run_rag_ingestion.py"
    )
    target = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(target)
    return target


class IngestionCLITests(unittest.TestCase):
    def setUp(self):
        self.cli = load_ingestion_cli()

    def test_success_exits_zero_and_passes_requested_path(self):
        with patch.object(self.cli, "IngestionPipeline") as factory:
            with patch.object(sys, "argv", ["ingestion", "--input-dir", "sample/approved"]):
                self.assertEqual(0, self.cli.main())
            factory.return_value.run_pipeline.assert_called_once_with(
                input_dir_path="sample/approved"
            )

    def test_failed_ingestion_exits_nonzero(self):
        with patch.object(self.cli, "IngestionPipeline") as factory:
            factory.return_value.run_pipeline.side_effect = RuntimeError("index failure")
            with patch.object(sys, "argv", ["ingestion", "--input-dir", "sample/approved"]):
                self.assertEqual(1, self.cli.main())
            factory.return_value.run_pipeline.assert_called_once()

    def test_default_uses_processed_data_directory(self):
        with patch.object(self.cli, "IngestionPipeline") as factory:
            with patch.object(sys, "argv", ["ingestion"]):
                self.assertEqual(0, self.cli.main())
            factory.return_value.run_pipeline.assert_called_once_with(
                input_dir_path=str(self.cli.config.PROCESSED_DATA_DIR)
            )


if __name__ == "__main__":
    unittest.main()
