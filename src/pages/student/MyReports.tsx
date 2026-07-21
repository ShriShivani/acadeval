import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getMyProjects } from '../../api/endpoints';
import { LoadingState, ErrorState, EmptyState } from '../../components/States';
import Badge from '../../components/Badge';
import { FileText, Upload, ChevronRight, Clock, AlertCircle, Cpu, CheckCircle } from 'lucide-react';
import type { ProjectSummary } from '../../types';
import clsx from 'clsx';

const statusSteps = ['uploaded', 'ai_processing', 'awaiting_review', 'reviewed'];
const statusLabels: Record<string, string> = {
  uploaded: 'Uploaded',
  ai_processing: 'AI Processing',
  awaiting_review: 'Awaiting Review',
  reviewed: 'Reviewed',
};

const ProjectCard: React.FC<{ project: ProjectSummary; onClick: () => void }> = ({ project, onClick }) => {
  const stepIndex = statusSteps.indexOf(project.pipelineStatus);
  const isReviewed = project.pipelineStatus === 'reviewed';

  return (
    <div className="card-hover cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Badge type="submission" value={project.submissionType} size="sm" />
            <Badge type="domain" value={project.domain} size="sm" />
          </div>
          <h3 className="font-semibold text-slate-800 text-base leading-snug">{project.title}</h3>
          <p className="text-sm text-slate-400 mt-1">Submitted {new Date(project.submittedOn).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</p>
        </div>
        {project.overallScore !== null ? (
          <div className="flex-shrink-0 text-center">
            <div className={clsx(
              'w-14 h-14 rounded-2xl flex items-center justify-center font-display font-bold text-xl',
              project.overallScore >= 80 ? 'bg-teal-50 text-teal-700' :
              project.overallScore >= 60 ? 'bg-gold-50 text-gold-700' : 'bg-red-50 text-red-700'
            )}>
              {project.overallScore}
            </div>
            <p className="text-xs text-slate-400 mt-1">/ 100</p>
          </div>
        ) : (
          <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center flex-shrink-0">
            <Cpu size={22} className="text-slate-400 animate-pulse-soft" />
          </div>
        )}
      </div>

      {/* Pipeline progress */}
      <div className="mb-4">
        <div className="flex items-center gap-0">
          {statusSteps.map((step, i) => (
            <React.Fragment key={step}>
              <div className={clsx(
                'flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold transition-colors flex-shrink-0',
                i < stepIndex ? 'bg-teal-500 text-white' :
                i === stepIndex ? 'bg-teal-100 text-teal-700 ring-2 ring-teal-500' :
                'bg-slate-100 text-slate-400'
              )}>
                {i < stepIndex ? <CheckCircle size={14} /> : i + 1}
              </div>
              {i < statusSteps.length - 1 && (
                <div className={clsx('flex-1 h-0.5', i < stepIndex ? 'bg-teal-500' : 'bg-slate-100')} />
              )}
            </React.Fragment>
          ))}
        </div>
        <div className="flex justify-between mt-1.5">
          {statusSteps.map(step => (
            <span key={step} className={clsx(
              'text-[9px] font-medium',
              step === project.pipelineStatus ? 'text-teal-600' : 'text-slate-300'
            )}>
              {statusLabels[step]}
            </span>
          ))}
        </div>
      </div>

      {/* Status message */}
      {!isReviewed && project.pipelineStatus === 'awaiting_review' && project.overallScore !== null && (
        <div className="bg-gold-50 border border-gold-100 rounded-xl p-3 flex items-start gap-2">
          <Clock size={14} className="text-gold-600 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-gold-700">
            <strong>AI Draft Ready</strong> — Your AI-generated report is available as a preliminary view.
            Awaiting guide/reviewer finalization before full report is released.
          </p>
        </div>
      )}

      <div className="flex items-center justify-between mt-4">
        <Badge type="pipeline" value={project.pipelineStatus} />
        <button className="flex items-center gap-1 text-teal-600 text-sm font-medium hover:text-teal-700">
          {isReviewed ? 'View Full Report' : 'View Preliminary'} <ChevronRight size={15} />
        </button>
      </div>
    </div>
  );
};

const MyReports: React.FC = () => {
  const navigate = useNavigate();
  const { data: projects, isLoading, isError, refetch } = useQuery({
    queryKey: ['myProjects'],
    queryFn: getMyProjects,
  });

  if (isLoading) return <LoadingState message="Loading your submissions..." />;
  if (isError) return <ErrorState retry={refetch} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-navy-900">My Reports</h1>
          <p className="text-slate-500 mt-1">Track your project submissions and evaluation status</p>
        </div>
        <button onClick={() => navigate('/student/upload')} className="btn-primary">
          <Upload size={16} /> New Submission
        </button>
      </div>

      {!projects?.length ? (
        <EmptyState
          icon={<FileText size={28} />}
          title="No submissions yet"
          description="Submit your first project to get AI-powered evaluation with radar charts, improvement roadmap, and viva preparation."
          action={
            <button onClick={() => navigate('/student/upload')} className="btn-primary">
              <Upload size={16} /> Submit Project
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {projects.map(project => (
            <ProjectCard
              key={project.projectId}
              project={project}
              onClick={() => navigate(`/student/report/${project.projectId}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default MyReports;
