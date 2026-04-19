import cadquery as cq
import random
import json
import os

def get_edge_center(edge):
    """Calculates the 3D center point of a CadQuery Edge."""
    return edge.Center().toTuple()

def generate_plate_with_holes(sample_id, output_dir="dataset"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Randomize Base Dimensions
    length = random.uniform(50, 150)
    width = random.uniform(50, 150)
    thickness = random.uniform(5, 20)
    
    # Generate Base Shape
    # base_plate = cq.Workplane("XY").box(length, width, thickness)
    base_plate = (cq.Workplane("XY")
             .polyline([(0,0), (20,0), (20,5), (5,5), (5,45), (20,45), (20,50), (0,50)])
             .mirrorY().extrude(500))
    # Get the centers of all edges BEFORE cuts (These are "Perimeter/Base" edges)
    base_edges = base_plate.val().Edges()
    base_edge_centers = [get_edge_center(e) for e in base_edges]

    # 2. Randomize Cut Features (Manufacturing Modes)
    num_holes = random.randint(1, 4)
    hole_pts =[(random.uniform(-length/4, length/4), random.uniform(-width/3, width/3)) for _ in range(num_holes)]
    hole_radius = random.uniform(0.5, 10)
    
    # Apply cuts
    final_shape = base_plate.faces(">Z").workplane().pushPoints(hole_pts).hole(hole_radius*2)
    
    # 3. Auto-Labeling Logic
    # We iterate through the FINAL shape. If an edge center was in the base shape, 
    # it's a perimeter. If it's NEW, it was created by the manufacturing cut!
    labels =[]
    final_edges = final_shape.val().Edges()
    
    # Tolerance for matching 3D points (floats can be slightly off)
    TOLERANCE = 1e-4 
    
    for edge in final_edges:
        center = get_edge_center(edge)
        geom_type = edge.geomType() # e.g., 'LINE', 'CIRCLE'
        
        # Check if this edge existed before the cut
        is_base_edge = any(
            abs(center[0] - bc[0]) < TOLERANCE and 
            abs(center[1] - bc[1]) < TOLERANCE and 
            abs(center[2] - bc[2]) < TOLERANCE 
            for bc in base_edge_centers
        )
        
        if is_base_edge:
            label = "base_perimeter"
        else:
            # It's a new edge! We can classify it further by its geometry
            if geom_type == "CIRCLE":
                label = "cut_hole"
            else:
                label = "cut_pocket" # Or other custom logic
                
        labels.append({
            "center_x": center[0],
            "center_y": center[1],
            "center_z": center[2],
            "geom_type": geom_type,
            "label": label
        })

    # 4. Export the Data
    step_filename = os.path.join(output_dir, f"sample_{sample_id}.step")
    json_filename = os.path.join(output_dir, f"sample_{sample_id}.json")
    
    cq.exporters.export(final_shape, step_filename)
    
    with open(json_filename, "w") as f:
        json.dump(labels, f, indent=4)
        
    print(f"Generated {step_filename} with {len(labels)} edges.")

# Run the generator
if __name__ == "__main__":
    print("Starting dataset generation...")
    for i in range(10): # Change to 10000 for your full dataset
        generate_plate_with_holes(i)