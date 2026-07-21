import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, Title, Tooltip, Legend, Filler,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import type { SemesterBenchmark } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler);

interface TrendChartProps {
  data: { month: string; avgScore: number }[];
  title?: string;
}

interface BenchmarkChartProps {
  benchmarks: SemesterBenchmark[];
  metric?: keyof Omit<SemesterBenchmark, 'semester' | 'year' | 'totalProjects'>;
}

const chartFont = { family: 'Inter' };
const tooltipStyle = {
  backgroundColor: '#1B2A4A',
  titleFont: chartFont,
  bodyFont: chartFont,
  padding: 10,
};

export const TrendChart: React.FC<TrendChartProps> = ({ data, title = 'Score Trend' }) => {
  const labels = data.map(d => d.month);
  const values = data.map(d => d.avgScore);

  const chartData = {
    labels,
    datasets: [{
      label: 'Avg Score',
      data: values,
      borderColor: '#1E7F72',
      backgroundColor: 'rgba(30, 127, 114, 0.1)',
      borderWidth: 2.5,
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#1E7F72',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 5,
    }],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: !!title, text: title, font: { ...chartFont, size: 14 }, color: '#334155' },
      tooltip: tooltipStyle,
    },
    scales: {
      y: {
        min: 50,
        max: 100,
        ticks: { font: { size: 11 }, color: '#94a3b8' },
        grid: { color: 'rgba(148, 163, 184, 0.15)' },
      },
      x: {
        ticks: { font: { size: 11 }, color: '#94a3b8' },
        grid: { display: false },
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export const BenchmarkChart: React.FC<BenchmarkChartProps> = ({
  benchmarks,
  metric = 'avgOverall',
}) => {
  const labels = benchmarks.map(b => `${b.semester} ${b.year}`);
  const values = benchmarks.map(b => b[metric] as number);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Dept. Average',
        data: values,
        backgroundColor: 'rgba(30, 127, 114, 0.7)',
        borderRadius: 8,
        borderSkipped: false,
      },
      {
        label: 'Top Score',
        data: benchmarks.map(b => b.topScore),
        backgroundColor: 'rgba(201, 154, 58, 0.7)',
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: { font: chartFont, color: '#475569' },
      },
      tooltip: tooltipStyle,
    },
    scales: {
      y: {
        min: 40,
        max: 100,
        ticks: { font: { size: 11 }, color: '#94a3b8' },
        grid: { color: 'rgba(148, 163, 184, 0.15)' },
      },
      x: {
        ticks: { font: { size: 11 }, color: '#94a3b8' },
        grid: { display: false },
      },
    },
  };

  return <Bar data={chartData} options={options} />;
};
