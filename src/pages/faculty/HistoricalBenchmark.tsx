import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getBenchmarks } from '../../api/endpoints';
import { LoadingState, ErrorState } from '../../components/States';
import { BenchmarkChart } from '../../components/Charts';
import type { SemesterBenchmark } from '../../types';

type Metric = keyof Omit<SemesterBenchmark, 'semester' | 'year' | 'totalProjects'>;

const METRICS: { key: Metric; label: string }[] = [
  { key: 'avgOverall', label: 'Overall Average' },
  { key: 'avgNovelty', label: 'Novelty' },
  { key: 'avgFeasibility', label: 'Feasibility' },
  { key: 'avgCompleteness', label: 'Completeness' },
  { key: 'avgTechnicalDepth', label: 'Technical Depth' },
  { key: 'avgClarity', label: 'Clarity' },
];

const HistoricalBenchmark: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = useState<Metric>('avgOverall');
  const { data: benchmarks, isLoading, isError, refetch } = useQuery({
    queryKey: ['benchmarks'],
    queryFn: getBenchmarks,
  });

  if (isLoading) return <LoadingState message="Loading benchmarks..." />;
  if (isError) return <ErrorState retry={refetch} />;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Historical Benchmarking</h1>
        <p className="text-slate-500 mt-1">Compare current semester scores against previous semesters</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
        {benchmarks?.slice(-1).map(b => [
          { label: 'Avg Score', value: b.avgOverall, suffix: '/100' },
          { label: 'Top Score', value: b.topScore, suffix: '/100' },
          { label: 'Total Projects', value: b.totalProjects, suffix: '' },
        ]).flat().map(stat => (
          <div key={stat.label} className="card py-4 text-center">
            <p className="text-xs text-slate-400 font-medium">{stat.label} (This Sem)</p>
            <p className="text-2xl font-display font-bold text-navy-900 mt-1">{stat.value}<span className="text-sm text-slate-400">{stat.suffix}</span></p>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-semibold text-navy-900">Score Comparison by Semester</h2>
          <select
            value={selectedMetric}
            onChange={e => setSelectedMetric(e.target.value as Metric)}
            className="input w-auto text-sm"
          >
            {METRICS.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
          </select>
        </div>
        <BenchmarkChart benchmarks={benchmarks || []} metric={selectedMetric} />
      </div>

      <div className="table-container mt-6">
        <table className="table">
          <thead>
            <tr>
              <th>Semester</th>
              <th>Year</th>
              <th>Avg Novelty</th>
              <th>Avg Feasibility</th>
              <th>Avg Completeness</th>
              <th>Avg Technical</th>
              <th>Avg Overall</th>
              <th>Top Score</th>
              <th>Projects</th>
            </tr>
          </thead>
          <tbody>
            {benchmarks?.map(b => (
              <tr key={`${b.semester}-${b.year}`}>
                <td className="font-medium">{b.semester}</td>
                <td>{b.year}</td>
                <td className="text-teal-600 font-semibold">{b.avgNovelty}</td>
                <td className="text-teal-600 font-semibold">{b.avgFeasibility}</td>
                <td className="text-teal-600 font-semibold">{b.avgCompleteness}</td>
                <td className="text-teal-600 font-semibold">{b.avgTechnicalDepth}</td>
                <td className="font-bold text-navy-900">{b.avgOverall}</td>
                <td className="text-gold-600 font-bold">{b.topScore}</td>
                <td className="text-slate-500">{b.totalProjects}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoricalBenchmark;
