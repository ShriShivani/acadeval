import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getLeaderboard } from '../../api/endpoints';
import { LoadingState, ErrorState } from '../../components/States';
import Badge from '../../components/Badge';
import { Trophy, Settings, RotateCcw } from 'lucide-react';
import clsx from 'clsx';

const LeaderboardAdmin: React.FC = () => {
  const { data: entries, isLoading, isError, refetch } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: getLeaderboard,
  });

  if (isLoading) return <LoadingState message="Loading leaderboard..." />;
  if (isError) return <ErrorState retry={refetch} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-navy-900">Leaderboard Admin</h1>
          <p className="text-slate-500 mt-1">Manage department leaderboard and badge thresholds</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-outline"><Settings size={15} /> Configure Thresholds</button>
          <button className="btn-danger"><RotateCcw size={15} /> Reset Leaderboard</button>
        </div>
      </div>

      {/* Badge threshold config */}
      <div className="card mb-6">
        <h2 className="font-semibold text-navy-900 mb-4 flex items-center gap-2"><Settings size={16} className="text-teal-500" /> Badge Award Thresholds</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[
            { badge: 'Novel Idea Award', threshold: 'Novelty ≥ 80', className: 'badge-teal' },
            { badge: 'Publication Ready', threshold: 'Pub. Potential ≥ 85', className: 'badge-gold' },
            { badge: 'Most Improved', threshold: 'Score increase ≥ 15 pts', className: 'badge-purple' },
            { badge: 'High Feasibility', threshold: 'Feasibility ≥ 85', className: 'badge-teal' },
            { badge: 'Top Scorer', threshold: 'Overall ≥ 90', className: 'badge-gold' },
            { badge: 'Completeness Star', threshold: 'Completeness = 100', className: 'badge-navy' },
          ].map(({ badge, threshold, className }) => (
            <div key={badge} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <span className={`badge ${className} mb-2`}><Trophy size={11} /> {badge}</span>
              <p className="text-xs text-slate-500 mt-2">{threshold}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Full table */}
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Student</th>
              <th>Project</th>
              <th>Domain</th>
              <th>Score</th>
              <th>Badges</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {entries?.map(entry => (
              <tr key={entry.rollNo}>
                <td>
                  <div className="flex items-center justify-center w-8">
                    {entry.rank <= 3 ? (
                      <span className="text-gold-500 font-bold">#{entry.rank}</span>
                    ) : (
                      <span className="text-slate-400 text-sm">#{entry.rank}</span>
                    )}
                  </div>
                </td>
                <td>
                  <div>
                    <p className="font-medium text-slate-800">{entry.studentName}</p>
                    <p className="text-xs text-slate-400">{entry.rollNo}</p>
                  </div>
                </td>
                <td><p className="text-sm text-slate-600 max-w-[180px] truncate">{entry.projectTitle}</p></td>
                <td><Badge type="domain" value={entry.domain} size="sm" /></td>
                <td>
                  <span className={clsx('font-bold', entry.overallScore >= 85 ? 'text-teal-600' : 'text-slate-600')}>
                    {entry.overallScore}
                  </span>
                </td>
                <td>
                  <div className="flex flex-wrap gap-1">
                    {entry.badges.map(b => <Badge key={b} type="achievement" value={b} size="sm" />)}
                  </div>
                </td>
                <td>
                  <button className="text-xs text-teal-600 hover:underline">Edit Badges</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeaderboardAdmin;
