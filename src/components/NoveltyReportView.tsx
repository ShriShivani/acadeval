import React from 'react';
import {
  Sparkles,
  Network,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Layers,
  Cpu,
  Database,
  Grid
} from 'lucide-react';

export interface SignalBreakdown {
  graph_distance: number;
  feature_rarity: number;
  relationship_rarity: number;
  graph_density: number;
  new_connection_discovery: number;
}

export interface ExtractedEntities {
  algorithms: string[];
  technologies: string[];
  frameworks: string[];
  libraries: string[];
  datasets: string[];
  applications: string[];
  hardware: string[];
}

export interface TrendContext {
  topic: string;
  growth_rate_pct: number | null;
  paper_count_3yr: number | null;
  citation_velocity: number | null;
  trend_status: string;
  data_source?: string;
}

export interface SimilarProject {
  project_id: string;
  title: string;
  similarity_score: number;
}

export interface NoveltyReportData {
  project_id: string;
  title: string;
  domain: string;
  sub_domain: string;
  overall_novelty_band: string;
  overall_novelty_score: number;
  signals_breakdown: SignalBreakdown;
  extracted_entities: ExtractedEntities;
  trend_context: TrendContext;
  most_similar_projects: SimilarProject[];
  explanation_lines: string[];
}

interface Props {
  report: NoveltyReportData;
  onFacultyScoreSubmit?: (facultyScore: number, reason: string) => void;
}

export const NoveltyReportView: React.FC<Props> = ({ report, onFacultyScoreSubmit }) => {
  const [facultyRating, setFacultyRating] = React.useState<number>(8);
  const [overrideReason, setOverrideReason] = React.useState<string>('');
  const [submitted, setSubmitted] = React.useState<boolean>(false);

  const getBandColor = (band: string) => {
    if (band.includes('Highly')) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (band.includes('Moderately')) return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-blue-50 text-blue-700 border-blue-200';
  };

  const handleFacultySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onFacultyScoreSubmit) {
      onFacultyScoreSubmit(facultyRating, overrideReason);
      setSubmitted(true);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-4">
      {/* Header Banner */}
      <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
            <Network className="w-4 h-4" /> AcadEval+ Graph Novelty Engine
          </div>
          <h2 className="text-2xl font-bold">{report.title}</h2>
          <p className="text-slate-400 text-sm mt-1">
            Domain: <span className="text-white font-medium">{report.domain}</span> &rarr;{' '}
            <span className="text-indigo-300">{report.sub_domain}</span>
          </p>
        </div>

        <div className="flex items-center gap-4 bg-slate-800/80 p-4 rounded-xl border border-slate-700">
          <div className="text-center">
            <div className="text-3xl font-extrabold text-indigo-400">{report.overall_novelty_score}</div>
            <div className="text-[10px] text-slate-400 uppercase tracking-widest mt-0.5">Novelty Score</div>
          </div>
          <div className="h-10 w-px bg-slate-700" />
          <span className={`px-3 py-1.5 text-xs font-semibold rounded-full border ${getBandColor(report.overall_novelty_band)}`}>
            {report.overall_novelty_band}
          </span>
        </div>
      </div>

      {/* 5 Graph Signals Breakdown */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-600" /> 5 Explainable Graph Novelty Signals
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            { label: 'Graph Distance', score: report.signals_breakdown.graph_distance, icon: Network, color: 'bg-indigo-500' },
            { label: 'Feature Rarity', score: report.signals_breakdown.feature_rarity, icon: Cpu, color: 'bg-emerald-500' },
            { label: 'Rel. Rarity', score: report.signals_breakdown.relationship_rarity, icon: Layers, color: 'bg-amber-500' },
            { label: 'Graph Density', score: report.signals_breakdown.graph_density, icon: Grid, color: 'bg-cyan-500' },
            { label: 'Discovery', score: report.signals_breakdown.new_connection_discovery, icon: Sparkles, color: 'bg-purple-500' },
          ].map((signal, idx) => (
            <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-slate-500 text-xs">
                <span className="font-medium">{signal.label}</span>
                <signal.icon className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <div className="text-xl font-bold text-slate-800">{(signal.score * 100).toFixed(1)}%</div>
              <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                <div className={`h-full ${signal.color}`} style={{ width: `${Math.min(100, signal.score * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>

        {/* Plain Language Explanations */}
        <div className="mt-4 p-4 bg-slate-50 rounded-xl space-y-2 border border-slate-100">
          <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">System Explanations</h4>
          <ul className="space-y-1.5 text-xs text-slate-600">
            {report.explanation_lines.map((line, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-indigo-500 mt-0.5">•</span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Grid: Extracted Entities & Trend Context */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Extracted Entities */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-600" /> Extracted Graph Entities
          </h3>
          <div className="space-y-2 text-xs">
            {report.extracted_entities.algorithms.length > 0 && (
              <div>
                <span className="font-semibold text-slate-600">Algorithms:</span>{' '}
                {report.extracted_entities.algorithms.map((a, i) => (
                  <span key={i} className="inline-block bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded mr-1 mb-1 font-mono">
                    {a}
                  </span>
                ))}
              </div>
            )}
            {report.extracted_entities.frameworks.length > 0 && (
              <div>
                <span className="font-semibold text-slate-600">Frameworks / Libraries:</span>{' '}
                {report.extracted_entities.frameworks.map((f, i) => (
                  <span key={i} className="inline-block bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded mr-1 mb-1 font-mono">
                    {f}
                  </span>
                ))}
              </div>
            )}
            {report.extracted_entities.datasets.length > 0 && (
              <div>
                <span className="font-semibold text-slate-600">Datasets:</span>{' '}
                {report.extracted_entities.datasets.map((d, i) => (
                  <span key={i} className="inline-block bg-purple-50 text-purple-700 px-2 py-0.5 rounded mr-1 mb-1 font-mono">
                    {d}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Literature Trend Context */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" /> Literature Trend (Semantic Scholar)
          </h3>
          {report.trend_context.trend_status === 'unavailable' ? (
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-slate-500">
              Trend data unavailable (Semantic Scholar API could not be reached).
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100">
                <div className="text-slate-500">Topic Growth (YoY)</div>
                <div className="text-lg font-bold text-emerald-700">+{report.trend_context.growth_rate_pct}%</div>
              </div>
              <div className="p-3 bg-blue-50/50 rounded-xl border border-blue-100">
                <div className="text-slate-500">Trend Status</div>
                <div className="text-lg font-bold text-blue-700">{report.trend_context.trend_status}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Most Similar Existing Projects */}
      {report.most_similar_projects.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600" /> Most Similar Existing Projects
          </h3>
          <ul className="divide-y divide-slate-100 text-xs">
            {report.most_similar_projects.map((p, idx) => (
              <li key={idx} className="py-2 flex items-center justify-between gap-4">
                <span className="text-slate-700">{p.title}</span>
                <span className="font-mono text-slate-400 shrink-0">{(p.similarity_score * 100).toFixed(1)}% similar</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Module 7: Faculty Review Ground Truth Form */}
      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4">
        <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-indigo-600" /> Module 7: Faculty Ground Truth Feedback
        </h3>
        {submitted ? (
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-xs font-medium border border-emerald-200">
            Thank you! Faculty rating has been submitted into AcadEval_FacultyEvaluation to calibrate the graph engine.
          </div>
        ) : (
          <form onSubmit={handleFacultySubmit} className="space-y-3">
            <div className="flex items-center gap-4">
              <label className="text-xs font-medium text-slate-700">Faculty Rating (1 - 10):</label>
              <input
                type="number"
                min="1"
                max="10"
                value={facultyRating}
                onChange={(e) => setFacultyRating(Number(e.target.value))}
                className="w-20 px-3 py-1.5 border border-slate-300 rounded-lg text-sm font-bold text-slate-800"
              />
            </div>
            <div>
              <textarea
                placeholder="Optional feedback / justification..."
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                className="w-full p-2.5 text-xs border border-slate-300 rounded-lg"
                rows={2}
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
            >
              Submit Faculty Ground Truth Rating
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
