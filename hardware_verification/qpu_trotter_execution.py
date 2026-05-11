import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Operator
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import LieTrotter
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# 1. Define the Truncated N=4 Hamiltonian (Shock State)
H_matrix = np.array([
    [ 0.01, -0.90, -0.15, -0.15],
    [-0.90,  0.01, -0.15, -0.15],
    [-0.15, -0.15,  0.50, -0.90],
    [-0.15, -0.15, -0.90,  0.50]
])

# 2. Decompose into Pauli Strings
pauli_op = SparsePauliOp.from_operator(Operator(H_matrix))

# 3. Construct the Coherent Evolution Circuit (V = e^{-i H dt})
dt = 2.5  # Time parameter calibrated to force amplitude shift
evo_gate = PauliEvolutionGate(pauli_op, time=dt, synthesis=LieTrotter(reps=3))

qc = QuantumCircuit(2)
qc.h([0, 1]) 
qc.append(evo_gate, [0, 1])
qc.measure_all()

# 4. Hardware Connection
service = QiskitRuntimeService(channel="ibm_quantum_platform", token="IBM_QUANTUM_TOKEN")
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
print(f"Targeting QPU: {backend.name}")

# Transpile the circuit for the specific hardware topology
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa_circuit = pm.run(qc)

# 5. Initialize SamplerV2 (Stripped of options for API compatibility)
sampler = Sampler(mode=backend)

# 6. Execute 
print("Submitting to IBM Quantum Queue...")
job = sampler.run([isa_circuit], shots=4096)
print(f"Job ID: {job.job_id()}")

# 7. Output extraction
result = job.result()
pub_result = result[0]
counts = pub_result.data.meas.get_counts()

qpu_weights = np.zeros(4)
for bitstring, count in counts.items():
    idx = int(bitstring, 2)
    qpu_weights[idx] = count / 4096

print("\n--- QPU Coherent State Probabilities ---")
print(f"Lattice 0 (|00>): {qpu_weights[0]:.4f}")
print(f"Lattice 1 (|01>): {qpu_weights[1]:.4f}")
print(f"Hash 2    (|10>): {qpu_weights[2]:.4f}")
print(f"Hash 3    (|11>): {qpu_weights[3]:.4f}")
