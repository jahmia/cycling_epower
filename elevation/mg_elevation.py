"""
Get elevation from a local dem file
once the file is downloaded, we can process elevation in offline mode
"""
import os
import requests

import rasterio
import pandas as pd
import numpy as np

def download_madagascar_dem():
    """
    Download SRTM 90m DEM for Madagascar from OpenTopography
    Coverage: approximately 12°S-25°S, 43°E-51°E
    """
    # "https://portal.opentopography.org/API/globaldem?demtype=SRTMGL3&south=-23.37&north=-16.46&west=43.7&east=50.26&outputFormat=GTiff&API_Key=a10ad8d29e9a6006963c62ee87f4ad08"
    print("Downloading Madagascar DEM...")


    # For this example, assume you've already downloaded it
    # You can manually download from: https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL3/

    return "madagascar_dem.tif"

def create_madagascar_points():
    """
    Create sample elevation points across Madagascar
    Major cities and regions
    """
    points_data = {
        'location': [
            'Antananarivo', 'Toliara', 'Antsirabe', 'Fianarantsoa', 'Anywhere'
        ],
        'latitude': [
            -18.8792, -23.3627, -19.8776, -21.4515, -19.8641677
        ],
        'longitude': [
            47.5079, 43.6675, 47.5211, 47.2900, 47.0258242
        ]
    }

    return pd.DataFrame(points_data)

def get_elevations_madagascar(raster_file, points_df):
    """
    Extract elevations from DEM for Madagascar points
    """
    elevations = []
    missing_indices = []

    with rasterio.open(raster_file) as src:
        print(f"DEM Resolution: {src.res}")
        print(f"DEM Bounds: {src.bounds}")

        for idx, (lat, lon) in enumerate(zip(points_df['latitude'],
                                             points_df['longitude'])):
            try:
                # Convert lat/lon to pixel coordinates
                row, col = src.index(lon, lat)

                # Extract elevation value
                elevation_data = src.read(1).astype('float32')
                elevation_data[elevation_data == src.nodata] = np.nan
                elev = elevation_data[int(row), int(col)]
                elevations.append(float(elev))

            except (IndexError, ValueError):
                elevations.append(None)
                missing_indices.append(idx)

    if missing_indices:
        print(f"Warning: {len(missing_indices)} points outside DEM bounds")

    return elevations

# Step 4: Analyze Madagascar elevation data
def analyze_madagascar_elevation(df):
    """
    Analyze elevation statistics for Madagascar
    """
    valid_elevations = df['elevation'].dropna()

    print("\n=== Madagascar Elevation Analysis ===")
    print(f"Total points: {len(df)}")
    print(f"Points with elevation data: {len(valid_elevations)}")
    print(f"\nElevation Statistics (meters):")
    print(f"  Min elevation: {valid_elevations.min():.2f}m")
    print(f"  Max elevation: {valid_elevations.max():.2f}m")
    print(f"  Mean elevation: {valid_elevations.mean():.2f}m")
    print(f"  Median elevation: {valid_elevations.median():.2f}m")
    print(f"  Std Dev: {valid_elevations.std():.2f}m")

    print("\n=== Locations by Elevation ===")
    df_sorted = df.sort_values('elevation', ascending=False)
    print(df_sorted[['location', 'latitude', 'longitude', 'elevation']])

# Step 5: Visualize elevation (optional)
def plot_madagascar_elevation(df):
    """
    Plot elevation map of Madagascar points
    """
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 8))

        scatter = ax.scatter(df['longitude'], df['latitude'],
                           c=df['elevation'], s=200, cmap='terrain',
                           edgecolors='black', linewidth=1.5)

        # Add location labels
        for idx, row in df.iterrows():
            ax.annotate(row['location'],
                       (row['longitude'], row['latitude']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold')

        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title('Madagascar Elevation Map', fontsize=14, fontweight='bold')

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Elevation (meters)', fontsize=11)

        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('madagascar_elevation.png', dpi=150, bbox_inches='tight')
        print("\nMap saved as 'madagascar_elevation.png'")
        plt.show()

    except ImportError:
        print("Matplotlib not installed. Skipping visualization.")

# Main execution
if __name__ == "__main__":
    # Create sample Madagascar points
    points_df = create_madagascar_points()
    print("Madagascar Sample Points:")
    print(points_df)

    # Use your downloaded DEM file
    RF = "madagascar_dem.tif"

    # Check if file exists
    if not os.path.exists(RF):
        print(f"\n⚠️  DEM file '{RF}' not found!")
        print("Download from: https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL3/")
        print("Select bounds for Madagascar: 12°S-25°S, 43°E-51°E")
    else:
        # Extract elevations
        elevations = get_elevations_madagascar(raster_file, points_df)
        points_df['elevation'] = elevations

        # Analyze results
        analyze_madagascar_elevation(points_df)

        # Save to CSV
        # points_df.to_csv('madagascar_elevations.csv', index=False)
        # print("\n✓ Results saved to 'madagascar_elevations.csv'")

        # Visualize
        # plot_madagascar_elevation(points_df)
