import sys
import subprocess

# Map command names to Python code
COMMANDS = {
    "d1": """
L=[60,30,78,23,10]
n=len(L)
for i in range(n-1):
    min=i
    for j in range(i+1,n):
        if L[j]<L[min]:
            min=j
    L[i],L[min]=L[min],L[i]
print(L)
""",
#pmg2
    "d2": """def find_min_max(arr, low, high):

    if low == high:
        return arr[low], arr[low]

    if high == low + 1:
        return (min(arr[low], arr[high]), max(arr[low], arr[high]))

    mid = (low + high) // 2
    min1, max1 = find_min_max(arr, low, mid)
    min2, max2 = find_min_max(arr, mid + 1, high)
    return min(min1, min2), max(max1, max2)

arr = list(map(int, input("Enter elements of the array separated by spaces: ").split()))
minimum, maximum = find_min_max(arr, 0, len(arr) - 1)

print("Minimum element:", minimum)
print("Maximum element:", maximum)
""",
#pmg3
"d3":"""
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid])
    right_half = merge_sort(arr[mid:])
    return merge(left_half, right_half)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

n = int(input("Enter the number of elements: "))
arr = []

for _ in range(n):
    num = int(input("Enter number: "))
    arr.append(num)

sorted_arr = merge_sort(arr)
print("Sorted list:", sorted_arr)""",
#pmg4
"d4":"""
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=' ')
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

n = int(input("Enter number of edges: "))
graph = {}

print("Enter edges (e.g., A B):")
for _ in range(n):
    u, v = input().split()
    graph.setdefault(u, []).append(v)
    graph.setdefault(v, [])  # Ensure all nodes are in the graph

start_node = input("Enter start node for DFS: ")
print("DFS Traversal:")
dfs(graph, start_node)""",

#pmg5
"d5":"""

from collections import deque
graph = {}
n = int(input("Number of nodes: "))
for _ in range(n):
    node = input(f"Node {_+1}: ")
    graph[node] = []
print("Enter edges (u v), type 'done' to stop:")
while True:
    edge = input()
    if edge == "done":
        break
    u, v = edge.split()
    graph[u].append(v)
start = input("Start BFS from: ")
visited = set()
queue = deque([start])
print("BFS:", end=' ')
while queue:
    node = queue.popleft()
    if node not in visited:
        print(node, end=' ')
        visited.add(node)
        queue.extend(graph[node])"""
}

def main():
    args = sys.argv[1:]

    if not args:
        print("ok ig is now activated")
        return

    command = args[0]
    if command in COMMANDS:
        code = COMMANDS[command]

        temp_file = f"{command}_temp.py"
        with open(temp_file, "w") as f:
            f.write(code)

        try:
            subprocess.run(["python", "-m", "idlelib", temp_file])
        except Exception as e:
            print("Error opening IDLE:", e)
    else:
        print(f"Unknown command '{command}'")
