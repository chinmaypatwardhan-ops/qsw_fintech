## Hardware Verification (Appendix A)

This directory contains the telemetry and execution scripts for the physical IBM Quantum hardware verification.

### 1. Reproducing the Manuscript Data
Due to the daily recalibration cycles, variable decoherence profiles ($T_1/T_2$), and stochastic shot noise inherent to NISQ superconducting processors, executing a live run will yield similar macroscopic probability trapping, but non-identical scalar outputs. 

The exact dataset printed in the manuscript (Appendix A) was executed on the 150-qubit `ibm_fez` processor on April 9, 2026. 
* **Immutable Artifact:** The raw execution output is preserved in `job-d7bj29m5nvhs73a3eaq0-result.json`.

### 2. Live Execution
To execute a live verification of the Anderson-like probability trapping on current IBM hardware:
1. Insert your IBM Quantum API token in `qpu_trotter_execution.py`.
2. Run the script. The system will dynamically select the least busy processor. 
3. Observe the output. The hardware will systematically trap the majority of the probability mass in the correlated Lattice states ($|00\rangle, |01\rangle$), confirming the failure of pure unitary evolution.
4. Pass your new hardware array into `hybrid_gkls_evacuation.py` to observe the classical Lindblad dissipator force the trapped state back to the defined utility baseline.
