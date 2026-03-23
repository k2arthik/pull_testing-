import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('loadtest_results_stats_history.csv')

# Plotting Average Response Time vs User Count
plt.figure(figsize=(10, 6))
plt.plot(df['User Count'], df['Total Average Response Time'], marker='o', linestyle='-', color='blue', label='Avg Response Time')

# To show if there were any failures, let's plot error rate or indicate it
if 'Failures/s' in df.columns:
    # Just checking for failures to annotate graph if need be
    pass

plt.title('Locust Load Test: Response Time vs Number of Users (Up to 50 Users)')
plt.xlabel('Number of Concurrent Users')
plt.ylabel('Average Response Time (ms)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(r'C:\Users\prash\.gemini\antigravity\brain\5cee659e-d32e-427c-a6fe-4ec87c9b18d1\response_time_chart.png')
print("Graph generated directly in artifacts directory.")
