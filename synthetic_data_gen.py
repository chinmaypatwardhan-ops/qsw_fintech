import numpy as np
import pandas as pd

# System Architecture Bounds
N_NODES = 30
SIMULATION_SECONDS = 3600
BASE_TPS = 5000
PEAK_MULTIPLIER = 3.5

def generate_financial_traffic_model():
    print("Generating synthetic transaction arrival model...")
    time_index = np.arange(SIMULATION_SECONDS)
    diurnal_wave = np.sin(np.linspace(0, np.pi, SIMULATION_SECONDS)) 
    base_rate = BASE_TPS + (diurnal_wave * BASE_TPS * 0.5)
    
    burst_intervals = np.random.choice(time_index, size=15, replace=False)
    for t in burst_intervals:
        burst_duration = np.random.randint(5, 30)
        end_t = min(t + burst_duration, SIMULATION_SECONDS)
        base_rate[t:end_t] *= np.random.uniform(2.0, PEAK_MULTIPLIER)
        
    arrivals = np.random.poisson(base_rate)
    df = pd.DataFrame({
        'timestamp_sec': time_index,
        'arrival_rate_tps': arrivals,
        'payload_bytes_avg': np.random.normal(1200, 150, SIMULATION_SECONDS).astype(int)
    })
    df.to_csv("synthetic_tx_traffic.csv", index=False)
    print(f"Traffic model saved. Max TPS peak: {arrivals.max()}")

def generate_infrastructure_covariance():
    print("Generating synthetic infrastructure covariance matrix...")
    N_ASNs = 5
    node_asn_map = np.random.randint(0, N_ASNs, size=N_NODES)
    Sigma_net = np.zeros((N_NODES, N_NODES))
    
    for i in range(N_NODES):
        for j in range(N_NODES):
            if i == j:
                Sigma_net[i, j] = 1.0
            elif node_asn_map[i] == node_asn_map[j]:
                Sigma_net[i, j] = np.random.normal(0.85, 0.05)
            else:
                Sigma_net[i, j] = np.random.normal(0.15, 0.05)
                
    Sigma_net = (Sigma_net + Sigma_net.T) / 2
    Sigma_net = np.clip(Sigma_net, 0.0, 1.0)
    np.save("synthetic_sigma_net.npy", Sigma_net)
    print("Covariance matrix saved to synthetic_sigma_net.npy.")
    return Sigma_net, node_asn_map

if __name__ == "__main__":
    generate_financial_traffic_model()
    Sigma_net, asn_map = generate_infrastructure_covariance()