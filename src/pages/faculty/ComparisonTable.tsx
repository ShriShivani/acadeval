import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAllProjects } from '../../api/endpoints';
import { LoadingState, ErrorState } from '../../components/States';
import Badge from '../../components/Badge';
import { Download, ArrowUpDown } from 'lucide-react';
import type { ProjectSummary } from '../../types';
import clsx from 'clsx';

type SortKey = 'studentName' | 'overallScore' | 'domain' | 'pipelineStatus';

const ComparisonTable: React.FC = () => {
  const [sortKey, setSortKey] = useState<SortKey>('overallScore');
  const [sortAsc, setSortAsc] = useState(false);

  const { data: projects, isLoading, isError, refetch } = useQuery({
    queryKey: ['allProjects'],
    queryFn: getAllProjects,
  });

  const sorted = [...(projects || [])].sort((a, b) => {
    const va = a[sortKey] ?? '';
    const vb = b[sortKey] ?? '';
    if (va < vb) return sortAsc ? -1 : 1;
    if (va > vb) return sortAsc ? 1 : -1;
    return 0;
  });

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(p => !p);
    else { setSortKey(key); setSortAsc(true); }
  };

  const SortHeader: React.FC<{ label: string; k: SortKey }> = ({ label, k }) => (
    <th className="cursor-pointer select-none" onClick={() => handleSort(k)}>
      <div className="flex items-center gap-1">
        {label}
        <ArrowUpDown size={12} className={clsx('text-slate-300', sortKey === k && 'text-teal-500')} />
      </div>
    </th>
  );

  if (isLoading) return <LoadingState message="Loading comparison data..." />;
  if (isError) return <ErrorState retry={refetch} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-navy-900">Comparison Table</h1>
          <p className="text-slate-500 mt-1">Side-by-side evaluation comparison across all projects</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-outline"><Download size={15} /> Export CSV</button>
          <button className="btn-outline"><Download size={15} /> Export PDF</button>
        </div>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <SortHeader label="Student" k="studentName" />
              <th>Title</th>
              <SortHeader label="Domain" k="domain" />
              <th>Type</th>
              <SortHeader label="Status" k="pipelineStatus" />
              <th>Novelty</th>
              <th>Feasibility</th>
              <th>Completeness</th>
              <th>Tech Depth</th>
              <th>Clarity</th>
              <SortHeader label="Overall" k="overallScore" />
            </tr>
          </thead>
          <tbody>
            {sorted.map(p => (
              <tr key={p.projectId}>
                <td>
                  <div>
                    <p className="font-medium text-slate-800">{p.studentName}</p>
                    <p className="text-xs text-slate-400">{p.rollNo}</p>
                  </div>
                </td>
                <td>
                  <p className="text-slate-700 text-sm max-w-[180px] truncate" title={p.title}>{p.title}</p>
                </td>
                <td><Badge type="domain" value={p.domain} size="sm" /></td>
                <td><Badge type="submission" value={p.submissionType} size="sm" /></td>
                <td><Badge type="pipeline" value={p.pipelineStatus} size="sm" /></td>
                {/* Mock dimension scores since ProjectSummary doesn't have them individually */}
                {[78, 85, 79, 82, 76].map((score, i) => (
                  <td key={i}>
                    <span className={clsx('font-semibold text-sm',
                      score >= 80 ? 'text-teal-600' : score >= 60 ? 'text-gold-500' : 'text-red-500'
                    )}>
                      {p.overallScore !== null ? score : '—'}
                    </span>
                  </td>
                ))}
                <td>
                  {p.overallScore !== null ? (
                    <div className={clsx(
                      'inline-flex items-center justify-center w-10 h-10 rounded-xl font-bold text-sm',
                      p.overallScore >= 80 ? 'bg-teal-50 text-teal-700' :
                      p.overallScore >= 60 ? 'bg-gold-50 text-gold-700' : 'bg-red-50 text-red-700'
                    )}>
                      {p.overallScore}
                    </div>
                  ) : <span className="text-slate-300">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComparisonTable;
