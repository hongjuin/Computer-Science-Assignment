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

        # Initialize CPU measurements (important for accurate percentages)
        psutil.cpu_percent(interval=None)
        psutil.cpu_times_percent(interval=None)

    def setup_log_file(self):
        """Create CSV file with headers"""
        headers = [
            'timestamp',
            'cpu_percent', 'cpu_user', 'cpu_system', 'cpu_idle',
            'load_1min', 'load_5min', 'load_15min',
            'mem_total_gb', 'mem_used_gb', 'mem_available_gb', 'mem_percent',
            'disk_total_gb', 'disk_used_gb', 'disk_free_gb', 'disk_percent',
            'uptime_hours', 'system_idle_seconds',
            'process_count', 'running_processes', 'sleeping_processes',
            'top_cpu_1', 'top_cpu_2', 'top_cpu_3',
            'top_mem_1', 'top_mem_2', 'top_mem_3',
            'gpu_available', 'gpu_usage', 'gpu_memory_used', 'gpu_memory_total'
        ]

        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                csv.writer(f).writerow(headers)

    def get_gpu_info(self):
        """Get GPU information if available"""
        gpu_info = {
            'available': False,
            'usage': 0,
            'memory_used': 0,
            'memory_total': 0
        }

        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi',
                 '--query-gpu=utilization.gpu,memory.used,memory.total',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                data = result.stdout.strip().split(',')
                gpu_info = {
                    'available': True,
                    'usage': float(data[0]),
                    'memory_used': float(data[1]),
                    'memory_total': float(data[2])
                }
        except Exception:
            pass

        return gpu_info

    def get_detailed_cpu_info(self):
        """Get CPU time breakdown"""
        cpu = psutil.cpu_times_percent(interval=None)
        return {
            'user': cpu.user,
            'system': cpu.system,
            'idle': cpu.idle
        }

    def get_top_processes(self):
        """Get top 3 processes by CPU and memory usage"""
        processes = []

        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                p.cpu_percent()
            except Exception:
                pass

        time.sleep(0.1)

        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if p.info['cpu_percent'] is not None:
                    processes.append(p.info)
            except Exception:
                pass

        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        top_cpu = [(p['name'], p['cpu_percent']) for p in processes[:3]]

        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        top_mem = [(p['name'], p['memory_percent']) for p in processes[:3]]

        return top_cpu, top_mem

    def collect_metrics(self):
        """Collect all system metrics"""

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_detail = self.get_detailed_cpu_info()

        # Load average (Linux only)
        try:
            load_1, load_5, load_15 = psutil.getloadavg()
        except AttributeError:
            load_1 = load_5 = load_15 = 0.0

        # Memory
        mem = psutil.virtual_memory()

        # Disk (cross-platform)
        disk_path = '/' if os.name != 'nt' else 'C:\\'
        disk = psutil.disk_usage(disk_path)

        # Uptime & idle time
        uptime_seconds = time.time() - psutil.boot_time()
        idle_seconds = psutil.cpu_times().idle

        # Processes
        process_count = len(psutil.pids())
        running = sleeping = 0

        for p in psutil.process_iter(['status']):
            try:
                if p.info['status'] == psutil.STATUS_RUNNING:
                    running += 1
                elif p.info['status'] == psutil.STATUS_SLEEPING:
                    sleeping += 1
            except Exception:
                pass

        top_cpu, top_mem = self.get_top_processes()
        gpu = self.get_gpu_info()

        return [
            timestamp,
            cpu_percent, cpu_detail['user'], cpu_detail['system'], cpu_detail['idle'],
            load_1, load_5, load_15,
            round(mem.total / 1024**3, 2),
            round(mem.used / 1024**3, 2),
            round(mem.available / 1024**3, 2),
            mem.percent,
            round(disk.total / 1024**3, 2),
            round(disk.used / 1024**3, 2),
            round(disk.free / 1024**3, 2),
            disk.percent,
            round(uptime_seconds / 3600, 2),
            round(idle_seconds, 2),
            process_count, running, sleeping,
            f"{top_cpu[0][0]}({top_cpu[0][1]:.1f}%)",
            f"{top_cpu[1][0]}({top_cpu[1][1]:.1f}%)",
            f"{top_cpu[2][0]}({top_cpu[2][1]:.1f}%)",
            f"{top_mem[0][0]}({top_mem[0][1]:.1f}%)",
            f"{top_mem[1][0]}({top_mem[1][1]:.1f}%)",
            f"{top_mem[2][0]}({top_mem[2][1]:.1f}%)",
            gpu['available'], gpu['usage'],
            gpu['memory_used'], gpu['memory_total']
        ]

    def log_metrics(self):
        row = self.collect_metrics()

        with open(self.log_file, 'a', newline='') as f:
            csv.writer(f).writerow(row)

        print(f"[{row[0]}] ", f"CPU {row[1]}% | "f"Mem {row[11]}% |" f"Disk {row[16]}% |" f"Uptime {row[16]}h |" f"Processes {row[17]} (Run {row[18]} / Sleep {row[19]})")

    def run_monitor(self, interval=10):
        print("System Performance Monitor started")
        next_run = time.time()

        try:
            while True:
                self.log_metrics()
                next_run += interval
                sleep_time = next_run - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

if __name__ == "__main__":
    tracker = SystemPerformanceTracker()

    interval = input("Enter monitoring interval in seconds (default 10): ").strip()
    interval = int(interval) if interval.isdigit() else 10

    tracker.run_monitor(interval)

