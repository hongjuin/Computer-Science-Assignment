#!/usr/bin/env python3
"""
COMPLETE SYSTEM PERFORMANCE MONITOR
Tracks: CPU, Memory, Disk, Processes, GPU (if available)
Logs: Every 10 seconds with exact timestamps
"""

import psutil
import time
from datetime import datetime
import csv
import os

class SystemPerformanceTracker:
    """Track all system resources including GPU"""
    
    def __init__(self, log_file="system_performance_log.csv"):
        self.log_file = log_file
        self.setup_log_file()
        
    def setup_log_file(self):
        """Create CSV file with headers"""
        headers = [
            'timestamp', 'cpu_percent', 'cpu_user', 'cpu_system', 'cpu_idle',
            'load_1min', 'load_5min', 'load_15min',
            'mem_total_gb', 'mem_used_gb', 'mem_free_gb', 'mem_percent',
            'disk_total_gb', 'disk_used_gb', 'disk_free_gb', 'disk_percent',
            'uptime_hours', 'process_count', 'running_processes', 'sleeping_processes',
            'top_cpu_1', 'top_cpu_2', 'top_cpu_3',
            'top_mem_1', 'top_mem_2', 'top_mem_3',
            'gpu_available', 'gpu_usage', 'gpu_memory_used', 'gpu_memory_total'
        ]
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def get_gpu_info(self):
        """Try to get GPU information (if available)"""
        gpu_info = {
            'available': False,
            'usage': 0,
            'memory_used': 0,
            'memory_total': 0
        }
        
        try:
            # Method 1: Try nvidia-smi (for NVIDIA GPUs)
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = result.stdout.strip().split(',')
                gpu_info = {
                    'available': True,
                    'usage': float(data[0].strip()),
                    'memory_used': float(data[1].strip()),
                    'memory_total': float(data[2].strip())
                }
                
        except Exception:
            try:
                # Method 2: Try GPUtil library (if installed)
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_info = {
                        'available': True,
                        'usage': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal
                    }
            except:
                pass
        
        return gpu_info
    
    def get_detailed_cpu_info(self):
        """Get detailed CPU breakdown"""
        cpu_times = psutil.cpu_times_percent(interval=1)
        return {
            'user': cpu_times.user,
            'system': cpu_times.system,
            'idle': cpu_times.idle,
            'iowait': getattr(cpu_times, 'iowait', 0)
        }
    
    def get_top_processes(self):
        """Get top 3 processes by CPU and Memory"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                # Update CPU percent for each process
                proc.cpu_percent()
            except:
                pass
        
        time.sleep(0.1)  # Small delay for CPU measurement
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                # Only include if we have valid data
                if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                    processes.append(info)
            except:
                pass
        
        # Sort by CPU and get top 3
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        top_cpu = [(p.get('name', 'N/A'), p.get('cpu_percent', 0)) for p in processes[:3]]
        
        # Sort by Memory and get top 3
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        top_memory = [(p.get('name', 'N/A'), p.get('memory_percent', 0)) for p in processes[:3]]
        
        return top_cpu, top_memory
    
    def collect_metrics(self):
        """Collect ALL system metrics"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. CPU Metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_details = self.get_detailed_cpu_info()
        load_avg = psutil.getloadavg()
        
        # 2. Memory Metrics
        memory = psutil.virtual_memory()
        
        # 3. Disk Metrics
        disk = psutil.disk_usage('/')
        
        # 4. Uptime
        uptime_seconds = time.time() - psutil.boot_time()
        
        # 5. Process Metrics
        process_count = len(psutil.pids())
        running = 0
        sleeping = 0
        
        for proc in psutil.process_iter(['status']):
            try:
                status = proc.info['status']
                if status == psutil.STATUS_RUNNING:
                    running += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping += 1
            except:
                pass
        
        # 6. Top Processes
        top_cpu, top_memory = self.get_top_processes()
        
        # 7. GPU Metrics (if available)
        gpu_info = self.get_gpu_info()
        
        # Prepare data row
        row = [
            timestamp,                                      # 1. Timestamp
            cpu_percent,                                    # 2. CPU %
            cpu_details['user'],                            # 3. CPU user %
            cpu_details['system'],                          # 4. CPU system %
            cpu_details['idle'],                            # 5. CPU idle %
            load_avg[0],                                    # 6. Load 1min
            load_avg[1],                                    # 7. Load 5min
            load_avg[2],                                    # 8. Load 15min
            round(memory.total / (1024**3), 2),             # 9. Memory total GB
            round(memory.used / (1024**3), 2),              # 10. Memory used GB
            round(memory.available / (1024**3), 2),         # 11. Memory free GB
            memory.percent,                                 # 12. Memory %
            round(disk.total / (1024**3), 2),               # 13. Disk total GB
            round(disk.used / (1024**3), 2),                # 14. Disk used GB
            round(disk.free / (1024**3), 2),                # 15. Disk free GB
            disk.percent,                                   # 16. Disk %
            round(uptime_seconds / 3600, 2),                # 17. Uptime hours
            process_count,                                  # 18. Process count
            running,                                        # 19. Running processes
            sleeping,                                       # 20. Sleeping processes
            f"{top_cpu[0][0]}({top_cpu[0][1]:.1f}%)",      # 21. Top CPU 1
            f"{top_cpu[1][0]}({top_cpu[1][1]:.1f}%)",      # 22. Top CPU 2
            f"{top_cpu[2][0]}({top_cpu[2][1]:.1f}%)",      # 23. Top CPU 3
            f"{top_memory[0][0]}({top_memory[0][1]:.1f}%)", # 24. Top Memory 1
            f"{top_memory[1][0]}({top_memory[1][1]:.1f}%)", # 25. Top Memory 2
            f"{top_memory[2][0]}({top_memory[2][1]:.1f}%)", # 26. Top Memory 3
            gpu_info['available'],                          # 27. GPU available?
            gpu_info['usage'],                              # 28. GPU usage %
            gpu_info['memory_used'],                        # 29. GPU memory used MB
            gpu_info['memory_total']                        # 30. GPU memory total MB
        ]
        
        return row
    
    def log_metrics(self):
        """Save metrics to CSV file"""
        row = self.collect_metrics()
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Display on screen (optional)
        print(f"[{row[0]}] CPU: {row[1]}% | Mem: {row[11]}% | Disk: {row[16]}%")
        if row[26]:  # If GPU available
            print(f"  GPU: {row[27]}% | GPU Mem: {row[28]}/{row[29]} MB")
    
    def run_monitor(self, interval_seconds=10):
        """Run monitoring loop"""
        print("Starting System Performance Monitor")
        print(f"Logging to: {self.log_file}")
        print(f"Interval: {interval_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.log_metrics()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nSystem monitoring stopped.")

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    # Create tracker
    tracker = SystemPerformanceTracker()
    
    # Get interval from user (default 10 seconds)
    interval = input("Enter monitoring interval in seconds (default 10): ").strip()
    
    try:
        interval = int(interval) if interval else 10
    except:
        interval = 10
    
    # Start monitoring
    tracker.run_monitor(interval)
