"""
File: abm_core.py
Author: Matthew R. Marcelino, PhD

Version 2.0 adds functions for implementing an intervention (dynamic environment) and
agent heterogeneity (vaccination).
"""

import os
import sys
import random
import argparse
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

# --- Model Constants ---
SUSCEPTIBLE = 0
INFECTED = 1
REMOVED = 2

# --- Core Agent-Based Model Classes ---
class Agent:
    """Represents a single entity on the grid with its own state and behavior."""
    def __init__(self, agent_id, x, y, initial_state=SUSCEPTIBLE):
        self.id = agent_id
        self.x, self.y = x, y
        self.state = initial_state
        self.next_state = self.state
        self.is_vaccinated = False # Add this new attribute

        self.infection_timer = 0
        self.removed_timer = 0
        self.removed_recovery_goal = -1

    def step(self, model):
        """Determines the agent's next state based on its current state and surroundings."""
        if self.state == SUSCEPTIBLE and not self.is_vaccinated: # Add the check here
            if model.cost[self.y, self.x] <= model.cost_threshold:
                infected_neighbors = sum(1 for neighbor in model.get_neighbors(self) if neighbor.state == INFECTED)
                if infected_neighbors > 0 and random.random() < model.spread_probability:
                    self.next_state = INFECTED
        elif self.state == INFECTED:
            self.infection_timer += 1
            if self.infection_timer >= model.infection_duration:
                self.next_state = REMOVED
                self.removed_recovery_goal = random.randint(model.recovery_time_min, model.recovery_time_max)
        elif self.state == REMOVED:
            self.removed_timer += 1
            if self.removed_timer >= self.removed_recovery_goal:
                self.next_state = SUSCEPTIBLE

    def advance(self):
        """Applies the new state and resets timers if a state change occurs."""
        if self.state != self.next_state:
            if self.next_state == REMOVED: self.infection_timer = 0
            elif self.next_state == SUSCEPTIBLE: self.removed_timer = 0; self.removed_recovery_goal = -1
        self.state = self.next_state

class DiseaseModel:
    """Manages the grid, agents, and the overall simulation process."""
    def __init__(self, cost_path, initial_infection_path, params):
        self.cost_threshold = params.get('cost_threshold', 0.6)
        self.spread_probability = params.get('spread_probability', 0.05)
        self.infection_duration = params.get('infection_duration', 3)
        self.recovery_time_min = params.get('recovery_time_min', 8)
        self.recovery_time_max = params.get('recovery_time_max', 15)
        self.vaccination_rate = params.get('vaccination_rate', 0.0) # Get the new parameter

        self._load_and_align_rasters(cost_path, initial_infection_path)
        self._initialize_agents()

    def _load_and_align_rasters(self, cost_path, initial_infection_path):
        with rasterio.open(cost_path) as src:
            self.cost = src.read(1); self.profile = src.profile
            self.grid_height, self.grid_width = self.cost.shape
        with rasterio.open(initial_infection_path) as infection_src:
            self.initial_infection_mask = np.zeros_like(self.cost, dtype=rasterio.uint8)
            reproject(source=rasterio.band(infection_src, 1), destination=self.initial_infection_mask,
                      src_transform=infection_src.transform, src_crs=infection_src.crs,
                      dst_transform=self.profile['transform'], dst_crs=self.profile['crs'],
                      resampling=Resampling.nearest)

    def _initialize_agents(self):
        self.agents = []; self.grid = [[None] * self.grid_width for _ in range(self.grid_height)]
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                state = INFECTED if self.initial_infection_mask[y, x] else SUSCEPTIBLE
                agent = Agent((y, x), x, y, state)
                if agent.state == SUSCEPTIBLE and random.random() < self.vaccination_rate: # THIS IS THE NEW LOGIC
                    agent.is_vaccinated = True
                self.agents.append(agent); self.grid[y][x] = agent

    def get_neighbors(self, agent):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                nx, ny = (agent.x + dx) % self.grid_width, (agent.y + dy) % self.grid_height
                yield self.grid[ny][nx]

    def implement_control_measure(self):
        """Finds all infected cells and makes them (and neighbors) unsuitable. """
        print("n\Implementing control measure!")
        # Create a buffer around infected cells to make a firewall
        cells_to_control = set()
        for agent in self.agents:
            if agent.state == INFECTED:
                # Add the agent's cell
                cells_to_control.add((agent.x, agent.y))
                # Add all its neighbors' cells
                for neighbor in self.get_neighbors(agent):
                    cells_to_control.add((neighbor.x, neighbor.y))
        
        # Set the cost of these cells to 1, making them immune
        for x, y in cells_to_control:
            self.cost[y, x] = 1.0

    def step(self):
        for agent in self.agents: agent.step(self)
        for agent in self.agents: agent.advance()

    def run_simulation(self, time_steps, output_dir, intervention_time=-1): # Add intervention_time
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        print(f"Starting simulation for {time_steps} time steps, outputting to '{output_dir}'...")
        for t in range(time_steps):
            if t == intervention_time: # THIS IS THE NEW LOGIC
                self.implement_control_measure()
            self.step()
            state_grid = np.array([[agent.state for agent in row] for row in self.grid], dtype=np.int32)
            output_profile = self.profile.copy()
            output_profile.update(dtype=rasterio.int32, count=1, compress='lzw')
            filepath = os.path.join(output_dir, f"abm_state_year_{t:03d}.tif")
            with rasterio.open(filepath, 'w', **output_profile) as dst: dst.write(state_grid, 1)
            sys.stdout.write(f"\r  > Year {t+1}/{time_steps} complete."); sys.stdout.flush()
        print("\nSimulation finished.")

# This allows the script to be run directly to generate data if needed
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Core ABM Simulation Engine.")
    # Add argparse arguments here as before if you want this to be runnable
    print("This script contains the core model classes and is intended to be imported.")
    print("To run a simulation, import DiseaseModel into another script or notebook.")