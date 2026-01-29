#!/usr/bin/env python3
"""
COMPLETE SYSTEM PERFORMANCE MONITOR 
-Tracks: CPU, Memory, Disk, Processes, GPU (if available)
Logs: Every 10 seconds with exact timestamps
"""

import psutil
import time
from datetime import datetime
import csv
import os
import subprocess

class SystemPerformanceTracker:
    
    def __init__(self, log_file="system_performance_log.csv"):
        self.log_file = log_file
        self.setup_log_file()
        # Initialize CPU measurement with short interval
        psutil.cpu_percent(interval=0.1)
        
    def setup_log_file(self):
        headers = [
            'timestamp', 
            # CPU Metrics
            'cpu_percent', 'cpu_user', 'cpu_system', 'cpu_idle',
            'load_1min', 'load_5min', 'load_15min',
            # Memory Metrics
            'mem_total_gb', 'mem_used_gb', 'mem_available_gb', 'mem_percent',
            # Disk Metrics
            'disk_total_gb', 'disk_used_gb', 'disk_free_gb', 'disk_percent',
            # System Uptime
            'uptime_hours', 'system_idle_seconds',
            # Process Metrics
            'process_total', 'process_running', 'process_sleeping',
            # Top Processes
            'top_cpu_1', 'top_cpu_2', 'top_cpu_3',
            'top_mem_1', 'top_mem_2', 'top_mem_3',
            # GPU (optional)
            'gpu_available', 'gpu_usage', 'gpu_memory_used', 'gpu_memory_total'
        ]
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def get_system_idle_time(self):
        """Get system idle time from /proc/uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds, idle_seconds = map(float, f.read().split())
            return idle_seconds
        except:
            return 0
    
    def get_gpu_info(self):
        """Try to get GPU information (if available)"""
        gpu_info = {
            'available': False,
            'usage': 0,
            'memory_used': 0,
            'memory_total': 0
        }
        
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2  # Add timeout to prevent hanging
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = result.stdout.strip().split(',')
                if len(data) >= 3:
                    gpu_info = {
                        'available': True,
                        'usage': float(data[0].strip()),
                        'memory_used': float(data[1].strip()),
                        'memory_total': float(data[2].strip())
                    }
                
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            try:
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
        cpu_times = psutil.cpu_times_percent(interval=1)
        return {
            'user': cpu_times.user,
            'system': cpu_times.system,
            'idle': cpu_times.idle,
            'iowait': getattr(cpu_times, 'iowait', 0)
        }
    
    def count_process_states(self):
        """Count processes by state"""
        running = 0
        sleeping = 0
        total = 0
        
        for proc in psutil.process_iter(['pid', 'status']):
            try:
                status = proc.info['status']
                if status == psutil.STATUS_RUNNING:
                    running += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping += 1
                total += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                pass
        
        return total, running, sleeping
    
    def get_top_processes(self):
        """Get top 3 processes by CPU and Memory"""
        processes = []
        
        # First pass: initialize CPU percent measurement
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc.cpu_percent()  # Initialize measurement
            except:
                pass
        
        # Small delay for accurate measurement
        time.sleep(0.5)
        
        # Second pass: collect data
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                # Filter out None values and system processes
                if (info.get('cpu_percent') is not None and 
                    info.get('memory_percent') is not None and
                    info.get('name')):
                    processes.append(info)
            except:
                pass
        
        # Get top 3 by CPU
        top_cpu = []
        cpu_sorted = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:3]
        for proc in cpu_sorted:
            top_cpu.append(f"{proc.get('name', 'unknown')}:{proc.get('cpu_percent', 0):.1f}%")
        
        # Get top 3 by Memory
        top_mem = []
        mem_sorted = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:3]
        for proc in mem_sorted:
            top_mem.append(f"{proc.get('name', 'unknown')}:{proc.get('memory_percent', 0):.1f}%")
        
        # Ensure we always have 3 entries
        while len(top_cpu) < 3:
            top_cpu.append("None:0%")
        while len(top_mem) < 3:
            top_mem.append("None:0%")
        
        return top_cpu, top_mem
    
    def collect_metrics(self):
        """Collect ALL system metrics"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. CPU Metrics (REQUIREMENT i)
        cpu_percent = psutil.cpu_percent(interval=1)  # 1-second average for accuracy
        cpu_details = self.get_detailed_cpu_info()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        
        # 2. Memory Metrics (REQUIREMENT ii)
        memory = psutil.virtual_memory()
        
        # 3. Disk Metrics (REQUIREMENT iii)
        disk = psutil.disk_usage('/')
        
        # 4. System Uptime (REQUIREMENT iv)
        uptime_seconds = time.time() - psutil.boot_time()
        idle_seconds = self.get_system_idle_time()  # NEW: System idle time
        
        # 5. Active Processes (REQUIREMENT v)
        total_procs, running_procs, sleeping_procs = self.count_process_states()
        top_cpu, top_mem = self.get_top_processes()
        
        # 6. GPU Metrics (Optional bonus)
        gpu_info = self.get_gpu_info()
        
        # Prepare data row - ALL REQUIREMENTS COVERED
        row = [
            # Timestamp
            timestamp,
            
            # CPU Metrics (Requirement i)
            cpu_percent,                    # CPU usage percentage
            cpu_details['user'],            # CPU user time
            cpu_details['system'],          # CPU system time  
            cpu_details['idle'],            # CPU idle time
            load_avg[0],                    # Load average 1 min
            load_avg[1],                    # Load average 5 min
            load_avg[2],                    # Load average 15 min
            
            # Memory Metrics (Requirement ii)
            round(memory.total / (1024**3), 2),     # Total memory GB
            round(memory.used / (1024**3), 2),      # Used memory GB
            round(memory.available / (1024**3), 2), # Available memory GB
            memory.percent,                         # Memory usage percentage
            
            # Disk Metrics (Requirement iii)
            round(disk.total / (1024**3), 2),       # Total disk space GB
            round(disk.used / (1024**3), 2),        # Used disk space GB
            round(disk.free / (1024**3), 2),        # Free disk space GB
            disk.percent,                           # Disk usage percentage
            
            # System Uptime (Requirement iv)
            round(uptime_seconds / 3600, 2),        # Total uptime hours
            round(idle_seconds, 2),                 # System idle time seconds
            
            # Active Processes (Requirement v)
            total_procs,                            # Total number of processes
            running_procs,                          # Number of running processes
            sleeping_procs,                         # Number of sleeping processes
            
            # Top 3 processes by CPU usage
            top_cpu[0], top_cpu[1], top_cpu[2],
            
            # Top 3 processes by memory usage  
            top_mem[0], top_mem[1], top_mem[2],
            
            # GPU Metrics (Bonus - not required but good to have)
            gpu_info['available'],
            gpu_info['usage'],
            gpu_info['memory_used'],
            gpu_info['memory_total']
        ]
        
        return row
    
    def log_metrics(self):
        """Save metrics to CSV file"""
        row = self.collect_metrics()
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Display the performance
        print(f"[{row[0]}] CPU: {row[1]:.1f}% | Mem: {row[11]:.1f}% | Disk: {row[16]:.1f}%")
        print(f"  Processes: {row[19]} total, {row[20]} running, {row[21]} sleeping")
        print(f"  Load: {row[5]:.2f}, {row[6]:.2f}, {row[7]:.2f}")
        print(f"  Top CPU: {row[22]}, {row[23]}, {row[24]}")
    
    def run_monitor(self, interval_seconds=10):
        """Run monitoring loop with precise timing"""
        print("="*60)
        print("SYSTEM PERFORMANCE MONITOR - STARTING")
        print("="*60)
        print(f"Logging to: {self.log_file}")
        print(f"Interval: {interval_seconds} seconds")
        print("="*60)
        print("Monitoring the following: ")
        print("1. CPU Metrics: usage %, load average, process count")
        print("2. Memory Metrics: total/used/available, usage %")
        print("3. Disk Metrics: total/used/free, usage % (root)")
        print("4. System Uptime: total uptime, system idle time")
        print("5. Active Processes: total, running vs sleeping, top 3")
        print("="*60)
        print("Press Ctrl+C to stop\n")
        
        cycle_count = 0
        next_run = time.time()
        
        try:
            while True:
                cycle_count += 1
                print(f"\n--- Cycle #{cycle_count} ---")
                self.log_metrics()
                
                # Calculate precise sleep time
                next_run += interval_seconds
                sleep_time = next_run - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print(f"Warning: Monitoring cycle took longer than {interval_seconds}s")
                    next_run = time.time()  # Reset
                    
        except KeyboardInterrupt:
            print(f"\n{'='*60}")
            print("SYSTEM PERFORMANCE MONITOR - STOPPED")
            print(f"Total cycles completed: {cycle_count}")
            print(f"Data saved to: {self.log_file}")
            print("="*60)

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    # Create tracker
    tracker = SystemPerformanceTracker()
    
    # Get interval from user
    try:
        interval_input = input("Enter monitoring interval in seconds (default 10): ").strip()
        interval = int(interval_input) if interval_input else 10
    except ValueError:
        print("Invalid input, using default 10 seconds")
        interval = 10
    
    # Validate interval
    if interval < 1:
        print("Interval too small, using minimum 1 second")
        interval = 1
    elif interval > 300:
        print("Interval too large, using maximum 300 seconds (5 minutes)")
        interval = 300
    
    # Start monitoring
    tracker.run_monitor(interval)