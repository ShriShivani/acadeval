import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { generateVivaQuestions, submitVivaAnswer } from '../../api/endpoints';
import { LoadingState } from '../../components/States';
import type { VivaQuestion, VivaAnswerResult } from '../../types';
import {
  BookOpen, ChevronRight, CheckCircle, Star, Brain,
  RotateCcw, Trophy, Loader2,
} from 'lucide-react';
import clsx from 'clsx';

const DIFFICULTY_COLORS = {
  Easy: 'badge-teal',
  Medium: 'badge-gold',
  Hard: 'badge-red',
};

const ScoreDots: React.FC<{ score: number; max?: number }> = ({ score, max = 5 }) => (
  <div className="flex gap-1.5">
    {Array.from({ length: max }).map((_, i) => (
      <div
        key={i}
        className={clsx(
          'w-3 h-3 rounded-full',
          i < score ? 'bg-teal-500' : 'bg-slate-200'
        )}
      />
    ))}
  </div>
);

const VivaSimulation: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const projectId = searchParams.get('projectId') || 'p001';

  const [sessionId] = useState(`session_${Date.now()}`);
  const [questions, setQuestions] = useState<VivaQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [answers, setAnswers] = useState<VivaAnswerResult[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);

  const submitMutation = useMutation({
    mutationFn: () => submitVivaAnswer(sessionId, questions[currentIndex].questionId, answer),
    onSuccess: (result) => {
      setAnswers(prev => [...prev, result]);
      setAnswer('');
      if (currentIndex + 1 >= questions.length) {
        setIsComplete(true);
      } else {
        setCurrentIndex(i => i + 1);
      }
    },
  });

  const handleStart = async () => {
    setIsLoadingQuestions(true);
    try {
      const qs = await generateVivaQuestions(projectId);
      setQuestions(qs);
      setIsStarted(true);
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  const totalScore = answers.reduce((sum, a) => sum + a.score, 0);
  const maxScore = answers.length * 5;
  const percentage = maxScore > 0 ? Math.round((totalScore / maxScore) * 100) : 0;

  if (!isStarted) {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <div className="card text-center py-12">
          <div className="w-20 h-20 bg-navy-50 rounded-full flex items-center justify-center mx-auto mb-5">
            <Brain size={36} className="text-navy-900" />
          </div>
          <h1 className="text-2xl font-display font-bold text-navy-900 mb-2">Viva Simulation</h1>
          <p className="text-slate-500 mb-6 max-w-md mx-auto">
            The AI has generated 10 viva questions from your project. Answer each one and receive a 0–5 score with feedback.
          </p>

          <div className="grid grid-cols-3 gap-4 mb-8 text-sm">
            {[
              { icon: <BookOpen size={20} />, label: '10 Questions', sub: 'Based on your project' },
              { icon: <Star size={20} />, label: '0–5 Per Answer', sub: 'Scored by AI' },
              { icon: <CheckCircle size={20} />, label: 'Full Summary', sub: 'With key points' },
            ].map(item => (
              <div key={item.label} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                <div className="flex items-center justify-center text-teal-500 mb-2">{item.icon}</div>
                <p className="font-semibold text-slate-700">{item.label}</p>
                <p className="text-xs text-slate-400 mt-0.5">{item.sub}</p>
              </div>
            ))}
          </div>

          <button onClick={handleStart} disabled={isLoadingQuestions} className="btn-navy px-8 py-3 text-base">
            {isLoadingQuestions ? <><Loader2 size={18} className="animate-spin" /> Generating Questions...</> : <>Start Viva <ChevronRight size={18} /></>}
          </button>
        </div>
      </div>
    );
  }

  if (isComplete) {
    const grade = percentage >= 80 ? 'Excellent' : percentage >= 60 ? 'Good' : percentage >= 40 ? 'Average' : 'Needs Practice';
    const gradeColor = percentage >= 80 ? 'text-teal-600' : percentage >= 60 ? 'text-gold-500' : 'text-red-500';

    return (
      <div className="max-w-3xl mx-auto mt-8 space-y-6">
        <div className="card text-center py-10">
          <Trophy size={48} className="text-gold-500 mx-auto mb-4" />
          <h2 className="text-2xl font-display font-bold text-navy-900 mb-1">Viva Complete!</h2>
          <p className={clsx('text-4xl font-display font-bold mt-4', gradeColor)}>
            {totalScore}/{maxScore}
          </p>
          <p className="text-xl text-slate-500 mt-1">{percentage}% — {grade}</p>
          <div className="flex gap-3 justify-center mt-6">
            <button onClick={() => navigate('/student/reports')} className="btn-primary">Back to Reports</button>
            <button onClick={() => { setIsStarted(false); setAnswers([]); setCurrentIndex(0); setIsComplete(false); }} className="btn-outline">
              <RotateCcw size={15} /> Retry
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {questions.map((q, i) => {
            const ans = answers[i];
            if (!ans) return null;
            return (
              <div key={q.questionId} className="card">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-slate-400">Q{i + 1}</span>
                      <span className={clsx('badge', DIFFICULTY_COLORS[q.difficulty])}>{q.difficulty}</span>
                      <span className="badge badge-slate">{q.category}</span>
                    </div>
                    <p className="text-sm font-medium text-slate-800">{q.text}</p>
                  </div>
                  <div className="flex-shrink-0 text-center">
                    <p className={clsx('text-2xl font-bold font-display',
                      ans.score >= 4 ? 'text-teal-600' : ans.score >= 2 ? 'text-gold-500' : 'text-red-500'
                    )}>{ans.score}<span className="text-sm font-normal text-slate-400">/5</span></p>
                    <ScoreDots score={ans.score} />
                  </div>
                </div>
                <p className="text-sm text-slate-500 italic border-t border-slate-50 pt-3">{ans.feedback}</p>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  const progress = ((currentIndex) / questions.length) * 100;

  return (
    <div className="max-w-2xl mx-auto mt-8 space-y-5">
      {/* Progress */}
      <div className="card py-4">
        <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
          <span>Question {currentIndex + 1} of {questions.length}</span>
          <span>{Math.round(progress)}% complete</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-2">
          <div className="bg-teal-500 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Question */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <span className={clsx('badge', DIFFICULTY_COLORS[currentQ.difficulty])}>{currentQ.difficulty}</span>
          <span className="badge badge-slate">{currentQ.category}</span>
        </div>
        <p className="text-lg font-semibold text-navy-900 leading-relaxed mb-6">{currentQ.text}</p>

        <label className="label">Your Answer</label>
        <textarea
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          rows={6}
          className="input resize-none"
          placeholder="Type your answer here. Be specific and reference your project where applicable..."
        />

        <button
          onClick={() => submitMutation.mutate()}
          disabled={submitMutation.isPending || answer.trim().length < 10}
          className="btn-primary w-full justify-center mt-4 py-3"
        >
          {submitMutation.isPending
            ? <><Loader2 size={16} className="animate-spin" /> Evaluating...</>
            : currentIndex + 1 === questions.length ? 'Submit Final Answer' : <>Submit & Next <ChevronRight size={16} /></>}
        </button>

        {/* Last answer result */}
        {answers.length > 0 && !submitMutation.isPending && (
          <div className="mt-4 bg-slate-50 rounded-xl border border-slate-100 p-4 animate-fade-in">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold text-slate-500">PREVIOUS ANSWER FEEDBACK</p>
              <div className="flex items-center gap-2">
                <p className="font-bold text-teal-700">{answers[answers.length - 1].score}/5</p>
                <ScoreDots score={answers[answers.length - 1].score} />
              </div>
            </div>
            <p className="text-sm text-slate-600">{answers[answers.length - 1].feedback}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VivaSimulation;
