import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getLeaderboard } from '../../api/endpoints';
import { LoadingState, ErrorState, EmptyState } from '../../components/States';
import Badge from '../../components/Badge';
import { Trophy, Medal, Award, Star } from 'lucide-react';
import clsx from 'clsx';

const RankIcon: React.FC<{ rank: number }> = ({ rank }) => {
  if (rank === 1) return <Trophy size={18} className="text-gold-500" />;
  if (rank === 2) return <Medal size={18} className="text-slate-400" />;
  if (rank === 3) return <Award size={18} className="text-gold-700" />;
  return <span className="text-sm font-bold text-slate-400">#{rank}</span>;
};

const Leaderboard: React.FC = () => {
  const { data: entries, isLoading, isError, refetch } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: getLeaderboard,
  });

  if (isLoading) return <LoadingState message="Loading leaderboard..." />;
  if (isError) return <ErrorState retry={refetch} />;

  const top3 = entries?.slice(0, 3) || [];
  const rest = entries?.slice(3) || [];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Department Leaderboard</h1>
        <p className="text-slate-500 mt-1">Top-performing projects this semester ranked by overall evaluation score</p>
      </div>

      {/* Top 3 Podium */}
      <div className="card bg-navy-gradient mb-6 overflow-hidden">
        <div className="flex items-end justify-center gap-4 py-8 px-4">
          {/* 2nd Place */}
          {top3[1] && (
            <div className="flex flex-col items-center gap-2 flex-1 max-w-48">
              <div className="w-14 h-14 rounded-full bg-slate-300 flex items-center justify-center text-slate-700 font-bold text-xl border-4 border-slate-200">
                {top3[1].studentName.charAt(0)}
              </div>
              <div className="text-center">
                <p className="text-white font-semibold text-sm">{top3[1].studentName}</p>
                <p className="text-white/50 text-xs">{top3[1].rollNo}</p>
                <p className="text-2xl font-display font-bold text-slate-300 mt-1">{top3[1].overallScore}</p>
              </div>
              <div className="w-full bg-slate-500/50 rounded-t-xl py-4 flex items-center justify-center">
                <Medal size={24} className="text-slate-300" />
              </div>
            </div>
          )}

          {/* 1st Place */}
          {top3[0] && (
            <div className="flex flex-col items-center gap-2 flex-1 max-w-52">
              <div className="relative">
                <div className="w-16 h-16 rounded-full bg-gold-400 flex items-center justify-center text-white font-bold text-2xl border-4 border-gold-300">
                  {top3[0].studentName.charAt(0)}
                </div>
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Star size={20} className="text-gold-400" fill="currentColor" />
                </div>
              </div>
              <div className="text-center">
                <p className="text-white font-bold text-sm">{top3[0].studentName}</p>
                <p className="text-white/50 text-xs">{top3[0].rollNo}</p>
                <p className="text-3xl font-display font-bold text-gold-400 mt-1">{top3[0].overallScore}</p>
              </div>
              <div className="w-full bg-gold-500/50 rounded-t-xl py-6 flex items-center justify-center">
                <Trophy size={28} className="text-gold-300" />
              </div>
            </div>
          )}

          {/* 3rd Place */}
          {top3[2] && (
            <div className="flex flex-col items-center gap-2 flex-1 max-w-48">
              <div className="w-14 h-14 rounded-full bg-gold-800 flex items-center justify-center text-gold-200 font-bold text-xl border-4 border-gold-700">
                {top3[2].studentName.charAt(0)}
              </div>
              <div className="text-center">
                <p className="text-white font-semibold text-sm">{top3[2].studentName}</p>
                <p className="text-white/50 text-xs">{top3[2].rollNo}</p>
                <p className="text-2xl font-display font-bold text-gold-700 mt-1">{top3[2].overallScore}</p>
              </div>
              <div className="w-full bg-gold-800/50 rounded-t-xl py-3 flex items-center justify-center">
                <Award size={22} className="text-gold-600" />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Full Table */}
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Student</th>
              <th>Project Title</th>
              <th>Domain</th>
              <th>Score</th>
              <th>Achievements</th>
            </tr>
          </thead>
          <tbody>
            {entries?.map(entry => (
              <tr key={entry.rollNo} className={clsx(entry.isCurrentUser && 'bg-teal-50 border-l-4 border-l-teal-500')}>
                <td>
                  <div className="flex items-center justify-center w-8">
                    <RankIcon rank={entry.rank} />
                  </div>
                </td>
                <td>
                  <div>
                    <p className={clsx('font-semibold text-slate-800', entry.isCurrentUser && 'text-teal-700')}>
                      {entry.studentName} {entry.isCurrentUser && <span className="text-xs text-teal-500 font-normal">(You)</span>}
                    </p>
                    <p className="text-xs text-slate-400">{entry.rollNo}</p>
                  </div>
                </td>
                <td>
                  <p className="text-slate-600 text-sm max-w-xs truncate" title={entry.projectTitle}>{entry.projectTitle}</p>
                </td>
                <td><Badge type="domain" value={entry.domain} size="sm" /></td>
                <td>
                  <span className={clsx(
                    'text-lg font-bold font-display',
                    entry.overallScore >= 85 ? 'text-teal-600' : entry.overallScore >= 70 ? 'text-gold-500' : 'text-slate-600'
                  )}>
                    {entry.overallScore}
                  </span>
                </td>
                <td>
                  <div className="flex flex-wrap gap-1">
                    {entry.badges.slice(0, 2).map(b => <Badge key={b} type="achievement" value={b} size="sm" />)}
                    {entry.badges.length > 2 && <span className="badge badge-slate">+{entry.badges.length - 2}</span>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leaderboard;
