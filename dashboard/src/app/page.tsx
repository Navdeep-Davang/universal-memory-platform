import { 
  Activity, 
  Database, 
  Layers, 
  Zap,
  TrendingUp,
  Clock
} from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-8">
      <header>
        <h2 className="text-3xl font-bold tracking-tight">System Overview</h2>
        <p className="text-slate-400 mt-2">Real-time status and performance of your cognitive memory engine.</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: "Total Memories", value: "12,842", icon: Database, color: "text-blue-400" },
          { label: "Graph Nodes", value: "4,201", icon: Layers, color: "text-indigo-400" },
          { label: "Avg Latency", value: "142ms", icon: Zap, color: "text-amber-400" },
          { label: "Recall Accuracy", value: "94.2%", icon: TrendingUp, color: "text-emerald-400" },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">{stat.label}</p>
                <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
              </div>
              <stat.icon className={`${stat.color} opacity-80`} size={24} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-800 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Activity size={20} className="text-blue-400" />
              <h3 className="font-semibold">Recent Ingestions</h3>
            </div>
            <button className="text-xs text-blue-400 hover:underline">View All</button>
          </div>
          <div className="divide-y divide-slate-800">
            {[1, 2, 3, 4, 5].map((_, i) => (
              <div key={i} className="p-4 flex items-center gap-4 hover:bg-slate-800/50 transition-colors">
                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-blue-400">
                  <Database size={18} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    Memory ingested: "The user prefers dark mode for all interfaces"
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500">Agent: assistant-v2</span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock size={12} /> 5 mins ago
                    </span>
                  </div>
                </div>
                <div className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-wider">
                  Episodic
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="space-y-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold mb-4">Storage Backend</h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-400 uppercase">Memgraph (Graph)</span>
                  <span className="text-emerald-400">Healthy</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 w-[65%]" />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-400 uppercase">Redis (Cache)</span>
                  <span className="text-emerald-400">Healthy</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 w-[12%]" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-900/50 to-blue-900/50 border border-indigo-500/30 rounded-xl p-6 relative overflow-hidden group">
            <div className="relative z-10">
              <h3 className="font-semibold text-indigo-100">Performance Tip</h3>
              <p className="text-sm text-indigo-200/70 mt-2 italic">
                "Enable query caching for repetitive retrieval patterns to reduce average latency by up to 40%."
              </p>
              <button className="mt-4 px-4 py-2 bg-indigo-500 hover:bg-indigo-400 text-white rounded-lg text-sm font-medium transition-colors">
                Configure Cache
              </button>
            </div>
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <Zap size={64} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
