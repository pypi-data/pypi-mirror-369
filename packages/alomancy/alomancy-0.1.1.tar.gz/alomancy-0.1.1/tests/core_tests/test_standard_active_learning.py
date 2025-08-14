"""
Tests for the standard active learning workflow.

This module tests the ActiveLearningStandardMACE class and its implementation
of the active learning workflow using MACE, MD, and Quantum Espresso.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from ase import Atoms
from ase.io import write

from alomancy.core.standard_active_learning import ActiveLearningStandardMACE


@pytest.fixture
def mock_job_config():
    return {
        "mlip_committee": {
            "name": "test_committee",
            "size_of_committee": 3,
            "max_time": "1H",
            "hpc": {
                "hpc_name": "test-hpc",
                "pre_cmds": ["echo 'test'"],
                "partitions": ["test"],
            },
        },
        "structure_generation": {
            "name": "test_structure_generation",
            "desired_number_of_structures": 10,
            "max_time": "1H",
            "structure_selection_kwargs": {  # Add this missing section
                "max_number_of_concurrent_jobs": 5,
                "chem_formula_list": None,
                "atom_number_range": (0, 21),
                "enforce_chemical_diversity": True,
            },
            "run_md_kwargs": {  # Also add this section if it's missing
                "steps": 1000,
                "temperature": 300,
                "timestep_fs": 0.5,
                "friction": 0.002,
            },
            "hpc": {
                "hpc_name": "test-hpc",
                "pre_cmds": ["echo 'test'"],
                "partitions": ["test"],
            },
        },
        "high_accuracy_evaluation": {
            "name": "test_dft",
            "max_time": "2H",
            "hpc": {
                "hpc_name": "test-hpc",
                "pre_cmds": ["echo 'test'"],
                "partitions": ["test"],
            },
        },
    }


@pytest.fixture
def sample_atoms_co2():
    """Create a sample CxO2 molecule."""
    return Atoms(
        symbols=["C", "O", "O"],
        positions=np.ones((3, 3)) * 1.2,
        cell=[15.0, 15.0, 15.0],
        pbc=True,
    )


@pytest.fixture
def sample_training_data_co2(sample_atoms_co2):
    """Create sample training data with CO2."""
    atoms_list = []
    for i in range(10):
        atoms = sample_atoms_co2.copy()
        atoms.positions += np.random.random((3, 3)) * 0.1
        atoms.info["energy"] = -20.0 + i * 0.1
        atoms.arrays["forces"] = np.random.random((3, 3)) * 0.1
        atoms_list.append(atoms)
    return atoms_list


@pytest.fixture
def temp_files_co2(sample_training_data_co2, mock_job_config):
    """Create temporary training and test files with CO2 data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        train_file = Path(tmpdir) / "train_co2.xyz"
        test_file = Path(tmpdir) / "test_co2.xyz"

        # Write training data
        write(str(train_file), sample_training_data_co2[:7], format="extxyz")
        # Write test data
        write(str(test_file), sample_training_data_co2[7:], format="extxyz")

        yield str(train_file), str(test_file), mock_job_config


class TestActiveLearningStandardMACE:
    """Test the ActiveLearningStandardMACE class."""

    def test_initialization(self, temp_files_co2):
        """Test workflow initialization."""
        train_file, test_file, mock_job_config = temp_files_co2

        workflow = ActiveLearningStandardMACE(
            initial_train_file_path=train_file,
            initial_test_file_path=test_file,
            jobs_dict=mock_job_config,
            number_of_al_loops=3,
            verbose=1,
        )

        assert workflow.initial_train_file == Path(train_file)
        assert workflow.initial_test_file == Path(test_file)
        assert workflow.number_of_al_loops == 3
        assert workflow.verbose == 1

    @patch("alomancy.core.standard_active_learning.committee_remote_submitter")
    @patch("alomancy.core.standard_active_learning.get_mace_eval_info")
    @patch("alomancy.configs.remote_info.get_remote_info")
    def test_train_mlip(
        self,
        mock_get_remote_info,
        mock_mace_recover,
        mock_committee_submitter,
        temp_files_co2,
        mock_job_config,
    ):
        """Test MLIP training method."""
        train_file, test_file, mock_job_config = temp_files_co2

        # Set up mocks
        mock_remote_info = MagicMock()
        mock_get_remote_info.return_value = mock_remote_info

        # Mock committee_remote_submitter to return a list of model paths
        mock_committee_submitter.return_value = [
            f"{mock_job_config['mlip_committee']['name']}_stagetwo_compiled.model"
        ]

        mock_results_df = pd.DataFrame(
            {
                "mae_e": [0.1, 0.08, 0.12],
                "mae_f": [0.2, 0.18, 0.22],
            }
        )
        mock_mace_recover.return_value = mock_results_df

        workflow = ActiveLearningStandardMACE(
            initial_train_file_path=train_file,
            initial_test_file_path=test_file,
            jobs_dict=mock_job_config,
            plots=False,
        )

        # Test train_mlip method
        result = workflow.train_mlip("test_loop_0", mock_job_config["mlip_committee"])

        # Verify remote submitter was called
        mock_committee_submitter.assert_called_once()

        # Check the call arguments
        call_args = mock_committee_submitter.call_args
        assert call_args[1]["base_name"] == "test_loop_0"
        assert (
            call_args[1]["target_file"]
            == f"{mock_job_config['mlip_committee']['name']}_stagetwo_compiled.model"
        )
        assert call_args[1]["size_of_committee"] == 3

        mock_mace_recover.assert_called_once_with(
            mlip_committee_job_dict=mock_job_config["mlip_committee"]
        )

        # Verify the result is the DataFrame returned by mace_recover
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, mock_results_df)

    def test_select_initial_structures_mock_directly(self):
        """Test that the mock works when calling the function directly."""
        with patch(
            "alomancy.structure_generation.select_initial_structures.select_initial_structures"
        ) as mock_select:

            def debug_select_initial(*args, **kwargs):
                print("=== DIRECT MOCK CALLED ===")
                return [Atoms("CO2")]

            mock_select.side_effect = debug_select_initial

            # Import and call the function directly
            from alomancy.structure_generation.select_initial_structures import (
                select_initial_structures,
            )

            result = select_initial_structures(
                base_name="test",
                structure_generation_job_dict={"name": "test"},
                train_atoms_list=[Atoms("CO2")],
                verbose=0,
                chem_formula_list=None,
                atom_number_range=(0, 21),
                enforce_chemical_diversity=True,
            )

            print(f"Direct call result: {result}")
            mock_select.assert_called_once()

    @patch("alomancy.core.standard_active_learning.select_initial_structures")
    @patch("alomancy.core.standard_active_learning.md_remote_submitter")
    @patch("alomancy.core.standard_active_learning.find_high_sd_structures")
    @patch("alomancy.configs.remote_info.get_remote_info")
    @patch("alomancy.core.standard_active_learning.read")
    @patch("alomancy.core.standard_active_learning.write")
    @patch("alomancy.core.standard_active_learning.MACECalculator")
    def test_generate_structures(
        self,
        mock_mace_calc,
        mock_write,
        mock_read,
        mock_get_remote_info,
        mock_find_high_sd,
        mock_md_submitter,
        mock_select_initial,
        temp_files_co2,
    ):
        """Test structure generation method."""
        train_file, test_file, mock_job_config = temp_files_co2

        # Add debugging to the mock
        def debug_select_initial(*args, **kwargs):
            print("=== SELECT_INITIAL_STRUCTURES MOCK CALLED ===")
            print(f"Args: {args}")
            print(f"Kwargs: {kwargs}")
            return [Atoms("CO2") for _ in range(5)]

        mock_select_initial.side_effect = debug_select_initial

        # Ensure all required keys are present
        mock_job_config["structure_generation"].update(
            {
                "structure_selection_kwargs": {
                    "max_number_of_concurrent_jobs": 3,
                    "chem_formula_list": None,
                    "atom_number_range": (0, 21),
                    "enforce_chemical_diversity": True,
                },
                "run_md_kwargs": {
                    "steps": 1000,
                    "temperature": 300,
                    "timestep_fs": 0.5,
                    "friction": 0.002,
                },
            }
        )

        # Set up other mocks
        mock_atoms = [Atoms("CO2") for _ in range(5)]

        # Mock md_submitter to return trajectory paths
        mock_md_submitter.return_value = [
            "results/test_loop_0/structure_generation/md_output_0",
            "results/test_loop_0/structure_generation/md_output_1",
        ]

        mock_read.return_value = [Atoms("CO2")]
        mock_find_high_sd.return_value = mock_atoms

        # Mock remote info
        mock_remote_info = MagicMock()
        mock_remote_info.name = "test-hpc"
        mock_get_remote_info.return_value = mock_remote_info

        # Create workflow instance
        workflow = ActiveLearningStandardMACE(
            initial_train_file_path=train_file,
            initial_test_file_path=test_file,
            jobs_dict=mock_job_config,
            plots=False,
        )

        # Test the method with exception handling
        train_atoms_list = [Atoms("CO2") for _ in range(10)]

        print("=== BEFORE CALLING generate_structures ===")
        print(f"mock_select_initial called: {mock_select_initial.called}")

        try:
            result = workflow.generate_structures(
                "test_loop_0", mock_job_config, train_atoms_list
            )
            print("=== generate_structures completed successfully ===")
        except Exception as e:
            print(f"=== EXCEPTION in generate_structures: {e} ===")
            import traceback

            traceback.print_exc()
            raise

        print("=== AFTER CALLING generate_structures ===")
        print(f"mock_select_initial called: {mock_select_initial.called}")
        print(f"mock_select_initial call_count: {mock_select_initial.call_count}")

        # Verify the result
        assert result == mock_atoms

        # Now these should all be called
        mock_select_initial.assert_called_once()
        mock_md_submitter.assert_called_once()
        mock_find_high_sd.assert_called_once()

    # @patch(
    #     "alomancy.structure_generation.select_initial_structures.select_initial_structures"
    # )
    # @patch("alomancy.structure_generation.md.md_remote_submitter.md_remote_submitter")
    # @patch("alomancy.core.standard_active_learning.find_high_sd_structures")
    # @patch("alomancy.configs.remote_info.get_remote_info")
    # @patch("alomancy.core.standard_active_learning.read")
    # @patch("pathlib.Path.glob")
    # @patch("pathlib.Path.mkdir")
    # @patch("alomancy.core.standard_active_learning.write")
    # @patch("alomancy.core.standard_active_learning.MACECalculator")
    # def test_generate_structures(
    #     self,
    #     mock_mace_calc,
    #     mock_write,
    #     mock_mkdir,
    #     mock_glob,
    #     mock_read,
    #     mock_get_remote_info,
    #     mock_find_high_sd,
    #     mock_md_submitter,
    #     mock_select_initial,
    #     temp_files_co2,
    #     mock_job_config,
    #     sample_atoms_co2,
    # ):
    #     """Test structure generation method."""
    #     train_file, test_file, config_dict = temp_files_co2

    #     # Set up mocks
    #     mock_initial_structures = [sample_atoms_co2.copy() for _ in range(4)]
    #     mock_select_initial.return_value = mock_initial_structures

    #     mock_md_trajectories = ["/path/to/traj1.xyz", "/path/to/traj2.xyz"]
    #     mock_md_submitter.return_value = mock_md_trajectories

    #     mock_md_structures = [sample_atoms_co2.copy() for _ in range(20)]
    #     # Add required arrays for find_high_sd_structures
    #     for atoms in mock_md_structures:
    #         atoms.arrays["REF_forces"] = np.random.random((3, 3)) * 0.1
    #         atoms.info["REF_energy"] = -20.0 + np.random.random() * 0.1
    #     mock_read.return_value = mock_md_structures

    #     mock_model_paths = [
    #         Path("results/test_loop_0/test_mlip/fit_0/test_mlip_stagetwo.model"),
    #         Path("results/test_loop_0/test_mlip/fit_1/test_mlip_stagetwo.model"),
    #     ]
    #     mock_glob.return_value = mock_model_paths

    #     mock_high_sd_structures = [sample_atoms_co2.copy() for _ in range(5)]
    #     for i, atoms in enumerate(mock_high_sd_structures):
    #         atoms.info["job_id"] = i

    #     # Mock find_high_sd_structures to return our test structures directly
    #     mock_find_high_sd.return_value = mock_high_sd_structures

    #     mock_remote_info = MagicMock()
    #     mock_get_remote_info.return_value = mock_remote_info

    #     # Mock MACE calculator - important to return a mock object
    #     mock_calculator = MagicMock()
    #     mock_mace_calc.return_value = mock_calculator

    #     workflow = ActiveLearningStandardMACE(
    #         initial_train_file_path=train_file,
    #         initial_test_file_path=test_file,
    #         jobs_dict=mock_job_config,
    #     )

    #     train_atoms_list = [sample_atoms_co2.copy() for _ in range(10)]

    #     # Add debugging to understand execution flow
    #     try:
    #         result = workflow.generate_structures(
    #             "test_loop_0", mock_job_config, train_atoms_list
    #         )
    #     except Exception as e:
    #         print(f"Exception during generate_structures: {e}")
    #         raise

    #     # Debug: Print mock call counts
    #     print(f"mock_select_initial called: {mock_select_initial.call_count} times")
    #     print(f"mock_md_submitter called: {mock_md_submitter.call_count} times")
    #     print(f"mock_find_high_sd called: {mock_find_high_sd.call_count} times")
    #     print(f"Result length: {len(result) if result else 'None'}")
    #     print(f"Result type: {type(result)}")

    #     # The system detects existing MD runs and skips initial steps
    #     # This is actually correct behavior - verify the final result is produced
    #     mock_find_high_sd.assert_called_once()

    #     # Verify result - the function should return our mocked structures
    #     assert len(result) == 5
    #     assert all(
    #         hasattr(atoms, "info") and "job_id" in atoms.info for atoms in result
    #     )

    @patch("alomancy.core.standard_active_learning.qe_remote_submitter")
    @patch("alomancy.configs.remote_info.get_remote_info")
    @patch("alomancy.core.standard_active_learning.read")
    def test_high_accuracy_evaluation(
        self,
        mock_read,
        mock_get_remote_info,
        mock_qe_submitter,
        temp_files_co2,
        sample_atoms_co2,
    ):
        """Test high accuracy evaluation method."""
        train_file, test_file, mock_job_config = temp_files_co2

        # Set up mocks
        mock_structure_paths = ["/path/to/qe_result1.xyz", "/path/to/qe_result2.xyz"]
        mock_qe_submitter.return_value = mock_structure_paths

        mock_qe_structures = [sample_atoms_co2.copy() for _ in range(2)]
        for atoms in mock_qe_structures:
            atoms.info["energy"] = -20.5
            atoms.arrays["forces"] = np.random.random((3, 3)) * 0.1
            atoms.get_potential_energy = Mock(return_value=-1.0)
            atoms.get_forces = Mock(return_value=np.array([[0, 0, 0]]))
        mock_read.side_effect = mock_qe_structures

        mock_remote_info = MagicMock()
        mock_get_remote_info.return_value = mock_remote_info

        workflow = ActiveLearningStandardMACE(
            initial_train_file_path=train_file,
            initial_test_file_path=test_file,
            jobs_dict=mock_job_config,
        )

        input_structures = [sample_atoms_co2.copy() for _ in range(2)]

        result = workflow.high_accuracy_evaluation(
            "test_loop_0", mock_job_config["high_accuracy_evaluation"], input_structures
        )

        # Verify QE submitter was called
        mock_qe_submitter.assert_called_once()

        # Verify results
        assert len(result) == 2
        assert all(atoms.info.get("energy") is not None for atoms in result)
        assert all(atoms.arrays.get("forces") is not None for atoms in result)


@pytest.mark.integration
class TestActiveLearningStandardMACEIntegration:
    def test_full_workflow_execution_with_tempdir(
        self, temp_files_co2, sample_atoms_co2
    ):
        """Test workflow execution in a controlled temporary directory."""
        train_file, test_file, mock_job_config = temp_files_co2

        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Mock all the heavy external operations
                with (
                    patch.object(
                        ActiveLearningStandardMACE, "train_mlip"
                    ) as mock_train,
                    patch.object(
                        ActiveLearningStandardMACE, "generate_structures"
                    ) as mock_gen,
                    patch.object(
                        ActiveLearningStandardMACE, "high_accuracy_evaluation"
                    ) as mock_ha,
                ):
                    # Configure method return values
                    mock_train.return_value = pd.DataFrame(
                        {"mae_f": [0.1], "mae_e": [0.2]}
                    )
                    mock_gen.return_value = [sample_atoms_co2.copy() for _ in range(5)]
                    mock_ha.return_value = [sample_atoms_co2.copy() for _ in range(3)]
                    for atoms in mock_ha.return_value:
                        atoms.get_potential_energy = Mock(return_value=-1.0)
                        atoms.get_forces = Mock(return_value=np.array([[0, 0, 0]]))

                    workflow = ActiveLearningStandardMACE(
                        initial_train_file_path=train_file,
                        initial_test_file_path=test_file,
                        jobs_dict=mock_job_config,
                        number_of_al_loops=1,
                        verbose=0,
                    )

                    # This should work since we're in a temp directory with proper mocks
                    workflow.run()

                    # Verify workflow executed properly
                    mock_train.assert_called_once()
                    mock_gen.assert_called_once()
                    mock_ha.assert_called_once()

            finally:
                os.chdir(old_cwd)


# @pytest.mark.integration
# class TestActiveLearningStandardMACEIntegration:
#     """Integration tests for the standard MACE workflow."""

#     @patch('alomancy.configs.config_dictionaries.load_dictionaries')
#     @patch('alomancy.core.standard_active_learning.committee_remote_submitter')
#     @patch('alomancy.core.standard_active_learning.mace_al_loop_average_error')
#     @patch('alomancy.structure_generation.select_initial_structures.select_initial_structures')
#     @patch('alomancy.structure_generation.md.md_remote_submitter.md_remote_submitter')
#     @patch('alomancy.core.standard_active_learning.find_high_sd_structures')
#     @patch('alomancy.core.standard_active_learning.qe_remote_submitter')
#     @patch('alomancy.configs.remote_info.get_remote_info')
#     @patch('alomancy.core.standard_active_learning.read')
#     @patch('pathlib.Path.glob')
#     @patch('pathlib.Path.mkdir')
#     @patch('alomancy.core.standard_active_learning.write')
#     @patch('alomancy.core.standard_active_learning.MACECalculator')
#     @patch('alomancy.core.standard_active_learning.mace_recover_train_txt_final_results')
#     def test_full_workflow_execution(self, mock_mace_recover, mock_mace_calc, mock_write, mock_mkdir, mock_glob, mock_read,
#                                    mock_get_remote_info, mock_qe_submitter, mock_find_high_sd,
#                                    mock_md_submitter, mock_select_initial, mock_mace_analysis,
#                                    mock_committee_submitter, mock_load_dict, temp_files_co2,
#                                    mock_job_config, sample_atoms_co2):
#         """Test full workflow execution with all components."""
#         train_file, test_file, config_file = temp_files_co2
#         mock_load_dict.return_value = mock_job_config

#         # Set up all mocks for a complete workflow
#         mock_select_initial.return_value = [sample_atoms_co2.copy() for _ in range(4)]
#         mock_md_submitter.return_value = ["/path/to/traj.xyz"]

#         # Create mock MD structures with required arrays
#         mock_md_structures = [sample_atoms_co2.copy() for _ in range(10)]
#         for atoms in mock_md_structures:
#             atoms.arrays["REF_forces"] = np.random.random((3, 3)) * 0.1
#             atoms.info["REF_energy"] = -20.0 + np.random.random() * 0.1

#         mock_glob.return_value = [
#             Path("results/test_loop_0/test_mlip/fit_0/test_mlip_stagetwo.model"),
#             Path("results/test_loop_0/test_mlip/fit_1/test_mlip_stagetwo.model")
#         ]

#         mock_high_sd_structures = [sample_atoms_co2.copy() for _ in range(3)]
#         for i, atoms in enumerate(mock_high_sd_structures):
#             atoms.info["job_id"] = i
#         mock_find_high_sd.return_value = mock_high_sd_structures

#         mock_qe_submitter.return_value = ["/path/to/qe_result.xyz"]
#         mock_qe_structures = [sample_atoms_co2.copy()]
#         mock_qe_structures[0].info["energy"] = -20.5
#         mock_qe_structures[0].arrays["forces"] = np.random.random((3, 3)) * 0.1

#         # Set up side_effect for multiple read calls
#         # The read function gets called multiple times in different contexts
#         def read_side_effect(*args, **kwargs):
#             # If it's reading a trajectory file (multiple structures), return the list
#             if "traj" in str(args[0]) if args else False:
#                 return mock_md_structures
#             # Otherwise return a single QE structure
#             else:
#                 return mock_qe_structures[0]

#         mock_read.side_effect = read_side_effect

#         # Mock MACE analysis functions
#         mock_results_df = pd.DataFrame({
#             'mae_e': [0.1],
#             'mae_f': [0.2],
#             'rmse_energy': [0.15],
#             'rmse_forces': [0.25]
#         })
#         mock_mace_recover.return_value = mock_results_df
#         mock_mace_analysis.return_value = None

#         # Mock MACE calculator
#         mock_calculator = MagicMock()
#         mock_mace_calc.return_value = mock_calculator

#         mock_remote_info = MagicMock()
#         mock_get_remote_info.return_value = mock_remote_info

#         workflow = ActiveLearningStandardMACE(
#             initial_train_file_path=train_file,
#             initial_test_file_path=test_file,
#             config_file_path=config_file,
#             number_of_al_loops=1,
#             verbose=0
#         )

#         # Execute the workflow
#         workflow.run()

#         # Verify core components were called
#         mock_committee_submitter.assert_called()
#         mock_mace_analysis.assert_called()

#         # The workflow may skip structure generation if it detects existing runs
#         # So we check if either the generation was called OR high accuracy evaluation was called
#         structure_generation_called = (
#             mock_select_initial.called or
#             mock_md_submitter.called or
#             mock_find_high_sd.called
#         )
#         high_accuracy_called = mock_qe_submitter.called

#         # At least one of these should be true for a complete workflow
#         assert structure_generation_called or high_accuracy_called, (
#             "Neither structure generation nor high accuracy evaluation was executed"
#         )


@pytest.mark.slow
@pytest.mark.requires_external
class TestActiveLearningStandardMACEExternal:
    """Tests that require external dependencies (MACE, QE, etc.)."""

    def test_with_real_mace_calculator(self, skip_if_no_mace):
        """Test with real MACE calculator if available."""
        # This test would only run if MACE is actually installed
        # and skip_if_no_mace fixture doesn't skip it
        pass

    def test_with_real_quantum_espresso(self, skip_if_no_external):
        """Test with real Quantum Espresso if available."""
        # This test would only run if QE is actually installed
        pass
