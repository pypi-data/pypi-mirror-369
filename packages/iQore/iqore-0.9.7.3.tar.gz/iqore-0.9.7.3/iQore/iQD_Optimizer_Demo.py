# --------------------------------------------------------------
# HMAC-SHA256 Integrity Tag
# Digest: 744b745c0bbe879e1e484010ec546d31aca7571f41bec73034b11bad5eb16207
# Signature Key: [Redacted] — held by iQore for internal validation
# Timestamp: 2025-08-13
# Purpose: Authenticated integrity check — tamper-evident validation layer
# --------------------------------------------------------------

# WARNING: This script operates in a production-grade quantum circuit execution 
# environment. Execution pathways include quantum circuit simulation and quantum 
# hardware execution, with a focus on comparing the performance of **simulated** 
# and **real-world quantum hardware** circuits to prove the efficiency, accuracy, 
# and scalability of the iQD Quantum Execution Framework.
#
# DO NOT MODIFY WITHOUT AUTHORIZATION.
# ==============================================================
#
# Title   : iQD Quantum Optimizer Demo
# Author  : Sean W. Null, Founder & Chief Architect, iQore Inc. & Dennis Baleta, Software Engineer, iQore Inc. 
# Version : Internal Build — iQore iQD Stack
# Date    : August 13, 2025
# Version : 1.0.2
#
# © 2025 iQore Inc. All Rights Reserved. U.S. and international patents pending.
# --------------------------------------------------------------
# CONFIDENTIAL & PROPRIETARY
# --------------------------------------------------------------
# This software is a protected component of the iQore iQD stack.
#
# LICENSE RESTRICTIONS:
# - Internal execution only — not licensed for public or third-party use.
# - Unauthorized redistribution, decompilation, reverse engineering, or analysis is 
#   strictly prohibited.
# - Commercialization, modification, or external integration requires prior written 
#   authorization from iQore.
#
# This software stack is protected under trade secret, copyright, and patent laws.
# Violations will be pursued under U.S. intellectual property enforcement statutes.
#
# --------------------------------------------------------------
# PURPOSE & SCOPE
# --------------------------------------------------------------
# The iQD Quantum Optimizer Demo script is designed to showcase the functionality
# of the iQD Quantum Circuit Execution Framework, enabling users to execute quantum
# circuits and compare performance between baseline quantum circuits and optimized
# iQD circuits.
#
# This script performs the following core functions:
# - **Execution Mode Selection**: Allows users to choose between **Simulation** or 
#   **Hardware** modes for running the quantum circuit.
# - **User Input**: Collects input from users on circuit parameters, test selection, 
#   and qubit count.
# - **Backend Selection**: Selects either the **AerSimulator** (for simulation) or 
#   **IBM QPU** (for hardware execution) based on the selected mode.
# - **Quantum Circuit Generation**: Builds baseline and iQD optimized circuits based 
#   on user input, leveraging quantum circuit libraries and backend integration.
# - **Execution and Analysis**: Executes the quantum circuit, computes fidelity, 
#   total variation distance (TVD), and outputs results in CSV, JSON, and PDF formats.
# - **Metrics Logging**: Logs key performance metrics including gate counts, fidelity, 
#   execution times, and backend calibration data.
#
# This demo showcases the iQD stack's ability to optimize quantum circuits and 
# provide detailed performance metrics for both simulated and hardware-based quantum 
# systems, enabling researchers and developers to benchmark and compare quantum 
# circuit performance.
#
# --------------------------------------------------------------
# SYSTEM DESIGN OVERVIEW
# --------------------------------------------------------------
# System Modules:
# ┌────────────────────────────────────────────────────────────┐
# │ 1. **Argument Parsing** — Collects user input for execution │
# │    parameters including mode (Simulation/Hardware), test  │
# │    number, qubit count, shot count, and dimension.        │
# │ 2. **Quantum Circuit Builder** — Generates user-selected  │
# │    quantum circuits, including baseline and optimized     │
# │    circuits based on iQD optimization.                    │
# │ 3. **Backend Handler** — Selects either **AerSimulator**   │
# │    for simulation or **IBM QPU** for hardware execution   │
# │    based on user input.                                   │
# │ 4. **Execution Engine** — Transpiles and runs the quantum │
# │    circuits on the selected backend, including depth      │
# │    management and error handling.                         │
# │ 5. **Analysis Kernel** — Calculates Output Fidelity,   │
# │    TVD, and other metrics for quantum circuit comparison. │
# │ 6. **Export Layer** — Serializes results into **JSON**,    │
# │    **CSV**, and **PDF** formats for reporting and export. │
# └────────────────────────────────────────────────────────────┘
#
# --------------------------------------------------------------
# EXECUTION FLOW & LOGGING
# --------------------------------------------------------------
# This script includes two execution modes:
# - **Simulation Mode (S)**: Uses the **AerSimulator** backend for simulating quantum 
#   circuits. Results are calculated using a statevector simulation method.
# - **Hardware Mode (H)**: Executes quantum circuits on **IBM QPU** hardware, retrieving 
#   real-world performance metrics such as gate fidelities, T1/T2 times, and readout error rates.
#
# The script also generates baseline quantum circuits (QAOA, VQE, Quantum Volume, etc.) 
# for comparison against the iQD optimized circuits, providing comprehensive insights 
# into circuit performance.
#
# --------------------------------------------------------------
# INTERNAL SYSTEM DESIGN (Technical Insights)
# --------------------------------------------------------------
# Argument Parsing:
#
# - Collects input for the execution mode (S or H), test parameters, qubit count, and 
#   other relevant details for circuit construction.
#
# Quantum Circuit Builder:
#
# - Supports multiple baseline circuits (e.g., QAOA, VQE, Quantum Volume) and iQD 
#   optimized circuits.
#
# Backend Handler:
#
# - Selects the correct quantum backend based on user input (simulation vs hardware).
# - In hardware mode, the script connects to the **IBM Qiskit Runtime Service** to select 
#   an appropriate quantum backend based on qubit count and operational status.
#
# Execution Engine:
#
# - Transpiles quantum circuits for compatibility with the chosen backend.
# - Handles depth management, adjusting the circuit's depth if necessary and logging any 
#   related adjustments.
#
# Analysis Kernel:
#
# - Computes key performance metrics such as Output Fidelity, TVD, and entanglement metrics.
#
# Export Layer:
#
# - Exports results in various formats (JSON, CSV, PDF) for further analysis and reporting.
#
# --------------------------------------------------------------
# EXECUTION ENTRYPOINT
# --------------------------------------------------------------
# This script can be executed directly via:
#     python iQD_Optimizer_Demo.py
#
# Alternatively, it can be invoked within a larger quantum application to automate 
# optimization and performance benchmarking.
# ==============================================================

# --------------------------------------------------------------
# Standard Libraries
# --------------------------------------------------------------
# The following are Python standard libraries used for various utilities including:
# - File and system interaction
# - Data management and time operations
# - Argument parsing and logging for execution traceability and debugging
import os                       # Interact with the operating system (e.g., file management)
import sys                      # System-specific parameters and functions
import time                     # Time tracking (e.g., for execution duration)
import json                     # JSON serialization for result export
import csv                      # Export to CSV format for structured results
from datetime import datetime   # Time and date handling
import argparse                 # Command-line argument parsing for user input
import logging                  # Logging framework for runtime information and error handling

# --------------------------------------------------------------
# Third-party Libraries
# --------------------------------------------------------------
# These third-party libraries enhance functionality in key areas like scientific computing,
# data processing, and document generation:
import numpy as np               # Numerical operations (matrix operations, random numbers, etc.)
from numpy import pi
import pandas as pd              # Data manipulation and analysis (DataFrame handling)
from fpdf import FPDF            # PDF generation for reporting and exporting results

# --------------------------------------------------------------
# iQore Library
# --------------------------------------------------------------

from iQore import iQD

# --------------------------------------------------------------
# Qiskit Libraries
# --------------------------------------------------------------
# Qiskit provides a comprehensive suite of tools for quantum circuit construction, execution,
# and analysis. The following libraries are critical to the iQD framework:
from qiskit import QuantumCircuit, transpile, ClassicalRegister, assemble  # Basic quantum circuit creation, transpilation, and assembly
from qiskit_aer import AerSimulator   # AerSimulator backend for quantum circuit simulation
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error  # Noise modeling for accurate simulation
from qiskit.quantum_info import state_fidelity, DensityMatrix, entropy, Statevector  # Quantum information metrics (fidelity, entropy, etc.)
from qiskit.transpiler import PassManager, CouplingMap  # Circuit transpilation tools for optimization
from qiskit.transpiler.passes import SabreLayout, SabreSwap, Depth, RemoveBarriers, Optimize1qGates  # Circuit optimization passes
from qiskit.circuit.library import QuantumVolume  # Predefined quantum circuits (e.g., Quantum Volume circuit)
from qiskit.exceptions import QiskitError  # Error handling specific to Qiskit library
from qiskit.circuit.library import TwoLocal, RZGate, RZXGate, RZZGate  # Custom gate types for enhanced circuit design
from qiskit.circuit.library import HGate, SGate, TGate  # Standard quantum gates (Hadamard, S, T)
from qiskit.circuit.library.standard_gates import CXGate  # Standard 2-qubit gate (CNOT)
import random  # Random number generation for circuit construction and testing

# --------------------------------------------------------------
# Hardware-Related Libraries for Advanced Metrics
# --------------------------------------------------------------
# The following library is specifically used for advanced hardware interaction and metrics
# retrieval, such as entropy-based performance measurements for quantum circuits executed on
# real IBM quantum processors:
from qiskit_experiments.library import StateTomography  # Quantum state tomography for entropy and other metrics

# --------------------------------------------------------------
# QASM3 Serialization Support
# --------------------------------------------------------------
# The following import facilitates the export of quantum circuits in the new QASM3 format, which
# addresses deprecation issues with the previous `.qasm()` method:
from qiskit.qasm3 import dumps as qasm3_dumps  # For serializing quantum circuits in QASM3 format

# --------------------------------------------------------------
# Hardware-Related Imports (If Available)
# --------------------------------------------------------------
# These imports enable interaction with IBM Quantum hardware via the Qiskit Runtime Service.
# They allow for connecting to quantum processors, managing sessions, and sampling from real quantum hardware.
# Note: If the `qiskit_ibm_runtime` module is not available, the code will fall back gracefully.
try:
    from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2 as Sampler  # IBM QPU session and sampling interface
except ImportError:
    pass  # Handle the case where QiskitRuntimeService is not available, likely in simulation mode

# -----------------------LIB END -------------------------------

# --------------------------------------------------------------
# Logging Configuration for iQD Quantum Circuit Execution Framework
# --------------------------------------------------------------
# Logging is configured to capture runtime information, warnings, and errors
# during the execution of quantum circuits in the iQD Quantum Execution Framework.
# This configuration ensures traceability, debuggability, and monitoring of execution 
# behavior across simulation and hardware modes (including the iQD Optimizer Demo).
#
# The logging level is set to **DEBUG**, which ensures that detailed runtime status updates, 
# debugging information, warnings, and errors are captured during the execution of quantum 
# circuits. In production environments, the logging level should be set to **WARNING** or 
# **ERROR** to reduce verbosity, but during development and testing, **DEBUG** and **INFO** 
# levels are appropriate to capture all relevant details.
#
# The **format** for log messages includes:
# - **levelname**: The severity level of the log (e.g., DEBUG, INFO, WARNING, ERROR).
# - **message**: The actual content of the log message, providing insight into the execution flow.
#
# **Log Levels**:
# - **DEBUG**: Detailed information for diagnosing issues (e.g., successful circuit creation, optimization steps).
# - **INFO**: General runtime information, such as backend selection and execution start/finish.
# - **WARNING**: Alerts about potential issues that do not disrupt execution (e.g., circuit depth approaching maximum).
# - **ERROR**: Errors that may cause execution to fail, often with recoverable solutions (e.g., invalid backend).
# - **CRITICAL**: Severe errors indicating a failure that prevents further execution (e.g., hardware connection loss).
#
# By default, log outputs will be directed to standard output (console), but this can be easily 
# configured to output to log files or external logging services (e.g., for cloud-based or distributed systems).
#
# The `logging` module is used here to ensure that all runtime logs during quantum circuit execution
# (whether simulated or on hardware) are captured consistently. This allows for runtime feedback, error 
# tracking, and audit trails to facilitate debugging, performance analysis, and issue resolution.
#
# Usage Example:
#   logging.info("Execution started with backend: %s", backend_name)
#   logging.warning("Circuit depth exceeded the maximum limit.")
#   logging.error("Error during circuit execution: %s", error_message)
#
# NOTE: This logging configuration is essential for tracking execution flow and debugging the iQD Optimizer 
# Demo in both development and production settings. Ensure the logging level is set appropriately for each environment.

# -Disabled by Default
# --------------------------------------------------------------

'''
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
'''

# ----------------------- Logging (END) -----------------------


# --------------------------------------------------------------
# Global Constants for Quantum Circuit Depth Constraints
# --------------------------------------------------------------
# These constants define the minimum and maximum allowable depths 
# for quantum circuits within the iQD framework. Circuit depth refers 
# to the number of gate layers in a circuit.
#
# The constants ensure that quantum circuits:
# 1. Stay within the hardware's capacity, avoiding overflow errors on 
#    real quantum processors.
# 2. Have sufficient complexity for meaningful benchmarking and analysis.
#
# - **MIN_DEPTH**: The minimum depth required for valid circuits. If a circuit 
#   falls below this depth, additional gates are added to reach the threshold.
# 
# - **MAX_DEPTH**: The maximum depth to prevent excessive resource consumption 
#   or long execution times. Exceeding this depth may trigger re-optimization 
#   of the circuit.
#
# These depth constraints are critical when running on hardware backends, 
# where high depths can strain qubit connectivity and gate fidelities.

# --------------------------------------------------------------

MIN_DEPTH = 9  # Minimum circuit depth (lower depths may be padded)
MAX_DEPTH = 19000  # Maximum allowable depth to avoid excessive cost or overflow

# --------------------------------------------------------------

# --------------------------------------------------------------
# Command-Line Argument Parsing for iQD Quantum Circuit Execution
# --------------------------------------------------------------
# This function uses the `argparse` module to parse command-line arguments, 
# enabling dynamic configuration of execution parameters. This allows users 
# to run the iQD framework with different settings without modifying the source code.
#
# **Arguments:**
# - **--mode**: Specifies execution mode:
#   - "S" for **Simulation Mode** (uses a simulator backend).
#   - "H" for **Hardware Mode** (executes on real quantum hardware, e.g., IBM QPU).
#
# - **--test_number**: A unique identifier for each test (e.g., `001`), useful for tracking and organizing tests.
#
# - **--qubit_count**: Specifies the number of qubits for the circuit. Must be a positive integer (e.g., 5, 10).
#
# - **--shot_count**: Defines the number of shots (iterations) for quantum circuit execution. More shots improve result accuracy.
#
# - **--dimension**: A floating-point value to adjust a specific dimension of the circuit (e.g., depth or complexity).
#
# **Return:**
# - The function returns a parsed `argparse.Namespace` object containing all command-line arguments for use in the script.
#
# Example usage:
#   python iqd_execution.py --mode S --test_number 001 --qubit_count 5 --shot_count 1000 --dimension 2.5
#
# **Error Handling:**
# - `argparse` handles invalid arguments and displays appropriate error messages.
# - The `--mode` argument restricts input to "S" or "H", with errors prompting re-entry.
# --------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="iQD Quantum Circuit Execution")
    parser.add_argument("--mode", choices=["S", "H"], help="Execution mode: S for Simulation, H for Hardware")
    parser.add_argument("--test_number", type=str, help="Test number (e.g., 001)")
    parser.add_argument("--qubit_count", type=int, help="Number of qubits (e.g., 5, 10, 20)")
    parser.add_argument("--shot_count", type=int, help="Number of shots")
    parser.add_argument("--dimension", type=float, help="Dimension parameter for the circuit")
    return parser.parse_args()

# --------------------------------------------------------------

# --------------------------------------------------------------
# QASM File Path Input Collection for Custom Circuit
# --------------------------------------------------------------
# This function prompts the user to input a file path for a QASM file, representing a custom quantum circuit.
# The QASM file must be in valid QASM format, allowing it to be parsed and executed by quantum backends.
#
# **Purpose:**
# Enables users to dynamically load custom quantum circuits from external QASM files without modifying the source code.
# Useful for testing, benchmarking, and simulating custom-designed quantum circuits.
#
# **Functionality:**
# - Prompts the user to input the path of a QASM file, removing any leading/trailing whitespace.
# - Returns the file path (either absolute or relative) to the QASM file.
#
# **Expected Input:**
# - A valid file path to a QASM file representing the quantum circuit.
#
# **Return Value:**
# - The file path (string) to the QASM file entered by the user.
#
# **Example Usage:**
#   qasm_file_path = get_qasm_file_input()
#   print(f"The user selected the QASM file: {qasm_file_path}")
#
# **Error Handling:**
# - Assumes the user provides a valid file path. Future improvements could include file validation, such as:
#   - Ensuring the file exists.
#   - Verifying correct file permissions and QASM syntax.

# --------------------------------------------------------------

def get_qasm_file_input() -> str:
    # Collect the path to the QASM file for the custom quantum circuit
    qasm_file_path = input("\nEnter the QASM file path for the custom circuit: ").strip()
    return qasm_file_path

# ----------------------- Get QASM File (END) -----------------------

# --------------------------------------------------------------
# Function: `get_user_input()`
# --------------------------------------------------------------
# **Purpose**:
# Collects user input for configuring and executing a quantum circuit simulation or hardware execution.
# Users can select execution mode, test ID, qubit count, shot count, circuit dimension, baseline circuit type,
# and optionally, provide a custom QASM file for the quantum circuit.
#
# **Parameters**:
# None (input is gathered interactively).
#
# **Returns**:
# A dictionary containing:
# - `"mode"`: Execution mode (`'S'` for Simulation, `'H'` for Hardware).
# - `"test_name"`: Test identifier string, constructed from mode and test number.
# - `"qubit_count"`: Number of qubits for the quantum circuit.
# - `"shot_count"`: Number of shots to execute per circuit.
# - `"dimension"`: Dimension parameter for the circuit.
# - `"baseline_choice"`: Numeric choice for baseline circuit type (e.g., `'1'` for QAOA).
# - `"baseline_type"`: Name of the selected baseline circuit.
# - `"user_circuit"`: Path to a custom QASM file, if selected; otherwise `None`.
#
# **Functionality**:
# 1. Displays prompts for user input, including execution mode, test details, and quantum circuit parameters.
# 2. Validates input (e.g., positive integers for qubit and shot counts) and prompts re-entry if necessary.
# 3. Maps numeric baseline choices to corresponding circuit names (e.g., `'1'` to `'QAOA Circuit'`).
# 4. Allows for optional custom QASM file input if the user selects "custom circuit."
# 5. Returns a dictionary of all user inputs for later use in circuit execution.
#
# **Error Handling**:
# - Ensures valid inputs for numerical fields and re-prompts if the input is invalid.
# - Handles custom circuit selection by invoking `get_qasm_file_input()` to obtain the file path if applicable.
#
# **Example Usage**:
# ```python
# user_inputs = get_user_input()
# print(user_inputs["mode"])  # Output: 'S' or 'H'
# print(user_inputs["test_name"])  # Output: 'iQD_SIM_001'
# ```
#
# **Key Considerations**:
# - The function assumes the user is running in an interactive environment for input collection.
# - The execution mode ("S" or "H") determines whether the circuit will be simulated or executed on real hardware.
# --------------------------------------------------------------

def get_user_input() -> dict:
    """
    Collects user input for execution mode, test identification, qubit count,
    shot count, dimension parameter, and baseline circuit selection.
    Returns a dictionary with these values.
    """
    args = parse_arguments()

    print("\n")
    print("=" * 72)
    print("\033[1m" + "iQORE PRESENTS: iNTELLIGENT QUANTUM DYNAMICS".center(72) + "\033[0m")
    print("=" * 72)
    print("              iiii        QQQQQQQQQ     DDDDDDDDDDDDD        ")
    print("             i::::i     QQ:::::::::QQ   D::::::::::::DDD     ")
    print("              iiii    QQ:::::::::::::QQ D:::::::::::::::DD   ")
    print("                     Q:::::::QQQ:::::::QDDD:::::DDDDD:::::D  ")
    print("             iiiiiii Q::::::O   Q::::::Q  D:::::D    D:::::D ")
    print("             i:::::i Q:::::O     Q:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q:::::O     Q:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q:::::O     Q:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q:::::O     Q:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q:::::O     Q:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q:::::O  QQQQ:::::Q  D:::::D     D:::::D")
    print("             i::::i  Q::::::O Q::::::::Q  D:::::D    D:::::D ")
    print("             i::::::iQ:::::::QQ::::::::QDDD:::::DDDDD:::::D  ")
    print("             i::::::i QQ::::::::::::::Q D:::::::::::::::DD   ")
    print("             i::::::i   QQ:::::::::::Q  D::::::::::::DDD     ")
    print("             iiiiiiii     QQQQQQQQ::::QQDDDDDDDDDDDDD        ")
    print("                                 Q:::::Q                    ")
    print("                                  QQQQQQ                    ")
    print("=" * 72)
    print("© 2025 iQore Inc. All rights reserved.".center(72))
    print("=" * 72)

    print("\nSelect Execution Type:")
    print("")
    print(" 1 - Performance (Compare Baseline vs iQD Performance)")
    print(" 2 - Optimize    (Compare Baseline vs iQD Optimized Baseline)")
    print("")
    type_choice = input("Enter the number of your selection: ").strip()

    # Validate input
    while type_choice not in ['1', '2']:
        type_choice = input("Invalid selection. Please enter '1' for Performance or '2' for Optimization: ").strip()

    # Set 'optimize' to True for 2 (Optimization), False for 1 (Performance)
    optimize = True if type_choice == '2' else False
 
    print("\nSelect Execution Mode:")
    print("")
    print(" S - Simulation Mode")
    print(" H - Hardware Mode")
    print("")
    mode = args.mode if args.mode else input("Enter the letter of your selection: ").strip().upper()
    while mode not in ["S", "H"]:
        mode = input("Invalid selection. Please enter 'S' or 'H': ").strip().upper()

    selected_backend = None
    if mode == "H":
        print("\nSelect QPU Backend :")
        print("")
        print(" 1 - IBM Brisbane")
        print(" 2 - IBM Fez")
        print(" 3 - IBM Sherbrooke")
        print(" 4 - IBM Torino")
        print(" 5 - IBM Marrakesh")
        print(" 6 - IBM Kingston")
        print("")
        backend_choice = input("Enter the number of your selection: ").strip()
        while backend_choice not in ['1', '2', '3', '4', '5', '6']:
            backend_choice = input("Invalid selection. Please select a valid backend (1–6): ").strip()

        backend_map = {
            '1': 'ibm_brisbane',
            '2': 'ibm_fez',
            '3': 'ibm_sherbrooke',
            '4': 'ibm_torino',
            '5': 'ibm_marrakesh',
            '6': 'ibm_kingston'
        }
        selected_backend = backend_map[backend_choice]

    print("\nSelect Baseline Circuit:")
    print("")
    print(" 1 - QAOA Circuit")
    print(" 2 - VQE Circuit")
    print(" 3 - Quantum Volume Circuit")
    print(" 4 - Grover's Circuit")
    print(" 5 - Clifford+T Circuit")
    print(" 6 - GHZ Circuit")
    print(" 7 - Boson Sampling Circuit")
    print(" 8 - QPE Circuit")
    # print(" 9 - Upload Circuit - IN DEVELOPMENT")
    print("")
    baseline_choice = input("Enter the number of your selection: ").strip()

    while baseline_choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        baseline_choice = input("Invalid selection. Please select a valid circuit (1-4): ").strip()
    
    user_circuit = None
    if baseline_choice == '9':
        # Use QASM file path instead of custom Python circuit input
        user_circuit = get_qasm_file_input()  # Now gets the file path instead of inputting Python code

    baseline_circuit_map = {
        '1': 'QAOA Circuit',
        '2': 'VQE Circuit',
        '3': 'Quantum Volume Circuit',
        '4': 'Grover\'s Circuit',
        '5': 'Clifford+T Circuit',    
        '6': 'GHZ Circuit',
        '7': 'Boson Sampling Circuit',
        '8': 'QPE Circuit',    
        '9': 'Upload Circuit'
    }

    baseline_type = baseline_circuit_map.get(baseline_choice, 'Unknown Circuit')  # Default to 'Unknown Circuit' if invalid
    
    # Then continue asking for the remaining inputs
    test_number = args.test_number if args.test_number else input("\nEnter the Test ID: ").strip()
    test_name = f"{'iQD_SIM' if mode == 'S' else 'iQD_QHT'}_{test_number}"
    
    if args.qubit_count:
        qubit_count = args.qubit_count
    else:
        while True:
            try:
                qubit_count = int(input("\nEnter the number of qubits to be used: "))
                if qubit_count > 0:
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a positive integer.")
    
    if args.shot_count:
        shot_count = args.shot_count
    else:
        while True:
            try:
                shot_count = int(input("\nEnter the number of shots: "))
                if shot_count > 0:
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a positive integer.")
    
    if args.dimension:
        dimension = args.dimension
    else:
        while True:
            try:
                dimension = float(input("\nEnter the dimension parameter for the circuit (1-5): "))
                if dimension > 0:
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a positive number.")
    
    return {
        "mode": mode,
        "test_name": test_name,
        "qubit_count": qubit_count,
        "shot_count": shot_count,
        "dimension": dimension,
        "baseline_choice": baseline_choice,
        "baseline_type": baseline_type,
        "optimize": optimize,  # Store the optimize flag
        "user_circuit": user_circuit,  # Store the file path
        "backend": selected_backend 
    }

# ----------------------- User Input (END) -----------------------

# --------------------------------------------------------------
# Function: `select_backend()`
# --------------------------------------------------------------
# **Purpose**:
# Selects the appropriate backend for quantum circuit execution based on the user’s input:
# - **Simulation Mode ("S")**: Uses the `AerSimulator` for simulating circuits with the statevector method.
# - **Hardware Mode ("H")**: Connects to IBM Quantum services, selects a backend with the required qubit count,
#   and retrieves the backend's calibration metrics (T1, T2, and readout error).
#
# **Parameters**:
# - `user_input` (dict): A dictionary containing:
#   - `"mode"`: Execution mode (`"S"` for simulation, `"H"` for hardware).
#   - `"qubit_count"`: The number of qubits required for the quantum circuit.

# **Returns**:
# A tuple (`backend`, `service`):
# - `backend`: The selected quantum backend:
#   - `AerSimulator` in simulation mode.
#   - IBM Quantum backend in hardware mode.
# - `service`: The `QiskitRuntimeService` for hardware mode (or `None` in simulation mode).

# **Functionality**:
# - In **Simulation Mode**:
#   - The backend is set to `AerSimulator` for statevector simulation.
#   - Logs backend details (mode, qubit count).
# - In **Hardware Mode**:
#   - Connects to the IBM Quantum service, selects an appropriate backend, and retrieves calibration data (T1, T2, readout error).
#   - Logs backend and calibration details (e.g., available qubits, pending jobs).
#   - If no suitable backend is found, the program exits with an error.
#
# **Error Handling**:
# - In hardware mode, if no suitable backend is found or an error occurs, the program logs the error and exits.
# - In simulation mode, fallback to `AerSimulator` without issues.

# **Example Usage**:
# ```python
# user_input = {"mode": "H", "qubit_count": 5}
# backend, service = select_backend(user_input)
# print(backend.name)  # Output: Selected IBM backend name
# ```

# **Key Considerations**:
# - Assumes that the IBM Quantum service is configured and authenticated.
# - Simulation mode always uses `AerSimulator`, while hardware mode requires valid backend configuration.

# --------------------------------------------------------------

def select_backend(user_input: dict) -> tuple:
    mode = user_input["mode"]
    qubit_count = user_input["qubit_count"]

    if mode == "S":
        backend = AerSimulator()
        backend.set_options(method="statevector")
        logging.info("========== SIMULATION MODE SELECTED ==========")
        logging.info(f"[SIMULATION] Backend: AerSimulator (Statevector Method)")
        logging.info(f"[SIMULATION] Qubit Count: {qubit_count}")
        logging.info("==============================================")
        return backend, None

    else:
        try:
            logging.info("=========== HARDWARE MODE SELECTED ===========")
            logging.info("[HARDWARE] Validating IBM Quantum Service...")
            service = QiskitRuntimeService()

            if "backend" in user_input and user_input["backend"]:
                backend = service.backend(user_input["backend"])
            else:
                available_backends = service.backends(
                    filters=lambda b: b.configuration().n_qubits >= qubit_count and b.status().operational
                )
                if not available_backends:
                    logging.error("[HARDWARE] No suitable backend found.")
                    sys.exit(1)
                backend = min(available_backends, key=lambda b: b.status().pending_jobs)

            logging.info(f"[HARDWARE] Selected Backend: {backend.name}")
            logging.info(f"[HARDWARE] Available Qubits: {backend.configuration().n_qubits}")
            logging.info(f"[HARDWARE] Pending Jobs in Queue: {backend.status().pending_jobs}")

            backend_props = backend.properties()
            if backend_props:
                t1_times = []
                t2_times = []
                readout_errors = []

                for qubit_props in backend_props.qubits:
                    t1 = next((item.value for item in qubit_props if item.name == "T1"), None)
                    t2 = next((item.value for item in qubit_props if item.name == 'T2'), None)
                    readout_err = next((item.value for item in qubit_props if item.name == 'readout_error'), None)
                    if t1 is not None:
                        t1_times.append(t1)
                    if t2 is not None:
                        t2_times.append(t2)
                    if readout_err is not None:
                        readout_errors.append(readout_err)

                avg_t1 = np.mean(t1_times) if t1_times else float('nan')
                avg_t2 = np.mean(t2_times) if t2_times else float('nan')
                avg_readout_error = np.mean(readout_errors) if readout_errors else float('nan')

                logging.info("[HARDWARE] ---- Calibration Metrics ----")
                logging.info(f"[HARDWARE] Avg T1: {avg_t1:.2f} µs")
                logging.info(f"[HARDWARE] Avg T2: {avg_t2:.2f} µs")
                logging.info(f"[HARDWARE] Avg Readout Error: {avg_readout_error:.4f}")
            else:
                logging.warning("[HARDWARE] Backend properties unavailable for calibration stats.")

            logging.info("==============================================")
            return backend, service

        except Exception as e:
            logging.error(f"[HARDWARE] Backend selection failed: {e}")
            sys.exit(1)


# ----------------------- Select Backend (END) -----------------------

# --------------------------------------------------------------
# Function: `build_baseline_circuit()`
# --------------------------------------------------------------
# **Purpose**:  
# Constructs a baseline quantum circuit based on the user's selection. 
# It supports predefined circuits (e.g., Bell, Quantum Volume, Clifford+T) and custom circuits loaded from a QASM file.
#
# **Parameters**:
# - `qubit_count` (int): Number of qubits for the circuit.
# - `baseline_choice` (str): User's choice for the baseline circuit (1-9).
# - `user_circuit` (str, optional): File path to a custom QASM file if baseline_choice is '9'.
#
# **Returns**:
# - `QuantumCircuit`: The selected or custom-built quantum circuit.
#
# **Functionality**:
# - Based on `baseline_choice`, the function calls corresponding helper functions to build standard circuits (e.g., QAOA, VQE, etc.).
# - If the user chooses '9' for a custom circuit, it loads the circuit from the provided QASM file using `build_user_circuit()`.
# - If an invalid choice or QASM file format is provided, raises a `ValueError`.
#
# **Example Usage**:
# ```python
# circuit = build_baseline_circuit(5, '1')  # Creates a Bell circuit with 5 qubits
# ```

# --------------------------------------------------------------

def build_baseline_circuit(qubit_count: int, baseline_choice: str, user_circuit: str = None) -> QuantumCircuit:
    """
    Builds the selected baseline circuit based on the user's choice or custom circuit.
    
    Parameters:
    - qubit_count: Number of qubits for the circuit.
    - baseline_choice: The user's selection for the baseline circuit (1-4).
    - user_circuit: A custom circuit string if the user selects '4' for a custom circuit.
    
    Returns:
    - QuantumCircuit: The generated baseline quantum circuit.
    """
    if baseline_choice == '1':
        return build_qaoa_circuit(qubit_count)
    elif baseline_choice == '2':
        return build_vqe_circuit(qubit_count)
    elif baseline_choice == '3':
        return build_quantum_volume_circuit(qubit_count)
    elif baseline_choice == '4':
        return build_grover_circuit(qubit_count)
    elif baseline_choice == '5':
        return build_clifford_t_circuit(qubit_count)
    elif baseline_choice == '6':
        return build_ghz_circuit(qubit_count)
    elif baseline_choice == '7':
        return build_boson_circuit(qubit_count)
    elif baseline_choice == '8':
        return build_qpe_circuit(qubit_count)
    elif baseline_choice == '9' and user_circuit:
        # Load the custom circuit using the updated function
        return build_user_circuit(qubit_count, user_circuit)
    else:
        raise ValueError("Invalid baseline circuit choice or custom circuit format.")
    
def build_qaoa_circuit(qubit_count: int, reps: int = 1) -> QuantumCircuit:
    """
    Generates a QAOA circuit for MaxCut on a ring graph using qubit_count nodes.
    
    Parameters:
        qubit_count (int): Number of qubits (graph nodes)
        reps (int): QAOA depth (number of alternating operator layers)
    
    Returns:
        QuantumCircuit: A Qiskit-ready QAOA circuit with measurement
    """
    qc = QuantumCircuit(qubit_count)

    # Step 1: Initialize in superposition
    for q in range(qubit_count):
        qc.h(q)

    # Step 2: Set fixed angles for testing (can be optimized classically later)
    gamma = pi / 4  # Problem unitary parameter
    beta = pi / 8   # Mixer unitary parameter

    # Step 3: Apply QAOA layers
    for _ in range(reps):
        # Problem unitary (Z⊗Z on ring-connected graph)
        for i in range(qubit_count):
            j = (i + 1) % qubit_count  # Wrap-around connection
            qc.cx(i, j)
            qc.rz(2 * gamma, j)
            qc.cx(i, j)

        # Mixer unitary (X-rotations)
        for q in range(qubit_count):
            qc.rx(2 * beta, q)

    # Step 4: Measure all qubits
    qc.measure_all()
    return qc

def build_vqe_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a simplified VQE-style ansatz circuit with fixed parameters.
    """
    # Create the TwoLocal ansatz with symbolic parameters
    ansatz = TwoLocal(num_qubits=qubit_count,
                      rotation_blocks=['ry', 'rz'],
                      entanglement_blocks='cx',
                      entanglement='linear',
                      reps=2,
                      insert_barriers=True)

    # Create a parameter vector and bind it to fixed dummy values
    param_vec = ansatz.parameters
    param_bindings = {param: pi / 4 for param in param_vec}  # or any float

    # Bind parameters
    bound_ansatz = ansatz.assign_parameters(param_bindings)

    # Compose into final circuit
    qc = QuantumCircuit(qubit_count)
    qc.compose(bound_ansatz, inplace=True)
    qc.measure_all()
    return qc


def build_quantum_volume_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a valid Quantum Volume (QV) circuit using Qiskit's built-in QuantumVolume class.
    This circuit generates a random structure with multiple layers, using randomized SU(4) gates
    and entangling gates, which is appropriate for quantum volume benchmarking.
    """
    # Generate a Quantum Volume circuit with random SU(4) gates and randomized entangling operations
    qv = QuantumVolume(qubit_count, seed=42)  # Specify seed for reproducibility
    
    # Measure all qubits
    qv.measure_all()
    
    return qv

def build_grover_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a Grover's Algorithm circuit with a simple 1-solution oracle.
    The oracle marks the |11...1⟩ state as the solution (Z gate on all qubits).

    Parameters:
        qubit_count (int): Number of qubits for the search space (≥2 recommended)

    Returns:
        QuantumCircuit: Qiskit-ready Grover circuit with measurement
    """
    qc = QuantumCircuit(qubit_count)

    # Step 1: Apply Hadamard to all qubits to create uniform superposition
    qc.h(range(qubit_count))

    # Step 2: Oracle to mark |11...1⟩ (all Z gates flip sign of |11...1⟩)
    qc.h(qubit_count - 1)
    qc.mcx(list(range(qubit_count - 1)), qubit_count - 1)  # Multi-controlled X
    qc.h(qubit_count - 1)

    # Step 3: Diffusion operator (inversion about the mean)
    qc.h(range(qubit_count))
    qc.x(range(qubit_count))
    qc.h(qubit_count - 1)
    qc.mcx(list(range(qubit_count - 1)), qubit_count - 1)
    qc.h(qubit_count - 1)
    qc.x(range(qubit_count))
    qc.h(range(qubit_count))

    # Step 4: Measure all qubits
    qc.measure_all()
    return qc

def build_clifford_t_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a Clifford+T circuit for baseline testing.
    The circuit involves a series of single-qubit Clifford gates and T-gates,
    with entangling operations using CX gates.
    """
    qc = QuantumCircuit(qubit_count)
    # Apply a sequence of Hadamard gates to initialize the qubits
    for i in range(qubit_count):
        qc.h(i)
    # Apply the T-gate (non-Clifford) to each qubit
    for i in range(qubit_count):
        qc.t(i)
    # Apply entangling gates (CX gates) in a pattern to create entanglement
    for i in range(qubit_count - 1):
        qc.cx(i, i + 1)
    # Additional entangling gates for more depth (if qubit_count > 2)
    if qubit_count > 2:
        for i in range(qubit_count - 2):
            qc.cx(i, i + 2)
    # Apply additional Clifford gates (e.g., S and T gates)
    for i in range(qubit_count):
        qc.s(i)  # Apply the S gate, which is part of the Clifford group
        qc.t(i)  # Apply the T gate again for more complexity
    # Measure all qubits
    qc.measure_all()
    return qc

def build_ghz_circuit(n: int) -> QuantumCircuit:
    """
    Generates an N-qubit GHZ (Greenberger-Horne-Zeilinger) circuit.
    |GHZ⟩ = (|000...0⟩ + |111...1⟩)/√2
    """
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(1, n):
        qc.cx(0, i)
    qc.measure_all()
    return qc

def build_boson_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a Boson sampling circuit as a benchmark for iQD performance.
    Boson sampling is a quantum algorithm used to sample from a distribution
    of outputs generated by a linear optical network with photons.

    Parameters:
        qubit_count (int): The number of qubits for the Boson sampling circuit.

    Returns:
        QuantumCircuit: A Qiskit-ready Boson sampling circuit with measurement.
    """
    if qubit_count < 2:
        raise ValueError("Boson circuit requires at least 2 qubits.")

    qc = QuantumCircuit(qubit_count)

    # Step 1: Initialize qubits in superposition
    for q in range(qubit_count):
        qc.h(q)

    # Step 2: Apply entangling gates (CX) to create quantum interference
    for i in range(qubit_count - 1):
        qc.cx(i, i + 1)

    # Step 3: Apply additional operations for Boson sampling complexity
    # (This can be replaced with more specific Boson sampling operations)
    for i in range(qubit_count):
        qc.rz(np.pi / 2, i)

    # Step 4: Measure all qubits
    qc.measure_all()

    return qc

def build_qpe_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a basic Quantum Phase Estimation (QPE) circuit.
    
    Parameters:
        qubit_count (int): The number of qubits in the system (counting and work qubits).
    
    Returns:
        QuantumCircuit: A Qiskit-ready QPE circuit with measurement.
    """
    # Number of counting qubits
    count = 4
    # Work qubits
    work = qubit_count - count
    n_qubits = count + work

    # Initialize the quantum circuit
    qc = QuantumCircuit(n_qubits, count)

    # Apply Hadamard to the counting qubits (creating superposition)
    for q in range(count):
        qc.h(q)

    # Initialize work qubits to |1> state
    for q in range(count, n_qubits):
        qc.x(q)

    # Apply modular exponentiation (U_a) for a chosen value of 'a' (a=7 for N=15)
    for q in range(count):
        qc.append(RZGate(2**q * np.pi), [q])  # Apply the RZ gate with exponential angles

    # Apply inverse QFT (Quantum Fourier Transform) to the counting qubits
    for i in range(count // 2):
        qc.swap(i, count - i - 1)

    for j in range(count):
        for k in range(j):
            qc.cp(-np.pi / float(2 ** (j - k)), k, j)
        qc.h(j)

    # Measure the counting register qubits
    for q in range(count):
        qc.measure(q, q)

    return qc

def build_user_circuit(qubit_count: int, user_circuit: str) -> QuantumCircuit:
    """
    Loads a custom circuit from a QASM file and returns it as a QuantumCircuit,
    ensuring it matches the specified qubit count and includes necessary measurements.
    
    Parameters:
    - qubit_count (int): Number of qubits for the circuit.
    - user_circuit (str): Path to the custom QASM file.
    
    Returns:
    - QuantumCircuit: A quantum circuit loaded from the QASM file, measured if not already.
    """
    try:
        # Load the QASM circuit
        qc = QuantumCircuit.from_qasm_file(user_circuit)
        
        # Ensure the circuit has the correct qubit count
        if qc.num_qubits != qubit_count:    
            raise ValueError(f"QASM circuit has {qc.num_qubits} qubits, expected {qubit_count} qubits.")
        
        # Ensure the circuit is measured if not already measured
        if not qc.has_measurement:
            qc.measure_all()  # Measure all qubits if no measurement exists
        
        return qc
    
    except Exception as e:
        print(f"Error in loading QASM file: {e}")
        raise ValueError("Custom circuit execution failed.")

def build_bell_circuit(qubit_count: int) -> QuantumCircuit:
    """
    Generates a Bell circuit.
    If qubit_count >= 2, entangles qubits 0 and 1 using H and CX.
    If qubit_count < 2, raises a ValueError.
    """
    if qubit_count < 2:
        raise ValueError("Bell circuit requires at least 2 qubits.")

    qc = QuantumCircuit(qubit_count)
    qc.h(0)        # Create superposition on qubit 0
    qc.cx(0, 1)    # Entangle qubit 1 with qubit 0
    qc.measure_all()
    return qc

# ----------------------- Build Baseline Circuits (END) -----------------------

# --------------------------------------------------------------
# Function: `build_iqd_circuit()`
# --------------------------------------------------------------
# **Purpose**:  
# Constructs an iQD (iQore Dynamic) quantum circuit with stages for entanglement, modulation, noise correction, 
# and optional dynamic tensor control. The circuit is designed to simulate high-performance quantum operations 
# with customizable entanglement and tensor interaction, incorporating noise scaling if a backend is provided.

# **Parameters**:
# - `qubit_count` (int): The number of qubits for the quantum circuit.
# - `backend` (optional, object): Quantum hardware backend (QPU) used for noise scaling. If not provided, default noise scaling is applied.
# - `dimension` (float, optional, default = 1.0): Scaling factor for circuit modulation, adjusting interaction strengths and rotations.
# - `enable_tensor_controller` (bool, optional, default = True): Flag to enable dynamic tensor control for improved entanglement.
# - `matrix` (optional, 2D array-like): Custom interaction matrix for adjusting gate strengths between qubits. Defaults to random matrix if not provided.
# - `optimize` (bool, optional, default = False): Flag to enable optimization with a baseline circuit.
# - `baseline_choice` (optional, int): User choice for baseline circuit (e.g., '1' for Bell circuit).

# **Returns**:
# - `QuantumCircuit`: The fully constructed quantum circuit, which may include baseline composition, dynamic tensor control, and noise correction.

# **Functionality**:
# - **Stage 1: Initialization**: Initializes qubits with Hadamard gates, followed by Z rotations (based on `dimension` and `matrix`).
# - **Stage 2: Entanglement**: Entangles qubits with CX gates and parameterized Y rotations, with entanglement strength controlled by `matrix`.
# - **Stage 3: Noise Scaling**: Applies noise corrections using T1 and T2 times from the provided backend (if available).
# - **Stage 4: Tensor Control**: Applies dynamic tensor control during cycles if enabled, adjusting qubit interactions.
# - **Stage 5: Final Phase Locking**: Final RZ and RX rotations lock the qubits' phases and optimize the final state.
# - **Stage 6: Entanglement Enhancement**: Applies additional RZZ rotations to enhance entanglement further.
# - Final measurement of all qubits completes the circuit.

# **Example Usage**:
# ```python
# qubit_count = 5
# matrix = np.random.rand(5, 5)  # Example matrix
# backend = some_backend_instance  # Optional backend for noise scaling
# circuit = build_iqd_circuit(qubit_count, backend=backend, matrix=matrix)
# ```

# ---------------- Build iQD Circuit/Optimizer -----------------

def build_iqd_circuit(
    qubit_count: int,
    backend=None,
    dimension: float = 1.0,
    enable_tensor_controller: bool = True,
    matrix=None,
    optimize=False,
    baseline_choice=None
):
    qc = QuantumCircuit(qubit_count)

    logging.debug("Initializing iQD cloud optimizer...")

    if matrix is None:
        matrix = np.random.rand(qubit_count, qubit_count)

    # --- Cloud-Injection Optimization ---
    iQD.optimize(
        qc,
        qubit_count=qubit_count,
        backend=backend,
        matrix=matrix,
        enable_iQD_dtc=enable_tensor_controller
    )

    logging.debug("Cloud-injected iQD optimization complete.")

    # --- Optional Composition of Baseline Circuit ---
    if optimize:
        logging.debug("Composing with baseline circuit...")
        baseline_circuit = build_baseline_circuit(qubit_count, baseline_choice)
        qc.compose(baseline_circuit, qubits=range(qubit_count), inplace=True)
        logging.debug(f"\n[BASELINE CIRCUIT]\n{baseline_circuit.draw(fold=120)}")
        logging.debug(f"\n[FINAL iQD CIRCUIT AFTER COMPOSE]\n{qc.draw(fold=120)}")
        logging.debug("Baseline optimization completed.")
    else:
        logging.debug("Skipping baseline composition step.")

    # --- Final Measurement Step ---
    qc.measure_all()
    logging.debug("Measurement added. Circuit build finalized.")

    return qc

# ----------------------- Build iQD (END) -----------------------

# --------------------------------------------------------------
# Function: `transpile_circuit()`
# --------------------------------------------------------------
# **Purpose**:
# This function transpiles a quantum circuit (`qc`) to ensure compatibility with a specified quantum backend. 
# It optimizes the circuit and handles depth constraints (either adding padding for under-depth circuits 
# or re-optimizing over-depth circuits). The circuit is adjusted for backend-specific requirements like 
# qubit mapping, gate set, and routing based on the backend's coupling map.

# **Parameters**:
# - `qc` (QuantumCircuit): The quantum circuit to be transpiled.
# - `backend` (object): The quantum backend (e.g., IBM QPU or simulator) used for transpilation, 
#   which provides the coupling map and other hardware-specific configurations.
# - `constrain_depth` (bool, optional, default = False): If `True`, the circuit depth is constrained 
#   within the defined `MAX_DEPTH` and `MIN_DEPTH` values. Padding is added if the depth is too low, 
#   and optimization retries are performed if the depth exceeds the maximum allowed.

# **Returns**:
# - `QuantumCircuit`: The transpiled and optimized quantum circuit, with depth constraints if applicable.

# **Functionality**:
# 1. **Initial Transpilation**:
#    - Uses Qiskit's `transpile()` to adjust the circuit for the selected backend, optimizing for qubit connectivity 
#      and gate routing. The circuit is prepared based on the backend's coupling map, layout, and routing method.
# 2. **Depth Constraints**:
#    - **Maximum Depth**: If the circuit depth exceeds `MAX_DEPTH`, the function re-transpiles with a higher optimization 
#      level using the backend’s basis gates. If the depth remains too high, the function terminates the process.
#    - **Minimum Depth**: If the circuit depth is below `MIN_DEPTH`, padding is added using small RZ rotations to meet 
#      the minimum required depth.
# 3. **Logging**:
#    - Logs include the circuit depth before and after transpilation, with warnings if the depth is outside the acceptable range.
#    - Logs the re-transpilation process for over-depth circuits, helping track optimization stages.

# **Key Considerations**:
# - The depth constraints ensure the circuit is compatible with backend capabilities.
# - The transpilation process adjusts qubit layout, routing, and gate sets based on backend configurations.
# - Re-transpilation is dynamically handled for complex circuits, ensuring execution is feasible even with depth constraints.

# **Example Usage**:
# ```python
# backend = some_backend_instance  # Backend for transpiling the circuit
# qc = QuantumCircuit(5)  # A sample quantum circuit
# transpiled_qc = transpile_circuit(qc, backend, constrain_depth=True)
# ```

# **Key Operations**:
# - **transpile()**: Adjusts the quantum circuit to fit the backend's requirements.
# - **depth()**: Measures the depth of the quantum circuit to enforce depth constraints.
# - **rz()**: Applied during padding to meet the minimum depth requirements.
# - **logging.info()**: Provides detailed logging of the transpilation and depth adjustment process.

# --------------------------------------------------------------

def transpile_circuit(qc: QuantumCircuit, backend, constrain_depth: bool = False) -> QuantumCircuit:
    coupling_map = getattr(backend.configuration(), 'coupling_map', None)
    transpiled_qc = transpile(
        qc,
        backend=backend,
        optimization_level=0,
        coupling_map=coupling_map,
        initial_layout=list(range(qc.num_qubits)),
        layout_method='sabre',
        routing_method='sabre'
    )
    current_depth = transpiled_qc.depth()
    logging.info(f"[TRANSPILE] Initial circuit depth: {current_depth}")
    
    if constrain_depth:
        if current_depth > MAX_DEPTH:
            #logging.warning(f"[TRANSPILE] Circuit depth {current_depth} exceeds MAX_DEPTH {MAX_DEPTH}. Retrying with higher optimization.")
            # Dynamic Basis Gates Assignment based on Backend Capabilities
            basis_gates = backend.configuration().basis_gates

            transpiled_qc = transpile(
                qc,
                backend=backend,
                optimization_level=0,
                initial_layout=list(range(qc.num_qubits)),
                layout_method='sabre',
                routing_method='sabre',
                basis_gates=basis_gates  # Ensure compatibility with backend
            )
            new_depth = transpiled_qc.depth()
            logging.info(f"[TRANSPILE] Depth after re-transpilation: {new_depth}")
            if new_depth > MAX_DEPTH:
                logging.error(f"[TRANSPILE] Circuit depth {new_depth} still exceeds MAX_DEPTH {MAX_DEPTH}.")
                sys.exit(1)
        elif current_depth < MIN_DEPTH:
            #logging.warning(f"[TRANSPILE] Circuit depth {current_depth} is below MIN_DEPTH {MIN_DEPTH}. Adding padding.")
            qubit_idx = 0
            while transpiled_qc.depth() < MIN_DEPTH:
                transpiled_qc.rz(1e-6, qubit_idx % transpiled_qc.num_qubits)
                qubit_idx += 1
            final_depth = transpiled_qc.depth()
            logging.info(f"[TRANSPILE] Circuit depth after padding: {final_depth}")
    else:
        logging.info("[TRANSPILE] No depth constraints enforced.")
    
    logging.info(f"[TRANSPILE] Final circuit depth: {transpiled_qc.depth()}")
    return transpiled_qc

# ----------------------- Transpile Circuit (END) -----------------------

# --------------------------------------------------------------
# Function: `output_fidelity()`
# --------------------------------------------------------------
# **Purpose**:
# This function calculates the fidelity between two quantum states by comparing their measured outcome frequencies.
# Fidelity is a measure of the similarity between two quantum states and is calculated using the square root of the product 
# of the corresponding probabilities of states from two distributions: one from the iQD quantum circuit and one from a baseline.

# **Parameters**:
# - `iqd_counts` (dict): A dictionary where the keys are state labels (e.g., bitstrings) and the values are the counts 
#   of those states in the outcome distribution from the iQD quantum circuit.
# - `baseline_counts` (dict): A dictionary where the keys are state labels (e.g., bitstrings) and the values are the counts 
#   of those states from a baseline quantum circuit or reference distribution.

# **Returns**:
# - `float`: The fidelity value between the two distributions, expressed as a percentage, rounded to two decimal places.

# **Functionality**:
# 1. **Normalization**:
#    - The total number of counts in both the iQD circuit (`total_iqd`) and the baseline circuit (`total_baseline`) is computed.
#    - For each state, the probability is calculated by dividing the individual state counts by the total count for that distribution.

# 2. **Fidelity Calculation**:
#    - The fidelity is calculated as the sum of the square roots of the products of the corresponding state probabilities 
#      from the two distributions. For each state in either the iQD or baseline distribution, the fidelity contribution is:
#      `sqrt(iqd_prob[state] * baseline_prob[state])`. Missing states in one distribution are treated as zero probability.

# 3. **Edge Case Handling**:
#    - If the total count for either the iQD or baseline circuit is zero (i.e., no valid measurements), the function returns zero.
#    - This handles the case where no valid comparisons can be made between the two distributions.

# 4. **Result**:
#    - The fidelity value is multiplied by 100 to convert it to a percentage and rounded to two decimal places for final output.

# **Key Considerations**:
# - This function assumes that the state labels in both the `iqd_counts` and `baseline_counts` are comparable.
# - If a state is present in one distribution but not the other, its probability is considered zero, ensuring that only matching states contribute to the fidelity.
# - A fidelity of 100% indicates perfect overlap between the state distributions, while a lower percentage suggests less similarity.

# **Example Usage**:
# ```python
# iqd_counts = {'000': 150, '111': 50}
# baseline_counts = {'000': 160, '111': 40}
# fidelity = output_fidelity(iqd_counts, baseline_counts)
# print(fidelity)  # Output: 98.16
# ```

# **Key Operations**:
# - **sum()**: Computes the total counts for both the iQD and baseline distributions.
# - **get()**: Retrieves the probabilities for each state in the dictionary, defaulting to zero if the state is absent.
# - **round()**: Rounds the final fidelity value to two decimal places for a clean output.

# --------------------------------------------------------------

def output_fidelity(iqd_counts: dict, baseline_counts: dict) -> float:
    total_iqd = sum(iqd_counts.values())
    total_baseline = sum(baseline_counts.values())
    if total_iqd == 0 or total_baseline == 0:
        return 0
    iqd_prob = {state: count / total_iqd for state, count in iqd_counts.items()}
    baseline_prob = {state: count / total_baseline for state, count in baseline_counts.items()}
    fidelity_val = sum(((iqd_prob.get(state, 0) * baseline_prob.get(state, 0)) ** 0.5)
                       for state in set(iqd_counts.keys()).union(baseline_prob.keys()))
    return round(fidelity_val, 6)

# ----------------------- Output Fidelity (END) -----------------------

# --------------------------------------------------------------
# Function: `total_variation_distance()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the Total Variation Distance (TVD) between two probability distributions, represented as dictionaries of state counts.
# TVD measures the divergence between the two distributions, with a value between 0 (identical) and 1 (completely dissimilar).

# **Parameters**:
# - `counts1` (dict): Dictionary representing the first probability distribution, with quantum states as keys and counts as values.
# - `counts2` (dict): Dictionary representing the second probability distribution, with the same structure as `counts1`.

# **Returns**:
# - `float`: The Total Variation Distance (TVD), between 0 and 1. A TVD of 0 indicates identical distributions, while 1 indicates maximum divergence.

# **Functionality**:
# 1. **Normalization**:
#    - Calculates the total counts for both distributions (`total1` and `total2`).
#    - Converts counts to probabilities by dividing each state's count by the total count for its distribution.
# 2. **Handling Empty Distributions**:
#    - If either distribution is empty (i.e., has zero total count), the function logs an error and returns a TVD of 1.0, indicating maximum divergence.
# 3. **TVD Calculation**:
#    - The function computes the absolute differences between corresponding state probabilities and sums them up, scaled by 0.5, to get the TVD.
# 4. **Edge Case Handling**:
#    - If both distributions are empty, it returns a TVD of 1.0.

# **Key Considerations**:
# - States present in only one distribution are treated as having zero probability in the other.
# - TVD is often used in quantum information theory to quantify the difference between quantum states or distributions.

# **Example Usage**:
# ```python
# counts1 = {'000': 150, '111': 50}
# counts2 = {'000': 160, '111': 40}
# tvd = total_variation_distance(counts1, counts2)
# print(tvd)  # Output: 0.06666666666666667
# ```

# **Key Operations**:
# - **sum()**: Computes the total counts for both distributions.
# - **get()**: Retrieves the probability of each state, defaulting to 0 if the state is missing in either distribution.
# - **abs()**: Calculates the absolute difference between state probabilities.
# - **Logging**: Logs errors for empty distributions to aid debugging.

# --------------------------------------------------------------

def total_variation_distance(counts1: dict, counts2: dict) -> float:
    total1 = sum(counts1.values())
    total2 = sum(counts2.values())
    if total1 == 0 or total2 == 0:
        logging.error("Detected empty counts distribution. Returning maximum divergence (1.0) for TVD.")
        return 1.0
    prob1 = {state: count / total1 for state, count in counts1.items()}
    prob2 = {state: count / total2 for state, count in counts2.items()}
    all_states = set(prob1.keys()).union(prob2.keys())
    tvd = 0.5 * sum(abs(prob1.get(state, 0) - prob2.get(state, 0)) for state in all_states)
    return tvd

# ----------------------- Calculate TVD (END) -----------------------

# --------------------------------------------------------------
# Function: `tvd_iqd_vs_ideal()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the Total Variation Distance (TVD) between the output of the iQD execution and an ideal uniform distribution.
# TVD quantifies how far the observed output distribution is from the perfectly uniform case, with values between 0 (identical) and 1 (maximally different).
#
# **Parameters**:
# - `iqd_counts` (dict): Dictionary containing the iQD output as `{bitstring: count}`, where `bitstring` length corresponds to the number of qubits.
#
# **Returns**:
# - `float`: The Total Variation Distance (TVD) between the iQD output and the ideal uniform distribution, rounded to six decimal places.
#
# **Functionality**:
# 1. **Empty Input Handling**:
#    - Returns `1.0` immediately if `iqd_counts` is empty, indicating maximum divergence.
# 2. **Bitstring Generation**:
#    - Determines qubit count from bitstring length.
#    - Generates the full set of possible bitstrings using `itertools.product`.
# 3. **Probability Normalization**:
#    - Calculates total counts from iQD output.
#    - Converts counts to probabilities for each bitstring.
# 4. **Ideal Uniform Distribution**:
#    - Assigns equal probability (`1 / number_of_bitstrings`) to each bitstring.
# 5. **TVD Calculation**:
#    - Computes \( 0.5 \times \sum |p_{\text{iqd}} - p_{\text{ideal}}| \) across all bitstrings.
# 6. **Rounding**:
#    - Returns the TVD rounded to six decimal places.
#
# **Key Considerations**:
# - Assumes all keys in `iqd_counts` have the same bitstring length.
# - Missing bitstrings in `iqd_counts` are treated as having zero probability.
# - A uniform distribution serves as the ideal benchmark, representing equal probability for all outcomes.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# tvd = tvd_iqd_vs_ideal(counts)
# print(tvd)  # Example output: 0.25
# ```
#
# **Key Operations**:
# - **product()**: Generates all possible bitstrings.
# - **sum()**: Computes total counts for normalization.
# - **abs()**: Finds absolute difference between probabilities.
#
# --------------------------------------------------------------

from itertools import product

def tvd_iqd_vs_ideal(iqd_counts: dict) -> float:
    """
    Computes the Total Variation Distance between iQD output and ideal uniform distribution.
    """
    if not iqd_counts:
        return 1.0  # Maximum divergence if empty

    qubit_count = len(next(iter(iqd_counts.keys()), ''))  # Assumes all keys are same length
    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]

    iqd_total = sum(iqd_counts.values())
    if iqd_total == 0:
        return 1.0

    iqd_probs = {k: iqd_counts.get(k, 0) / iqd_total for k in bitstrings_full}
    ideal_probs = {k: 1 / len(bitstrings_full) for k in bitstrings_full}

    tvd = 0.5 * sum(abs(iqd_probs[k] - ideal_probs[k]) for k in bitstrings_full)
    return round(tvd, 6)
# ----------------------- Calculate TVD vs Ideal (iQD) (END) -----------------------

# --------------------------------------------------------------
# Function: `fidelity_vs_ideal()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the fidelity between an empirical bitstring distribution and an ideal uniform distribution over the full 2^n state space.
# Fidelity values range from 0 (completely dissimilar) to 1 (identical), providing a measure of similarity between the observed and ideal distributions.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to observed counts. All bitstrings are assumed to be the same length, corresponding to the number of qubits.
#
# **Returns**:
# - `float`: Fidelity between the observed distribution and the ideal uniform distribution, rounded to six decimal places. Returns 0.0 for invalid or empty input.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty, has a total count of zero, or if the inferred qubit count is zero.
# 2. **State Space Generation**:
#    - Determines the number of qubits from the length of any bitstring key.
#    - Generates all possible bitstrings using `itertools.product`.
# 3. **Probability Conversion**:
#    - Converts `counts` into probabilities across the full bitstring space, assigning 0 to missing states.
#    - Creates an ideal uniform distribution with equal probability for each bitstring.
# 4. **Fidelity Computation**:
#    - Uses `hellinger_fidelity()` to calculate similarity between the observed and ideal distributions.
# 5. **Error Handling**:
#    - Returns 0.0 if a `ZeroDivisionError` occurs during computation.
#
# **Key Considerations**:
# - Missing states in `counts` are treated as zero probability, which can lower fidelity.
# - Fidelity is calculated over the entire 2^n state space, not just the observed states.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# fidelity = fidelity_vs_ideal(counts)
# print(fidelity)  # Example output: 0.73...
# ```
#
# **Key Operations**:
# - **product()**: Generates all possible bitstrings for the given qubit count.
# - **sum()**: Calculates the total counts for probability normalization.
# - **hellinger_fidelity()**: Computes classical fidelity between two probability distributions.
# --------------------------------------------------------------

from qiskit.quantum_info import hellinger_fidelity

def fidelity_vs_ideal(counts: dict) -> float:
    """
    Computes the fidelity between a given count distribution and
    an ideal uniform distribution. Returns 0.0 on invalid input.
    """
    if not counts:
        return 0.0  # Empty counts

    total = sum(counts.values())
    if total == 0:
        return 0.0  # Avoid division by zero

    qubit_count = len(next(iter(counts.keys()), ''))
    if qubit_count == 0:
        return 0.0

    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]
    probs = {k: counts.get(k, 0) / total for k in bitstrings_full}
    ideal_probs = {k: 1 / len(bitstrings_full) for k in bitstrings_full}

    try:
        return round(hellinger_fidelity(probs, ideal_probs), 6)
    except ZeroDivisionError:
        return 0.0
    
# ----------------------- Calculate Fidelity vs Ideal (END) -----------------------

# --------------------------------------------------------------
# Function: `fidelity_iqd_baseline()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the Hellinger fidelity between the iQD output distribution and a baseline distribution over the full 2^n state space.
# Fidelity ranges from 0 (completely dissimilar) to 1 (identical), measuring the similarity between the two probability distributions.
#
# **Parameters**:
# - `iqd_counts` (dict): Dictionary mapping bitstrings to observed counts for the iQD output. All keys should have the same length, representing the number of qubits.
# - `baseline_counts` (dict): Dictionary mapping bitstrings to observed counts for the baseline output. Keys must match the qubit length used in `iqd_counts`.
#
# **Returns**:
# - `float`: Hellinger fidelity between the iQD and baseline distributions, rounded to six decimal places. Returns 0.0 for empty or invalid inputs.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if either input dictionary is empty or missing.
#    - Returns 0.0 if total counts in either distribution are zero.
# 2. **State Space Generation**:
#    - Determines the number of qubits from the length of a key in `iqd_counts`.
#    - Generates the complete set of possible bitstrings using `itertools.product`.
# 3. **Probability Conversion**:
#    - Converts counts for iQD and baseline into probabilities over the full state space, assigning 0 probability to missing states.
# 4. **Fidelity Computation**:
#    - Uses `hellinger_fidelity()` to compute similarity between the two probability distributions.
# 5. **Error Handling**:
#    - Catches `ZeroDivisionError` and returns 0.0 if encountered.
#
# **Key Considerations**:
# - Assumes both distributions correspond to the same qubit count.
# - Missing states in either distribution are treated as zero probability.
# - Fidelity is computed over the complete 2^n space, not just the states observed in both.
#
# **Example Usage**:
# ```python
# iqd_counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# baseline_counts = {'00': 480, '01': 320, '10': 100, '11': 100}
# fidelity = fidelity_iqd_baseline(iqd_counts, baseline_counts)
# print(fidelity)  # Example output: 0.98...
# ```
#
# **Key Operations**:
# - **product()**: Generates all possible bitstrings for the given qubit count.
# - **sum()**: Computes total counts for normalization.
# - **hellinger_fidelity()**: Calculates the Hellinger fidelity between two probability distributions.
# --------------------------------------------------------------

def fidelity_iqd_baseline(iqd_counts: dict, baseline_counts: dict) -> float:
    """
    Computes the Hellinger fidelity between iQD and baseline probability distributions.
    Returns 0.0 on error or empty inputs.
    """
    if not iqd_counts or not baseline_counts:
        return 0.0

    total_iqd = sum(iqd_counts.values())
    total_baseline = sum(baseline_counts.values())

    if total_iqd == 0 or total_baseline == 0:
        return 0.0

    qubit_count = len(next(iter(iqd_counts.keys()), ''))
    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]

    iqd_probs = {k: iqd_counts.get(k, 0) / total_iqd for k in bitstrings_full}
    baseline_probs = {k: baseline_counts.get(k, 0) / total_baseline for k in bitstrings_full}

    try:
        return round(hellinger_fidelity(iqd_probs, baseline_probs), 6)
    except ZeroDivisionError:
        return 0.0
# ----------------------- Calculate Fidelity (iQD vs Baseline) (END) -----------------------

# --------------------------------------------------------------
# Function: `output_entropy()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the Shannon entropy (in bits) of a quantum measurement output distribution over the full 2^n state space.
# Entropy measures the uncertainty or randomness in the distribution, with 0 representing a fully deterministic output and a maximum of n bits for a uniform n-qubit distribution.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to observed counts. All keys are assumed to have the same length, representing the number of qubits.
#
# **Returns**:
# - `float`: Shannon entropy in bits, rounded to six decimal places. Returns 0.0 for empty or invalid input.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty.
#    - Returns 0.0 if the total count of measurements is zero.
# 2. **State Space Generation**:
#    - Infers the number of qubits from the length of any key in `counts`.
#    - Generates the complete set of possible bitstrings using `itertools.product`.
# 3. **Probability Conversion**:
#    - Normalizes counts into probabilities over the full state space, assigning 0 probability to missing bitstrings.
# 4. **Entropy Calculation**:
#    - Computes \( H = -\sum p \log_2 p \) over all nonzero probabilities.
# 5. **Rounding**:
#    - Rounds the result to six decimal places before returning.
#
# **Key Considerations**:
# - Missing states are included with probability 0, which does not contribute to entropy.
# - The maximum possible entropy is equal to the number of qubits when the distribution is perfectly uniform.
# - Entropy is computed over the complete 2^n space, not just observed states.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# H = output_entropy(counts)
# print(H)  # Example output: 1.846439
# ```
#
# **Key Operations**:
# - **product()**: Generates all possible bitstrings for the inferred qubit count.
# - **sum()**: Totals counts for normalization.
# - **math.log2()**: Computes the logarithm base 2 for entropy calculation.
# --------------------------------------------------------------

import math
from itertools import product

def output_entropy(counts: dict) -> float:
    """
    Computes the output entropy (in bits) of a quantum measurement distribution.
    Returns 0.0 on empty or invalid input.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    qubit_count = len(next(iter(counts.keys()), ''))
    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]
    probs = {k: counts.get(k, 0) / total for k in bitstrings_full}

    entropy = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    return round(entropy, 6)

# ----------------------- Calculate Output Entropy (END) -----------------------

# --------------------------------------------------------------
# Function: `kl_divergence_vs_ideal()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the Kullback–Leibler (KL) divergence between an observed quantum measurement distribution and an ideal uniform distribution over the full 2^n state space.
# KL divergence quantifies how much information is lost when the ideal uniform distribution is used to approximate the observed distribution. 
# A value of 0 indicates identical distributions, while higher values indicate greater divergence.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to observed counts. All keys must be the same length, corresponding to the number of qubits.
#
# **Returns**:
# - `float`: KL divergence value (natural log base e). Returns 0.0 for empty or invalid input.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty or total counts are zero.
# 2. **State Space Generation**:
#    - Infers qubit count from the length of a bitstring key.
#    - Generates all possible bitstrings using `itertools.product`.
# 3. **Probability Conversion**:
#    - Converts counts to a probability list (`probs`) covering the full state space.
#    - Creates an ideal uniform probability list (`ideal`) with equal probability for all states.
# 4. **KL Divergence Computation**:
#    - Uses `scipy.stats.entropy()` (aliased as `kl_divergence`) to compute \( D_{KL}(P \parallel Q) \) where `P` is the observed distribution and `Q` is the ideal distribution.
#    - Result is in nats (natural log base e) by default.
# 5. **Error Handling**:
#    - Catches `ZeroDivisionError` and returns 0.0 if computation fails.
#
# **Key Considerations**:
# - Missing states are treated as having zero probability in the observed distribution.
# - The current implementation uses the natural log base (nats); set `base=2` in `entropy()` for bits.
# - KL divergence is asymmetric; swapping the distributions changes the result.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# d_kl = kl_divergence_vs_ideal(counts)
# print(d_kl)  # Example output: 0.12...
# ```
#
# **Key Operations**:
# - **product()**: Generates the complete set of bitstrings for the qubit count.
# - **sum()**: Totals counts for normalization.
# - **entropy()**: Computes KL divergence between two probability distributions.
# --------------------------------------------------------------

from scipy.stats import entropy as kl_divergence

def kl_divergence_vs_ideal(counts: dict) -> float:
    """
    Computes the KL Divergence between a measured distribution and an ideal uniform distribution.
    Returns 0.0 if counts are empty or malformed.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    qubit_count = len(next(iter(counts.keys()), ''))
    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]

    probs = [counts.get(k, 0) / total for k in bitstrings_full]
    ideal = [1 / len(bitstrings_full) for _ in bitstrings_full]

    try:
        return kl_divergence(probs, ideal)  # base=e
    except ZeroDivisionError:
        return 0.0

# ----------------------- Calculate KL Divergence (END) -----------------------

# --------------------------------------------------------------
# Function: `average_hamming_weight_bits()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the unweighted average Hamming weight of a quantum output distribution reconstructed from a counts dictionary.
# The Hamming weight of a bitstring is the number of '1' bits it contains. This metric provides insight into the average population of qubits in the |1⟩ state.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed frequencies in measurement results.
#
# **Returns**:
# - `float`: The unweighted average Hamming weight, rounded to six decimal places. Returns 0.0 if the input is empty or contains no data.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty.
# 2. **Bitstring Reconstruction**:
#    - Expands the `counts` dictionary into a flat list of bitstrings (`all_bits`), where each bitstring appears as many times as its observed count.
# 3. **Empty Data Handling**:
#    - Returns 0.0 if the reconstructed list is empty.
# 4. **Hamming Weight Computation**:
#    - Uses `.count('1')` to compute the number of ones in each bitstring.
#    - Computes the arithmetic mean of these Hamming weights using `numpy.mean()`.
# 5. **Rounding**:
#    - Rounds the final mean to six decimal places before returning.
#
# **Key Considerations**:
# - This implementation treats each occurrence of a bitstring equally (unweighted mean).
# - Large distributions are expanded into memory; for very large datasets, a streaming approach may be more memory-efficient.
# - Only the number of '1's in each bitstring is considered; bit position is not weighted.
#
# **Example Usage**:
# ```python
# counts = {'00': 2, '01': 3, '11': 1}
# avg_weight = average_hamming_weight_bits(counts)
# print(avg_weight)  # Example output: 0.833333
# ```
#
# **Key Operations**:
# - **list comprehension**: Reconstructs the flat list of bitstrings from `counts`.
# - **count('1')**: Counts the number of '1' bits in each bitstring.
# - **numpy.mean()**: Computes the average Hamming weight.
# --------------------------------------------------------------

def average_hamming_weight_bits(counts: dict) -> float:
    """
    Reconstructs iqd_bits-style list from counts and computes the unweighted average Hamming weight.
    Returns 0.0 if counts is empty.
    """
    if not counts:
        return 0.0

    # Reconstruct flat bitstring list (like iqd_bits)
    all_bits = [bit for bit, freq in counts.items() for _ in range(freq)]
    
    if not all_bits:
        return 0.0

    return round(np.mean([bit.count('1') for bit in all_bits]), 6)

# ----------------------- Calculate Average Hamming Weight (END) -----------------------

# --------------------------------------------------------------
# Function: `max_state_probability()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the maximum probability of any single bitstring (quantum state) from a measurement counts dictionary.
# This metric indicates the dominance of the most likely outcome in the distribution.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed counts.
#
# **Returns**:
# - `float`: The highest probability among all states, rounded to six decimal places. Returns 0.0 if the input is empty or contains zero total counts.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty.
#    - Returns 0.0 if the sum of all counts is zero.
# 2. **Maximum Probability Calculation**:
#    - Converts counts to probabilities by dividing each count by the total number of measurements.
#    - Finds the maximum probability value among all states.
# 3. **Rounding**:
#    - Rounds the maximum probability to six decimal places before returning.
#
# **Key Considerations**:
# - A high maximum probability can indicate strong bias or successful targeting of a specific state.
# - For a perfectly uniform distribution over \(2^n\) states, the maximum probability will be \(1 / 2^n\).
# - This metric is sensitive to noise or drift if the distribution is expected to be balanced.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# max_prob = max_state_probability(counts)
# print(max_prob)  # Example output: 0.5
# ```
#
# **Key Operations**:
# - **sum()**: Calculates the total number of measurements.
# - **max()**: Finds the largest probability value.
# --------------------------------------------------------------

def max_state_probability(counts: dict) -> float:
    """
    Computes the maximum state probability from a counts dictionary.
    Returns 0.0 if counts are empty.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    max_prob = max((count / total) for count in counts.values())
    return round(max_prob, 6)

# ----------------------- Calculate Max State Probablity (END) -----------------------

# --------------------------------------------------------------
# Function: `stddev_state_probabilities()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the standard deviation of state probabilities in a quantum measurement distribution.
# This metric measures how much the probabilities of different states deviate from the mean probability, providing insight into the spread or imbalance of the distribution.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed counts.
#
# **Returns**:
# - `float`: Standard deviation of the state probabilities, rounded to six decimal places. Returns 0.0 if fewer than two unique states are present or if total counts are zero.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty or contains fewer than two unique states.
#    - Returns 0.0 if the sum of all counts is zero.
# 2. **Probability Calculation**:
#    - Converts counts into a list of probabilities by dividing each count by the total count.
# 3. **Standard Deviation Computation**:
#    - Uses `statistics.stdev()` to calculate the standard deviation of these probabilities.
# 4. **Rounding**:
#    - Rounds the result to six decimal places before returning.
#
# **Key Considerations**:
# - Low standard deviation indicates probabilities are close to uniform.
# - High standard deviation suggests certain states dominate the distribution.
# - This is a generic statistical measure and not proprietary to iQore.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# sd = stddev_state_probabilities(counts)
# print(sd)  # Example output: 0.158114
# ```
#
# **Key Operations**:
# - **sum()**: Calculates the total number of measurements.
# - **statistics.stdev()**: Computes the standard deviation of a list of values.
# --------------------------------------------------------------

import statistics

def stddev_state_probabilities(counts: dict) -> float:
    """
    Computes the standard deviation of state probabilities from a counts dictionary.
    Returns 0.0 if fewer than 2 unique states.
    """
    if not counts or len(counts) < 2:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    probabilities = [count / total for count in counts.values()]
    return round(statistics.stdev(probabilities), 6)

# ----------------------- Calculate Std Dev of State Probabilities (END) -----------------------

# --------------------------------------------------------------
# Function: `entanglement_depth_est()`
# --------------------------------------------------------------
# **Purpose**:
# Estimates entanglement depth by calculating the range of Hamming weights (maximum minus minimum) across all measured bitstrings.
# This metric serves as a heuristic indicator of how many qubits may be entangled, based on the observed diversity in qubit excitations (|1⟩ states).
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed counts.
#
# **Returns**:
# - `int` or `float`: Estimated entanglement depth as the difference between the highest and lowest Hamming weights in the reconstructed list of measured bitstrings. Returns 0 if input is empty or contains no valid data.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0 if `counts` is empty.
# 2. **Bitstring Reconstruction**:
#    - Expands `counts` into a flat list of bitstrings, repeating each bitstring according to its observed count.
# 3. **Empty Data Handling**:
#    - Returns 0 if the reconstructed list is empty.
# 4. **Hamming Weight Calculation**:
#    - Computes the Hamming weight for each bitstring using `.count('1')`.
# 5. **Depth Estimation**:
#    - Returns the difference between the maximum and minimum Hamming weights in the dataset.
#
# **Key Considerations**:
# - This is a **heuristic** and not a formal entanglement depth measure from quantum information theory.
# - Larger depth values suggest a broader range of qubit excitations, which may imply deeper or more complex entanglement.
# - Sensitive to measurement noise, which can artificially inflate the range.
#
# **Example Usage**:
# ```python
# counts = {'00': 2, '01': 3, '11': 1}
# depth_est = entanglement_depth_est(counts)
# print(depth_est)  # Example output: 2
# ```
#
# **Key Operations**:
# - **list comprehension**: Reconstructs the flat list of bitstrings.
# - **count('1')**: Determines Hamming weight of each bitstring.
# - **max() / min()**: Finds the extremes of Hamming weights to compute the range.
# --------------------------------------------------------------

def entanglement_depth_est(counts: dict) -> float:
    """
    Estimates entanglement depth as the range of Hamming weights (max - min) 
    across all bitstrings, reconstructed from counts.
    """
    if not counts:
        return 0

    # Rebuild the iqd_bits-style list
    all_bits = [bit for bit, freq in counts.items() for _ in range(freq)]
    if not all_bits:
        return 0

    weights = [bit.count('1') for bit in all_bits]
    return max(weights) - min(weights) if weights else 0

# ----------------------- Calculate Entanglement Depth Estimate (END) -----------------------

# --------------------------------------------------------------
# Function: `state_coherence_signature()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the State Coherence Signature (SCS) as the cosine similarity between the measured quantum state probability distribution and the ideal uniform distribution over the full 2^n state space.
# SCS values range from 0 (no alignment) to 1 (perfect alignment), providing a normalized measure of how closely the observed distribution matches the ideal uniform profile.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to observed counts. All keys must be of equal length, representing the number of qubits.
#
# **Returns**:
# - `float`: Cosine similarity score (SCS) between the measured and ideal distributions, rounded to six decimal places. Returns 0.0 for invalid inputs or zero-norm vectors.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty or if total counts are zero.
# 2. **State Space Generation**:
#    - Infers `qubit_count` from the length of a key in `counts`.
#    - Generates all possible bitstrings using `itertools.product`.
#    - Determines total number of possible states (`n_states`).
# 3. **Vector Construction**:
#    - Builds a NumPy array of probabilities (`iqd_probs`) for the measured distribution.
#    - Builds a NumPy array of equal probabilities (`ideal_probs`) for the ideal uniform distribution.
# 4. **Cosine Similarity Computation**:
#    - Computes the dot product between the two probability vectors.
#    - Computes the product of their Euclidean norms.
#    - Divides the dot product by the norm product to obtain cosine similarity.
# 5. **Rounding and Edge Case Handling**:
#    - Returns 0.0 if either vector has zero norm.
#    - Otherwise, returns the similarity rounded to six decimal places.
#
# **Key Considerations**:
# - This metric is **custom to your implementation** — cosine similarity for quantum probability distributions is not a standard industry measure under this name.
# - High SCS values indicate the measured distribution is well-aligned with uniformity; low values indicate bias or deviation.
# - SCS is mathematically equivalent to √(N_eff / n), where N_eff = 1 / Σ p_i² is the “effective number of states” (inverse participation ratio), related to Rényi-2 entropy.
# - Sensitive to missing states, which will lower similarity.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# scs = state_coherence_signature(counts)
# print(scs)  # Example output: 0.96...
# ```
#
# **Key Operations**:
# - **product()**: Generates all possible bitstrings for the given qubit count.
# - **np.array()**: Builds numerical vectors for probabilities.
# - **np.dot()**: Calculates the dot product between vectors.
# - **np.linalg.norm()**: Computes vector magnitudes for cosine similarity.
# --------------------------------------------------------------

def state_coherence_signature(counts: dict) -> float:
    """
    Computes the State Coherence Signature (SCS) as cosine similarity
    between the measured distribution and the ideal uniform distribution.
    Returns 0.0 if invalid input or zero-norm vectors.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    qubit_count = len(next(iter(counts.keys()), ''))
    bitstrings_full = [''.join(bits) for bits in product('01', repeat=qubit_count)]
    n_states = len(bitstrings_full)

    # Build vectors
    iqd_probs = np.array([counts.get(k, 0) / total for k in bitstrings_full])
    ideal_probs = np.array([1 / n_states] * n_states)

    dot_product = np.dot(iqd_probs, ideal_probs)
    norm_product = np.linalg.norm(iqd_probs) * np.linalg.norm(ideal_probs)

    return round(dot_product / norm_product, 6) if norm_product != 0 else 0.0

# ----------------------- Calculate State Coherence Signature (END) -----------------------

# --------------------------------------------------------------
# Function: `mean_top_5_probability()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the mean probability of the five most probable bitstrings (states) from a quantum measurement distribution.
# This metric highlights how much of the total probability mass is concentrated in the most likely outcomes.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed counts.
#
# **Returns**:
# - `float`: Mean probability of the top five most probable states, rounded to six decimal places. Returns 0.0 if the input is empty, total counts are zero, or no valid probabilities exist.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty.
#    - Returns 0.0 if the total count of all measurements is zero.
# 2. **Probability Calculation**:
#    - Converts each count to a probability by dividing by the total count.
# 3. **Sorting**:
#    - Sorts all probabilities in descending order.
# 4. **Top-5 Extraction**:
#    - Selects the first five probabilities from the sorted list (or fewer if fewer states exist).
# 5. **Averaging**:
#    - Computes the arithmetic mean of the top five probabilities.
# 6. **Rounding**:
#    - Rounds the result to six decimal places before returning.
#
# **Key Considerations**:
# - If fewer than five states exist, the mean is computed over the available states.
# - A higher mean indicates stronger concentration of probability mass in a small subset of states.
# - This is a generic statistical measure, not proprietary to iQore.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# avg_top5 = mean_top_5_probability(counts)
# print(avg_top5)  # Example output: 0.25
# ```
#
# **Key Operations**:
# - **sorted()**: Sorts the list of probabilities in descending order.
# - **np.mean()**: Computes the arithmetic mean of the top probabilities.
# --------------------------------------------------------------

def mean_top_5_probability(counts: dict) -> float:
    """
    Computes the mean probability of the top 5 most probable bitstrings.
    Returns 0.0 if counts are empty or fewer than 1 bitstring exists.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    # Get list of probabilities sorted descending
    probs = sorted((count / total for count in counts.values()), reverse=True)
    top_probs = probs[:5]

    return round(np.mean(top_probs), 6) if top_probs else 0.0

# ----------------------- Calculate mean top 5 probability (END) -----------------------

# --------------------------------------------------------------
# Function: `top_10_state_probability_mass()`
# --------------------------------------------------------------
# **Purpose**:
# Calculates the total probability mass contained in the ten most probable bitstrings (states) from a quantum measurement distribution.
# This metric quantifies how concentrated the distribution is in its most likely outcomes.
#
# **Parameters**:
# - `counts` (dict): Dictionary mapping bitstrings to their observed counts.
#
# **Returns**:
# - `float`: Total probability mass of the top ten most probable states, rounded to six decimal places. Returns 0.0 if the input is empty or total counts are zero.
#
# **Functionality**:
# 1. **Validation Checks**:
#    - Returns 0.0 if `counts` is empty.
#    - Returns 0.0 if the total count of all measurements is zero.
# 2. **Probability Calculation**:
#    - Converts each count to a probability by dividing by the total count.
# 3. **Sorting**:
#    - Sorts all `(bitstring, probability)` pairs in descending order of probability.
# 4. **Top-10 Extraction**:
#    - Selects the top ten states (or fewer if fewer states exist).
# 5. **Summation**:
#    - Sums the probabilities of the top ten states to obtain the total probability mass.
# 6. **Rounding**:
#    - Rounds the result to six decimal places before returning.
#
# **Key Considerations**:
# - If fewer than ten states exist, the sum is taken over all available states.
# - A high top-10 mass indicates strong outcome concentration, while a low mass suggests a more diffuse distribution.
# - This is a generic statistical measure, not proprietary to iQore.
#
# **Example Usage**:
# ```python
# counts = {'00': 500, '01': 300, '10': 100, '11': 100}
# mass_top10 = top_10_state_probability_mass(counts)
# print(mass_top10)  # Example output: 1.0 (since only 4 states exist)
# ```
#
# **Key Operations**:
# - **sorted()**: Sorts state-probability pairs by probability in descending order.
# - **sum()**: Computes the total probability mass of the selected states.
# --------------------------------------------------------------

def top_10_state_probability_mass(counts: dict) -> float:
    """
    Computes the total probability mass of the top 10 most probable bitstrings.
    Returns 0.0 if counts are empty.
    """
    if not counts:
        return 0.0

    total = sum(counts.values())
    if total == 0:
        return 0.0

    # Build and sort (bitstring, prob) pairs
    sorted_probs = sorted(
        ((bit, count / total) for bit, count in counts.items()),
        key=lambda x: x[1],
        reverse=True
    )

    top_10_mass = sum(prob for _, prob in sorted_probs[:10])
    return round(top_10_mass, 6)

# ----------------------- Calculate top 10 state probabilty mass (END) -----------------------

# --------------------------------------------------------------
# Function: `execute_circuit()`
# --------------------------------------------------------------
# **Purpose**:
# Executes a quantum circuit (`qc`) on either a simulator or a real quantum backend (QPU) based on the mode. 
# It performs transpilation, optimizes the circuit's layout and depth, handles depth constraints, and manages 
# the execution either in simulation or on hardware. Optionally, it can return the statevector of the quantum circuit.

# **Parameters**:
# - `qc` (QuantumCircuit): The quantum circuit to be executed.
# - `backend` (object): The quantum backend (simulator or QPU) to execute the circuit.
# - `shot_count` (int): The number of shots (measurements) for executing the circuit.
# - `service` (optional, object): The quantum service for hardware execution (QPU), typically used with QPU backends.
# - `return_statevector` (bool, optional, default=False): If True, the function returns the statevector instead of measurement results.
# - `enforce_depth` (bool, optional, default=False): If True, ensures the circuit depth is within the specified constraints (either padding or re-optimization).

# **Returns**:
# - If `return_statevector` is True:
#   - `Statevector`: The statevector of the quantum circuit.
#   - `QuantumCircuit`: The transpiled circuit used for execution.
#   - `float`: Time taken for transpilation (in milliseconds).
#   
# - If `return_statevector` is False:
#   - `dict`: A dictionary containing measurement counts from the execution.
#   - `QuantumCircuit`: The transpiled circuit used for execution.
#   - `float`: Time taken for transpilation (in milliseconds).
#   - `float`: Time taken for execution (in milliseconds).

# **Functionality**:
# 1. **Circuit Transpilation**:
#    - The quantum circuit (`qc`) is transpiled for the specified backend, optimizing its layout and routing.
#    - If `enforce_depth` is True, the circuit's depth is checked against `MIN_DEPTH` and `MAX_DEPTH`. Padding is added if the depth is below `MIN_DEPTH`, and the circuit is re-transpiled with higher optimization if it exceeds `MAX_DEPTH`.
# 2. **Execution**:
#    - If `return_statevector` is True, the circuit's measurements are removed, and the statevector is retrieved.
#    - In **Simulation Mode**: Uses `AerSimulator` to run the circuit and retrieves measurement results.
#    - In **Hardware Mode**: Uses QPU backends and the `Session` context manager for quantum hardware execution.
# 3. **Time Measurement**:
#    - The function logs the time taken for both transpilation and execution.

# **Key Considerations**:
# - The circuit depth is dynamically adjusted to fit within acceptable limits for simulation and hardware execution.
# - Supports both simulation mode (`AerSimulator`) and hardware mode (QPU backends).
# - Uses the `Session` context manager for hardware execution to manage the quantum job.
# - Extensive logging for monitoring and debugging the transpilation and execution stages.
# - Error handling ensures that any issues during circuit execution are logged and addressed.

# **Example Usage**:
# ```python
# from qiskit import Aer
# backend = Aer.get_backend('qasm_simulator')
# shot_count = 1024
# result, transpiled_qc, transpile_time, execution_time = execute_circuit(qc, backend, shot_count, return_statevector=False)
# print(f"Execution time: {execution_time} ms")
# ```

# **Key Operations**:
# - **Transpilation**: Uses Qiskit's `transpile()` method to optimize the quantum circuit for the specified backend.
# - **Statevector Retrieval**: If `return_statevector` is True, the statevector of the quantum circuit is returned.
# - **QASM Simulation**: Executes the circuit on a simulated backend (`AerSimulator`).
# - **Quantum Hardware Execution**: Executes the circuit on a QPU using the `Session` interface for real hardware execution.
# - **Logging**: Tracks transpilation, execution stages, and performance metrics for debugging and optimization.

# --------------------------------------------------------------

def execute_circuit(qc: QuantumCircuit, backend, shot_count: int, service=None, return_statevector=False, enforce_depth=False) -> tuple:

    try:
        logging.info("Starting transpilation...")
        coupling_map = backend.configuration().coupling_map if hasattr(backend.configuration(), 'coupling_map') else None
        transpile_start = time.time()

        transpiled_qc = transpile(
            qc,
            backend=backend,
            optimization_level=0,
            coupling_map=coupling_map,
            initial_layout=list(range(qc.num_qubits)),
            layout_method='sabre',
            routing_method='sabre'
        )

        transpile_time = (time.time() - transpile_start) * 1000
        current_depth = transpiled_qc.depth()
        logging.info(f"[STRUCTURED MANAGEMENT] Post-transpile depth: {current_depth}")
        if enforce_depth:
            if current_depth > MAX_DEPTH:
                #logging.warning(f"[STRUCTURED MANAGEMENT] Depth {current_depth} exceeds max allowed {MAX_DEPTH}. Re-transpiling with higher optimization...")
                # Dynamic Basis Gates Assignment ba sed on Backend Capabilities
                basis_gates = backend.configuration().basis_gates

                transpiled_qc = transpile(
                    qc,
                    backend=backend,
                    optimization_level=3,
                    initial_layout=list(range(qc.num_qubits)),
                    layout_method='sabre',
                    routing_method='sabre',
                    basis_gates=basis_gates  # Ensure compatibility with backend
                )
                new_depth = transpiled_qc.depth()
                logging.info(f"[STRUCTURED MANAGEMENT] Circuit depth after re-optimization: {new_depth}")

                if new_depth > MAX_DEPTH:
                    logging.error(f"[DEPTH ERROR] Circuit depth {new_depth} still exceeds maximum allowed depth {MAX_DEPTH}. Review circuit design.")
                    sys.exit(1)
                else:
                    logging.info(f"[DEPTH FIXED] Final optimized circuit depth is acceptable: {new_depth}")

            elif current_depth < MIN_DEPTH:
                #logging.warning(f"[STRUCTURED MANAGEMENT] Depth {current_depth} below minimum required {MIN_DEPTH}. Adding small-angle rotations for reliable padding.")
                qubit_idx = 0
                while transpiled_qc.depth() < MIN_DEPTH:
                    transpiled_qc.rz(1e-6, qubit_idx % transpiled_qc.num_qubits)
                    qubit_idx += 1
                final_depth = transpiled_qc.depth()
                logging.info(f"[STRUCTURED MANAGEMENT] Circuit depth after padding: {final_depth}")

            else:
                logging.info(f"[STRUCTURED MANAGEMENT] Circuit depth within acceptable range: {current_depth}")

        logging.info(f"[STRUCTURED MANAGEMENT] Final circuit depth: {transpiled_qc.depth()}")

        logging.info("Executing circuit...")
        if return_statevector:
            transpiled_qc.remove_final_measurements()
            statevector = Statevector.from_instruction(transpiled_qc)
            logging.info("[EXECUTION COMPLETE] Statevector retrieved successfully.")
            return statevector, transpiled_qc, transpile_time

        if isinstance(backend, AerSimulator):
            logging.info("[MODE DETECTED] Executing in SIMULATION mode using AerSimulator.")
            exec_start = time.time()
            job = backend.run(transpiled_qc, shots=shot_count)
            result = job.result()
            execution_time = (time.time() - exec_start) * 1000  # in ms

            raw_counts = result.get_counts()
            # Fix duplicated bitstrings like "00001 00001"
            counts = {}
            for bitstring, freq in raw_counts.items():
                parts = bitstring.split()
                if len(parts) == 2 and parts[0] == parts[1]:
                    counts[parts[0]] = freq
                else:
                    counts[bitstring] = freq

            logging.info("[SIMULATION EXECUTION COMPLETE] Counts retrieved successfully.")
            return counts, transpiled_qc, transpile_time, execution_time
        else:
            logging.info("[MODE DETECTED] Executing in HARDWARE mode using QPU backend.")
            with Session(backend=backend) as session:
                sampler = Sampler()
                exec_start = time.time()
                baseline_job = sampler.run([transpiled_qc], shots=shot_count, session=session)
                result = baseline_job.result()
                execution_time = (time.time() - exec_start) * 1000

                raw_counts = result[0].data.meas.get_counts()
                # Fix duplicated bitstrings like "00001 00001"
                counts = {}
                for bitstring, freq in raw_counts.items():
                    parts = bitstring.split()
                    if len(parts) == 2 and parts[0] == parts[1]:
                        counts[parts[0]] = freq
                    else:
                        counts[bitstring] = freq

                logging.info("[HARDWARE EXECUTION COMPLETE] Counts retrieved successfully.")
                return counts, transpiled_qc, transpile_time, execution_time

    except Exception as e:
        logging.error(f"[EXECUTION ERROR] Circuit execution failed: {e}")
        return None, None, None
    
# ----------------------- Execute Circuit (END) -----------------------

# --------------------------------------------------------------
# Function: `state_fidelity_from_circuits()`
# --------------------------------------------------------------
# **Purpose**:
# Computes the state fidelity between two quantum circuits, comparing their unitary states 
# (ignoring measurement outcomes) to assess the similarity of their quantum states.

# **Parameters**:
# - `actual_circuit` (QuantumCircuit): The quantum circuit representing the actual state (post-execution circuit).
# - `ideal_circuit` (QuantumCircuit): The quantum circuit representing the ideal or target state (expected outcome circuit).

# **Returns**:
# - `float`: The state fidelity value between the two circuits, as a percentage (0 to 1).
# - `"N/A (Too many qubits)"`: If the number of qubits exceeds the maximum allowed (24 qubits for statevector).
# - `"Error"`: If an error occurs during the fidelity calculation (e.g., failure in unitary extraction).

# **Functionality**:
# 1. **Preparation**:  
#    - Copies the circuits, removing measurements to focus on the unitary evolution (statevector).
#
# 2. **Statevector Representation**:  
#    - Ensures the qubit count is within the allowable limit (24 qubits) for statevector computation.
#    - Converts both circuits to statevectors (unitary form) using `Statevector.from_instruction`.
#
# 3. **Fidelity Calculation**:  
#    - Uses `state_fidelity()` to calculate the fidelity between the two statevectors, which measures the similarity of the quantum states.
#
# 4. **Error Handling**:  
#    - Handles errors gracefully by logging any issues and returning `"Error"` if fidelity calculation fails.

# **Key Considerations**:
# - Designed for circuits with a maximum of 24 qubits to avoid memory overload during statevector simulation.
# - The fidelity is calculated using the statevector (ignoring measurements), ensuring that the comparison is done based on the unitary evolution.
# - Error handling ensures robustness when calculating fidelity for large circuits or invalid operations.

# **Example Usage**:
# ```python
# actual_circuit = QuantumCircuit(3)
# ideal_circuit = QuantumCircuit(3)
# actual_circuit.h(0)
# ideal_circuit.h(0)
# fidelity = state_fidelity_from_circuits(actual_circuit, ideal_circuit)
# print(f"State Fidelity: {fidelity}")
# ```

# **Key Operations**:
# - **Statevector Extraction**: Converts quantum circuits to statevectors using `Statevector.from_instruction`.
# - **Fidelity Calculation**: Computes the fidelity using Qiskit's `state_fidelity()` function.
# - **Error Handling**: Catches errors, logs them, and returns `"Error"` if any issue arises during computation.

# --------------------------------------------------------------

def state_fidelity_from_circuits(actual_circuit: QuantumCircuit, ideal_circuit: QuantumCircuit) -> float:
    actual_circuit_no_measurements = actual_circuit.copy()
    ideal_circuit_no_measurements = ideal_circuit.copy()
    actual_circuit_no_measurements.remove_final_measurements()
    ideal_circuit_no_measurements.remove_final_measurements()
    MAX_QUBITS_FOR_STATEVECTOR = 24
    if actual_circuit.num_qubits > MAX_QUBITS_FOR_STATEVECTOR:
        return "N/A (Too many qubits)"
    try:
        actual_unitary = Statevector.from_instruction(actual_circuit_no_measurements).data
        ideal_unitary = Statevector.from_instruction(ideal_circuit_no_measurements).data
        fidelity = state_fidelity(actual_unitary, ideal_unitary)
        return fidelity
    except Exception as e:
        logging.error(f"State fidelity calculation failed: {e}")
        return "Error"

# ----------------------- State Fidelity (END) -----------------------

# --------------------------------------------------------------
# Function: `compute_gate_fidelity_from_backend()`
# --------------------------------------------------------------
# **Purpose**:
# Approximates the gate fidelity of a quantum circuit based on backend calibration data. 
# The fidelity is calculated by averaging the fidelity of each gate used in the circuit, 
# where the fidelity is computed as 1 minus the error rate for each gate (extracted from 
# the backend’s calibration data). A fallback fidelity value is used for gates without 
# calibration data.

# **Parameters**:
# - `circuit` (QuantumCircuit): The quantum circuit for which the gate fidelity is to be computed.
# - `backend` (object): The quantum backend (hardware or simulator) used to retrieve calibration data for gate fidelities.

# **Returns**:
# - `float`: The average gate fidelity of the quantum circuit, as a value between 0 and 1.
# - `-1`: If the circuit contains no gates or is empty.

# **Functionality**:
# 1. **Calibration Data Extraction**:
#    - Retrieves the backend’s calibration data using `backend.properties()`, which includes gate error rates.
#    - The error rate is used to calculate the fidelity (1 - error rate).
#
# 2. **Gate Fidelity Calculation**:
#    - For each gate in the circuit, its name and qubit indices are used to extract the corresponding calibration data.
#    - The gate fidelity is computed as `1 - gate_error` for each gate, where `gate_error` is the error rate for the gate.
#    - If no calibration data is found for a gate, a fallback fidelity value of `0.999` is used.
#
# 3. **Average Fidelity Calculation**:
#    - The total fidelity of the circuit is accumulated by adding the fidelities of all gates.
#    - The average fidelity is computed by dividing the total fidelity by the number of gates (`gate_count`).
#
# 4. **Edge Case Handling**:
#    - If the circuit contains no gates (i.e., `gate_count` is 0), the function returns `-1`, indicating that the fidelity 
#      cannot be computed for an empty circuit.

# **Key Considerations**:
# - The function relies on the backend's calibration data, which must include gate error rates for each gate in the circuit.
# - If calibration data is missing for a gate, the function uses a default fallback fidelity value (`0.999`), which may not be 
#   accurate but allows the computation to proceed.
# - The average fidelity is computed across all gates in the circuit, so circuits with more gates (especially those with higher error rates) 
#   may have a lower overall fidelity.

# **Example Usage**:
# ```python
# backend = some_backend_instance  # Example backend (QPU or simulator)
# qc = QuantumCircuit(3)
# qc.h(0)
# qc.cx(0, 1)
# fidelity = compute_gate_fidelity_from_backend(qc, backend)
# print(f"Gate Fidelity: {fidelity}")
# ```

# **Key Operations**:
# - **Gate Fidelity Calculation**: Uses the backend’s calibration data to determine the error rate and compute the fidelity.
# - **Fallback Mechanism**: If no calibration data is found for a gate, the default fallback fidelity of `0.999` is used.
# - **Average Fidelity**: Computes the overall fidelity by averaging the fidelities of all gates in the circuit.

# --------------------------------------------------------------

def compute_gate_fidelity_from_backend(circuit: QuantumCircuit, backend) -> float:
    """
    Approximates gate fidelity using backend calibration data.
    Computes 1 - average error rate over all gates used in the circuit.
    """
    props = backend.properties()
    total_fidelity = 0
    gate_count = 0

    total_fidelity = 0
    gate_count = 0
    fallback_fidelity = 0.999  # Fallback fidelity in case calibration data is missing

    for instruction in circuit.data:
        instr = instruction.operation
        qargs = instruction.qubits
        gate_name = instr.name
        qubit_indices = [circuit.qubits.index(q) for q in qargs]

        try:
            cal = next(g for g in props.gates if g.gate == gate_name and g.qubits == qubit_indices)
            error_val = next(p.value for p in cal.parameters if p.name == 'gate_error')
            gate_fid = 1 - error_val
        except StopIteration:
            #logging.warning(f"No calibration data for gate {gate_name} on qubits {qubit_indices}")
            gate_fid = fallback_fidelity  # Dynamic fallback to default fidelity
        total_fidelity += gate_fid
        gate_count += 1

    if gate_count == 0:
        return -1
    return total_fidelity / gate_count

# ----------------------- Compute Gate Fidelity (END) -----------------------

# --------------------------------------------------------------
# Function: `run_with_noise()`
# --------------------------------------------------------------
# **Purpose**:
# Simulates a quantum circuit with noise using a noise model, replicating real-world quantum behavior.
# This function executes the quantum circuit under the specified noise model and returns the measurement counts.

# **Parameters**:
# - `circuit` (QuantumCircuit): The quantum circuit to be simulated, which may include quantum gates and measurements.
# - `noise_model` (NoiseModel): The noise model to be applied during the simulation. It can include errors such as 
#   depolarizing noise, thermal relaxation, and others, simulating how noise affects the quantum circuit.
# - `backend` (Backend): The backend (typically a simulator) used to run the quantum circuit with noise.
# - `shots` (int, optional, default=1024): The number of simulation shots (repetitions of the circuit execution) used 
#   to gather statistics. More shots improve the statistical reliability of the result.

# **Returns**:
# - `dict`: A dictionary of measurement counts from the simulated quantum circuit execution. The dictionary keys 
#   are quantum states (bitstrings), and the values are the frequencies with which each state was measured across 
#   the specified number of shots.

# **Functionality**:
# 1. **Simulator Initialization**:
#    - Creates an instance of `AerSimulator` from Qiskit’s Aer simulation library, setting it to run with the specified 
#      noise model by setting `noise_model` in the simulator’s options.
#
# 2. **Circuit Execution**:
#    - Runs the quantum circuit (`circuit`) with the specified noise model for the given number of shots (`shots`). 
#      The simulation is executed using the `simulator.run()` method.
#
# 3. **Result Retrieval**:
#    - Retrieves the results using `job.result()` and calls `get_counts()` to fetch the measurement counts.
#    - The counts represent the frequency of each measured state across the simulation shots.
#
# 4. **Logging**:
#    - Logs the results of the simulation, including the measurement counts and an informational message specifying that 
#      the simulation was performed with noise.
#
# 5. **Return Value**:
#    - Returns the measurement counts as a dictionary, where the keys represent the measured quantum states (e.g., '000', '111'),
#      and the values represent how often each state was measured in the simulation.

# **Key Considerations**:
# - The noise model simulates realistic quantum effects such as gate errors, decoherence, and crosstalk.
# - The number of shots impacts the accuracy of the simulation results. More shots provide better statistical significance but
#   increase computational time.
# - This function uses the `AerSimulator` backend from Qiskit Aer, which supports noise simulation on quantum circuits.

# **Example Usage**:
# ```python
# from qiskit import QuantumCircuit
# from qiskit_aer.noise import NoiseModel
# from qiskit_aer import AerSimulator
# import logging
#
# # Define a simple quantum circuit
# qc = QuantumCircuit(2)
# qc.h(0)
# qc.cx(0, 1)
# qc.measure_all()
#
# # Define a noise model (e.g., depolarizing noise)
# noise_model = NoiseModel.from_backend(AerSimulator())
#
# # Run the circuit with noise
# counts = run_with_noise(qc, noise_model, AerSimulator(), shots=1024)
# print(counts)
# ```
#
# **Key Operations**:
# - **Noise Model Application**: Simulates real-world errors in the quantum circuit by applying the provided noise model.
# - **Shot-based Simulation**: Executes the quantum circuit a set number of times to gather statistical measurement outcomes.
# - **Result Logging**: Logs the measurement outcomes, helping track the results of the noisy simulation.

# --------------------------------------------------------------

def run_with_noise(circuit: QuantumCircuit, noise_model: NoiseModel, backend, shots: int = 1024):
    simulator = AerSimulator()
    simulator.set_options(noise_model=noise_model)
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()
    logging.info(f"Simulation with noise: {counts}")
    return counts

# ----------------------- Run With Noise (END) -----------------------

# --------------------------------------------------------------
# Function: `estimate_virtual_qubits()`
# --------------------------------------------------------------
# **Purpose**:
# Estimates the number of virtual or topological qubits required for executing a quantum circuit with 
# a given complexity, based on entanglement and temporal overlap. This function simulates the qubit expansion 
# in a non-QEC (Quantum Error Correction) hybrid architecture and uses a nonlinear model to determine 
# the virtual qubit count based on circuit depth and two-qubit gate count.

# **Parameters**:
# - `depth` (int): The depth of the quantum circuit, representing the number of layers of gates applied 
#   to the quantum state. Higher depths typically introduce more entanglement and circuit complexity.
# - `two_qubit_gate_count` (int): The number of two-qubit gates in the circuit, directly affecting the 
#   entanglement level. More two-qubit gates lead to more entanglement and, consequently, more virtual qubits.
# - `logical_qubits` (int): The initial number of qubits in the circuit (logical qubits) before accounting 
#   for the expansion due to entanglement and overlap.

# **Returns**:
# - `int`: The estimated number of virtual or topological qubits required to execute the quantum circuit, 
#   accounting for complexity and entanglement. The returned value represents the overhead due to entanglement 
#   and temporal effects, rounded to the nearest integer.

# **Functionality**:
# 1. **Entanglement Density**:
#    - The function calculates the entanglement density as the ratio of two-qubit gates to logical qubits. 
#      This represents how much entanglement is introduced by the circuit.
#
# 2. **Temporal Overlap**:
#    - Temporal overlap is computed as the ratio of the circuit's depth to the number of logical qubits. 
#      This represents how the circuit’s complexity evolves over time.
#
# 3. **Empirical Coefficients**:
#    - The function uses empirically tuned coefficients for entanglement-induced expansion (`ent_coeff`) 
#      and temporal scaling (`time_coeff`). These coefficients were derived based on hybrid simulations and 
#      quantum processing unit (QPU) data.
#
# 4. **Nonlinear Scaling**:
#    - The scaling factor is computed using a nonlinear activation model, incorporating `tanh` for entanglement 
#      and `log1p` for temporal overlap. These functions help to ensure that the scaling saturates after reaching 
#      a certain threshold, preventing unrealistic qubit growth in deep circuits.
#
# 5. **Virtual Qubit Estimation**:
#    - The estimated number of virtual qubits is calculated by multiplying the number of logical qubits by the 
#      scaling factor (minus one), then rounding to the nearest integer. This represents the overhead in qubits 
#      required due to entanglement and temporal effects.
#
# **Key Considerations**:
# - The function models the emergent expansion of virtual qubits in a non-QEC hybrid architecture. 
#   It does not assume the use of surface codes or traditional QEC methods.
# - Nonlinear scaling ensures that the estimate remains realistic for both small and large circuits.
# - The empirical coefficients (`ent_coeff` and `time_coeff`) can be adjusted based on experimental data or simulation results to refine the model.

# **Example Usage**:
# ```python
# depth = 100
# two_qubit_gate_count = 150
# logical_qubits = 20
# virtual_qubits_estimate = estimate_virtual_qubits(depth, two_qubit_gate_count, logical_qubits)
# print(f"Estimated Virtual Qubits: {virtual_qubits_estimate}")
# ```

# **Key Operations**:
# - **Entanglement Density**: Computes the ratio of two-qubit gates to logical qubits.
# - **Temporal Overlap**: Computes the ratio of circuit depth to logical qubits.
# - **Nonlinear Scaling**: Uses `tanh` and `log1p` functions to scale the virtual qubits realistically.
# - **Virtual Qubit Estimation**: Estimates the number of virtual qubits by multiplying the scaling factor with the logical qubits.

# -------------------------------------------------------------------

def estimate_virtual_qubits(depth: int, two_qubit_gate_count: int, logical_qubits: int) -> int:
    """
    Estimate virtual/topological qubits based on circuit complexity in a non-QEC hybrid architecture.
    
    This model captures emergent spatial-temporal qubit expansion from entanglement,
    without relying on surface code assumptions.
    
    Uses nonlinear activation to saturate scaling, ensuring stability across circuit sizes.
    """
    import math
    import numpy as np

    if logical_qubits == 0:
        return 0

    # Core metrics
    entanglement_density = two_qubit_gate_count / logical_qubits
    temporal_overlap = depth / logical_qubits

    # Tuned empirical coefficients (based on hybrid simulation + QPU)
    ent_coeff = 0.22  # strength of entanglement-induced expansion
    time_coeff = 0.08  # temporal scaling rate

    # Nonlinear saturation using tanh and log1p for realistic scaling
    scaling_factor = 1 + ent_coeff * np.tanh(entanglement_density) + time_coeff * np.log1p(temporal_overlap)

    # Estimated virtual/topological qubit overhead
    virtual_qubits = logical_qubits * (scaling_factor - 1)

    return math.ceil(virtual_qubits)

# -------------------- Virtual Qubit Estimator (END) --------------------

# --------------------------------------------------------------
# Function: `export_results_to_files()`
# --------------------------------------------------------------
# **Purpose**:
# Exports the results of a quantum circuit execution to multiple file formats (CSV, JSON, PDF).
# This function creates a directory to store the results and saves the data in structured formats 
# for easy retrieval and further analysis. The output includes state counts, fidelity measures, 
# total variation distance (TVD), and additional circuit performance metrics.

# **Parameters**:
# - `save_path` (str): The directory path where the results will be saved. If the directory does not exist, it will be created.
# - `test_name` (str): A string representing the name of the test. This will be used as a prefix for the saved files.
# - `iqd_counts` (dict): A dictionary containing the counts of the quantum states from the iQD execution.
# - `baseline_counts` (dict): A dictionary containing the counts of the quantum states from the baseline circuit execution.
# - `output_fid` (float): The Output Fidelity value calculated from the comparison between the iQD and baseline circuits.
# - `backend_performance` (dict): A dictionary containing performance metrics for the backend (e.g., QPU or simulator).
# - `tvd` (float): The total variation distance between the iQD counts and baseline counts, representing the divergence.
# - `metrics` (dict): A dictionary containing general performance metrics of the quantum circuit execution.
# - `advanced_metrics` (dict): A dictionary containing advanced metrics of the quantum circuit execution.

# **Returns**:
# - `None`: This function does not return any value. It performs file writing operations and logs the completion.

# **Functionality**:
# - **Directory Creation**:  
#   The function first ensures the existence of the directory specified by `save_path` using `os.makedirs()`. 
#   If the directory does not exist, it will be created.
#
# - **CSV File Export**:  
#   The function exports the `iqd_counts` (quantum state counts from the iQD execution) to a CSV file. 
#   It writes the state names and their corresponding counts to the file, allowing for easy analysis of the raw output.
#
# - **JSON File Export**:  
#   The results from `iqd_counts` are also saved in a JSON file, providing a structured data format that can 
#   be easily loaded for further programmatic analysis or reporting.
#
# - **PDF Report Generation**:  
#   A PDF report is generated that summarizes the results of the quantum circuit execution. This includes:
#   - **Title and Timestamp**: The name of the test and the timestamp of when the report was generated.
#   - **Circuit Metrics**: General performance metrics are printed in the PDF, providing key details of the execution.
#   - **Advanced Metrics**: Additional advanced metrics are included, offering a deeper level of analysis of the execution.
#   - **Output Fidelity and TVD**: The report includes the calculated Output Fidelity (percentage) and total variation distance.
#   - **Footer**: A footer is added with a copyright message, marking the report as proprietary and confidential to iQore.
#
# - **Logging**:  
#   The function logs the path to the saved PDF file, confirming the completion of the export process.

# **Key Considerations**:
# - The function handles three output formats (CSV, JSON, and PDF), making the results available for both programmatic analysis 
#   (via CSV and JSON) and human-readable reports (via PDF).
# - The function includes both basic and advanced circuit performance metrics, giving a comprehensive view of the quantum execution.
# - It ensures that the output files are saved in the specified directory (`save_path`), which is created if it doesn't exist.
# - The PDF report includes detailed information on the execution metrics, including fidelity, total variation distance, and other circuit-specific data.

# **Example Usage**:
# ```python
# save_path = "/path/to/results"
# test_name = "test_001"
# export_results_to_files(save_path, test_name, iqd_counts, baseline_counts, output_fid, backend_performance, tvd, metrics, advanced_metrics)
# ```

# **Key Operations**:
# - **CSV Export**: Uses the `csv.writer` to save the quantum state counts in CSV format.
# - **JSON Export**: Uses `json.dump` to save the quantum state counts in JSON format.
# - **PDF Generation**: Uses `FPDF` to generate a report that includes the test name, timestamp, metrics, and results.
# - **Logging**: Uses `logging.info()` to log the successful saving of the PDF report.

# ----------------------- Export Results -----------------------

import os, json, csv
from datetime import datetime
from fpdf import FPDF

def export_results_to_files(save_path: str, test_name: str,
                            iqd_counts: dict, baseline_counts: dict,
                            output_fid: float, backend_performance: dict, tvd: float,
                            metrics: dict, advanced_metrics: dict, execution_data: dict) -> None:
    os.makedirs(save_path, exist_ok=True)

    # -----------------------
    # 1. Save full_report.json
    # -----------------------
    full_report = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "mode": execution_data.get("mode", "Unknown"),
        "qubit_count": execution_data.get("qubit_count"),
        "backend_performance": backend_performance,
        "baseline_type": execution_data.get("baseline_type"),
        "iqd_counts": iqd_counts,
        "baseline_counts": baseline_counts,
        "output_fidelity": f"{output_fid:.6f}",
        "total_variation_distance": tvd,
        "metrics": metrics,
        "advanced_metrics": advanced_metrics,
        "execution_times": {
            "iqd_transpile_time_ms": f"{execution_data.get('iqd_transpile_time_ms', 0):.6f}",
            "iqd_execution_time_ms": f"{execution_data.get('iqd_execution_time_ms', 0):.6f}" if execution_data.get("mode") == "S" else f"{execution_data.get('iqd_exe_time', 0):.6f}",
            "baseline_transpile_time_ms": f"{execution_data.get('baseline_transpile_time_ms', 0):.6f}",
            "baseline_execution_time_ms": f"{execution_data.get('baseline_execution_time_ms', 0):.6f}" if execution_data.get("mode") == "S" else f"{execution_data.get('baseline_exe_time', 0):.6f}"
            },
        "job_ids": {
            "iqd_job_id": execution_data.get("iqd_job_id"),
            "baseline_job_id": execution_data.get("baseline_job_id")
        }
    }

    # -----------------------
    # 2. Save full_report.pdf
    # -----------------------
    pdf_file_path = os.path.join(save_path, "full_report.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def add_header(title: str):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=title, ln=True)
        pdf.set_font("Arial", size=10)

    def add_kv_section(section: dict, title: str):
        add_header(title)
        for k, v in section.items():
            pdf.multi_cell(0, 8, f"{k}: {v}")
        pdf.ln(2)

    # -----------------------
    # Helpers
    # -----------------------
    m  = full_report.get("metrics", {})
    a  = full_report.get("advanced_metrics", {})
    bp = full_report.get("backend_performance", {})
    et = full_report.get("execution_times", {})
    jobs = full_report.get("job_ids", {})

    def fmt_num(v, ndigits=None, default="N/A"):
        # format numbers; pass through strings/None safely
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return str(round(v, ndigits)) if ndigits is not None else str(v)
        return str(v)

    # -----------------------
    # Header and Footer
    # -----------------------
    class ReportPDF(FPDF):
        def header(self):
        # Set font for header
            self.set_font("Arial", "B", 12)
            # Title line
            self.cell(0, 10, f"iQD Execution Report - {self.test_name}", ln=True, align='C')
            # Timestamp line
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            self.ln(2)  # Space after header
        
        def footer(self):
            self.set_y(-20)
            self.set_font("Arial", "I", 10)
            self.multi_cell(
                0, 5,
                "© 2025 iQore. Proprietary and Confidential.\n"
                "Unauthorized distribution or disclosure of this report is prohibited.",
                align='C'
            )

            # Page number (bottom right)
            self.set_y(-10)  # Slightly lower
            self.cell(0, 5, f"Page {self.page_no()}", align='R')

    pdf = ReportPDF()
    pdf.test_name = test_name  # Pass dynamic value to the header
    pdf.set_auto_page_break(True, margin=20)  # leave space for the footer
    pdf.add_page()

    # -----------------------
    # Execution Overview
    # -----------------------
    add_header("Execution Overview")

    execution_mode_str = "Hardware (H)" if full_report.get("mode") == "H" else "Simulation (S)"
    pdf.cell(0, 6, f"Test ID: {test_name}", ln=True)
    pdf.cell(0, 6, f"Execution Mode: {execution_mode_str}", ln=True)

    backend_name = bp.get("Backend Name", "N/A")
    pdf.cell(0, 6, f"Backend: {backend_name}", ln=True)

    qubits = full_report.get("qubit_count", "N/A")
    pdf.cell(0, 6, f"Qubit Count: {qubits}", ln=True)

    shots = bp.get("Shot Count", "N/A")
    shots_str = f"{shots:,}" if isinstance(shots, int) else str(shots)
    pdf.cell(0, 6, f"Shots: {shots_str}", ln=True)

    pdf.cell(0, 6, f"iQD Job ID: {jobs.get('iqd_job_id','N/A')}", ln=True)
    pdf.cell(0, 6, f"Baseline Job ID: {jobs.get('baseline_job_id','N/A')}", ln=True)
    pdf.ln(2)

    # -----------------------
    # Execution Timing (ms)
    # -----------------------
    add_header("Execution Timing (ms)")
    # Baseline Section
    pdf.set_font("Arial", "B", 12)  # Bold for subheader
    pdf.cell(0, 6, "Baseline", ln=True)
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.cell(0, 6, f"Transpile Time (Baseline): {fmt_num(et.get('baseline_transpile_time_ms'))}", ln=True)
    pdf.cell(0, 6, f"Execution Time (Baseline): {fmt_num(et.get('baseline_execution_time_ms'))}", ln=True)
    pdf.ln(2)
    # iQD Optimized Section
    pdf.set_font("Arial", "B", 12)  # Bold for subheader
    pdf.cell(0, 6, "iQD Optimized", ln=True)
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.cell(0, 6, f"Transpile Time (iQD):      {fmt_num(et.get('iqd_transpile_time_ms'))}", ln=True)
    pdf.cell(0, 6, f"Execution Time (iQD):      {fmt_num(et.get('iqd_execution_time_ms'))}", ln=True)
    pdf.ln(2)

    # -----------------------
    # Circuit Complexity 
    # -----------------------
    add_header("Circuit Complexity")
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.multi_cell(0, 6, f"Baseline Type: {full_report.get('baseline_type', 'N/A')}")
    
    # Baseline metrics
    pdf.set_font("Arial", "B", 12)  # Bold for subheader
    pdf.cell(0, 6, "Baseline", ln=True)
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.multi_cell(0, 6, f"Circuit Depth (Baseline): {m.get('Baseline Circuit Depth', 'N/A')}")
    pdf.multi_cell(0, 6, f"Total Gate Count (Baseline): {m.get('Baseline Total Gate Count', 'N/A')}")
    pdf.multi_cell(0, 6, f"Single-Qubit Gates (Baseline): {m.get('Baseline Single-Qubit Gates', 'N/A')}")
    pdf.multi_cell(0, 6, f"Two-Qubit Gates (Baseline): {m.get('Baseline Two-Qubit Gates', 'N/A')}")
    pdf.ln(2)

    # iQD metrics
    pdf.set_font("Arial", "B", 12)  # Bold for subheader
    pdf.cell(0, 6, "iQD Optimized", ln=True)
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.multi_cell(0, 6, f"Circuit Depth (iQD): {m.get('iQD Circuit Depth', 'N/A')}")
    pdf.multi_cell(0, 6, f"Total Gate Count (iQD): {m.get('iQD Total Gate Count', 'N/A')}")
    pdf.multi_cell(0, 6, f"Single-Qubit Gates (iQD): {m.get('iQD Single-Qubit Gates', 'N/A')}")
    pdf.multi_cell(0, 6, f"Two-Qubit Gates (iQD): {m.get('iQD Two-Qubit Gates', 'N/A')}")
    pdf.ln(2)

    # -----------------------
    # Gate Quality
    # -----------------------
    add_header("Gate Quality")
    
    pdf.multi_cell(0, 6, f"Average Gate Fidelity (Baseline): {fmt_num(m.get('Baseline Gate Fidelity'))}")
    pdf.multi_cell(0, 6, f"Average Gate Fidelity (iQD): {fmt_num(m.get('iQD Gate Fidelity'))}")
    pdf.ln(2)

    # -----------------------
    # Backend Calibration Summary
    # -----------------------
    add_header("Backend Calibration Summary")
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.cell(0, 6, f"Avg T1 (µs): {fmt_num(a.get('Backend Avg T1'), 2)}", ln=True)
    pdf.cell(0, 6, f"Avg T2 (µs): {fmt_num(a.get('Backend Avg T2'), 2)}", ln=True)
    # a['Backend Avg Readout Error'] is a fraction (e.g., 0.0191). Show as %
    readout_err = a.get('Backend Avg Readout Error')
    readout_str = f"{round(readout_err*100, 2)}%" if isinstance(readout_err, (int,float)) else fmt_num(readout_err)
    pdf.cell(0, 6, f"Avg Readout Error: {readout_str}", ln=True)
    pdf.ln(2)

    # Page 2
    # -----------------------
    # Fidelity Metrics
    # -----------------------
    add_header("Fidelity Metrics")
    pdf.set_font("Arial", "", 10)   # Reset to normal
    pdf.multi_cell(0, 6, f"Output Fidelity (%): {fmt_num(m.get('Output Fidelity (%)'))}")
    pdf.multi_cell(0, 6, f"Fidelity (iQD vs Baseline): {fmt_num(m.get('Fidelity (iQD vs Baseline)'))}")
    pdf.multi_cell(0, 6, f"Fidelity vs Ideal (Baseline): {fmt_num(m.get('Fidelity vs Ideal (Baseline)'))}")
    pdf.multi_cell(0, 6, f"Fidelity vs Ideal (iQD): {fmt_num(m.get('Fidelity vs Ideal (iQD)'))}")
    pdf.ln(2)

    # -----------------------
    # Information Theory & Statistical Metrics
    # -----------------------
    add_header("Information Theory & Statistical Metrics")
    pdf.cell(0, 6, f"Entropy (iQD, bits): {fmt_num(m.get('Output Entropy (iQD, bits)'), 4)}", ln=True)
    pdf.cell(0, 6, f"KL Divergence (iQD vs Ideal): {fmt_num(m.get('KL Divergence vs Ideal (iQD)'), 6)}", ln=True)
    pdf.cell(0, 6, f"Total Variation Distance (iQD vs Baseline): {fmt_num(m.get('Total Variation Distance'), 4)}", ln=True)
    pdf.cell(0, 6, f"TVD (iQD vs Ideal): {fmt_num(m.get('TVD (iQD vs Ideal)'), 4)}", ln=True)
    pdf.cell(0, 6, f"Average Hamming Weight (iQD): {fmt_num(m.get('Average Hamming Weight (iQD)'), 4)}", ln=True)
    pdf.cell(0, 6, f"Std Dev of State Probabilities: {fmt_num(m.get('Std Dev of State Probabilities (iQD)'), 6)}", ln=True)
    pdf.cell(0, 6, f"Max State Probability (iQD): {fmt_num(m.get('Max State Probability (iQD)'), 4)}", ln=True)
    pdf.ln(2)

    # -----------------------
    # Qubit Utilization
    # -----------------------
    add_header("Qubit Utilization")
    pdf.cell(0, 6, f"Estimated Virtual Qubits: {fmt_num(m.get('Estimated Virtual Qubits'))}", ln=True)
    pdf.cell(0, 6, f"Topological Qubit Count (TQC): {fmt_num(m.get('Topological Qubit Count (TQC)'))}", ln=True)
    pdf.cell(0, 6, f"Entanglement Depth Estimate: {fmt_num(m.get('Entanglement Depth Estimate (iQD)'))}", ln=True)
    pdf.cell(0, 6, f"Structured Coherence Score (SCS): {fmt_num(m.get('SCS (iQD)'), 6)}", ln=True)
    pdf.ln(2)

    # -----------------------
    # State Probability Distribution
    # -----------------------
    add_header("State Probability Distribution")
    pdf.cell(0, 6, f"Mean Top 5 State Probability: {fmt_num(m.get('Mean Top 5 Prob (iQD)'))}", ln=True)
    pdf.cell(0, 6, f"Top 10 State Probability Mass: {fmt_num(m.get('Top 10 State Probability Mass (iQD)'))}", ln=True)
    pdf.cell(0, 6, f"Total Unique States (iQD): {len(iqd_counts)}", ln=True)
    pdf.cell(0, 6, f"Total Unique States (Baseline): {len(baseline_counts)}", ln=True)
    pdf.ln(2)

    pdf.output(pdf_file_path)
    logging.info(f"PDF report saved at: {pdf_file_path}")

    # -----------------------
    # 3. Save baseline_bitstrings.csv
    # -----------------------
    baseline_csv_path = os.path.join(save_path, "bitstring_counts_baseline.csv")
    with open(baseline_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Bitstring", "Count"])
        for bit, count in sorted(baseline_counts.items()):
            writer.writerow([bit, count])
    logging.info(f"Baseline bitstring CSV saved at: {baseline_csv_path}")

    # -----------------------
    # 4. Save iqd_bitstrings.csv
    # -----------------------
    iqd_csv_path = os.path.join(save_path, "bitstring_counts_iqd.csv")
    with open(iqd_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Bitstring", "Count"])
        for bit, count in sorted(iqd_counts.items()):
            writer.writerow([bit, count])
    logging.info(f"iQD bitstring CSV saved at: {iqd_csv_path}")

    # -----------------------
    # 5. Save PDF-mirrored JSON
    # -----------------------
    pdf_mirrored_json = {
        "Execution Overview": {
            "Test ID": test_name,
            "Execution Mode": "Hardware (H)" if full_report.get("mode") == "H" else "Simulation (S)",
            "Backend": bp.get("Backend Name", "N/A"),
            "Qubit Count": full_report.get("qubit_count", "N/A"),
            "Shots": bp.get("Shot Count", "N/A"),
            "iQD Job ID": jobs.get("iqd_job_id", "N/A"),
            "Baseline Job ID": jobs.get("baseline_job_id", "N/A")
        },
        "Execution Timing (ms)": {
            "Baseline": {
                "Transpile Time (Baseline)": et.get("baseline_transpile_time_ms"),
                "Execution Time (Baseline)": et.get("baseline_execution_time_ms")
            },
            "iQD Optimized": {
                "Transpile Time (iQD)": et.get("iqd_transpile_time_ms"),
                "Execution Time (iQD)": et.get("iqd_execution_time_ms")
            }
        },
        "Circuit Complexity": {
            "Baseline Type": full_report.get("baseline_type", "N/A"),
            "Baseline": {
                "Circuit Depth (Baseline)": m.get("Baseline Circuit Depth", "N/A"),
                "Total Gate Count (Baseline)": m.get("Baseline Total Gate Count", "N/A"),
                "Single-Qubit Gates (Baseline)": m.get("Baseline Single-Qubit Gates", "N/A"),
                "Two-Qubit Gates (Baseline)": m.get("Baseline Two-Qubit Gates", "N/A")
            },
            "iQD Optimized": {
                "Circuit Depth (iQD)": m.get("iQD Circuit Depth", "N/A"),
                "Total Gate Count (iQD)": m.get("iQD Total Gate Count", "N/A"),
                "Single-Qubit Gates (iQD)": m.get("iQD Single-Qubit Gates", "N/A"),
                "Two-Qubit Gates (iQD)": m.get("iQD Two-Qubit Gates", "N/A")
            }
        },
        "Gate Quality": {
            "Average Gate Fidelity (Baseline)": m.get("Baseline Gate Fidelity"),
            "Average Gate Fidelity (iQD)": m.get("iQD Gate Fidelity")
        },
        "Backend Calibration Summary": {
            "Avg T1 (µs)": a.get("Backend Avg T1"),
            "Avg T2 (µs)": a.get("Backend Avg T2"),
            "Avg Readout Error": (
                f"{round(a.get('Backend Avg Readout Error')*100, 2)}%"
                if isinstance(a.get('Backend Avg Readout Error'), (int, float))
                else a.get('Backend Avg Readout Error')
            )
        },
        "Fidelity Metrics": {
            "Output Fidelity (%)": m.get("Output Fidelity (%)"),
            "Fidelity (iQD vs Baseline)": m.get("Fidelity (iQD vs Baseline)"),
            "Fidelity vs Ideal (Baseline)": m.get("Fidelity vs Ideal (Baseline)"),
            "Fidelity vs Ideal (iQD)": m.get("Fidelity vs Ideal (iQD)")
        },
        "Information Theory & Statistical Metrics": {
            "Entropy (iQD, bits)": m.get("Output Entropy (iQD, bits)"),
            "KL Divergence (iQD vs Ideal)": m.get("KL Divergence vs Ideal (iQD)"),
            "Total Variation Distance (iQD vs Baseline)": m.get("Total Variation Distance"),
            "TVD (iQD vs Ideal)": m.get("TVD (iQD vs Ideal)"),
            "Average Hamming Weight (iQD)": m.get("Average Hamming Weight (iQD)"),
            "Std Dev of State Probabilities": m.get("Std Dev of State Probabilities (iQD)"),
            "Max State Probability (iQD)": m.get("Max State Probability (iQD)")
        },
        "Qubit Utilization": {
            "Estimated Virtual Qubits": m.get("Estimated Virtual Qubits"),
            "Topological Qubit Count (TQC)": m.get("Topological Qubit Count (TQC)"),
            "Entanglement Depth Estimate": m.get("Entanglement Depth Estimate (iQD)"),
            "Structured Coherence Score (SCS)": m.get("SCS (iQD)")
        },
        "State Probability Distribution": {
            "Mean Top 5 State Probability": m.get("Mean Top 5 Prob (iQD)"),
            "Top 10 State Probability Mass": m.get("Top 10 State Probability Mass (iQD)"),
            "Total Unique States (iQD)": len(iqd_counts),
            "Total Unique States (Baseline)": len(baseline_counts)
        },
        "baseline_counts": dict(baseline_counts),
        "iqd_counts": dict(iqd_counts)
    }

    json_display_path = os.path.join(save_path, "full_report_display.json")
    with open(json_display_path, "w") as f:
        json.dump(pdf_mirrored_json, f, indent=4)
    logging.info(f"PDF-mirrored JSON report saved at: {json_display_path}")

# ----------------------- Export Results (END)-----------------------

# --------------------------------------------------------------
# Function: `get_true_execution_time_ms()`
# --------------------------------------------------------------
# **Purpose**:
# Retrieves the true execution time in milliseconds for a given job by calculating the time difference
# between the "start" and "end" timestamps provided in the job metadata.
# This function is designed to handle different types of timestamps that indicate when the job started
# and when it finished, returning the execution time as a float value in milliseconds.

# **Parameters**:
# - `job` (QiskitRuntimeService.Job): The job object from which the metadata is extracted. It contains the execution timestamps.

# **Returns**:
# - `float`: The execution time of the job in milliseconds. Returns `-1` if timestamps are unavailable or invalid.

# **Functionality**:
# - Extracts the "running" and "completed" timestamps from the job metadata, if available, and calculates
#   the time difference between them in milliseconds.
# - If the "running" timestamp is unavailable, it uses the "queued" timestamp as the start time. Similarly,
#   if the "completed" timestamp is unavailable, it uses the "creation" timestamp as the end time.
# - If valid timestamps are found, the difference between the start and end times is multiplied by 1000
#   to convert it to milliseconds and returned.
# - If no valid timestamps are available, the function returns `-1` to indicate an error in fetching execution time.

# **Key Considerations**:
# - The function ensures that the start and end timestamps are either in float or int formats before performing the calculation.
# - If valid timestamps are not present, it returns `-1` to indicate an error or missing data.
# - The function relies on job metadata, which may vary depending on the quantum backend or job status.

# ----------------------- Execution Time -----------------------

def get_true_execution_time_ms(job) -> float:
    timestamps = job.metadata.get("timestamps", {})
    #print("DEBUG timestamps:", timestamps)
    start = timestamps.get("running") or timestamps.get("queued")
    end = timestamps.get("completed") or timestamps.get("creation")
    if isinstance(start, (float, int)) and isinstance(end, (float, int)):
        return (end - start) * 1000
    return -1

# ----------------------- Execution Time (END)-----------------------

# --------------------------------------------------------------
# Function: `retrieve_full_raw_data()`
# --------------------------------------------------------------
# **Purpose**:
# Retrieves comprehensive raw data from a completed job, including counts, probabilities, backend properties, 
# backend configuration, and additional metadata. This function assembles all relevant data into a structured 
# dictionary for further analysis or reporting.

# **Parameters**:
# - `job_id` (str): The ID of the job from which raw data needs to be retrieved.
# - `service` (QiskitRuntimeService): The service instance that provides access to job details.

# **Returns**:
# - `dict`: A dictionary containing various data related to the job execution, including state counts, probabilities,
#   backend properties, configuration, metadata, and more.

# **Functionality**:
# - The function retrieves the job object using the `job_id` and calls `job.result()` to get the job results.
# - It extracts the `meas.get_counts()` from the result and computes the normalized probabilities for each quantum state.
# - The `backend_properties` and `backend_configuration` are extracted from the job's backend object and converted to dictionaries.
# - The metadata related to the job, including `transpilation_metadata`, is retrieved from the job's metadata and added to the output.
# - The job's current status is fetched and added to the dictionary, along with the run options, if available.
# - All the gathered data is returned as a structured dictionary for easy access and further analysis.

# **Key Considerations**:
# - The function assumes the job is completed, and it depends on the job metadata and result object to extract relevant data.
# - The function collects data from both the quantum backend (e.g., qubit properties and configuration) and job execution (e.g., counts, status).
# - It combines different types of information (e.g., counts, probabilities, backend data) into a single dictionary for easy consumption.
# - The function ensures that all required job metadata and backend details are included in the output, making it suitable for comprehensive analysis.

# ----------------------- Raw Data Retrieval -----------------------

def retrieve_full_raw_data(job_id: str, service: QiskitRuntimeService) -> dict:
    job = service.job(job_id)
    result = job.result()
    backend = job.backend()

    # Check if the result contains the expected measurement data
    if hasattr(result[0].data, 'meas') and result[0].data.meas is not None:
        counts = result[0].data.meas.get_counts()

    else:
        # Log and handle missing measurement data for specific circuits like QPE
        print(f"Warning: 'meas' or 'counts' data not found for job {job_id}.")
        counts = {}

    total_shots = sum(counts.values()) if counts else 0
    probabilities = {state: count / total_shots for state, count in counts.items()} if total_shots else {}

    raw_data = {
        'counts': counts,
        'probabilities': probabilities,  # computed probabilities
        'backend_properties': backend.properties().to_dict(),
        'backend_configuration': backend.configuration().to_dict(),  # additional
        'execution_metadata': job.metadata,
        'transpilation_metadata': job.metadata.get('transpilation_metadata', {}),
        'job_status': job.status(),  # corrected to current API
        'run_options': job.inputs.get('run_options', {})  # additional
    }

    # If the counts are missing for QPE or any other reason, make sure raw_data can be used downstream.
    if not counts:
        raw_data['message'] = "No measurement data returned."
    
    return raw_data
    
# ----------------------- Retrieve Full Raw Data  (END)-----------------------

# --------------------------------------------------------------
# Function: `main_execute()`
# --------------------------------------------------------------
# **Purpose**:
# Orchestrates the execution of a quantum circuit in both simulation and hardware modes, 
# managing all steps from circuit transpilation, backend selection, to execution and result collection. 
# This function performs detailed timing analysis, collects performance data, and saves the results to files.

# **Parameters**:
# - None. The function uses user input collected via `get_user_input()`.

# **Returns**:
# - `None`: The function does not return a value. It writes the results to a file and logs important information.

# **Functionality**:
# - The function begins by collecting user input using `get_user_input()` and parsing necessary parameters such as:
#   - `mode`: Whether the execution is for hardware ("H") or simulation ("S").
#   - `test_name`, `qubit_count`, `shot_count`, and `baseline_type`: Other execution details for reporting.
# - **Backend Selection**: Calls `select_backend(user_input)` to select an appropriate quantum backend (either simulator or hardware) based on the mode.
# - **Circuit Generation**:
#   - Calls `build_baseline_circuit()` to construct the baseline circuit based on user input.
#   - Calls `build_iqd_circuit()` to create the iQD quantum circuit with additional entanglement and tensor control.
# - **Execution Flow**:
#   - If the mode is **hardware** ("H"):
#     - The function performs transpilation of both circuits using `transpile_circuit()`, measuring the time for each step.
#     - It executes the circuits using `Sampler.run()`, measuring the execution time.
#     - Performance data including job IDs, transpilation time, and execution time are collected.
#   - If the mode is **simulation** ("S"):
#     - The function executes the circuits using the `execute_circuit()` function, capturing both the transpilation and execution times.
#     - Quantum counts (results) from the simulation are captured.
# - **Result Collection**:
#   - Whether in hardware or simulation mode, the function constructs a dictionary (`execution_data`) containing detailed execution metrics such as:
#     - Transpiled circuit QASM for both baseline and iQD circuits.
#     - Execution times and other timing data (transpile time, execution time, etc.).
#   - In hardware mode, job IDs and associated logs are also included.
# - **Result Storage**:
#   - The execution data is written to a file in JSON format within the `iQD_Test` directory. The file is named based on the test name.
#   - Log entries are generated throughout to track the execution flow, circuit transpilation, and hardware execution times.

# **Key Considerations**:
# - **Simulation Mode**: Executes circuits on a local simulator using Qiskit AerSimulator and logs timing and results.
# - **Hardware Mode**: Executes circuits on a quantum processing unit (QPU), retrieves results from the backend, and logs detailed metrics.
# - **Performance Tracking**: Detailed tracking of transpilation time, execution time, and job durations for both baseline and iQD circuits.
# - **Execution Time Calculation**: Uses `get_true_execution_time_ms()` to capture accurate execution time in milliseconds for hardware jobs.
# - **Job Management**: Efficient handling of both transpilation and execution phases with job ID tracking and error handling.
# - **Data Export**: Saves all relevant execution data in JSON format for easy retrieval, documentation, and analysis.

# **Example Usage**:
# ```python
# main_execute()  # The function is designed to be called directly as the main execution routine.
# ```

# **Key Operations**:
# - **Circuit Transpilation**: Converts circuits into formats suitable for backend execution, with depth constraints and optimizations.
# - **Backend Selection**: Decides between hardware or simulation mode based on user input and available backends.
# - **Job Execution**: Runs the circuits and gathers performance metrics, distinguishing between simulation and hardware execution.
# - **Data Logging**: Logs all major events, execution times, and job details for later analysis.
# - **Result Saving**: Exports results to a structured JSON file for future reference or further processing.

# ----------------------- Execute Function -----------------------

def main_execute() -> None:
    # Collect user input
    user_input = get_user_input()
    mode = user_input["mode"]
    test_name = user_input["test_name"]
    qubit_count = user_input["qubit_count"]
    shot_count = user_input["shot_count"]
    baseline_type = user_input["baseline_type"] 
    
    # First, select the backend based on the user input
    backend, service = select_backend(user_input)
    
    # Now, we can safely create the circuits, passing the optimize flag to the iQD circuit
    baseline_circuit = build_baseline_circuit(
        qubit_count=user_input["qubit_count"],
        baseline_choice=user_input["baseline_choice"],
        user_circuit=user_input.get("user_circuit")  # user_circuit will be None if not provided
    )

    # Modify the build_iqd_circuit call to pass the 'optimize' flag
    iqd_circuit = build_iqd_circuit(
        qubit_count, 
        backend, 
        dimension=user_input["dimension"], 
        optimize=user_input["optimize"],  # Pass the optimize flag
        baseline_choice=user_input["baseline_choice"]
    )

    # Proceed with either hardware execution or simulation
    if mode == "H":
        with Session(backend=backend) as session:

            job_start = datetime.now()  # Job Time, start
            # Step 1: Fix SamplerV2 __init__ error by removing session argument
            sampler = Sampler()
            # Hardware Path: wrap transpilation calls in timing logic
            baseline_start = datetime.now()  # Job Time, Baseline Transpile Start
            start_baseline = time.time()
            transpiled_baseline = transpile_circuit(baseline_circuit, backend, constrain_depth=False)
            baseline_transpile_time = (time.time() - start_baseline) * 1000
            baseline_end = datetime.now()  # Job Time, Baseline Transpile End
            bl_t_time = (baseline_end - baseline_start)

            iqd_start = datetime.now()  # Job Time, iQD Transpile Start
            start_iqd = time.time()
            transpiled_iqd = transpile_circuit(iqd_circuit, backend, constrain_depth=True)
            iqd_transpile_time = (time.time() - start_iqd) * 1000
            iqd_end = datetime.now()  # Job Time, iQD Transpile End
            iqd_t_time = (iqd_end - iqd_start)

            # Step 2: Fix job submission by adding session argument to sampler.run()
            baseline_exe_start = datetime.now()  # Job Time, Baseline Execution Start
            baseline_job = sampler.run([transpiled_baseline], shots=shot_count)
            baseline_exe_end = datetime.now()  # Job Time, Baseline Execution End
            bl_exe_time = (baseline_exe_end - baseline_exe_start)

            iqd_exe_start = datetime.now()  # Job Time, iQD Execution Start
            iqd_job = sampler.run([transpiled_iqd], shots=shot_count)
            iqd_exe_end = datetime.now()  # Job Time, iQD Execution End
            iqd_exe_time = (iqd_exe_end - iqd_exe_start)

            baseline_result = baseline_job.result()
            iqd_result = iqd_job.result()

            baseline_exec_time = get_true_execution_time_ms(baseline_job)
            iqd_exec_time = get_true_execution_time_ms(iqd_job)

            logging.info(f"[TIMING] True Baseline Execution Time: {baseline_exec_time:.2f} ms")
            logging.info(f"[TIMING] True iQD Execution Time: {iqd_exec_time:.2f} ms")

            job_end = datetime.now()  # Job Time, End
            dt_job_time = (job_end - job_start)

        execution_data = {
            "mode": mode,
            "baseline_job_id": baseline_job.job_id(),
            "iqd_job_id": iqd_job.job_id(),
            "backend_name": backend.name,
            "baseline_type": baseline_type, 
            "shot_count": shot_count,
            "qubit_count": qubit_count,
            "test_name": test_name,
            "transpiled_baseline_qasm": qasm3_dumps(transpiled_baseline),
            "transpiled_iqd_qasm": qasm3_dumps(transpiled_iqd),
            "baseline_transpile_time_ms": baseline_transpile_time,
            "iqd_transpile_time_ms": iqd_transpile_time,
            "baseline_execution_time_ms": baseline_exec_time,
            "iqd_execution_time_ms": iqd_exec_time,
            "job_time" : dt_job_time.total_seconds(),  # * 1000 for ms, currently in seconds 
            "baseline_t_time" : bl_t_time.total_seconds() * 1000,
            "iQD_t_time" : iqd_t_time.total_seconds() * 1000,
            "baseline_exe_time" : bl_exe_time.total_seconds() * 1000,
            "iQD_exe_time" : iqd_exe_time.total_seconds() * 1000
        }
    else:
        # Simulation Path: capture transpile and execution times from execute_circuit()
        baseline_counts, transpiled_baseline, baseline_transpile_time, baseline_exec_time = execute_circuit(baseline_circuit, backend, shot_count)
        iqd_counts, transpiled_iqd, iqd_transpile_time, iqd_exec_time = execute_circuit(iqd_circuit, backend, shot_count, enforce_depth=True)
        execution_data = {
            "mode": mode,
            "baseline_counts": baseline_counts,
            "iqd_counts": iqd_counts,
            "backend_name": backend.name,
            "baseline_type": baseline_type, 
            "shot_count": shot_count,
            "qubit_count": qubit_count,
            "test_name": test_name,
            "transpiled_baseline_qasm": qasm3_dumps(transpiled_baseline),
            "transpiled_iqd_qasm": qasm3_dumps(transpiled_iqd),
            "baseline_transpile_time_ms": baseline_transpile_time,
            "iqd_transpile_time_ms": iqd_transpile_time,
            "baseline_execution_time_ms": baseline_exec_time,
            "iqd_execution_time_ms": iqd_exec_time
        }
    
    
    if mode == "H":
        logging.info(f"Job ID for Baseline Circuit: {baseline_job.job_id()}")
        logging.info(f"Job ID for iQD Circuit: {iqd_job.job_id()}")

    # This file is used to feed the analysis
    home_path = os.path.expanduser("~")
    save_path = os.path.join(home_path, "iQD_Test", "Reports", test_name)
    os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path, f"{test_name}.json"), "w") as f:
        json.dump(execution_data, f, indent=4)


# ----------------------- Execute Function (END) -----------------------

# --------------------------------------------------------------
# Function: `main_analysis()`
# --------------------------------------------------------------
# **Purpose**:
# The main analysis function processes the latest execution results, either from hardware or simulation mode, 
# and computes various quantum metrics. It retrieves the execution data, performs calculations for 
# fidelity and performance, and outputs the results both to the console and logs. This function also generates
# a detailed report and saves the data to various file formats (CSV, JSON, PDF) for further analysis.

# **Parameters**:
# - None: This function operates independently and retrieves its data from files in the "iQD_Test" directory.

# **Returns**:
# - `None`: The function writes results to the console, logs, and files but does not return any values.

# **Functionality**:
# - **Retrieve Latest Test Data**: 
#   - Loads the latest test results stored in the "iQD_Test" directory by reading the most recently modified file.
#   - The file contains execution data, which is used to retrieve the baseline and iQD counts (depending on the mode: "S" or "H").
# - **Mode Handling**:
#   - **Hardware Mode ("H")**: 
#     - Retrieves raw data from the quantum hardware (backend) by fetching results using job IDs.
#     - Retrieves the backend calibration data for metrics such as T1, T2, and readout error.
#   - **Simulation Mode ("S")**: 
#     - Uses previously saved counts from the execution data.
# - **Calculation of Metrics**:
#   - **Fidelity Metrics**: Calculates Output Fidelity and total variation distance (TVD) between the baseline and iQD circuits.
#   - **Gate Fidelity**: Computes the gate fidelity for both baseline and iQD circuits (using backend calibration data in hardware mode).
#   - **Gate Count**: Calculates the number of single-qubit and two-qubit gates for both baseline and iQD circuits.
#   - **Virtual Qubits Estimation**: Estimates the number of virtual/topological qubits based on the iQD circuit's complexity.
# - **Logging and Printing Results**: 
#   - Logs detailed metrics, including circuit depths, gate counts, fidelity metrics, execution times, and hardware properties.
#   - Prints the same metrics to the console for user visibility.
# - **Report Generation**:
#   - Saves the results to a variety of file formats (CSV, JSON, PDF) in a designated directory.
# - **Result Export**: 
#   - Uses `export_results_to_files()` to store the processed results, including:
#     - Counts and fidelity data.
#     - Backend performance details.
#     - Various other metrics (gate counts, virtual qubits, etc.).

# **Key Considerations**:
# - **Hardware Mode**: Includes additional hardware-related metrics such as T1, T2, and readout error, which are unavailable in simulation mode.
# - **File Retrieval**: The function automatically selects the most recent execution file for analysis, ensuring it works with the latest results.
# - **Report Generation**: It outputs results both in the console for immediate feedback and in multiple file formats for easy storage and sharing.
# - **Error Handling**: If the raw analysis results are unavailable, an error is raised, ensuring that no invalid or incomplete data is used in the analysis.
# - **Data Output**: Ensures all results are saved in a structured manner, making it easy for the user to review and analyze execution performance and accuracy.

# **Example Usage**:
# ```python
# main_analysis()  # Call the function to analyze the latest execution results and generate reports.
# ```

# **Key Operations**:
# - **File Reading**: Reads the latest test data from the "iQD_Test" directory.
# - **Raw Data Retrieval**: Retrieves raw data for hardware jobs, including counts, probabilities, and backend properties.
# - **Metric Calculations**: Computes Output Fidelity, TVD, gate fidelities, and virtual qubits.
# - **Report Generation**: Saves analysis results in CSV, JSON, and PDF formats.
# - **Logging**: Logs all important metrics for further review and records.

# ----------------------- Analysis Function -----------------------

def main_analysis() -> None:
    from qiskit_ibm_runtime import QiskitRuntimeService
    home_path = os.path.expanduser("~")
    reports_path = os.path.join(home_path, "iQD_Test", "Reports")
    all_test_dirs = [os.path.join(reports_path, d) for d in os.listdir(reports_path) if os.path.isdir(os.path.join(reports_path, d))]

    # Find the most recent test folder
    latest_test_dir = max(all_test_dirs, key=os.path.getmtime)

    # Find latest JSON inside that folder
    json_files = [f for f in os.listdir(latest_test_dir) if f.endswith(".json")]
    latest_json = max(json_files, key=lambda f: os.path.getmtime(os.path.join(latest_test_dir, f)))

    with open(os.path.join(latest_test_dir, latest_json), "r") as f:
        execution_data = json.load(f)

    
    # Load mode explicitly (default to 'S' if missing)
    mode = execution_data.get('mode', 'S')
    
    if mode == "H":
        service = QiskitRuntimeService()
        baseline_raw_data = retrieve_full_raw_data(execution_data['baseline_job_id'], service)
        iqd_raw_data = retrieve_full_raw_data(execution_data['iqd_job_id'], service)
        baseline_counts = baseline_raw_data['counts']
        iqd_counts = iqd_raw_data['counts']
    else:
        baseline_counts = execution_data['baseline_counts']
        iqd_counts = execution_data['iqd_counts']
    
    # Continue with identical metrics calculations:
    output_fid = output_fidelity(iqd_counts, baseline_counts)
    baseline_fid = fidelity_vs_ideal(baseline_counts)
    iqd_fid = fidelity_vs_ideal(iqd_counts)
    iqd_baseline_fid = fidelity_iqd_baseline(iqd_counts, baseline_counts)
    tvd = total_variation_distance(iqd_counts, baseline_counts)
    tvd_iQDvsIdeal = tvd_iqd_vs_ideal(iqd_counts)
    iqd_output_entropy = output_entropy(iqd_counts)
    kl_div_iqd = kl_divergence_vs_ideal(iqd_counts)
    avg_hamming_weight_iqd = average_hamming_weight_bits(iqd_counts)
    max_state_prob_iqd = max_state_probability(iqd_counts)
    std_dev_st_prob_iqd = stddev_state_probabilities(iqd_counts)
    baseline_type = execution_data.get('baseline_type', 'Unknown Circuit')  # Retrieve baseline_type
    backend = service.backend(execution_data['backend_name']) if mode == "H" else AerSimulator()

    entangle_depth_est_iqd = entanglement_depth_est(iqd_counts)
    state_coherence_signature_iqd = state_coherence_signature(iqd_counts)
    mean_top_5__prob_iqd = mean_top_5_probability(iqd_counts)
    top_10_state_prob_mass_iqd = top_10_state_probability_mass(iqd_counts)
 
    from qiskit.qasm3 import loads
    transpiled_baseline = loads(execution_data["transpiled_baseline_qasm"])
    transpiled_iqd = loads(execution_data["transpiled_iqd_qasm"])

    # Compute gate fidelity based on backend calibration data in Hardware mode.
    if mode == "H":
        gate_fid_baseline = compute_gate_fidelity_from_backend(transpiled_baseline, backend)
        gate_fid_iqd = compute_gate_fidelity_from_backend(transpiled_iqd, backend)
    else:
        gate_fid_baseline = "NOT APPLICABLE"
        gate_fid_iqd = "NOT APPLICABLE"
    
    single_qubit_gates = ['h', 'x', 'y', 'z', 'u', 'rx', 'ry', 'rz']
    two_qubit_gates = ['cx', 'cz', 'rzz', 'swap', 'ecr']
    single_qubit_gate_count_baseline = sum(transpiled_baseline.count_ops().get(gate, 0) for gate in single_qubit_gates)
    single_qubit_gate_count_iqd = sum(transpiled_iqd.count_ops().get(gate, 0) for gate in single_qubit_gates)
    two_qubit_gate_count_baseline = sum(transpiled_baseline.count_ops().get(gate, 0) for gate in two_qubit_gates)
    two_qubit_gate_count_iqd = sum(transpiled_iqd.count_ops().get(gate, 0) for gate in two_qubit_gates)

    N_virtual = estimate_virtual_qubits(
        depth=transpiled_iqd.depth(),
        two_qubit_gate_count=two_qubit_gate_count_iqd,
        logical_qubits=execution_data['qubit_count']
    )
    TQC = execution_data['qubit_count'] + N_virtual

    metrics = {
        "Baseline Circuit Depth": transpiled_baseline.depth(),
        "iQD Circuit Depth": transpiled_iqd.depth(),
        "Baseline Total Gate Count": sum(transpiled_baseline.count_ops().values()),
        "iQD Total Gate Count": sum(transpiled_iqd.count_ops().values()),
        "Output Fidelity (%)": output_fid,
        "Fidelity vs Ideal (Baseline)" : f"{baseline_fid:.6f}",
        "Fidelity vs Ideal (iQD)" : f"{iqd_fid:.6f}",
        "Fidelity (iQD vs Baseline)" : f"{iqd_baseline_fid:.6f}",
        "Output Entropy (iQD, bits)" : f"{iqd_output_entropy:.6f}",
        "KL Divergence vs Ideal (iQD)" : f"{kl_div_iqd:.6f}",
        "Average Hamming Weight (iQD)" : f"{avg_hamming_weight_iqd:.6f}",
        "Max State Probability (iQD)" : f"{max_state_prob_iqd:.6f}",
        "Std Dev of State Probabilities (iQD)" : f"{std_dev_st_prob_iqd:.6f}",
        "Total Variation Distance": f"{tvd:.6f}",
        "TVD (iQD vs Ideal)": f"{tvd_iQDvsIdeal:.6f}",
        "Baseline Gate Fidelity": gate_fid_baseline,
        "iQD Gate Fidelity": gate_fid_iqd,
        "Baseline Single-Qubit Gates": single_qubit_gate_count_baseline,
        "iQD Single-Qubit Gates": single_qubit_gate_count_iqd,
        "Baseline Two-Qubit Gates": two_qubit_gate_count_baseline,
        "iQD Two-Qubit Gates": two_qubit_gate_count_iqd,
        "Estimated Virtual Qubits": N_virtual,
        "Topological Qubit Count (TQC)": TQC,
        "Entanglement Depth Estimate (iQD)" : entangle_depth_est_iqd,
        "SCS (iQD)" : f"{state_coherence_signature_iqd:.6f}",
        "Mean Top 5 Prob (iQD)" : f"{mean_top_5__prob_iqd:.6f}",
        "Top 10 State Probability Mass (iQD)" : f"{top_10_state_prob_mass_iqd:.6f}"
    }
    
    backend_performance = {
        "Backend Name": execution_data['backend_name'],
        "Shot Count": execution_data['shot_count']
    }
    
    advanced_metrics = {
        "Backend Avg T1": np.mean([
            next((item['value'] for item in q if item['name'] == 'T1'), np.nan)
            for q in baseline_raw_data['backend_properties']['qubits']
        ]) if mode == "H" else None,
        "Backend Avg T2": np.mean([
            next((item['value'] for item in q if item['name'] == 'T2'), np.nan)
            for q in baseline_raw_data['backend_properties']['qubits']
        ]) if mode == "H" else None,
        "Backend Avg Readout Error": np.mean([
            next((item['value'] for item in q if item['name'] == 'readout_error'), np.nan)
            for q in baseline_raw_data['backend_properties']['qubits']
        ]) if mode == "H" else None
    }
    
    # ---- Added Logging Outputs for Detailed Metrics ----
    logging.info("\n==================== Execution Results ====================")
    logging.info(f"Test Name: {execution_data['test_name']}")
    logging.info(f"Backend Name: {execution_data['backend_name']}")
    
    if mode == "H":
        logging.info(f"Retrieved Baseline Job ID: {execution_data['baseline_job_id']}")
        logging.info(f"Retrieved iQD Job ID: {execution_data['iqd_job_id']}")
        

    logging.info(f"Qubit Count: {execution_data['qubit_count']}")
    logging.info(f"Shot Count: {execution_data['shot_count']}")
    
    logging.info("\n--------- Basic Circuit Metrics ---------")
    logging.info(f"Baseline Circuit Depth: {metrics['Baseline Circuit Depth']}")
    logging.info(f"iQD Circuit Depth: {metrics['iQD Circuit Depth']}")
    logging.info(f"Baseline Total Gate Count: {metrics['Baseline Total Gate Count']}")
    logging.info(f"iQD Total Gate Count: {metrics['iQD Total Gate Count']}")

    # Log and print the new gate fidelity metrics
    logging.info(f"Baseline Gate Fidelity (from backend props): {gate_fid_baseline}")
    logging.info(f"iQD Gate Fidelity (from backend props): {gate_fid_iqd}")

    # Log transpile times 
    logging.info("\n--------- Transpile Time ---------")
    logging.info(f"Baseline Transpile Time: {execution_data['baseline_transpile_time_ms']:.2f} ms")
    logging.info(f"iQD Transpile Time: {execution_data['iqd_transpile_time_ms']:.2f} ms")
    # Log execution times
    logging.info("\n--------- Execution Time ---------")
    logging.info(f"Baseline Execution Time: {execution_data['baseline_execution_time_ms']:.2f} ms")
    logging.info(f"iQD Execution Time: {execution_data['iqd_execution_time_ms']:.2f} ms")
    
    logging.info("\n--------- Gate Counts ---------")
    logging.info(f"Baseline Single-Qubit Gates: {metrics['Baseline Single-Qubit Gates']}")
    logging.info(f"iQD Single-Qubit Gates: {metrics['iQD Single-Qubit Gates']}")
    logging.info(f"Baseline Two-Qubit Gates: {metrics['Baseline Two-Qubit Gates']}")
    logging.info(f"iQD Two-Qubit Gates: {metrics['iQD Two-Qubit Gates']}")
    
    logging.info("\n--------- Fidelity Metrics ---------")
    logging.info(f"Output Fidelity (Baseline vs iQD): {metrics['Output Fidelity (%)']}%")
    logging.info(f"Fidelity vs Ideal (Baseline): {metrics['Fidelity vs Ideal (Baseline)']}")
    logging.info(f"Fidelity vs Ideal (iQD): {metrics['Fidelity vs Ideal (iQD)']}")
    logging.info(f"Fidelity vs Ideal (iQD): {metrics['Fidelity (iQD vs Baseline)']}")
    logging.info(f"Output Fidelity (Baseline vs iQD): {metrics['Output Fidelity (%)']}%")
    logging.info(f"Total Variation Distance (iQD vs Baseline): {metrics['Total Variation Distance']}")
    logging.info(f"TVD (iQD vs Ideal ): {metrics['TVD (iQD vs Ideal)']}")
    logging.info(f"Outout Entropy (iQD, bits): {metrics['Output Entropy (iQD, bits)']}")
    logging.info(f"KL Divergence vs Ideal (iQD): {metrics['KL Divergence vs Ideal (iQD)']}")
    logging.info(f"Average Hamming Weight (iQD): {metrics['Average Hamming Weight (iQD)']}")
    logging.info(f"Max State Probability (iQD): {metrics['Max State Probability (iQD)']}")
    logging.info(f"Std Dev of State Probabilities (iQD): {metrics['Std Dev of State Probabilities (iQD)']}")
    
    logging.info(f"Entanglement Depth Estimate (iQD): {metrics['Entanglement Depth Estimate (iQD)']}")
    logging.info(f"State Coherence Signature (iQD): {metrics['SCS (iQD)']}")
    logging.info(f"Mean Top 5 Prob (iQD): {metrics['Mean Top 5 Prob (iQD)']}")
    logging.info(f"Top 10 State Probability Mass (iQD): {metrics['Top 10 State Probability Mass (iQD)']}")
    
    logging.info("\n--------- Advanced Hardware Metrics ---------")
    if mode == "H":
        logging.info(f"Backend Avg T1: {advanced_metrics['Backend Avg T1']:.2f} µs")
        logging.info(f"Backend Avg T2: {advanced_metrics['Backend Avg T2']:.2f} µs")
        logging.info(f"Backend Avg Readout Error: {advanced_metrics['Backend Avg Readout Error']:.4f}")
    else:
        logging.info("Advanced hardware metrics are not available in Simulation Mode.")
    
    logging.info("==========================================================\n")

    logging.info("")
    # ------------------------------------------------------
    
    # Print Metrics
    # ---- Added Print Outputs for Detailed Metrics ----
    print("")
    print("=" * 57)
    print("\033[1m" + "iQD EXECUTION RESULTS".center(57) + "\033[0m")
    print("=" * 57)
    print(f"Test Name                    : {execution_data['test_name']}")
    print(f"Date-Time                    : {datetime.now().strftime('%m/%d/%y %H:%M')}")
    print(f"Backend Name                 : {execution_data['backend_name']}")

    print(f"Qubit Count                  : {execution_data['qubit_count']}")
    print(f"Shot Count                   : {execution_data['shot_count']}")

    if mode == "H":
        print(f"Retrieved Baseline Job ID    : {execution_data['baseline_job_id']}")
        print(f"Retrieved iQD Job ID         : {execution_data['iqd_job_id']}")
        print(f"Total Job Time               : {execution_data['job_time']:.2f} s")

    print("=" * 57)
    print("Execution Timing (ms)".center(57))
    print("=" * 57)
    print("-" * 57)
    print("Baseline".center(57))
    print("-" * 57)
    if mode == "H":
        print(f"Transpile Time (Baseline)    : {execution_data['baseline_t_time']:.2f} ms")
        print(f"Execution Time (Baseline)    : {execution_data['baseline_exe_time']:.2f} ms")
    else:
        print(f"Transpile Time (Baseline)    : {execution_data['baseline_transpile_time_ms']:.2f} ms")
        print(f"Execution Time (Baseline)    : {execution_data['baseline_execution_time_ms']:.2f} ms")
    
    print("-" * 57)
    print("iQD Optimized".center(57))
    print("-" * 57)
    if mode == "H":
        print(f"Transpile Time (iQD)         : {execution_data['iQD_t_time']:.2f} ms")
        print(f"Execution Time (iQD)         : {execution_data['iQD_exe_time']:.2f} ms")
    else:
        print(f"Transpile Time (iQD)         : {execution_data['iqd_transpile_time_ms']:.2f} ms")
        print(f"Execution Time (iQD)         : {execution_data['iqd_execution_time_ms']:.2f} ms")

    print("=" * 57)
    print("Circuit Complexity".center(57))
    print("=" * 57)
    print(f"Baseline Type                : {baseline_type}") 
    print("-" * 57)
    print("Baseline".center(57))
    print("-" * 57)
    print(f"Circuit Depth (Baseline)     : {metrics['Baseline Circuit Depth']}")
    print(f"Total Gate Count (Baseline)  : {metrics['Baseline Total Gate Count']}")
    print(f"Single-Qubit Gates (Baseline): {metrics['Baseline Single-Qubit Gates']}")
    print(f"Two-Qubit Gates (Baseline)   : {metrics['Baseline Two-Qubit Gates']}")

    print("-" * 57)
    print("iQD Optimized".center(57))
    print("-" * 57)
    print(f"Circuit Depth (iQD)          : {metrics['iQD Circuit Depth']}")
    print(f"Total Gate Count (iQD)       : {metrics['iQD Total Gate Count']}")
    print(f"Single-Qubit Gates (iQD)     : {metrics['iQD Single-Qubit Gates']}")
    print(f"Two-Qubit Gates (iQD)        : {metrics['iQD Two-Qubit Gates']}")
      
    print("=" * 57)
    print("Gate Quality".center(57))
    print("=" * 57)
    print(f"Gate Fidelity (Baseline)     : {gate_fid_baseline}")
    print(f"Gate Fidelity (iQD)          : {gate_fid_iqd}")
 
    print("=" * 57)
    print("Backend Calibration Summary".center(57))
    print("=" * 57)
    if mode == "H":
        print(f"Backend Avg T1               : {advanced_metrics['Backend Avg T1']:.2f} µs")
        print(f"Backend Avg T2               : {advanced_metrics['Backend Avg T2']:.2f} µs")
        print(f"Backend Avg Readout Error    : {advanced_metrics['Backend Avg Readout Error']:.4f}")
    else:
        print("Backend Metrics              : NOT APPLICABLE")

    print("=" * 57)
    print("FIDELITY METRICS".center(57))
    print("=" * 57)
    print(f"Output Fidelity (%)          : {metrics['Output Fidelity (%)']}")
    print(f"Fidelity (iQD vs Baseline)   : {metrics['Fidelity (iQD vs Baseline)']}")
    print(f"Fidelity vs Ideal (Baseline) : {metrics['Fidelity vs Ideal (Baseline)']}")
    print(f"Fidelity vs Ideal (iQD)      : {metrics['Fidelity vs Ideal (iQD)']}")
    
    print("=" * 57)
    print("Information Theory & Statistical Metrics".center(57))
    print("=" * 57)
    print(f"Entropy (iQD,bits)           : {metrics['Output Entropy (iQD, bits)']}")
    print(f"KL Divergence vs Ideal (iQD) : {metrics['KL Divergence vs Ideal (iQD)']}")
    print(f"TVD (iQD vs Baseline)        : {metrics['Total Variation Distance']}")
    print(f"TVD (iQD)                    : {metrics['TVD (iQD vs Ideal)']}")    
    print(f"Average Hamming Weight (iQD) : {metrics['Average Hamming Weight (iQD)']}")
    print(f"Std Dev of State Probs (iQD) : {metrics['Std Dev of State Probabilities (iQD)']}")
    print(f"Max State Probability (iQD)  : {metrics['Max State Probability (iQD)']}")
    
    print("=" * 57)
    print("Qubit Utilization".center(57))
    print("=" * 57) 
    print(f"Estimated Virtual Qubits            : {metrics['Estimated Virtual Qubits']}")
    print(f"Topological Qubit Count (TQC)       : {metrics['Topological Qubit Count (TQC)']}")
    print(f"Entanglement Depth Estimate (iQD)   : {metrics['Entanglement Depth Estimate (iQD)']}")
    print(f"Structured Coherence Score (SCS)    : {metrics['SCS (iQD)']}")

    print("=" * 57)
    print("State Probability Distribution".center(57))
    print("=" * 57) 
    print(f"Mean of Top 5 Probabilities (iQD)   : {metrics['Mean Top 5 Prob (iQD)']}")
    print(f"Top 10 State Probability Mass (iQD) : {metrics['Top 10 State Probability Mass (iQD)']}")
    print(f"Total Unique States (iQD)           : {len(iqd_counts)}")
    print(f"Total Unique States (Baseline)      : {len(baseline_counts)}")


    print("=" * 57)
    print("Powered by the iQD Engine | Version 1.0.2".center(57))
    print("=" * 57)
    # ------------------------------------------------------export

    home_path = os.path.expanduser("~")
    save_base_path = os.path.join(home_path, "iQD_Test", "Reports")
    timestamp = datetime.now().strftime('%Y-%m-%d')
    save_path = os.path.join(save_base_path, f"{execution_data['test_name']}")
    
    export_results_to_files(save_path, execution_data['test_name'],
                            iqd_counts, baseline_counts,
                            output_fid, backend_performance, tvd,
                            metrics, advanced_metrics,execution_data)
    
# ----------------------- Analysis Function (END) -----------------------

# --------------------------------------------------------------
# Main Sequence Entry Point
# --------------------------------------------------------------
# **Purpose**:
# The `if __name__ == "__main__":` block is the entry point of the program. It ensures that when the script
# is executed, the `main_execute()` and `main_analysis()` functions are called sequentially.
# 
# **Functionality**:
# - **`main_execute()`**: This function handles the core execution of the quantum circuits, including
#   user input collection, circuit creation, backend selection, and either simulation or hardware execution.
#   It also handles transpilation, execution time, and result generation.
# - **`main_analysis()`**: After the execution is complete, this function analyzes the results, calculates
#   relevant metrics (e.g., fidelity, TVD), and generates a detailed report, including saving the results to 
#   files (CSV, JSON, PDF) and printing/logging the performance metrics.
#
# **Key Considerations**:
# - This block ensures that both the execution and analysis of the quantum experiment are handled 
#   sequentially when the script is run.
# - The execution phase (`main_execute()`) starts by handling all the logic for circuit execution and results
#   collection, while the analysis phase (`main_analysis()`) processes the collected results and generates reports.
#
# **Example Usage**:
# This block is automatically executed when the script is run directly from the command line or an environment 
# where the script is invoked. No explicit call to this block is needed, as it is triggered by Python's 
# script execution system.

# **Key Operations**:
# - Executes the quantum experiment and analysis by calling `main_execute()` and `main_analysis()`.

# ----------------------- Sequence -----------------------

if __name__ == "__main__":
    main_execute()
    main_analysis()

# ----------------------- Sequence (END) -----------------------

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# This software uses the following third-party libraries under the Apache 2.0 License:
#
# 1. **Qiskit** (including `qiskit`, `qiskit_aer`, `qiskit_experiments`, `qiskit.quantum_info`, `qiskit.transpiler`, `qiskit.circuit.library`, `qiskit.exceptions`)
#    - License: Apache License 2.0
#    - Link: https://opensource.org/licenses/Apache-2.0
#
# 2. **Qiskit Experiments** (`qiskit_experiments`)
#    - License: Apache License 2.0
#    - Link: https://opensource.org/licenses/Apache-2.0
#
# 3. **QASM3** (`qiskit.qasm3`)
#    - License: Apache License 2.0
#    - Link: https://opensource.org/licenses/Apache-2.0
#
# 4. **Qiskit IBM Runtime** (`qiskit_ibm_runtime`)
#    - License: Apache License 2.0
#    - Link: https://opensource.org/licenses/Apache-2.0
#
# 5. **NumPy** (`numpy`)
#    - License: BSD 3-Clause License
#    - Link: https://opensource.org/licenses/BSD-3-Clause
#
# 6. **Pandas** (`pandas`)
#    - License: BSD 3-Clause License
#    - Link: https://opensource.org/licenses/BSD-3-Clause
#
# 7. **FPDF** (`fpdf`)
#    - License: LGPL 3.0 License
#    - Link: https://www.gnu.org/licenses/lgpl-3.0.html
#
# 8. **Random** (Standard Python library)
#    - License: Python Software Foundation License
#    - Link: https://opensource.org/licenses/Python-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
