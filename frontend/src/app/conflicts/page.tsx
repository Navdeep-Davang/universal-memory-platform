"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Conflict } from "@/types";
import { 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock,
  ArrowRight,
  Filter,
  RefreshCw
} from "lucide-react";

export default function ConflictsPage() {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterAgent, setFilterAgent] = useState("");

  const fetchConflicts = async () => {
    setLoading(true);
    try {
      const data = await api.getConflicts(filterAgent || undefined);
      setConflicts(data.conflicts || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch conflicts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConflicts();
  }, [filterAgent]);

  const handleResolve = async (id: string, status: string) => {
    try {
      await api.resolveConflict(id, status, "Resolved via dashboard");
      setConflicts(prev => prev.filter(c => c.id !== id));
    } catch (err: any) {
      alert(`Error resolving conflict: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Conflict Resolution</h2>
          <p className="text-slate-400 mt-2">Manage and resolve contradictory memories detected by the engine.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input 
              type="text" 
              placeholder="Filter by Agent ID"
              className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
            />
          </div>
          <button 
            onClick={fetchConflicts}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </header>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-xl text-red-400 flex items-center gap-3">
          <AlertTriangle size={20} />
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl h-48 animate-pulse" />
          ))}
        </div>
      ) : conflicts.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-400">
            <CheckCircle2 size={32} />
          </div>
          <h3 className="text-xl font-semibold">All Clear!</h3>
          <p className="text-slate-500 mt-2">No pending conflicts found in the memory engine.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {conflicts.map((conflict) => (
            <div key={conflict.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden group">
              <div className="p-6 border-b border-slate-800 flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="px-2 py-1 rounded bg-amber-500/10 text-amber-500 text-[10px] font-bold uppercase tracking-wider">
                    {conflict.conflict_type || "Contradiction"}
                  </div>
                  <span className="text-xs text-slate-500">ID: {conflict.id}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <Clock size={14} />
                  {new Date(conflict.created_at).toLocaleString()}
                </div>
              </div>
              
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 relative">
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Memory A (Existing)</p>
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 italic">
                    "{conflict.memory_a}"
                  </div>
                </div>
                
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Memory B (Incoming)</p>
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 italic">
                    "{conflict.memory_b}"
                  </div>
                </div>

                <div className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-slate-800 rounded-full border border-slate-700 items-center justify-center text-slate-400">
                  <ArrowRight size={16} />
                </div>
              </div>

              <div className="p-4 bg-slate-800/50 flex justify-between items-center">
                <div className="text-xs text-slate-400">
                  Agent: <span className="text-slate-200 font-mono">{conflict.agent_id}</span>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => handleResolve(conflict.id, "dismissed")}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-colors border border-slate-700"
                  >
                    <XCircle size={16} />
                    Dismiss
                  </button>
                  <button 
                    onClick={() => handleResolve(conflict.id, "active")}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors shadow-lg shadow-blue-900/20"
                  >
                    <CheckCircle2 size={16} />
                    Keep New (Supersede)
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

