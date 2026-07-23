import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEvaluationReport, overrideScore, addFacultyNote, publishReview, getNoveltyReport, submitFacultyNoveltyReview } from '../../api/endpoints';
import { useAuth } from '../../auth/AuthContext';
import { LoadingState, ErrorState } from '../../components/States';
import RadarChart from '../../components/RadarChart';
import ScoreGauge from '../../components/ScoreGauge';
import Badge from '../../components/Badge';
import ExplainabilityViewer from '../../components/ExplainabilityViewer';
import { NoveltyReportView } from '../../components/NoveltyReportView';
import type { InternalEvaluationReport } from '../../types';
import {
  Edit2, Save, X, Flag, StickyNote, Send, CheckCircle, Eye, EyeOff,
  User, Clock, ChevronDown, ChevronUp, Sparkles, Network,
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

const ProjectReportView: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<'report' | 'explainability' | 'notes' | 'history' | 'novelty'>('report');
  const [overrideState, setOverrideState] = useState<{ dim: string; value: number; comment: string } | null>(null);
  const [newNote, setNewNote] = useState('');
  const [showPublishConfirm, setShowPublishConfirm] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [noveltyAbstract, setNoveltyAbstract] = useState('');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['internalReport', projectId],
    queryFn: () => getEvaluationReport(projectId!, user!.role),
    enabled: !!projectId && !!user,
  });

  const overrideMutation = useMutation({
    mutationFn: () => overrideScore(projectId!, overrideState!.dim, overrideState!.value, overrideState!.comment),
    onSuccess: () => { setOverrideState(null); queryClient.invalidateQueries({ queryKey: ['internalReport', projectId] }); },
  });

  const noteMutation = useMutation({
    mutationFn: () => addFacultyNote(projectId!, newNote),
    onSuccess: () => { setNewNote(''); queryClient.invalidateQueries({ queryKey: ['internalReport', projectId] }); },
  });

  const publishMutation = useMutation({
    mutationFn: () => publishReview(projectId!),
    onSuccess: () => { setShowPublishConfirm(false); setPublishSuccess(true); },
  });

  const noveltyMutation = useMutation({
    mutationFn: () => getNoveltyReport(projectId!, noveltyAbstract),
  });

  const facultyNoveltyReviewMutation = useMutation({
    mutationFn: ({ facultyScore, reason }: { facultyScore: number; reason: string }) =>
      submitFacultyNoveltyReview(projectId!, facultyScore, noveltyMutation.data!.overall_novelty_score, reason),
  });

  if (isLoading) return <LoadingState message="Loading project report..." />;
  if (isError || !data) return <ErrorState retry={refetch} />;

  const r = data as InternalEvaluationReport;

  const TABS = [
    { id: 'report', label: 'Evaluation Report', icon: <Eye size={15} /> },
    { id: 'novelty', label: 'Graph Novelty', icon: <Network size={15} /> },
    { id: 'explainability', label: 'AI Explainability', icon: <Sparkles size={15} /> },
    { id: 'notes', label: `Faculty Notes (${r.facultyNotes?.length || 0})`, icon: <StickyNote size={15} /> },
    { id: 'history', label: 'Score History', icon: <Clock size={15} /> },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge type="submission" value={r.submissionType} />
              <Badge type="domain" value={r.domain} />
              <Badge type="pipeline" value={r.pipelineStatus} />
              {r.flaggingReasons?.length > 0 && (
                <span className="badge badge-red"><Flag size={11} />Flagged</span>
              )}
            </div>
            <h1 className="text-xl font-display font-bold text-navy-900">{r.title}</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
              {r.assignedGuide && <span className="flex items-center gap-1"><User size={13} />Guide: {r.assignedGuide}</span>}
              {r.assignedReviewer && <span className="flex items-center gap-1"><User size={13} />Reviewer: {r.assignedReviewer}</span>}
            </div>
          </div>
          <ScoreGauge value={r.overallScore} grade={r.grade} size={140} />
        </div>

        {r.flaggingReasons?.length > 0 && (
          <div className="mt-4 bg-red-50 border border-red-100 rounded-xl p-3">
            <p className="text-xs font-semibold text-red-700 mb-1 flex items-center gap-1"><Flag size={12} /> FLAGGING REASONS (Internal)</p>
            <ul className="space-y-1">
              {r.flaggingReasons.map((reason, i) => (
                <li key={i} className="text-sm text-red-600">• {reason}</li>
              ))}
            </ul>
          </div>
        )}

        {publishSuccess ? (
          <div className="mt-4 bg-teal-50 border border-teal-200 rounded-xl p-4 flex items-center gap-3">
            <CheckCircle size={20} className="text-teal-600" />
            <p className="text-teal-700 font-semibold">Review published! The student can now see their full report.</p>
          </div>
        ) : (
          <div className="flex gap-3 mt-5">
            {r.pipelineStatus !== 'reviewed' && (
              showPublishConfirm ? (
                <div className="flex items-center gap-3 bg-teal-50 rounded-xl p-3 border border-teal-200 flex-1">
                  <p className="text-sm text-teal-700 flex-1">Publish this review? The student will be notified and can see the final report.</p>
                  <button onClick={() => publishMutation.mutate()} className="btn-primary">
                    <Send size={15} /> Confirm Publish
                  </button>
                  <button onClick={() => setShowPublishConfirm(false)} className="btn-outline"><X size={15} /></button>
                </div>
              ) : (
                <button onClick={() => setShowPublishConfirm(true)} className="btn-primary">
                  <Send size={16} /> Publish Review
                </button>
              )
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 rounded-2xl p-1">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={clsx(
              'flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-sm font-medium transition-all',
              activeTab === tab.id
                ? 'bg-white text-navy-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            )}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Report */}
      {activeTab === 'report' && (
        <div className="space-y-5">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="card">
              <h2 className="font-semibold text-navy-900 mb-4">Dimension Scores</h2>
              <div className="space-y-3">
                {DIMENSION_KEYS.map(({ key, label }) => {
                  const score = r.dimensionScores[key as keyof typeof r.dimensionScores];
                  const isEditing = overrideState?.dim === key;
                  return (
                    <div key={key} className="group">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-slate-600 w-36">{label}</span>
                        {score !== null ? (
                          <>
                            <div className="flex-1 bg-slate-100 rounded-full h-2">
                              <div className={clsx(
                                'h-2 rounded-full',
                                score >= 80 ? 'bg-teal-500' : score >= 60 ? 'bg-gold-500' : 'bg-red-500'
                              )} style={{ width: `${score}%` }} />
                            </div>
                            {isEditing ? (
                              <input
                                type="number"
                                min="0"
                                max="100"
                                value={overrideState.value}
                                onChange={e => setOverrideState(prev => prev ? { ...prev, value: Number(e.target.value) } : null)}
                                className="w-16 text-center input py-1 text-sm"
                              />
                            ) : (
                              <span className="font-bold text-sm w-8 text-right">{score}</span>
                            )}
                            <button
                              onClick={() => isEditing ? setOverrideState(null) : setOverrideState({ dim: key, value: score, comment: '' })}
                              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg hover:bg-slate-100"
                            >
                              {isEditing ? <X size={13} className="text-red-500" /> : <Edit2 size={13} className="text-slate-400" />}
                            </button>
                          </>
                        ) : (
                          <span className="text-xs text-slate-300">N/A (Abstract)</span>
                        )}
                      </div>
                      {isEditing && (
                        <div className="mt-2 pl-36 space-y-2 animate-fade-in">
                          <input
                            className="input text-sm py-2"
                            placeholder="Required: reason for override..."
                            value={overrideState.comment}
                            onChange={e => setOverrideState(prev => prev ? { ...prev, comment: e.target.value } : null)}
                          />
                          <button
                            onClick={() => overrideMutation.mutate()}
                            disabled={!overrideState.comment || overrideMutation.isPending}
                            className="btn-primary py-1.5 text-xs"
                          >
                            <Save size={13} /> Save Override
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="card">
              <h2 className="font-semibold text-navy-900 mb-4">Radar Chart</h2>
              <RadarChart scores={r.dimensionScores} size="sm" />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="card">
              <h2 className="font-semibold text-navy-900 mb-3 flex items-center gap-2">
                <CheckCircle size={16} className="text-teal-500" /> Strengths
              </h2>
              <ul className="space-y-1.5">
                {r.strengths.map((s, i) => <li key={i} className="text-sm text-slate-600 flex items-start gap-2"><div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5" />{s}</li>)}
              </ul>
            </div>
            <div className="card">
              <h2 className="font-semibold text-navy-900 mb-3">Weaknesses</h2>
              <ul className="space-y-1.5">
                {r.weaknesses.map((w, i) => <li key={i} className="text-sm text-slate-600 flex items-start gap-2"><div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5" />{w}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Graph Novelty (AcadEval+) */}
      {activeTab === 'novelty' && (
        <div className="space-y-4">
          {!noveltyMutation.data && (
            <div className="card space-y-3">
              <h2 className="font-semibold text-navy-900">Run Graph-Based Novelty Assessment</h2>
              <p className="text-sm text-slate-500">
                Paste the project's title/abstract to classify its domain, extract structured entities, and
                score novelty against the Neo4j project knowledge graph.
              </p>
              <textarea
                value={noveltyAbstract}
                onChange={e => setNoveltyAbstract(e.target.value)}
                rows={4}
                className="input resize-none"
                placeholder="Paste the project abstract here..."
              />
              {noveltyMutation.isError && (
                <p className="text-sm text-red-600">
                  Could not compute a novelty score — the graph engine may be unavailable (Neo4j not running).
                </p>
              )}
              <button
                onClick={() => noveltyMutation.mutate()}
                disabled={!noveltyAbstract.trim() || noveltyMutation.isPending}
                className="btn-primary"
              >
                <Network size={15} /> {noveltyMutation.isPending ? 'Scoring…' : 'Run Novelty Assessment'}
              </button>
            </div>
          )}
          {noveltyMutation.data && (
            <NoveltyReportView
              report={noveltyMutation.data}
              onFacultyScoreSubmit={(facultyScore, reason) => facultyNoveltyReviewMutation.mutate({ facultyScore, reason })}
            />
          )}
        </div>
      )}

      {/* Tab: Explainability */}
      {activeTab === 'explainability' && (
        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <Sparkles size={18} className="text-gold-500" />
            <h2 className="font-semibold text-navy-900">AI Explainability (Internal — LIME/SHAP)</h2>
          </div>
          <div className="bg-gold-50 rounded-xl p-3 border border-gold-100 mb-5">
            <p className="text-xs text-gold-700">
              🔒 <strong>Internal Only</strong> — This view shows sentence-level feature attribution scores from the AI pipeline. It is never shown to students.
            </p>
          </div>
          <ExplainabilityViewer annotations={r.explainabilityAnnotations || []} />
        </div>
      )}

      {/* Tab: Faculty Notes */}
      {activeTab === 'notes' && (
        <div className="card space-y-5">
          <h2 className="font-semibold text-navy-900">Faculty Notes (Internal)</h2>
          <div className="bg-navy-50 rounded-xl p-3 border border-navy-200">
            <p className="text-xs text-navy-700">These notes are visible only to faculty and HOD. Students never see this section.</p>
          </div>

          <div className="space-y-3">
            {(r.facultyNotes || []).map((note, i) => (
              <div key={i} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-7 h-7 rounded-full bg-navy-900 flex items-center justify-center text-white text-xs font-bold">
                    {note.author.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-800">{note.author}</p>
                    <p className="text-xs text-slate-400 capitalize">{note.role} · {new Date(note.timestamp).toLocaleString('en-IN')}</p>
                  </div>
                </div>
                <p className="text-sm text-slate-700">{note.text}</p>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <textarea
              value={newNote}
              onChange={e => setNewNote(e.target.value)}
              rows={3}
              className="input resize-none"
              placeholder="Add an internal note (visible only to faculty)..."
            />
            <button
              onClick={() => noteMutation.mutate()}
              disabled={!newNote.trim() || noteMutation.isPending}
              className="btn-navy"
            >
              <StickyNote size={15} /> Add Note
            </button>
          </div>
        </div>
      )}

      {/* Tab: Score History */}
      {activeTab === 'history' && (
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Score Override History</h2>
          {!(r.scoreOverrideHistory?.length) ? (
            <p className="text-slate-400 text-sm">No score overrides have been made yet.</p>
          ) : (
            <div className="space-y-3">
              {r.scoreOverrideHistory.map((entry, i) => (
                <div key={i} className="flex items-start gap-4 bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <div className="w-8 h-8 rounded-lg bg-gold-100 flex items-center justify-center text-gold-700 flex-shrink-0">
                    <Edit2 size={14} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-slate-700 capitalize">{entry.dimension}</span>
                      <span className="text-sm text-slate-400">{entry.oldValue} → <strong className="text-teal-700">{entry.newValue}</strong></span>
                    </div>
                    <p className="text-sm text-slate-600">{entry.comment}</p>
                    <p className="text-xs text-slate-400 mt-1">By {entry.by} · {new Date(entry.timestamp).toLocaleString('en-IN')}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectReportView;
