import vpype as vp
import vpype_cli
import click
import numpy as np
from typing import List, Union
import logging

@click.command()
@click.option(
    "--tolerance", "-t",
    type=float,
    default=1e-6,
    help="Tolerance for considering points as identical (default: 1e-6)"
)
@vpype_cli.global_processor
def singlestroke(
    document: vp.Document,
    tolerance: float
) -> vp.Document:
    """Convert closed paths to open paths by preserving unique points.
    
    For each closed path, creates an open path that includes each unique point
    exactly once, using distance-based comparison with configurable tolerance.
    Points that are closer than the tolerance distance are considered identical.
    
    This is useful for creating single-stroke drawings from closed paths while
    preserving the essential geometry of the shape.
    """
    result = document.empty_copy()
    logger = logging.getLogger()
    
    for layer_id, layer in document.layers.items():
        new_layer = vp.LineCollection()
        path_count = 0
        
        for line in layer:
            if len(line) < 2:
                new_layer.append(line)
                continue
                
            points = np.array(line)
            
            # Check if path is closed (first and last points are within tolerance)
            first_last_distance = abs(points[0] - points[-1])
            if first_last_distance < tolerance:
                path_count += 1
                logger.info(f"Closed path #{path_count} - Original points: {len(points)}")
                
                # Check if points form a straight line
                if len(points) == 3:
                    # Calculate vectors between points
                    v1 = points[1] - points[0]
                    v2 = points[2] - points[1]
                    # Check if vectors are parallel (cross product near zero)
                    cross_prod = np.abs(v1.real * v2.imag - v1.imag * v2.real)
                    if cross_prod < 1e-10:  # Threshold for considering vectors parallel
                        # Create 2-point line from endpoints
                        new_layer.append(np.array([points[0], points[1]]))
                        continue
                
                # For a closed path, preserve all unique points in order
                # Use the specified tolerance for distance-based comparison
                
                # Track unique points and their first occurrence indices
                unique_points = []
                unique_indices = []
                
                # Process all points except the last (which should equal the first)
                points_to_process = points[:-1]
                
                # Use distance-based deduplication with tolerance
                for i, point in enumerate(points_to_process):
                    is_unique = True
                    
                    # Check if this point is too close to any already found unique point
                    for existing_point in unique_points:
                        distance = abs(point - existing_point)
                        if distance < tolerance:
                            is_unique = False
                            break
                    
                    if is_unique:
                        unique_points.append(point)
                        unique_indices.append(i)
                
                logger.info(f"  Found {len(unique_points)} unique points (tolerance: {tolerance})")
                
                # Create new path with unique points
                if len(unique_points) >= 2:
                    new_points = np.array(unique_points)
                    logger.info(f"  Created new path with {len(new_points)} points")
                    new_layer.append(new_points)
                elif len(unique_points) == 1:
                    # Single point - create a minimal line or point
                    logger.info(f"  Single unique point found")
                    new_layer.append(np.array([unique_points[0]]))
            else:
                # Keep non-closed paths as they are
                new_layer.append(points)
        
        if not new_layer.is_empty():
            result.add(new_layer, layer_id)
    
    return result

singlestroke.help_group = "Plugins" 