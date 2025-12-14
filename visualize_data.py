#!/usr/bin/env python3
"""
Traffic Management System - Data Visualization
Generates charts and reports from historical data
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys


def load_cycle_data(filepath: str = "traffic_data/cycle_data.json") -> List[Dict]:
    """Load cycle data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        return []


def print_summary(data: List[Dict]):
    """Print summary statistics"""
    if not data:
        print("No data available")
        return
    
    total_cycles = len(data)
    total_vehicles = sum(c['vehicle_count'] for c in data)
    avg_vehicles = total_vehicles / total_cycles
    
    avg_green = sum(c['green_time'] for c in data) / total_cycles
    min_green = min(c['green_time'] for c in data)
    max_green = max(c['green_time'] for c in data)
    
    # Vehicle types
    vehicle_breakdown = {}
    for cycle in data:
        for v_type, count in cycle.get('vehicle_stats', {}).items():
            if v_type != 'total':
                vehicle_breakdown[v_type] = vehicle_breakdown.get(v_type, 0) + count
    
    print("\n" + "="*60)
    print("TRAFFIC MANAGEMENT SYSTEM - DATA SUMMARY")
    print("="*60)
    
    print(f"\n📊 CYCLE STATISTICS")
    print(f"   Total Cycles: {total_cycles}")
    print(f"   Date Range: {data[0]['timestamp'][:10]} to {data[-1]['timestamp'][:10]}")
    
    print(f"\n🚗 VEHICLE STATISTICS")
    print(f"   Total Vehicles Detected: {total_vehicles}")
    print(f"   Average per Cycle: {avg_vehicles:.1f}")
    print(f"   Vehicle Breakdown:")
    for v_type, count in sorted(vehicle_breakdown.items()):
        percentage = (count / total_vehicles * 100) if total_vehicles > 0 else 0
        print(f"      - {v_type.capitalize()}: {count} ({percentage:.1f}%)")
    
    print(f"\n🚦 SIGNAL TIMING")
    print(f"   Average Green Time: {avg_green:.1f} seconds")
    print(f"   Minimum Green Time: {min_green} seconds")
    print(f"   Maximum Green Time: {max_green} seconds")
    print(f"   Time Saved vs Fixed (30s): {sum(c['green_time'] - 30 for c in data if c['green_time'] > 30):.0f} seconds total")
    
    print("\n" + "="*60 + "\n")


def print_ascii_chart(data: List[Dict], metric: str = "vehicle_count"):
    """Print ASCII bar chart"""
    if not data:
        return
    
    # Take last 20 data points
    recent_data = data[-20:]
    
    values = [d[metric] for d in recent_data]
    max_value = max(values) if values else 1
    
    chart_width = 50
    
    print(f"\n{metric.replace('_', ' ').title()} - Last 20 Cycles")
    print("-" * (chart_width + 15))
    
    for i, value in enumerate(values):
        bar_length = int((value / max_value) * chart_width)
        bar = "█" * bar_length
        print(f"{i+1:2d} | {bar} {value}")
    
    print("-" * (chart_width + 15))
    print(f"Max: {max_value}  Avg: {sum(values)/len(values):.1f}\n")


def print_time_distribution(data: List[Dict]):
    """Print distribution of green light times"""
    if not data:
        return
    
    green_times = [d['green_time'] for d in data]
    
    # Create histogram bins
    bins = {
        "15-30s": 0,
        "31-45s": 0,
        "46-60s": 0,
        "61-90s": 0,
        "91-120s": 0
    }
    
    for time in green_times:
        if time <= 30:
            bins["15-30s"] += 1
        elif time <= 45:
            bins["31-45s"] += 1
        elif time <= 60:
            bins["46-60s"] += 1
        elif time <= 90:
            bins["61-90s"] += 1
        else:
            bins["91-120s"] += 1
    
    total = len(green_times)
    max_count = max(bins.values())
    
    print("\nGreen Light Time Distribution")
    print("-" * 60)
    
    for range_str, count in bins.items():
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int((count / max_count) * 40) if max_count > 0 else 0
        bar = "█" * bar_length
        print(f"{range_str:10s} | {bar:40s} {count:3d} ({percentage:5.1f}%)")
    
    print("-" * 60 + "\n")


def print_efficiency_analysis(data: List[Dict]):
    """Analyze efficiency improvements"""
    if not data:
        return
    
    fixed_baseline = 30  # Assume 30s fixed green time
    
    total_adaptive_time = sum(d['green_time'] for d in data)
    total_fixed_time = len(data) * fixed_baseline
    
    time_diff = total_adaptive_time - total_fixed_time
    efficiency = (abs(time_diff) / total_fixed_time * 100)
    
    # Calculate better utilization
    low_traffic = sum(1 for d in data if d['vehicle_count'] < 5)
    high_traffic = sum(1 for d in data if d['vehicle_count'] > 15)
    
    print("\n⚡ EFFICIENCY ANALYSIS")
    print("-" * 60)
    print(f"Fixed Timing (30s baseline):")
    print(f"   Total time: {total_fixed_time} seconds ({total_fixed_time/60:.1f} minutes)")
    
    print(f"\nAdaptive Timing:")
    print(f"   Total time: {total_adaptive_time} seconds ({total_adaptive_time/60:.1f} minutes)")
    
    if time_diff > 0:
        print(f"\n   Additional time used: {time_diff} seconds ({efficiency:.1f}% more)")
        print(f"   Reason: Better service for high-traffic periods")
    else:
        print(f"\n   Time saved: {abs(time_diff)} seconds ({efficiency:.1f}% less)")
        print(f"   Reason: Reduced wait during low-traffic periods")
    
    print(f"\nTraffic Patterns:")
    print(f"   Low traffic cycles (<5 vehicles): {low_traffic} ({low_traffic/len(data)*100:.1f}%)")
    print(f"   High traffic cycles (>15 vehicles): {high_traffic} ({high_traffic/len(data)*100:.1f}%)")
    
    print("\n" + "="*60 + "\n")


def print_algorithm_comparison(data: List[Dict]):
    """Compare performance across algorithms"""
    if not data:
        return
    
    by_algorithm = {}
    for cycle in data:
        alg = cycle.get('algorithm', 'unknown')
        if alg not in by_algorithm:
            by_algorithm[alg] = []
        by_algorithm[alg].append(cycle)
    
    if len(by_algorithm) <= 1:
        return  # Only one algorithm used
    
    print("\n🔬 ALGORITHM COMPARISON")
    print("-" * 60)
    
    for alg, cycles in by_algorithm.items():
        avg_green = sum(c['green_time'] for c in cycles) / len(cycles)
        avg_vehicles = sum(c['vehicle_count'] for c in cycles) / len(cycles)
        
        print(f"\n{alg.upper()}")
        print(f"   Cycles: {len(cycles)}")
        print(f"   Avg Green Time: {avg_green:.1f}s")
        print(f"   Avg Vehicles: {avg_vehicles:.1f}")
    
    print("\n" + "-"*60 + "\n")


def export_report(data: List[Dict], output_file: str = "traffic_report.txt"):
    """Export text report"""
    with open(output_file, 'w') as f:
        # Redirect stdout to file
        old_stdout = sys.stdout
        sys.stdout = f
        
        print_summary(data)
        print_time_distribution(data)
        print_efficiency_analysis(data)
        print_ascii_chart(data, "vehicle_count")
        print_ascii_chart(data, "green_time")
        
        sys.stdout = old_stdout
    
    print(f"✅ Report exported to {output_file}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize traffic system data")
    parser.add_argument(
        '--file', default='traffic_data/cycle_data.json',
        help='Path to cycle data JSON file'
    )
    parser.add_argument(
        '--export', action='store_true',
        help='Export report to text file'
    )
    parser.add_argument(
        '--chart', choices=['vehicles', 'time', 'both'],
        default='both',
        help='Which chart to display'
    )
    
    args = parser.parse_args()
    
    # Load data
    data = load_cycle_data(args.file)
    
    if not data:
        print("No data to visualize. Run the system first to collect data.")
        return
    
    # Print summary
    print_summary(data)
    
    # Print time distribution
    print_time_distribution(data)
    
    # Print efficiency analysis
    print_efficiency_analysis(data)
    
    # Print algorithm comparison
    print_algorithm_comparison(data)
    
    # Print charts
    if args.chart in ['vehicles', 'both']:
        print_ascii_chart(data, "vehicle_count")
    
    if args.chart in ['time', 'both']:
        print_ascii_chart(data, "green_time")
    
    # Export if requested
    if args.export:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_report(data, f"traffic_report_{timestamp}.txt")


if __name__ == "__main__":
    main()
