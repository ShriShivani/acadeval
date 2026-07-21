import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getHODStats } from '../../api/endpoints';
import { LoadingState, ErrorState } from '../../components/States';
import { TrendChart } from '../../components/Charts';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { Users, GraduationCap, FileText, CheckCircle, TrendingUp } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend);

const DOMAIN_COLORS = [
  '#1E7F72', '#C99A3A', '#1B2A4A', '#3b82f6', '#8b5cf6', '#ef4444', '#f97316',
];

const DeptOverview: React.FC = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['hodStats'],
    queryFn: getHODStats,
  });

  if (isLoading) return <LoadingState message="Loading department overview..." />;
  if (isError || !data) return <ErrorState retry={refetch} />;

  const domainLabels = Object.keys(data.domainDistribution);
  const domainValues = Object.values(data.domainDistribution);

  const doughnutData = {
    labels: domainLabels,
    datasets: [{
      data: domainValues,
      backgroundColor: DOMAIN_COLORS,
      borderColor: '#ffffff',
      borderWidth: 3,
      hoverBorderWidth: 4,
    }],
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: { font: { family: 'Inter', size: 12 }, color: '#475569', padding: 16, boxWidth: 12 },
      },
      tooltip: {
        backgroundColor: '#1B2A4A',
        callbacks: {
          label: (ctx: { label: string; raw: unknown; dataset: { data: number[] }; dataIndex: number }) =>
            ` ${ctx.label}: ${ctx.raw} projects`,
        },
      },
    },
  };

  const reviewedPct = Math.round((data.reviewedCount / data.totalSubmissions) * 100);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Department Overview</h1>
        <p className="text-slate-500 mt-1">Aggregate statistics and trends across all faculty and students</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {[
          { icon: <GraduationCap size={22} className="text-teal-600" />, label: 'Students', value: data.totalStudents, color: 'bg-teal-50' },
          { icon: <Users size={22} className="text-gold-600" />, label: 'Faculty', value: data.totalFaculty, color: 'bg-gold-50' },
          { icon: <FileText size={22} className="text-navy-700" />, label: 'Submissions', value: data.totalSubmissions, color: 'bg-navy-50' },
          { icon: <CheckCircle size={22} className="text-teal-600" />, label: 'Reviewed', value: `${reviewedPct}%`, color: 'bg-teal-50' },
          { icon: <TrendingUp size={22} className="text-purple-600" />, label: 'Avg Score', value: `${data.avgScore.toFixed(1)}`, color: 'bg-purple-50' },
        ].map(stat => (
          <div key={stat.label} className="card text-center py-5">
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center mx-auto mb-2 ${stat.color}`}>
              {stat.icon}
            </div>
            <p className="text-2xl font-display font-bold text-navy-900">{stat.value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Domain Distribution */}
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-5">Domain Distribution</h2>
          <div style={{ height: 280 }}>
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </div>

        {/* Score Trend */}
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-5">Average Score Trend</h2>
          <TrendChart data={data.trendData} title="" />
        </div>
      </div>

      {/* Review Progress */}
      <div className="card">
        <h2 className="font-semibold text-navy-900 mb-4">Review Progress This Semester</h2>
        <div className="flex items-center gap-4 mb-3">
          <div className="flex-1 bg-slate-100 rounded-full h-4 overflow-hidden">
            <div
              className="bg-teal-500 h-4 rounded-full transition-all duration-1000"
              style={{ width: `${reviewedPct}%` }}
            />
          </div>
          <span className="text-lg font-bold text-teal-700">{reviewedPct}%</span>
        </div>
        <p className="text-sm text-slate-500">
          <strong>{data.reviewedCount}</strong> of <strong>{data.totalSubmissions}</strong> submissions have been reviewed.
          {data.totalSubmissions - data.reviewedCount} remain pending.
        </p>
      </div>
    </div>
  );
};

export default DeptOverview;
