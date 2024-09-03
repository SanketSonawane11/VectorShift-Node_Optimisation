from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: str = Form(...)):
    pipeline_data = json.loads(pipeline)

    num_nodes = len(pipeline_data.get('nodes', []))
    num_edges = len(pipeline_data.get('edges', []))
    
    try:
        pipeline_data = json.loads(pipeline)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    nodes = pipeline_data.get('nodes', [])
    edges = pipeline_data.get('edges', [])

    num_nodes = len(nodes)
    num_edges = len(edges)

    # Create an adjacency list to check if the graph is a DAG
    graph = {node['id']: [] for node in nodes}
    for edge in edges:
        graph[edge['source']].append(edge['target'])

    # Check if the graph is a DAG
    is_dag = is_directed_acyclic_graph(graph)

    return {"num_nodes": num_nodes, "num_edges": num_edges, "is_dag": is_dag}

def is_directed_acyclic_graph(graph):
    visited = set()
    stack = set()

    def visit(node):
        if node in stack:
            return False  # Detected a cycle
        if node in visited:
            return True  # Already checked node

        stack.add(node)
        for neighbor in graph[node]:
            if not visit(neighbor):
                return False
        stack.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in graph)