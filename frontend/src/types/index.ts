export interface MemoryResult {
  id: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
  agent_id: string;
  created_at: string;
}

export interface Conflict {
  id: string;
  agent_id: string;
  memory_a: string;
  memory_b: string;
  conflict_type: string;
  status: 'pending' | 'resolved' | 'dismissed';
  created_at: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'Entity' | 'Experience' | 'Context';
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

