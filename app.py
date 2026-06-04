import time
import random
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Initialize our Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key!'
socketio = SocketIO(app)

# --- Simulation State & Grid ---
# 1 = Walkable, 0 = Obstacle (wall)
MATRIX = [
  [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
  [1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
  [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
  [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
  [1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
  [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
  [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
grid = Grid(matrix=MATRIX)

# Store robot and fire positions
robot_pos = {'x': 0, 'y': 0}
fire_pos = {'x': 9, 'y': 9}

# --- NEW: Global flag to control the loop ---
# This ensures we only start the fire loop one time
fire_loop_started = False

# --- Objective 3: Fire Propagation (in a continuous loop) ---
def spread_fire_loop():
    global fire_pos, grid, MATRIX
    
    print("--- Continuous fire spread loop started! ---")
    while True:
        # We must use socketio.sleep() not time.sleep()
        socketio.sleep(10) # Wait 10 seconds
        
        # Get the current position
        current_x, current_y = fire_pos['x'], fire_pos['y']
        new_x, new_y = current_x, current_y
        
        # Keep trying until we find a *different* spot that is *walkable*
        while (new_x == current_x and new_y == current_y) or MATRIX[new_y][new_x] == 0:
            new_x = random.randint(0, 9)
            new_y = random.randint(0, 9)
            
        fire_pos = {'x': new_x, 'y': new_y}
        print(f"--- FIRE HAS SPREAD to ({new_x}, {new_y}) ---")
        
        # Send a broadcast to ALL connected users
        socketio.emit('fire_moved', fire_pos)

# This tells Flask to serve our webpage
@app.route('/')
def index():
    return render_template('index.html')

# --- Socket.IO Events ---

@socketio.on('connect')
def handle_new_connection():
    global fire_loop_started # Use the global flag
    print("A user connected!")
    
    # --- Start the loop ONLY if it's not already running ---
    if not fire_loop_started:
        socketio.start_background_task(spread_fire_loop)
        fire_loop_started = True
    
    # Send the current grid and positions to the new user
    emit('initial_state', {'grid': MATRIX, 'robot': robot_pos, 'fire': fire_pos})

@socketio.on('request_path')
def handle_path_request(data):
    global robot_pos, fire_pos, grid
    
    # Get current positions from the client
    robot_pos = data['robot_pos']
    fire_pos = data['fire_pos']
    
    # Clear the grid for a new calculation
    grid.cleanup()
    
    # Define Start and End nodes
    start_node = grid.node(robot_pos['x'], robot_pos['y'])
    end_node = grid.node(fire_pos['x'], fire_pos['y'])
    
    finder = AStarFinder()
    
    # --- Objective 4: Performance Metrics ---
    start_time = time.perf_counter() # Start timer
    path_nodes, runs = finder.find_path(start_node, end_node, grid)
    end_time = time.perf_counter() # Stop timer
    
    # Calculate compute time in milliseconds
    compute_time_ms = (end_time - start_time) * 1000
    
    # Convert path to simple (x, y) coordinates
    path_coords = [(node.x, node.y) for node in path_nodes]
    
    print(f"Path found in {compute_time_ms:.2f} ms.")
    
    # Send the new path AND the compute time back
    emit('new_path', {'path': path_coords, 'compute_time': compute_time_ms})

# This is the code to run the server
if __name__ == '__main__':
    print("Starting server... Go to http://127.0.0.1:5000 in your browser.")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)