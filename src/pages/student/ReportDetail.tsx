import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getEvaluationReport } from '../../api/endpoints';
import { useAuth } from '../../auth/AuthContext';
import { LoadingState, ErrorState } from '../../components/States';
import RadarChart from '../../components/RadarChart';
import ScoreGauge from '../../components/ScoreGauge';
import Badge from '../../components/Badge';
import AppealModal from '../../components/AppealModal';
import type { PublicEvaluationReport } from '../../types';
import {
  AlertTriangle, CheckCircle, XCircle, Download, BookOpen,
  TrendingUp, ChevronDown, ChevronUp, Info, Award, Lightbulb,
} from 'lucide-react';
import clsx from 'clsx';

const DIMENSION_KEYS = [
  { key: 'novelty', label: 'Novelty' },
  { key: 'feasibility', label: 'Feasibility' },
  { key: 'completeness', label: 'Completeness' },
  { key: 'technicalDepth', label: 'Technical Depth' },
  { key: 'clarity', label: 'Clarity' },
  { key: 'similarityRisk', label: 'Similarity Risk' },
  { key: 'publicationPotential', label: 'Publication Potential' },
];

const ScoreBar: React.FC<{ label: string; score: number | null; dimKey: string; projectId: string; onAppeal: (dim: string, score: number) => void }> = ({
  label, score, dimKey, onAppeal,
}) => {
  if (score === null) {
    return (
      <div className="flex items-center gap-4">
        <div className="w-32 text-sm font-medium text-slate-600 flex-shrink-0">{label}</div>
        <div className="flex-1 bg-slate-100 rounded-full h-2" />
        <span className="text-xs text-slate-400 w-12 text-right">N/A</span>
      </div>
    );
  }

  const color = score >= 80 ? 'bg-teal-500' : score >= 60 ? 'bg-gold-500' : 'bg-red-500';
  const textColor = score >= 80 ? 'text-teal-700' : score >= 60 ? 'text-gold-700' : 'text-red-700';

  return (
    <div className="flex items-center gap-4 group">
      <div className="w-32 text-sm font-medium text-slate-600 flex-shrink-0">{label}</div>
      <div className="flex-1 bg-slate-100 rounded-full h-2.5 overflow-hidden">
        <div className={clsx('h-full rounded-full transition-all duration-700', color)} style={{ width: `${score}%` }} />
      </div>
      <div className="flex items-center gap-2">
        <span className={clsx('text-sm font-bold w-8 text-right', textColor)}>{score}</span>
        <button
          onClick={() => onAppeal(dimKey, score)}
          className="opacity-0 group-hover:opacity-100 transition-opacity text-xs text-slate-400 hover:text-gold-600 border border-slate-200 hover:border-gold-300 rounded-lg px-2 py-0.5"
        >
          Appeal
        </button>
      </div>
    </div>
  );
};

const WeekCard: React.FC<{ week: number; focus: string; actions: string[]; isLast: boolean }> = ({
  week, focus, actions, isLast,
}) => {
  const [expanded, setExpanded] = useState(week === 1);

  return (
    <div className="relative flex gap-4">
      {!isLast && <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-slate-100" />}
      <div className="w-8 h-8 rounded-full bg-navy-900 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 z-10">
        {week}
      </div>
      <div className="flex-1 mb-6">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between bg-white rounded-xl border border-slate-100 px-4 py-3 hover:border-teal-200 transition-all text-left"
        >
          <div>
            <p className="text-xs text-slate-400 font-medium">WEEK {week}</p>
            <p className="font-semibold text-slate-800 text-sm">{focus}</p>
          </div>
          {expanded ? <ChevronUp size={16} className="text-slate-400" /> : <ChevronDown size={16} className="text-slate-400" />}
        </button>
        {expanded && (
          <div className="mt-2 bg-teal-50 rounded-xl border border-teal-100 p-3 space-y-1.5 animate-fade-in">
            {actions.map((action, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-teal-700">
                <CheckCircle size={14} className="text-teal-500 flex-shrink-0 mt-0.5" />
                {action}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const ReportDetail: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [appealState, setAppealState] = useState<{ dim: string; score: number } | null>(null);

  const { data: report, isLoading, isError, refetch } = useQuery({
    queryKey: ['report', projectId],
    queryFn: () => getEvaluationReport(projectId!, user!.role),
    enabled: !!projectId && !!user,
  });

  if (isLoading) return <LoadingState message="Loading evaluation report..." />;
  if (isError || !report) return <ErrorState retry={refetch} />;

  const r = report as PublicEvaluationReport;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Preliminary Banner */}
      {r.isPreliminary && (
        <div className="bg-gold-50 border border-gold-200 rounded-2xl p-4 flex items-start gap-3">
          <Info size={20} className="text-gold-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-gold-800">Preliminary Report — Pending Faculty Review</p>
            <p className="text-sm text-gold-700 mt-1">
              Your AI-generated report is ready, but your guide hasn't finalized it yet.
              Scores shown are AI-generated and may be adjusted by your guide/reviewer.
            </p>
          </div>
        </div>
      )}

      {/* Duplicate Warning */}
      {r.similarity.isDuplicate && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-800">High Similarity Detected</p>
            <p className="text-sm text-red-700 mt-1">
              Internal similarity: <strong>{r.similarity.internalScore}%</strong> | External: <strong>{r.similarity.externalScore}%</strong>.
              Your project may overlap with an existing submission. Please review your content for originality.
            </p>
          </div>
        </div>
      )}

      {/* Header Card */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <Badge type="submission" value={r.submissionType} />
              <Badge type="domain" value={r.domain} />
              <Badge type="novelty" value={r.noveltyVerdict} />
              <Badge type="feasibility" value={r.feasibilityRating} />
              {r.isPreliminary && <Badge type="pipeline" value="awaiting_review" />}
            </div>
            <h1 className="text-xl font-display font-bold text-navy-900 mb-2">{r.title}</h1>

            {/* Badges */}
            {r.badges.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {r.badges.map(badge => <Badge key={badge} type="achievement" value={badge} />)}
              </div>
            )}
          </div>
          <div className="flex items-center gap-6">
            <ScoreGauge value={r.overallScore} grade={r.grade} size={160} />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button onClick={() => navigate(`/student/viva?projectId=${r.projectId}`)} className="btn-navy">
            <BookOpen size={16} /> Viva Simulation
          </button>
          <button className="btn-outline">
            <Download size={16} /> Download PDF
          </button>
        </div>
      </div>

      {/* Two Columns: Radar + Scores */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4">Dimension Breakdown</h2>
          <RadarChart scores={r.dimensionScores} />
        </div>

        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-5">Score Details</h2>
          <div className="space-y-4">
            {DIMENSION_KEYS.map(({ key, label }) => (
              <ScoreBar
                key={key}
                label={label}
                score={r.dimensionScores[key as keyof typeof r.dimensionScores]}
                dimKey={key}
                projectId={r.projectId}
                onAppeal={(dim, score) => setAppealState({ dim, score })}
              />
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-4 flex items-center gap-1">
            <Info size={11} /> Hover over a dimension and click "Appeal" to dispute a score
          </p>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4 flex items-center gap-2">
            <CheckCircle size={18} className="text-teal-500" /> Strengths
          </h2>
          <ul className="space-y-2">
            {r.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4 flex items-center gap-2">
            <XCircle size={18} className="text-red-400" /> Areas for Improvement
          </h2>
          <ul className="space-y-2">
            {r.weaknesses.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Missing Sections */}
      {r.missingSections.length > 0 && (
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-gold-500" /> Missing Sections
          </h2>
          <div className="flex flex-wrap gap-2">
            {r.missingSections.map(s => (
              <span key={s} className="badge badge-red">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Percentile Ranks */}
      <div className="card">
        <h2 className="text-base font-semibold text-navy-900 mb-4 flex items-center gap-2">
          <TrendingUp size={18} className="text-teal-500" /> Historical Percentile Rankings
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {Object.entries(r.percentileRanks).map(([dim, pct]) => (
            <div key={dim} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p className="text-xs text-slate-500 capitalize">{dim}</p>
              <p className={clsx('text-2xl font-bold font-display mt-1',
                pct >= 80 ? 'text-teal-600' : pct >= 50 ? 'text-gold-500' : 'text-red-500'
              )}>Top {100 - pct}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Writing Quality */}
      {r.writingQuality && (
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4">Writing Quality Analysis</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <p className="text-xs text-slate-500">Readability Score</p>
              <p className={clsx('text-2xl font-bold font-display mt-1',
                r.writingQuality.readability >= 70 ? 'text-teal-600' : 'text-gold-500'
              )}>{r.writingQuality.readability}</p>
              <p className="text-xs text-slate-400">Flesch Reading Ease</p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <p className="text-xs text-slate-500">Passive Voice Count</p>
              <p className={clsx('text-2xl font-bold font-display mt-1',
                r.writingQuality.passiveVoiceCount <= 10 ? 'text-teal-600' : 'text-gold-500'
              )}>{r.writingQuality.passiveVoiceCount}</p>
              <p className="text-xs text-slate-400">instances found</p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <p className="text-xs text-slate-500 mb-2">Tone Flags</p>
              {r.writingQuality.toneFlags.map((f, i) => (
                <div key={i} className="flex items-start gap-1.5 text-xs text-gold-700 mb-1">
                  <AlertTriangle size={11} className="flex-shrink-0 mt-0.5 text-gold-500" /> {f}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Citations */}
      {r.citations && (
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4">Citation Validator</h2>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                className={clsx('h-full rounded-full', r.citations.ieeeCompliancePercent >= 80 ? 'bg-teal-500' : 'bg-gold-500')}
                style={{ width: `${r.citations.ieeeCompliancePercent}%` }}
              />
            </div>
            <span className="font-bold text-sm text-slate-700">{r.citations.ieeeCompliancePercent}% IEEE compliant</span>
          </div>
          {r.citations.missingReferences.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-slate-500 font-medium">References needing attention:</p>
              {r.citations.missingReferences.map((ref, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
                  <XCircle size={13} /> {ref}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Improvement Roadmap */}
      <div className="card">
        <h2 className="text-base font-semibold text-navy-900 mb-6 flex items-center gap-2">
          <Lightbulb size={18} className="text-gold-500" /> AI-Generated Improvement Roadmap
        </h2>
        <div>
          {r.improvementRoadmap.map((week, i) => (
            <WeekCard
              key={week.week}
              week={week.week}
              focus={week.focus}
              actions={week.actions}
              isLast={i === r.improvementRoadmap.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Appeal Modal */}
      {appealState && (
        <AppealModal
          isOpen={true}
          onClose={() => setAppealState(null)}
          projectId={r.projectId}
          dimension={appealState.dim}
          currentScore={appealState.score}
        />
      )}
    </div>
  );
};

export default ReportDetail;
