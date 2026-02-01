#!/usr/bin/env python3
'''
SYSTEM PERFORMANCE MONITOR
'''

import psutil
import time
from datetime import datetime
import csv
import os

class SystemPerformanceTracker:
    
    def __init__(self, log_file="system_performance_log.csv"):
        self.log_file = log_file
        self.setup_log_file()
        # Initialize CPU measurement
        psutil.cpu_percent(interval=0.1)
        
    def setup_log_file(self):
        headers = [
            'timestamp',
            # CPU Metrics 
            'cpu_percent', 'load_1min', 'load_5min', 'load_15min', 'running_processes',
            # Memory Metrics
            'mem_total_gb', 'mem_used_gb', 'mem_available_gb', 'mem_percent',
            # Disk Metrics 
            'disk_total_gb', 'disk_used_gb', 'disk_free_gb', 'disk_percent',
            # System Uptime
            'uptime_hours', 'system_idle_seconds',
            # Active Processes 
            'total_processes', 'running_vs_sleeping',  # Combined as string "running/sleeping"
            'top_cpu_1', 'top_cpu_2', 'top_cpu_3',
            'top_mem_1', 'top_mem_2', 'top_mem_3'
        ]
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def get_system_idle_time(self):
        '''Get system idle time from /proc/uptime '''
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds, idle_seconds = map(float, f.read().split())
            return idle_seconds
        except:
            print("Warning: Could not read /proc/uptime")
            return 0
    
    def get_memory_metrics(self):
        '''Get memory metrics exactly'''
        memory = psutil.virtual_memory()
        return {
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),  # NOT free!
            'percent': memory.percent
        }
    
    def get_process_counts(self):
        """Get process counts: total, running, sleeping"""
        running = 0
        sleeping = 0
        
        for proc in psutil.process_iter(['pid', 'status']):
            try:
                status = proc.info['status']
                if status == psutil.STATUS_RUNNING:
                    running += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping += 1
            except:
                continue
        
        total = running + sleeping  
        
        return total, running, sleeping
    
    def get_top_processes(self):
        '''Get top 3 processes by CPU and Memory'''
        processes = []
        
        # First pass: initialize CPU measurement
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc.cpu_percent()
            except:
                pass
        
        time.sleep(0.5)  # Allow time for measurement
        
        # collect data
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if (info.get('cpu_percent') is not None and 
                    info.get('memory_percent') is not None):
                    processes.append(info)
            except:
                pass
        
        # Top 3 by CPU
        top_cpu = []
        cpu_sorted = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:3]
        for proc in cpu_sorted:
            top_cpu.append(f"{proc.get('name', 'unknown')}:{proc.get('cpu_percent', 0):.1f}%")
        
        # Top 3 by Memory
        top_mem = []
        mem_sorted = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:3]
        for proc in mem_sorted:
            top_mem.append(f"{proc.get('name', 'unknown')}:{proc.get('memory_percent', 0):.1f}%")
        
        # Ensure we have 3 entries
        while len(top_cpu) < 3:
            top_cpu.append("None:0%")
        while len(top_mem) < 3:
            top_mem.append("None:0%")
        
        return top_cpu, top_mem
    
    def collect_metrics(self):
        '''Collect ALL metrics'''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. CPU METRICS (Requirement i)
        cpu_percent = psutil.cpu_percent(interval=1)  # 1-second average
        load_avg = psutil.getloadavg()  # (1min, 5min, 15min)
        
        # Get running process count for CPU metrics
        _, running_count, _ = self.get_process_counts()
        
        # 2. MEMORY METRICS (Requirement ii)
        mem = self.get_memory_metrics()
        
        # 3. DISK METRICS (Requirement iii)
        disk = psutil.disk_usage('/')  # Root partition only
        
        # 4. SYSTEM UPTIME (Requirement iv) - WITH IDLE TIME!
        uptime_seconds = time.time() - psutil.boot_time()
        idle_seconds = self.get_system_idle_time()  # THIS WAS MISSING!
        
        # 5. ACTIVE PROCESSES (Requirement v)
        total_procs, running_procs, sleeping_procs = self.get_process_counts()
        top_cpu, top_mem = self.get_top_processes()
        
        # Prepare data row - EXACTLY matching requirements
        row = [
            # Timestamp
            timestamp,
            
            # CPU Metrics (Requirement i)
            round(cpu_percent, 2),        # CPU usage percentage
            round(load_avg[0], 2),        # Load average 1 min
            round(load_avg[1], 2),        # Load average 5 min
            round(load_avg[2], 2),        # Load average 15 min
            running_count,                # Number of running processes
            
            # Memory Metrics (Requirement ii)
            mem['total_gb'],              # Total memory GB
            mem['used_gb'],               # Used memory GB
            mem['available_gb'],          # Available memory GB (NOT free!)
            mem['percent'],               # Memory usage percentage
            
            # Disk Metrics (Requirement iii)
            round(disk.total / (1024**3), 2),  # Total disk space GB
            round(disk.used / (1024**3), 2),   # Used disk space GB
            round(disk.free / (1024**3), 2),   # Free disk space GB
            disk.percent,                      # Disk usage percentage
            
            # System Uptime (Requirement iv)
            round(uptime_seconds / 3600, 2),   # Total uptime hours
            round(idle_seconds, 2),            # System idle time seconds (MISSING IN YOUR CODE!)
            
            # Active Processes (Requirement v)
            total_procs,                       # Total number of processes
            f"{running_procs}/{sleeping_procs}",  # Running vs sleeping processes
            top_cpu[0], top_cpu[1], top_cpu[2],   # Top 3 by CPU usage
            top_mem[0], top_mem[1], top_mem[2]    # Top 3 by memory usage
        ]
        
        return row
    
    def log_metrics(self):
        '''Save metrics to CSV file'''
        row = self.collect_metrics()
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            
        print(f"[{row[0]}]")
        print(f"CPU: {row[1]}% | Load: {row[2]}, {row[3]}, {row[4]} | Running: {row[5]} processes")
        print(f"Memory: {row[6]}GB total, {row[7]}GB used, {row[8]}GB available ({row[9]}%)")
        print(f"Disk: {row[10]}GB total, {row[11]}GB used, {row[12]}GB free ({row[13]}%)")
        print(f"Uptime: {row[14]} hours | System Idle: {row[15]} seconds")
        print(f"Processes: {row[16]} total, {row[17]} (running/sleeping)")
        print(f"Top CPU: {row[18]}, {row[19]}, {row[20]}")
        print(f"Top Memory: {row[21]}, {row[22]}, {row[23]}")
    
    def run_monitor(self, interval_seconds=10):
        
        print("Collecting tracking results:")
        print("1. CPU: % usage, load avg (min), running processes")
        print("2. Memory: total/used/available GB, usage %")
        print("3. Disk: total/used/free GB, % usage (root /)")
        print("4. Uptime: total hours + SYSTEM IDLE TIME seconds")
        print("5. Processes: total, running/sleeping, top 3 CPU/Memory")
        print("="*60)
        print(f"Interval: {interval_seconds} seconds")
        print(f"Log file: {self.log_file}")
        print("Press Ctrl+C to stop\n")
        
        cycle = 0
        next_run = time.time()
        
        try:
            while True:
                cycle += 1
                print(f"\n--- Cycle #{cycle} ---")
                self.log_metrics()
                
                # Precise timing
                next_run += interval_seconds
                sleep_time = next_run - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print(f"Warning: Cycle took longer than {interval_seconds}s")
                    next_run = time.time()
                    
        except KeyboardInterrupt:
            print(f"\n{'='*60}")
            print("MONITORING STOPPED")
            print(f"Total cycles: {cycle}")
            print(f"Data saved to: {self.log_file}")

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    tracker = SystemPerformanceTracker()
    
    # Get interval
    try:
        user_input = input("Monitoring interval (seconds, default 10): ").strip()
        interval = int(user_input) if user_input else 10
    except:
        interval = 10
    
    # Start monitoring
    tracker.run_monitor(interval)
