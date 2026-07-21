import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAllAppeals, resolveAppeal } from '../../api/endpoints';
import { LoadingState, ErrorState, EmptyState } from '../../components/States';
import Badge from '../../components/Badge';
import { MessageSquare, CheckCircle, XCircle, Edit2 } from 'lucide-react';
import { useState } from 'react';

const AppealsInbox: React.FC = () => {
  const qc = useQueryClient();
  const { data: appeals, isLoading, isError, refetch } = useQuery({
    queryKey: ['allAppeals'],
    queryFn: getAllAppeals,
  });

  const [resolving, setResolving] = useState<string | null>(null);
  const [response, setResponse] = useState('');

  const resolveMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'approve' | 'reject' }) =>
      resolveAppeal(id, action, undefined, response),
    onSuccess: () => { setResolving(null); setResponse(''); qc.invalidateQueries({ queryKey: ['allAppeals'] }); },
  });

  if (isLoading) return <LoadingState message="Loading appeals..." />;
  if (isError) return <ErrorState retry={refetch} />;

  const pending = (appeals || []).filter(a => a.status === 'pending' || a.status === 'under_review');
  const resolved = (appeals || []).filter(a => a.status === 'resolved' || a.status === 'rejected');

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Appeals Inbox</h1>
        <p className="text-slate-500 mt-1">{pending.length} pending appeal{pending.length !== 1 ? 's' : ''}</p>
      </div>

      {!appeals?.length ? (
        <EmptyState icon={<MessageSquare size={28} />} title="No appeals received" description="Students can appeal specific dimension scores from their report page." />
      ) : (
        <div className="space-y-6">
          {pending.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Pending</h2>
              <div className="space-y-4">
                {pending.map(appeal => (
                  <div key={appeal.appealId} className="card border-l-4 border-l-gold-500">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge type="appeal" value={appeal.status} />
                          <span className="text-xs text-slate-400">{new Date(appeal.createdAt).toLocaleDateString('en-IN')}</span>
                        </div>
                        <h3 className="font-semibold text-slate-800">{appeal.projectTitle}</h3>
                        <p className="text-sm text-slate-500 mt-0.5">
                          Disputed: <strong className="capitalize">{appeal.dimension}</strong> · Original score: <strong>{appeal.originalScore}/100</strong>
                        </p>
                      </div>
                    </div>

                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-4">
                      <p className="text-xs text-slate-500 mb-1 font-medium">STUDENT JUSTIFICATION</p>
                      <p className="text-sm text-slate-700">{appeal.studentJustification}</p>
                    </div>

                    {resolving === appeal.appealId ? (
                      <div className="space-y-3 animate-fade-in">
                        <textarea
                          value={response}
                          onChange={e => setResponse(e.target.value)}
                          rows={3}
                          className="input resize-none"
                          placeholder="Faculty response (will be shown to the student)..."
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => resolveMutation.mutate({ id: appeal.appealId, action: 'approve' })}
                            disabled={resolveMutation.isPending}
                            className="btn-primary flex-1"
                          >
                            <CheckCircle size={15} /> Approve Appeal
                          </button>
                          <button
                            onClick={() => resolveMutation.mutate({ id: appeal.appealId, action: 'reject' })}
                            disabled={resolveMutation.isPending}
                            className="btn-danger flex-1"
                          >
                            <XCircle size={15} /> Reject Appeal
                          </button>
                          <button onClick={() => { setResolving(null); setResponse(''); }} className="btn-outline">
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button onClick={() => setResolving(appeal.appealId)} className="btn-outline">
                        <Edit2 size={15} /> Review Appeal
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {resolved.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Resolved</h2>
              <div className="space-y-3">
                {resolved.map(appeal => (
                  <div key={appeal.appealId} className="card opacity-70">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-slate-700">{appeal.projectTitle}</h3>
                        <p className="text-xs text-slate-400 mt-0.5 capitalize">{appeal.dimension} · Original: {appeal.originalScore}</p>
                      </div>
                      <Badge type="appeal" value={appeal.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AppealsInbox;
