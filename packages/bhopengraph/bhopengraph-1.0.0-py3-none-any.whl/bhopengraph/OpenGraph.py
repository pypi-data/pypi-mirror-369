#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : OpenGraph.py
# Author             : Remi Gascou (@podalirius_)
# Date created       : 12 Aug 2025

import json
from typing import Dict, List, Optional
from bhopengraph.Node import Node
from bhopengraph.Edge import Edge

class OpenGraph(object):
    """
    OpenGraph class for managing a graph structure compatible with BloodHound OpenGraph.

    Follows BloodHound OpenGraph schema requirements and best practices.

    Sources:
    - https://bloodhound.specterops.io/opengraph/schema#opengraph
    - https://bloodhound.specterops.io/opengraph/schema#minimal-working-json
    """
    
    def __init__(self, source_kind: str = None):
        """
        Initialize an OpenGraph.
        
        Args:
          - source_kind (str): Optional source kind for all nodes in the graph
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.source_kind = source_kind
    
    def addNode(self, node: Node) -> bool:
        """
        Add a node to the graph.
        
        Args:
          - node (Node): Node to add
            
        Returns:
          - bool: True if node was added, False if node with same ID already exists
        """
        if node.id in self.nodes:
            return False
        
        # Add source_kind to node kinds if specified
        if self.source_kind and self.source_kind not in node.kinds:
            node.add_kind(self.source_kind)
        
        self.nodes[node.id] = node
        return True
    
    def addEdge(self, edge: Edge) -> bool:
        """
        Add an edge to the graph.
        
        Args:
          - edge (Edge): Edge to add
            
        Returns:
          - bool: True if edge was added, False if start or end node doesn't exist
        """
        # Verify both start and end nodes exist
        if edge.start_node_id not in self.nodes:
            return False
        if edge.end_node_id not in self.nodes:
            return False
        
        # Check if edge already exists
        for existing_edge in self.edges:
            if (existing_edge.start_node_id == edge.start_node_id and
                existing_edge.end_node_id == edge.end_node_id and
                existing_edge.kind == edge.kind):
                return False
        
        self.edges.append(edge)
        return True
    
    def removeNodeById(self, id: str) -> bool:
        """
        Remove a node and all its associated edges from the graph.
        
        Args:
          - id (str): ID of the node to remove
            
        Returns:
          - bool: True if node was removed, False if node doesn't exist
        """
        if id not in self.nodes:
            return False
        
        # Remove the node
        del self.nodes[id]
        
        # Remove all edges that reference this node
        self.edges = [edge for edge in self.edges 
                     if edge.start_node_id != id and edge.end_node_id != id]
        
        return True
    
    def getNode(self, id: str) -> Optional[Node]:
        """
        Get a node by ID.
        
        Args:
          - id (str): ID of the node to retrieve
            
        Returns:
          - Node: The node if found, None otherwise
        """
        return self.nodes.get(id)
    
    def getNodesByKind(self, kind: str) -> List[Node]:
        """
        Get all nodes of a specific kind.
        
        Args:
          - kind (str): Kind/type to filter by
            
        Returns:
          - List[Node]: List of nodes with the specified kind
        """
        return [node for node in self.nodes.values() if node.has_kind(kind)]
    
    def getEdgesByKind(self, kind: str) -> List[Edge]:
        """
        Get all edges of a specific kind.
        
        Args:
          - kind (str): Kind/type to filter by
            
        Returns:
          - List[Edge]: List of edges with the specified kind
        """
        return [edge for edge in self.edges if edge.kind == kind]
    
    def getEdgesFromNode(self, id: str) -> List[Edge]:
        """
        Get all edges starting from a specific node.
        
        Args:
          - id (str): ID of the source node
            
        Returns:
          - List[Edge]: List of edges starting from the specified node
        """
        return [edge for edge in self.edges if edge.start_node_id == id]
    
    def getEdgesToNode(self, id: str) -> List[Edge]:
        """
        Get all edges ending at a specific node.
        
        Args:
          - id (str): ID of the destination node
            
        Returns:
          - List[Edge]: List of edges ending at the specified node
        """
        return [edge for edge in self.edges if edge.end_node_id == id]
    
    def exportJSON(self, include_metadata: bool = True) -> str:
        """
        Export the graph to JSON format compatible with BloodHound OpenGraph.
        
        Args:
          - include_metadata (bool): Whether to include metadata in the export
            
        Returns:
          - str: JSON string representation of the graph
        """
        graph_data = {
            "graph": {
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "edges": [edge.to_dict() for edge in self.edges]
            }
        }
        
        if include_metadata and self.source_kind:
            graph_data["metadata"] = {
                "source_kind": self.source_kind
            }
        
        return json.dumps(graph_data, indent=2)
    
    def exportToFile(self, filename: str, include_metadata: bool = True):
        """
        Export the graph to a JSON file.
        
        Args:
          - filename (str): Name of the file to write
          - include_metadata (bool): Whether to include metadata in the export
        """
        json_data = self.exportJSON(include_metadata)
        with open(filename, 'w') as f:
            f.write(json_data)
    
    def getNodeCount(self) -> int:
        """
        Get the total number of nodes in the graph.
        
        Returns:
          - int: Number of nodes
        """
        return len(self.nodes)
    
    def getEdgeCount(self) -> int:
        """
        Get the total number of edges in the graph.
        
        Returns:
          - int: Number of edges
        """
        return len(self.edges)
    
    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.nodes.clear()
        self.edges.clear()
    
    def __len__(self) -> int:
        """Return the total number of nodes and edges."""
        return len(self.nodes) + len(self.edges)
    
    def __repr__(self) -> str:
        return f"OpenGraph(nodes={len(self.nodes)}, edges={len(self.edges)}, source_kind='{self.source_kind}')"
