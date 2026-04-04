import torch
import numpy as np
import os
import time

N = 30
ITERATIONS = 50
TOLERANCE = 1e-4

def load_infrastructure():
    if not os.path.exists("synthetic_sigma_net.npy"):
        # Auto-generate a dummy matrix if missing in repo to prevent crash
        return np.eye(N) 
    return np.load("synthetic_sigma_net.npy")

def generate_environment(device, state="nominal"):
    U = torch.zeros(N, dtype=torch.float32, device=device)
    if state == "nominal":
        U[0:10] = torch.FloatTensor(np.random.uniform(0.8, 1.0, 10))
    elif state == "shock":
        U[0:10] = 0.01                                                 
        
    U[10:20] = torch.FloatTensor(np.random.uniform(0.4, 0.6, 10))  
    U[20:30] = torch.FloatTensor(np.random.uniform(0.2, 0.4, 10))  
    
    Sigma_crypto = torch.zeros((N, N), dtype=torch.float32, device=device)
    Sigma_crypto[0:10, 0:10] = 0.9    
    Sigma_crypto[10:20, 10:20] = 0.9  
    Sigma_crypto[20:30, 20:30] = 0.9  
    
    Sigma_net = torch.tensor(load_infrastructure(), dtype=torch.float32, device=device)
    Sigma = 0.5 * Sigma_net + 0.5 * Sigma_crypto
    return U, Sigma

def construct_qsw_operators(U, Sigma, device):
    gamma_1, gamma_2 = 1.0, 0.5
    H = gamma_2 * Sigma
    H.diagonal().copy_(-gamma_1 * U)
    
    alpha, beta = 2.0, 5.0
    W = torch.exp(alpha * U.unsqueeze(0) - beta * Sigma)
    W.diagonal().fill_(0) 
    row_sums = W.sum(dim=1, keepdim=True)
    P = W / (row_sums + 1e-9) 
    
    damp = 0.85
    G = damp * P + (1 - damp) * (1.0 / N)
    return H, G

def execute_qsw_solver(H, G, device):
    rho = torch.eye(N, dtype=torch.complex64, device=device) / N
    dt = 0.1
    H_complex = H.to(torch.complex64)
    V = torch.matrix_exp(-1j * dt * H_complex)
    V_dagger = V.mH  
    G_T = G.T.to(torch.complex64)
    omega = 0.2
    
    for _ in range(ITERATIONS):
        coherent_term = torch.matmul(torch.matmul(V, rho), V_dagger)
        p_current = torch.diag(rho).unsqueeze(1)
        p_next = torch.matmul(G_T, p_current).squeeze()
        stochastic_term = torch.diag(p_next)
        
        rho_next = (1 - omega) * coherent_term + omega * stochastic_term
        rho_next = rho_next / torch.trace(rho_next)
        
        diff = torch.norm(torch.diag(rho_next).real - torch.diag(rho).real, p=1)
        if diff < TOLERANCE:
            break
        rho = rho_next
        
    weights = torch.diag(rho).real.cpu().numpy()
    return weights / np.sum(weights)

def push_weights_to_dataplane(weights, state_name):
    int_weights = np.maximum(0, np.round(weights * 1000)).astype(int)
    cmd = "sudo ovs-ofctl -O OpenFlow13 mod-group s_in 'group_id=1,type=select"
    for i in range(N):
        cmd += f",bucket=weight:{int_weights[i]},actions=output:{i+2}"
    cmd += "'"
    
    start_time = time.perf_counter()
    os.system(cmd)
    latency = (time.perf_counter() - start_time) * 1000
    
    print(f"\n[{state_name.upper()} STATE] Mod-group latency: {latency:.2f} ms")
    print(f"Distribution -> Lattice: {np.sum(weights[0:10])*100:.1f}% | Hash: {np.sum(weights[10:20])*100:.1f}% | Code: {np.sum(weights[20:30])*100:.1f}%")

if __name__ == "__main__":
    device = torch.device("cpu")
    print("--- INITIATING QSW CONTROL PLANE (CPU) ---")
    
    U_nom, Sigma_nom = generate_environment(device, "nominal")
    H_nom, G_nom = construct_qsw_operators(U_nom, Sigma_nom, device)
    weights_nom = execute_qsw_solver(H_nom, G_nom, device)
    push_weights_to_dataplane(weights_nom, "Nominal")
    
    print("\nSimulating Cryptographic Shock (Lattice Compromise)...")
    
    U_shock, Sigma_shock = generate_environment(device, "shock")
    H_shock, G_shock = construct_qsw_operators(U_shock, Sigma_shock, device)
    weights_shock = execute_qsw_solver(H_shock, G_shock, device)
    push_weights_to_dataplane(weights_shock, "Shock")