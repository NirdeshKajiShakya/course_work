from os import name


class City:
    def __init__(self, name:str, population:int, latitude:float, longitude:float):
        self.name = name
        self.population = population
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"City(Name: {self.name}, Pop: {self.population})"

class AVLNode:
    def __init__(self, city: City):
        self.city = city
        self.key = city.name.lower()
        self.left = None
        self.right = None
        self.height = 1  # Track node height to calculate balance

class BSTNode:
    def __init__(self, city: City):
        self.city = city
        self.key = city.name.lower()
        self.left = None
        self.right = None

    def __repr__(self):
        return repr(self.city)

    def insert(self, city: City):
        key = city.name.lower()
        if key < self.key:
            if self.left is None:
                self.left = BSTNode(city)
            else:
                self.left.insert(city)
        else:
            if self.right is None:
                self.right = BSTNode(city)
            else:
                self.right.insert(city)

class BinarySearchTree:
    def __init__(self):
        #initially we have no root node in the BST
        self.root = None
    
    def insert(self, city: City):
        if self.root is None:
            #when root node is empty plant a new node
            self.root = BSTNode(city)
        else:
            #if the tree does already have a root then start searching for the root node
            self._insert_recursive(self.root, city)

    def _insert_recursive(self, current_node: BSTNode, city: City):
        """helper function to insert a city into the BST recursively"""
        new_key = city.name.lower()

        #if the new name is alphabetically less than the current node's name, go left
        if new_key < current_node.key:
            if current_node.left is None:
                current_node.left = BSTNode(city)
            else:
                self._insert_recursive(current_node.left, city)

        #if the new name is alphabetically greater than or equal to the current node's name, go right
        if new_key > current_node.key:
            if current_node.right is None:
                current_node.right = BSTNode(city)
            else:
                self._insert_recursive(current_node.right, city)
    
    def search(self, name: str) -> City or None:
        """public search method to find a city by name in the BST"""
        return self._search_recursive(self.root, name)

    def _search_recursive(self, current_node: BSTNode, target_key: str) -> City or None:
        if current_node is None or current_node.key == target_key.lower():
            return current_node.city if current_node else None
        
        if target_key.lower() < current_node.key:
            return self._search_recursive(current_node.left, target_key)
    
        return self._search_recursive(current_node.right, target_key)
        
class AVLTree:
    def get_height(self, node: AVLNode) -> int:
        """Returns the height of a node, or 0 if None."""
        if not node:
            return 0
        return node.height

    def get_balance(self, node: AVLNode) -> int:
        """Calculates the balance factor of a node."""
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def right_rotate(self, z: AVLNode) -> AVLNode:
        """Fixes a Left-Heavy subtree."""
        y = z.left
        T3 = y.right

        # Perform rotation
        y.right = z
        z.left = T3

        # Update heights (order matters: update lower node 'z' first)
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        # Return the new root of this sub-tree
        return y

    def left_rotate(self, z: AVLNode) -> AVLNode:
        """Fixes a Right-Heavy subtree."""
        y = z.right
        T2 = y.left

        # Perform rotation
        y.left = z
        z.right = T2

        # Update heights
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        # Return the new root of this sub-tree
        return y
    
    def insert(self, root: AVLNode, city: City) -> AVLNode:
        """Recursively inserts a city and rebalances the tree on the way up."""
        # 1. Standard BST insertion
        if not root:
            return AVLNode(city)

        key = city.name.lower()
        if key < root.key:
            root.left = self.insert(root.left, city)
        elif key > root.key:
            root.right = self.insert(root.right, city)
        else:
            return root  # Duplicate keys ignored

        # 2. Update height of current ancestor node
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # 3. Check balance factor to see if this node became unbalanced
        balance = self.get_balance(root)

        # --- REBALANCING LOGIC ---

        # Case 1: Left Left (LL)
        if balance > 1 and key < root.left.key:
            return self.right_rotate(root)

        # Case 2: Right Right (RR)
        if balance < -1 and key > root.right.key:
            return self.left_rotate(root)

        # Case 3: Left Right (LR)
        if balance > 1 and key > root.left.key:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        # Case 4: Right Left (RL)
        if balance < -1 and key < root.right.key:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        # Return unchanged node pointer if balanced
        return root

    def search(self, root: AVLNode, name: str) -> City or None:
        """Search in an AVL tree works identically to a standard BST."""
        target = name.lower()
        if not root or root.key == target:
            return root.city if root else None

        if target < root.key:
            return self.search(root.left, name)
        return self.search(root.right, name)

#############
#testing the implementation
#############
avl = AVLTree()
root = None

# Insert alphabetically sorted cities
cities = [
    City("Bhaktapur", 100000, 27.6710, 85.4298),
    City("Chitwan", 200000, 27.5291, 84.3542),
    City("Kathmandu", 1400000, 27.7172, 85.3240)
]

for c in cities:
    root = avl.insert(root, c)

# In a standard BST, "Bhaktapur" would be the root, and "Kathmandu" would be 2 levels down.
# In our AVL tree, inserting "Kathmandu" triggers a Left Rotation, promoting "Chitwan" to Root!
print("AVL Root Node (Should be Chitwan):", root.key)
print("AVL Left Child (Should be bhaktapur):", root.left.key)
print("AVL Right Child (Should be kathmandu):", root.right.key)