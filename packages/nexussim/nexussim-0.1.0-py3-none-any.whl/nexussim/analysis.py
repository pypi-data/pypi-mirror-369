"""
File: abm_analysis.py
Author: Matthew R. Marcelino, PhD
"""

# =============================================================================
# Agent-Based Model Analysis Toolbox
#
# Description:
# A library of functions to analyze the raster outputs from an ABM simulation.
# This module is intended to be imported, not run directly. The functions
# process simulation data to generate plots, statistics, and animations.
#
# Dependencies:
# numpy, pandas, rasterio, matplotlib, scikit-imate, imageio, scipy
# =============================================================================

# Import dependencies
import os
import glob
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from skimage.measure import label
import imageio.v2 as imageio
from scipy.ndimage import center_of_mass, distance_transform_edt
from scipy.stats import linregress

# Analysis Constants
STATES_DICT = {0: "Susceptible", 1: "Infected", 2: "Removed"}
COLORS_DICT = {0: "green", 1: "red", 2: "gray"}

# Helper Function
def get_simulation_files(sim_output_dir):
  """
  Finds and sorts all GeoTIFF output files from a simulation run.

  Args:
    sim_output_dir (str): Path to the directory containing simulation raster files.
  
  Returns:
    list: A chronologically sorted list of GeoTIFF file paths. Returns an empty
          list if the directory is not found or contains no .tif files.
  """
  if not os.path.isdir(sim_output_dir):
    print(f"Error: Directory not found at '{sim_output_dir}'")
    return []
  tif_files = sorted(glob.glob(os.path.join(sim_output_dir, "*.tif")))
  if not tif_files:
    print(f"Warning: No .tif files found in '{sim_output_dir}'")
  return tif_files

# Analysis Tools
def generate_epidemic_curve(tif_files, output_path):
  """
  Counts cells in each state for each time step, saves a plot, and returns the data.

  Args:
    tif_files (list): A list of paths to the simulation's output raster files.
    output_path (str): The full path (including filename) to save the output plot.
  
  Returns:
    pandas.DataFrame: A DataFrame with the counts of each state per year.
  """
  print("Generating epidemic curve...")
  time_counts = []
  for time, file_path in enumerate(tif_files):
    with rasterio.open(file_path) as src:
      data = src.read(1)
      counts = {'time': time, **{name: np.sum(data == val) for val, name in STATES_DICT.items()}}
      time_counts.append(counts)
  
  df = pd.DataFrame(time_counts).set_index('time')
  plt.style.use('seaborn-v0_8-whitegrid')
  fig, ax = plt.subplots(figsize=(12, 7))
  df.plot(ax=ax, color=[COLORS_DICT[val] for val in STATES_DICT.keys()])
  ax.set_title('Epidemic Curve', fontsize=16)
  ax.set_xlabel('Time'); ax.set_ylabel('Number of Cells')
  ax.legend(title='State'); ax.grid(True)

  plt.savefig(output_path); plt.close()
  print(f" > Epidemic curve plot saved to {output_path}")
  return df

def analyze_patches(tif_file_path, state_to_analyze=1):
  """
  Analyzes spatial patches for a given state in a single raster file.

  Args:
    tif_file_path (str): The path to a single raster file.
    state_to_analyze (int, optional): The state value to analyze (default is 1 for Infected).
  
  Returns:
    dict: A dictionary containing patch statistics (num_patches, largest_patch, avg_patch).
  """
  print(f"Analyzing patches in {os.path.basename(tif_file_path)}...")
  with rasterio.open(tif_file_path) as src:
    data = src.read(1)
  mask = (data == state_to_analyze)
  labeled_array, num_patches = label(mask, return_num=True, connectivity=2)

  stats = {'num_patches': 0, 'largest_patch': 0, 'avg_patch': 0}
  if num_patches > 0:
    patch_sizes = np.bincount(labeled_array.ravel())[1:]
    stats['num_patches'] = num_patches
    stats['largest_patch'] =np.max(patch_sizes)
    stats['avg_patch'] = np.mean(patch_sizes)
    print(f" > Found {stats['num_patches']} patches. Largest: {stats['largest_patch']}, Avg: {stats['avg_patch']:.2f}")
  else:
    print(" > No patches of the specified state found.")
  return stats

def track_infection_centroid(tif_files, background_raster_path, output_path):
  """
  Calculates and plots the trajectory of the infection's center of mass.

  Args:
    tif_files (list): List of simulation output raster files.
    background_raster_path (str): Path to a raster to use as a background map (e.g., Cost).
    output_path (str): Full path to save the output plot.
  """
  print("Tracking infection centroid...")
  centroids = []
  for file_path in tif_files:
    with rasterio.open(file_path) as src:
      data = src.read(1)
      centroids.append(center_of_mass(data == 1) if np.any(data == 1) else None)
  
  with rasterio.open(background_raster_path) as src:
    background_data = src.read(1)
  fig, ax = plt.subplots(figsize=(10, 10))
  ax.imshow(background_data, cmap='viridis', interpolation='none')

  valid_centroids = [c for c in centroids if c is not None]
  if valid_centroids:
    y_coords, x_coords = zip(*valid_centroids)
    ax.plot(x_coords, y_coords, 'r-', marker='o', markersize=3, label='Centroid Path')
    ax.plot(x_coords[0], y_coords[0], 'go', markersize=10, label='Start')
    ax.plot(x_coords[-1], y_coords[-1], 'wo', markersize=10, label='End')
  
  ax.set_title('Trajectory of Infection Centroid'); ax.legend(); ax.set_aspect('equal')
  plt.savefig(output_path); plt.close()
  print(f" > Centroid trajectory plot saved to {output_path}")

def create_animation(tif_files, output_path, duration=0.2):
  """
  Creates an animated GIF of the simulation over time.

  Args:
    tif_files (list): List of simulation output raster files.
    output_path (str): Full path to save the output GIF file.
    duration (float, optional): The time to display each frame in seconds. Defaults to 0.2.
  """
  print("Creating simulation animation...")
  temp_image_files = []
  cmap = ListedColormap([COLORS_DICT[i] for i in sorted(COLORS_DICT.keys())])
  bounds = list(sorted(COLORS_DICT.keys())) + [len(COLORS_DICT)]
  norm = plt.Normalize(vmin=min(bounds), vmax=max(bounds))

  for i, file_path in enumerate(tif_files):
    with rasterio.open(file_path) as src:
      data = src.read(1)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(data, cmap=cmap, norm=norm, interpolation='none')
    ax.set_title(f'Time: {i}'); ax.set_xticks([]); ax.set_yticks([])

    temp_dir = os.path.dirname(output_path)
    temp_filename = os.path.join(temp_dir, f"_temp_frame_{i:03d}.png")
    plt.savefig(temp_filename); plt.close(fig)
    temp_image_files.append(temp_filename)
  
  with imageio.get_writer(output_path, mode='I', duration=duration, loop=0) as writer:
    for filename in temp_image_files:
      writer.append_data(imageio.imread(filename))
    for filename in temp_image_files:
      os.remove(filename)
    print(f" > Animation saved to {output_path}")

def calculate_rate_of_spread(tif_files, output_path):
  """
  Calculates the radial rate of spread from the initial infection sources.

  Args:
    tif_files (list): List of simulation output raster files.
    output_path (str): Full path to save the output plot.
  
  Returns:
    float: The calculated rate of spread (slope of the regression line).
           Returns None if calculation is not possible.
  """
  print("Calculating rate of spread...")
  with rasterio.open(tif_files[0]) as src:
    initial_mask = (src.read(1) != 1); pixel_size = src.transform[0]
  distance_grid = distance_transform_edt(initial_mask) * pixel_size
    
  wavefront_distances = [np.max(distance_grid[rasterio.open(fp).read(1) == 1]) if np.any(rasterio.open(fp).read(1) == 1) else 0 for fp in tif_files]

  time = np.arange(len(wavefront_distances)); valid_mask = np.array(wavefront_distances) > 0
  if np.sum(valid_mask) < 2:
    print("  > Not enough data to calculate spread rate."); return None
    
  slope, intercept, r, p, se = linregress(time[valid_mask], np.array(wavefront_distances)[valid_mask])
  print(f" > Calculated Rate of Spread: {slope:.2f} map units/time (R²={r**2:.2f})")

  plt.figure(figsize=(10, 6));
  plt.plot(time, wavefront_distances, 'bo', label='Max Distance')
  plt.plot(time[valid_mask], intercept + slope * time[valid_mask], 'r-', label=f'Fit (Rate = {slope:.2f})')
  plt.title('Disease Wavefront Distance'); plt.xlabel('Time'); plt.ylabel('Max Distance from Source')
  plt.legend(); plt.grid(True)
  plt.savefig(output_path); plt.close()
  print(f" > Rate of spread plot saved to {output_path}")
  return slope

def create_persistence_map(tif_files, output_tif_path, output_png_path):
  """
  Creates a raster and a plot showing the total number of years each cell was infected.

  Args:
    tif_files (list): List of simulation output raster files.
    output_tif_path (str): Full path to save the output GeoTIFF raster.
    output_png_path (str): Full path to save the output PNG plot.
  
  Returns:
    numpy.ndarray: The 2D array of the persistence grid.
  """
  print("Creating infection persistence map (hotspots)...")
  with rasterio.open(tif_files[0]) as src:
    profile = src.profile; persistence_grid = np.zeros(src.shape, dtype=np.int32)
  for file_path in tif_files:
    with rasterio.open(file_path) as src:
      persistence_grid[src.read(1) == 1] += 1
  
  profile.update(dtype=rasterio.int32, compress='lzw')
  with rasterio.open(output_tif_path, 'w', **profile) as dst:
    dst.write(persistence_grid, 1)
  
  plt.figure(figsize=(10, 8)); plt.imshow(persistence_grid, cmap='inferno')
  plt.colorbar(label='Number of Time Steps Infected'); plt.title('Infection Persistence Hotspots')
  plt.xticks([]); plt.yticks([])
  plt.savefig(output_png_path); plt.close()
  print(f" > Persistence map saved to {output_tif_path}")
  print(f" > Persistence plot saved to {output_png_path}")
  return persistence_grid

# def create_synthetic_rasters(): # This is the code to generate the synthetic raster for the tutorial
  """
  Generates the cost and initial infection rasters needed for the model.
  """
  print("Generating synthetic input data...")
  if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)

  # Define raster metadata
  transform = from_origin(0, GRID_SIZE[0], 1, 1) # Simple pixel-based transform
  profile = {
      'driver': 'GTiff',
      'height': GRID_SIZE[0],
      'width': GRID_SIZE[1],
      'count': 1,
      'dtype': rasterio.float32,
      'crs': CRS,
      'transform': transform,
  }

  # 1. Create the Cost Raster (e.g., a noisy gradient)
  # This simulates a landscape where suitability for the disease varies.
  y_gradient = np.linspace(0.1, 0.9, GRID_SIZE[0])
  x_gradient = np.linspace(0.1, 0.9, GRID_SIZE[1])
  xv, yv = np.meshgrid(x_gradient, y_gradient)
  noise = np.random.rand(GRID_SIZE[0], GRID_SIZE[1]) * 0.2 # Add some noise
  cost_data = (xv * yv) + noise
  cost_data = np.clip(cost_data, 0, 1) # Ensure values are between 0 and 1

  with rasterio.open(COST_RASTER_PATH, 'w', **profile) as dst:
    dst.write(cost_data.astype(rasterio.float32), 1)
  print(f" > Cost raster saved to: {COST_RASTER_PATH}")

  # 2. Create the Initial Infection Raster
  # This will be a small patch of infected cells in the center
  infection_data = np.zeros(GRID_SIZE, dtype=np.int32)
  center_y, center_x = GRID_SIZE[0] // 2, GRID_SIZE[1] // 2
  infection_data[center_y-5:center_y+5, center_x-5:center_x+5] = 1 # A 10x10 infected square

  profile.update(dtype=rasterio.int32) # Change dtype for this integer raster
  with rasterio.open(INIT_INFECTION_PATH, 'w', **profile) as dst:
    dst.write(infection_data, 1)
  print(f" > Initial infection raster saved to: {INIT_INFECTION_PATH}")

# def create_barrier_landscape(): # This is the code to generate the barrier landscape for the tutorial
  """
  Generates a cost raster with a vertical 'river' barrier.
  """
  print("Generating landscape with an impermeable barrier...")
  if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)

  # Base landscape is uniform and suitable (e.g., all 0.2)
  cost_data = np.full(GRID_SIZE, 0.2, dtype=np.float32)

  # Carve a 'river' down the middle by setting cost to 1
  # This creates a 4-pixel wide vertical barrier
  barrier_center = GRID_SIZE[1] // 2
  cost_data[:, barrier_center-2:barrier_center+2] = 1.0

  # Raster profile setup
  transform = from_origin(0, GRID_SIZE[0], 1, 1)
  profile = {'driver': 'GTiff', 'height': GRID_SIZE[0], 'width': GRID_SIZE[1],
             'count': 1, 'dtype': rasterio.float32, 'crs': CRS, 'transform': transform}

  with rasterio.open(COST_RASTER_PATH, 'w', **profile) as dst:
    dst.write(cost_data, 1)
  print(f" > Barrier cost raster saved to: {COST_RASTER_PATH}")

  # Create an initial infection on ONE side of the barrier
  infection_data = np.zeros(GRID_SIZE, dtype=np.int32)
  # Start infection in the center of the left half
  start_y, start_x = GRID_SIZE[0] // 2, GRID_SIZE[1] // 4
  infection_data[start_y-5:start_y+5, start_x-5:start_x+5] = 1

  profile.update(dtype=rasterio.int32)
  with rasterio.open(INIT_INFECTION_PATH, 'w', **profile) as dst:
    dst.write(infection_data, 1)
  print(f" > Initial infection raster saved to: {INIT_INFECTION_PATH}")

# def create_corridor_landscape(): # This is the code to generate the corridor landscape for the tutorial
  """
  Generates a cost landscape with a high-risk horizontal corridor.
  """
  print("Generating landscape with a high-risk corridor...")
  if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)

  # Base landscape is mostly unsuitable (cost = 0.9)
  cost_data = np.full(GRID_SIZE, 0.9, dtype=np.float32)

  # Create a 'valley' or 'road' of highly suitable cells
  corridor_center = GRID_SIZE[0] // 2
  cost_data[corridor_center-10:corridor_center+10, :] = 0.05

  # Raster profile setup
  transform = from_origin(0, GRID_SIZE[0], 1, 1)
  profile = {'driver': 'GTiff', 'height': GRID_SIZE[0], 'width': GRID_SIZE[1],
             'count': 1, 'dtype': rasterio.float32, 'crs': CRS, 'transform': transform}

  with rasterio.open(COST_RASTER_PATH, 'w', **profile) as dst:
    dst.write(cost_data, 1)
  print(f" > Corridor cost raster saved to: {COST_RASTER_PATH}")

  # Create an initial infection at the START of the corridor
  infection_data = np.zeros(GRID_SIZE, dtype=np.int32)
  start_y, start_x = GRID_SIZE[0] // 2, 10 # Center-left
  infection_data[start_y-5:start_y+5, start_x-5:start_x+5] = 1

  profile.update(dtype=rasterio.int32)
  with rasterio.open(INIT_INFECTION_PATH, 'w', **profile) as dst:
    dst.write(infection_data, 1)
  print(f" > Initial infection raster saved to: {INIT_INFECTION_PATH}")

# def create_fragmented_landscape(): # This is the code to generate the fragemented landscape for the tutorial
  """
  Generates a patchy landscape of suitable 'islands'.
  """
  print("Generating a fragmented landscape...")
  if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)

  # 1. Start with random noise
  random_data = np.random.rand(GRID_SIZE[0], GRID_SIZE[1])

  # 2. Blur the noise heavily to create smooth, blob-like shapes
  blurred_data = gaussian_filter(random_data, sigma=8)

  # 3. Use a threshold to turn blobs into distinct 'islands' and 'sea'
  cost_data = np.zeros(GRID_SIZE, dtype=np.float32)
  cost_data[blurred_data > 0.51] = 0.1 # High-suitability islands
  cost_data[blurred_data <= 0.51] = 0.9 # Unsuitable sea

  # Raster profile setup
  transform = from_origin(0, GRID_SIZE[0], 1, 1)
  profile = {'driver': 'GTiff', 'height': GRID_SIZE[0], 'width': GRID_SIZE[1],
             'count': 1, 'dtype': rasterio.float32, 'crs': CRS, 'transform': transform}

  with rasterio.open(COST_RASTER_PATH, 'w', **profile) as dst:
    dst.write(cost_data, 1)
  print(f" > Fragmented cost raster saved to: {COST_RASTER_PATH}")

  # Create an initial infection in the center
  infection_data = np.zeros(GRID_SIZE, dtype=np.int32)
  center_y, center_x = GRID_SIZE[0] // 2, GRID_SIZE[1] // 2
  infection_data[center_y-5:center_y+5, center_x-5:center_x+5] = 1

  # Ensure the starting point is actually on a suitable island!
  if cost_data[center_y, center_x] > 0.5:
    print("Warning: Infection started in an unsuitable area. The disease may die out instantly.")

  profile.update(dtype=rasterio.int32)
  with rasterio.open(INIT_INFECTION_PATH, 'w', **profile) as dst:
    dst.write(infection_data, 1)
  print(f" > Initial infection raster saved to: {INIT_INFECTION_PATH}")

if __name__ == '__main__':
  print("This is the 'abm_analysis' module.")
  print("It is intended to be imported into other scripts or notebooks to analyze simulation results.")
  print("Example usage:\n")
  print("import abm_analysis as an")
  print("tif_files = an.get_simulation_files('path/to/results')")
  print("df = an.generate_epidemic_curve(tif_files, 'path/to/plot.png')")