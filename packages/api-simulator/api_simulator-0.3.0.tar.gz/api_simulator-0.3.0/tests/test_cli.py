"""
Test CLI functionality including OpenAPI export
"""
import json
import tempfile
from pathlib import Path

import pytest

from api_simulator.cli import main


@pytest.fixture
def sample_config():
    """Minimal config for CLI testing"""
    return {
        "rest": {
            "port": 8000,
            "path": "/api",
            "apis": [
                {
                    "method": "GET",
                    "path": "/test",
                    "response": {"message": "test"}
                }
            ]
        }
    }


def test_openapi_export_command(sample_config, capsys):
    """Test apisim openapi export command with default output file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump(sample_config, config_f)
        config_path = config_f.name
    
    # Use temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "openapi.json"
        
        try:
            import sys
            sys.argv = ['apisim', 'openapi', 'export', '--config', config_path, '--out', str(output_path)]
            
            try:
                main()
            except SystemExit as e:
                # CLI should exit successfully
                assert e.code == 0
            
            # Check success message was printed
            captured = capsys.readouterr()
            assert "OpenAPI written to" in captured.out
            
            # Read and verify the generated OpenAPI spec
            with open(output_path, 'r') as f:
                openapi_spec = json.load(f)
            
            assert openapi_spec["openapi"] == "3.0.3"
            assert openapi_spec["info"]["title"] == "API Simulator"
            assert "/api/test" in openapi_spec["paths"]
            
        finally:
            Path(config_path).unlink()


def test_openapi_export_to_file(sample_config):
    """Test exporting OpenAPI to file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump(sample_config, config_f)
        config_path = config_f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out_f:
        out_path = out_f.name
    
    try:
        import sys
        sys.argv = ['apisim', 'openapi', 'export', '--config', config_path, '--out', out_path]
        
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
        
        # Read exported file
        with open(out_path, 'r') as f:
            openapi_spec = json.load(f)
        
        assert openapi_spec["openapi"] == "3.0.3"
        assert "/api/test" in openapi_spec["paths"]
        
    finally:
        Path(config_path).unlink()
        Path(out_path).unlink()


def test_validate_command(sample_config, capsys):
    """Test apisim validate command"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f)
        config_path = f.name
    
    try:
        import sys
        sys.argv = ['apisim', 'validate', '--config', config_path]
        
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
        
        captured = capsys.readouterr()
        assert "valid" in captured.out.lower() or "ok" in captured.out.lower()
        
    finally:
        Path(config_path).unlink()


def test_validate_invalid_config(capsys):
    """Test validate with invalid config"""
    invalid_config = {"invalid": "structure"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_config, f)
        config_path = f.name
    
    try:
        import sys
        sys.argv = ['apisim', 'validate', '--config', config_path]
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with error code
        assert exc_info.value.code != 0
        
    finally:
        Path(config_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])