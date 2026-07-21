import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getFacultyDashboard } from '../../api/endpoints';
import { useAuth } from '../../auth/AuthContext';
import { LoadingState, ErrorState } from '../../components/States';
import { TrendChart } from '../../components/Charts';
import {
  Users, Inbox, AlertTriangle, TrendingUp, CheckCircle, Upload,
  FileText, MessageSquare, Flag, Clock,
} from 'lucide-react';
import type { ActivityItem } from '../../types';
import clsx from 'clsx';

const ACTIVITY_ICONS: Record<string, React.ReactNode> = {
  submitted: <Upload size={14} className="text-teal-500" />,
  reviewed: <CheckCircle size={14} className="text-teal-500" />,
  appealed: <MessageSquare size={14} className="text-gold-500" />,
  published: <FileText size={14} className="text-navy-700" />,
  flagged: <Flag size={14} className="text-red-500" />,
};

const StatCard: React.FC<{ icon: React.ReactNode; label: string; value: string | number; sub?: string; color: string }> = ({
  icon, label, value, sub, color,
}) => (
  <div className="stat-card">
    <div className={clsx('stat-icon', color)}>{icon}</div>
    <div>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-display font-bold text-navy-900 mt-0.5">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['facultyDashboard'],
    queryFn: getFacultyDashboard,
  });

  const trendData = [
    { month: 'Jan', avgScore: 70 }, { month: 'Feb', avgScore: 72 }, { month: 'Mar', avgScore: 74 },
    { month: 'Apr', avgScore: 73 }, { month: 'May', avgScore: 76 }, { month: 'Jun', avgScore: 78 },
  ];

  if (isLoading) return <LoadingState message="Loading dashboard..." />;
  if (isError || !data) return <ErrorState retry={refetch} />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">
          Good morning, {user?.name?.split(' ')[1] || user?.name}!
        </h1>
        <p className="text-slate-500 mt-1">
          {user?.role === 'reviewer' ? 'Review queue summary' : 'Your students\' project submissions overview'}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard icon={<Users size={22} className="text-teal-600" />} label="Total Submissions" value={data.totalSubmissions} color="bg-teal-50" />
        <StatCard icon={<Inbox size={22} className="text-gold-600" />} label="Pending Review" value={data.pendingReview} sub="awaiting your review" color="bg-gold-50" />
        <StatCard icon={<AlertTriangle size={22} className="text-red-500" />} label="Flagged Duplicates" value={data.flaggedDuplicates} sub="similarity >80%" color="bg-red-50" />
        <StatCard icon={<TrendingUp size={22} className="text-navy-700" />} label="Avg Score This Sem" value={`${data.avgScoreThisSemester.toFixed(1)}/100`} color="bg-navy-50" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="card lg:col-span-2">
          <h2 className="text-base font-semibold text-navy-900 mb-4">Score Trend — This Semester</h2>
          <TrendChart data={trendData} title="" />
        </div>

        {/* Activity Feed */}
        <div className="card">
          <h2 className="text-base font-semibold text-navy-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {data.recentActivity.map((item: ActivityItem) => (
              <div key={item.id} className="flex items-start gap-3 pb-3 border-b border-slate-50 last:border-0 last:pb-0">
                <div className="w-7 h-7 rounded-lg bg-slate-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                  {ACTIVITY_ICONS[item.type] || <Clock size={14} className="text-slate-400" />}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800">{item.studentName}</p>
                  <p className="text-xs text-slate-500 truncate">{item.details || item.projectTitle}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {new Date(item.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} ·{' '}
                    {new Date(item.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
