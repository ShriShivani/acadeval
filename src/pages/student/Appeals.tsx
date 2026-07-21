import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMyAppeals } from '../../api/endpoints';
import { LoadingState, ErrorState, EmptyState } from '../../components/States';
import Badge from '../../components/Badge';
import { MessageSquare, Clock } from 'lucide-react';

const STATUS_MSG: Record<string, string> = {
  pending: 'Your appeal is in the queue and will be reviewed by your guide.',
  under_review: 'Your guide is currently reviewing this appeal.',
  resolved: 'Appeal resolved. Score has been updated.',
  rejected: 'Appeal was reviewed and the original score was upheld.',
};

const Appeals: React.FC = () => {
  const { data: appeals, isLoading, isError, refetch } = useQuery({
    queryKey: ['myAppeals'],
    queryFn: getMyAppeals,
  });

  if (isLoading) return <LoadingState message="Loading your appeals..." />;
  if (isError) return <ErrorState retry={refetch} />;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">My Appeals</h1>
        <p className="text-slate-500 mt-1">Track score appeals you've submitted to your guide or reviewer</p>
      </div>

      {!appeals?.length ? (
        <EmptyState
          icon={<MessageSquare size={28} />}
          title="No appeals submitted"
          description="You can appeal any dimension score from your Report Detail page. Appeals are reviewed by your assigned guide."
        />
      ) : (
        <div className="space-y-4">
          {appeals.map(appeal => (
            <div key={appeal.appealId} className="card">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge type="appeal" value={appeal.status} />
                    <span className="text-xs text-slate-400">
                      <Clock size={11} className="inline mr-1" />
                      {new Date(appeal.createdAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800">{appeal.projectTitle}</h3>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs text-slate-400">Dimension</p>
                  <p className="font-semibold text-slate-700 capitalize">{appeal.dimension}</p>
                  <p className="text-sm text-slate-500 mt-1">Original: <strong>{appeal.originalScore}</strong>/100</p>
                  {appeal.resolvedScore !== undefined && (
                    <p className="text-sm text-teal-600 font-semibold">Updated: <strong>{appeal.resolvedScore}</strong>/100</p>
                  )}
                </div>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 mb-3 border border-slate-100">
                <p className="text-xs text-slate-500 mb-1 font-medium">YOUR JUSTIFICATION</p>
                <p className="text-sm text-slate-700">{appeal.studentJustification}</p>
              </div>

              <div className={`text-sm px-4 py-3 rounded-xl border ${
                appeal.status === 'resolved' ? 'bg-teal-50 text-teal-700 border-teal-100' :
                appeal.status === 'rejected' ? 'bg-red-50 text-red-700 border-red-100' :
                'bg-gold-50 text-gold-700 border-gold-100'
              }`}>
                {appeal.facultyResponse || STATUS_MSG[appeal.status]}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Appeals;
