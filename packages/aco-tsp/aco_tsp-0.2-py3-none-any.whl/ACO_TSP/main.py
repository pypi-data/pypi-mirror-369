import numpy as np

class ACO_TSP:
    def __init__(self, distance_matrix, labels=None, num_ants=10, evap_rate=0.5, 
                 Q=100, alpha=1, beta=2, num_iterations=50, start_node=0):
        """
        Ant Colony Optimization for Traveling Salesman Problem.
        
        Parameters:
        distance_matrix (np.ndarray/list): Square matrix of distances between nodes
        labels (list): Optional node labels (default: indices)
        num_ants (int): Number of ants per iteration (>0)
        evap_rate (float): Pheromone evaporation rate (0-1)
        Q (float): Pheromone deposit constant (>0)
        alpha (float): Pheromone influence exponent (≥0)
        beta (float): Heuristic influence exponent (≥0)
        num_iterations (int): Number of ACO iterations (>0)
        start_node (int): Starting node index (0-based)
        """
        try:
            # Validate and convert input
            self.dist_matrix = np.array(distance_matrix, dtype=float)
            if self.dist_matrix.ndim != 2 or self.dist_matrix.shape[0] != self.dist_matrix.shape[1]:
                raise ValueError("Distance matrix must be square")
                
            self.size = len(self.dist_matrix)
            np.fill_diagonal(self.dist_matrix, 0)
            
            # Validate parameters
            if not (0 <= evap_rate <= 1):
                raise ValueError("Evaporation rate must be between 0 and 1")
            if any(x <= 0 for x in (num_ants, Q, num_iterations)):
                raise ValueError("num_ants, Q, and num_iterations must be > 0")
            if any(x < 0 for x in (alpha, beta)):
                raise ValueError("alpha and beta must be ≥ 0")
            if not (0 <= start_node < self.size):
                raise ValueError("start_node must be a valid node index")
            
            # Set parameters
            self.num_ants = int(num_ants)
            self.evap_rate = float(evap_rate)
            self.Q = float(Q)
            self.alpha = float(alpha)
            self.beta = float(beta)
            self.num_iterations = int(num_iterations)
            self.start_node = int(start_node)
            
            # Handle labels
            if labels is None:
                self.labels = [str(i) for i in range(self.size)]
            else:
                if len(labels) != self.size:
                    raise ValueError("Labels length must match distance matrix size")
                self.labels = labels
            
            # Initialize state
            self.best_path = None
            self.best_length = float('inf')
            self.best_tour = None
            self.pheromones = None
            self.heuristic = None
            self.convergence = []  # Track best length per iteration
            
        except Exception as e:
            raise ValueError(f"Initialization error: {str(e)}") from e

    def _initialize_pheromones(self, initial_val=1.0):
        """Create initial pheromone matrix"""
        return np.full((self.size, self.size), initial_val)
    
    def _compute_heuristic(self):
        """Compute heuristic matrix (1/distance)"""
        with np.errstate(divide='ignore', invalid='ignore'):
            heuristic = 1.0 / self.dist_matrix
            heuristic[self.dist_matrix == 0] = 0
        return heuristic
    
    def _update_pheromones(self, ants_tours, ants_lengths):
        """Update pheromone matrix with ants' solutions"""
        # Evaporation
        self.pheromones *= (1 - self.evap_rate)
        
        # Deposit pheromones
        for tour, length in zip(ants_tours, ants_lengths):
            # Close the tour cycle
            cycle = np.append(tour, tour[0])
            for i in range(len(cycle)-1):
                node_i, node_j = cycle[i], cycle[i+1]
                deposit = self.Q / length
                self.pheromones[node_i, node_j] += deposit
                self.pheromones[node_j, node_i] += deposit  # Symmetric update
    
    def _probability_matrix(self):
        """Compute transition probability matrix"""
        desirability = (self.pheromones ** self.alpha) * (self.heuristic ** self.beta)
        row_sums = desirability.sum(axis=1, keepdims=True)
        return np.divide(desirability, row_sums, where=row_sums!=0)
    
    def _build_ant_tour(self, prob_matrix):
        """Generate path for a single ant"""
        tour = [self.start_node]
        visited = {self.start_node}
        
        for _ in range(self.size - 1):
            current = tour[-1]
            probs = prob_matrix[current].copy()
            probs[list(visited)] = 0  # Disable visited nodes
            
            # Handle case where all probabilities become zero
            if np.all(probs == 0):
                # Allow movement to any unvisited node
                probs = np.ones(self.size)
                probs[list(visited)] = 0
                if np.sum(probs) == 0:
                    # Shouldn't happen normally, but safe fallback
                    break
            
            probs /= probs.sum()  # Normalize probabilities
            next_node = np.random.choice(self.size, p=probs)
            tour.append(next_node)
            visited.add(next_node)
            
        return tour
    
    def _calculate_tour_length(self, tour):
        """Calculate total length of a tour"""
        # Close the tour cycle
        cycle = tour + [tour[0]]
        length = 0
        for i in range(len(cycle)-1):
            node_i, node_j = cycle[i], cycle[i+1]
            length += self.dist_matrix[node_i, node_j]
        return length
    
    def solve(self):
        """Run ACO optimization and return best path and length"""
        try:
            # Initialize matrices
            self.pheromones = self._initialize_pheromones()
            self.heuristic = self._compute_heuristic()
            self.convergence = []
            
            # Optimization loop
            for _ in range(self.num_iterations):
                ants_tours = []
                ants_lengths = []
                
                # Generate solutions
                for _ in range(self.num_ants):
                    prob_mat = self._probability_matrix()
                    tour = self._build_ant_tour(prob_mat)
                    length = self._calculate_tour_length(tour)
                    
                    ants_tours.append(tour)
                    ants_lengths.append(length)
                    
                    # Update best solution
                    if length < self.best_length:
                        self.best_length = length
                        self.best_tour = tour.copy()
                
                # Track convergence
                self.convergence.append(self.best_length)
                
                # Update pheromones
                self._update_pheromones(ants_tours, ants_lengths)
            
            # Convert best tour to labels
            self.best_path = [self.labels[i] for i in self.best_tour]
            self.best_path.append(self.labels[self.best_tour[0]])  # Return to start
            
            return self.best_path, self.best_length
        
        except Exception as e:
            raise RuntimeError(f"Optimization failed: {str(e)}") from e
    
    def get_solution(self):
        """Return best solution found with convergence data"""
        if self.best_path is None:
            raise RuntimeError("No solution available. Call solve() first")
            
        return {
            'path': self.best_path,
            'length': self.best_length,
            'tour': self.best_tour,
            'convergence': self.convergence,
            'pheromones': self.pheromones.copy(),
            'parameters': {
                'num_ants': self.num_ants,
                'evap_rate': self.evap_rate,
                'Q': self.Q,
                'alpha': self.alpha,
                'beta': self.beta,
                'num_iterations': self.num_iterations,
                'start_node': self.start_node
            }
        }