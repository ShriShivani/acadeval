import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAllProjects } from '../../api/endpoints';
import { LoadingState } from '../../components/States';
import Badge from '../../components/Badge';
import { CheckCircle } from 'lucide-react';

const ReviewQueue: React.FC = () => {
  const navigate = useNavigate();

  const { data: allProjects, isLoading } = useQuery({
    queryKey: ['allProjects'],
    queryFn: getAllProjects,
  });

  const pending = (allProjects || []).filter(p => p.pipelineStatus === 'awaiting_review');

  if (isLoading) return <LoadingState message="Loading review queue..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Review Queue</h1>
        <p className="text-slate-500 mt-1">{pending.length} project{pending.length !== 1 ? 's' : ''} awaiting your review</p>
      </div>

      {!pending.length ? (
        <div className="card text-center py-16">
          <CheckCircle size={40} className="text-teal-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-700">All Caught Up!</h2>
          <p className="text-slate-400 mt-2">No projects are currently awaiting review.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {pending.map(p => (
            <div
              key={p.projectId}
              className="card-hover cursor-pointer flex items-center gap-4"
              onClick={() => navigate(`/faculty/report/${p.projectId}`)}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge type="submission" value={p.submissionType} size="sm" />
                  <Badge type="domain" value={p.domain} size="sm" />
                </div>
                <h3 className="font-semibold text-slate-800">{p.title}</h3>
                <p className="text-sm text-slate-500 mt-0.5">{p.studentName} · {p.rollNo}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-gold-500">{p.overallScore ?? '—'}</p>
                <p className="text-xs text-slate-400">AI Score</p>
                <button className="btn-primary mt-2 py-1.5 text-xs">Review Now</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewQueue;
