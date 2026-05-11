# A Quantum Stochastic Walk Approach to Dynamic Multipath Routing under Correlated Cryptographic Degradation

This repository contains the reference implementation, emulation environment, and physical hardware telemetry supporting the manuscript "A Quantum Stochastic Walk Approach to Dynamic Multipath Routing under Correlated Cryptographic Degradation."

The architecture executes a Gorini-Kossakowski-Lindblad-Sudarshan (GKLS) master equation to calculate routing distributions across networks secured by heterogeneous Post-Quantum Cryptography (PQC), enabling automated traffic evacuation during correlated algorithmic compromise (e.g., a Module-LWE utility shock).

## Repository Architecture

```text
qsw_fintech/
├── topo_fintech.py                 # Open vSwitch/Mininet data plane topology
├── qsw_controller.py               # OpenFlow QSW control plane and GKLS solver
├── synthetic_data_gen.py           # NHPP synthetic traffic and micro-burst generator
├── README.md                       # Root documentation
└── hardware_verification/          # IBM Quantum QPU scripts and telemetry
    ├── qpu_trotter_execution.py
    ├── hybrid_gkls_evacuation.py
    ├── job-d7bj29m5nvhs73a3eaq0-result.json
    └── README.md
