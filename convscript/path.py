from pathlib import Path

class ProjPaths:

    current_file_path = Path(__file__)
    pkg_src_path = current_file_path.parent
    project_path = current_file_path.parent.parent
    test_path = project_path / "test"
    env_variables_path = project_path / ".env"
    
    # Data directories
    data_path = project_path / "data"
    inputs_path = data_path / "inputs"
    outputs_path = data_path / "outputs"
    intermediate_path = data_path / "intermediate"
    
    @classmethod
    def create_directories(cls):
        """Create all data directories if they don't exist"""
        cls.data_path.mkdir(exist_ok=True)
        cls.inputs_path.mkdir(exist_ok=True)
        cls.outputs_path.mkdir(exist_ok=True)
        cls.intermediate_path.mkdir(exist_ok=True)
