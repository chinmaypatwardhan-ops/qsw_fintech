import numpy as np

# 1. Raw QPU Amplitudes (ibm_fez output from job d7bj29m5nvhs73a3eaq0)
p_qpu = np.array([0.3931, 0.3481, 0.1411, 0.1177])

print("--- Initial QPU State (Pure Unitary) ---")
print(f"Lattice (Compromised): {np.sum(p_qpu[0:2])*100:.2f}%")
print(f"Hash (Secure):         {np.sum(p_qpu[2:4])*100:.2f}%\n")

# 2. Classical Network Utility Boundaries (N=4)
u = np.array([0.01, 0.01, 0.50, 0.50])
G = u / np.sum(u) # Column-stochastic Google vector

# 3. Apply GKLS Dissipator 
omega = 0.2
iterations = 15

p_current = p_qpu.copy()

print("--- GKLS Hybrid Dissipation Loop ---")
for i in range(iterations):
    stochastic_term = G 
    p_next = (1 - omega) * p_current + (omega * stochastic_term)
    
    # Normalize
    p_current = p_next / np.sum(p_next)
    
    if (i+1) % 5 == 0:
        lattice_mass = np.sum(p_current[0:2])
        hash_mass = np.sum(p_current[2:4])
        print(f"Iteration {i+1:02d} -> Lattice: {lattice_mass*100:.2f}% | Hash: {hash_mass*100:.2f}%")

print("\n--- Final Hybrid Routing Distribution ---")
print(f"Lattice 0: {p_current[0]:.4f}")
print(f"Lattice 1: {p_current[1]:.4f}")
print(f"Hash 2:    {p_current[2]:.4f}")
print(f"Hash 3:    {p_current[3]:.4f}")
