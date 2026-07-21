import React from 'react';
import clsx from 'clsx';

interface ScoreGaugeProps {
  value: number;
  size?: number;
  strokeWidth?: number;
  showGrade?: boolean;
  grade?: string;
  label?: string;
}

const getScoreColor = (value: number): string => {
  if (value >= 80) return '#1E7F72';  // teal
  if (value >= 60) return '#C99A3A';  // gold
  return '#ef4444';                    // red
};

const getGradeBg = (grade: string): string => {
  if (['A+', 'A', 'A-'].includes(grade)) return 'text-teal-600';
  if (['B+', 'B', 'B-'].includes(grade)) return 'text-gold-500';
  return 'text-red-500';
};

const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  value,
  size = 160,
  strokeWidth = 12,
  showGrade = true,
  grade,
  label = 'Overall Score',
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;
  // We show 270-degree arc (from -225deg to 45deg)
  const arcFraction = 0.75;
  const progress = Math.min(Math.max(value, 0), 100) / 100;
  const dashArray = circumference * arcFraction;
  const dashOffset = dashArray * (1 - progress);
  const color = getScoreColor(value);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-[135deg]">
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
            strokeDasharray={`${dashArray} ${circumference}`}
            strokeLinecap="round"
          />
          {/* Progress arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${dashArray - dashOffset} ${circumference}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold font-display" style={{ color }}>
            {value}
          </span>
          {showGrade && grade && (
            <span className={clsx('text-sm font-semibold', getGradeBg(grade))}>
              Grade {grade}
            </span>
          )}
        </div>
      </div>
      {label && <p className="text-xs text-slate-500 font-medium">{label}</p>}
    </div>
  );
};

export default ScoreGauge;
