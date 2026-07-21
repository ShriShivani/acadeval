import apiClient from './client';
import type {
  LoginRequest, LoginResponse, ProjectSummary, PublicEvaluationReport,
  InternalEvaluationReport, VivaQuestion, VivaAnswerResult, Appeal,
  Rubric, LeaderboardEntry, BatchJobStatus, SemesterBenchmark,
  FacultyDashboardStats, HODDeptStats, User, SubmissionType,
} from '../types';
import {
  mockProjects, mockPublicReport, mockInternalReport, mockLeaderboard,
  mockVivaQuestions, mockVivaAnswer, mockAppeals, mockFacultyDashboard,
  mockRubric, mockBenchmarks, mockHODStats, mockUsers,
} from './mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 600) => new Promise(res => setTimeout(res, ms));

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const login = async (req: LoginRequest): Promise<LoginResponse> => {
  if (USE_MOCK) {
    await delay(800);
    const roleTokens: Record<string, string> = {
      student: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1MDAxIiwicm9sZSI6InN0dWRlbnQiLCJuYW1lIjoiUHJpeWEgU2hhcm1hIiwiZW1haWwiOiJwcml5YUBjb2xsZWdlLmVkdSIsImV4cCI6OTk5OTk5OTk5OX0.mock',
      guide: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDAxIiwicm9sZSI6Imd1aWRlIiwibmFtZSI6IkRyLiBNZWVyYSBLcmlzaG5hbiIsImVtYWlsIjoibWVlcmFAY29sbGVnZS5lZHUiLCJleHAiOjk5OTk5OTk5OTl9.mock',
      reviewer: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDAyIiwicm9sZSI6InJldmlld2VyIiwibmFtZSI6IlByb2YuIFN1cmVzaCBSYWphbiIsImVtYWlsIjoic3VyZXNoQGNvbGxlZ2UuZWR1IiwiZXhwIjo5OTk5OTk5OTk5fQ.mock',
      hod: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoMDAxIiwicm9sZSI6ImhvZCIsIm5hbWUiOiJEci4gQW5hbmQgS3Jpc2huYW11cnRoeSIsImVtYWlsIjoiaG9kQGNvbGxlZ2UuZWR1IiwiZXhwIjo5OTk5OTk5OTk5fQ.mock',
    };
    const userMap = {
      student: { id: 'u001', name: 'Priya Sharma', email: 'priya@college.edu', role: 'student' as const },
      guide: { id: 'f001', name: 'Dr. Meera Krishnan', email: 'meera@college.edu', role: 'guide' as const },
      reviewer: { id: 'f002', name: 'Prof. Suresh Rajan', email: 'suresh@college.edu', role: 'reviewer' as const },
      hod: { id: 'h001', name: 'Dr. Anand Krishnamurthy', email: 'hod@college.edu', role: 'hod' as const },
    };
    return { access_token: roleTokens[req.role], token_type: 'bearer', user: userMap[req.role] };
  }
  const { data } = await apiClient.post<LoginResponse>('/auth/login', req);
  return data;
};

// ─── Projects ─────────────────────────────────────────────────────────────────
export const getMyProjects = async (): Promise<ProjectSummary[]> => {
  if (USE_MOCK) { await delay(); return mockProjects.filter(p => p.rollNo === 'CS2021001'); }
  const { data } = await apiClient.get<ProjectSummary[]>('/projects/my');
  return data;
};

export const getAllProjects = async (): Promise<ProjectSummary[]> => {
  if (USE_MOCK) { await delay(); return mockProjects; }
  const { data } = await apiClient.get<ProjectSummary[]>('/projects');
  return data;
};

export const getProjectStatus = async (projectId: string): Promise<{ status: string }> => {
  if (USE_MOCK) {
    await delay(300);
    const p = mockProjects.find(x => x.projectId === projectId);
    return { status: p?.pipelineStatus || 'uploaded' };
  }
  const { data } = await apiClient.get(`/projects/${projectId}/status`);
  return data;
};

export const uploadProject = async (formData: FormData): Promise<{ projectId: string }> => {
  if (USE_MOCK) {
    await delay(1200);
    const mode = (formData.get('mode') as SubmissionType) || 'document';
    const domain = (formData.get('domain') as string) || 'AI/ML';
    
    // Find uploaded file name if any
    const files = formData.getAll('files') as File[];
    const fileName = files[0]?.name;
    const defaultTitle = mode === 'video' ? 'Video Presentation Analysis' : 'Submitted Project Report';
    const title = (formData.get('title') as string) || fileName || defaultTitle;
    const projectId = `p_${Date.now()}`;

    mockProjects.unshift({
      projectId,
      studentName: 'Priya Sharma',
      rollNo: 'CS2021001',
      title,
      submissionType: mode,
      domain,
      submittedOn: new Date().toISOString().split('T')[0],
      pipelineStatus: 'awaiting_review',
      overallScore: 82,
    });

    return { projectId };
  }
  const { data } = await apiClient.post('/projects/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

// ─── Evaluation Report ────────────────────────────────────────────────────────
// CRITICAL: branches on role — student routes NEVER call the internal endpoint
export const getEvaluationReport = async (
  projectId: string,
  role: string
): Promise<PublicEvaluationReport | InternalEvaluationReport> => {
  if (USE_MOCK) {
    await delay();
    const p = mockProjects.find(x => x.projectId === projectId);
    const title = p ? p.title : mockPublicReport.title;
    const domain = p ? p.domain : mockPublicReport.domain;
    const mode = p ? p.submissionType : mockPublicReport.submissionType;
    const isAbstract = mode === 'abstract';

    const overallScore = p && p.overallScore !== null ? p.overallScore : mockPublicReport.overallScore;
    const grade = overallScore >= 90 ? 'A+' : overallScore >= 80 ? 'A' : overallScore >= 70 ? 'B' : 'C';

    const baseReport: PublicEvaluationReport = {
      ...mockPublicReport,
      projectId,
      title,
      domain,
      submissionType: mode,
      overallScore,
      grade,
      dimensionScores: {
        ...mockPublicReport.dimensionScores,
        completeness: isAbstract ? null : mockPublicReport.dimensionScores.completeness,
      },
    };

    if (role === 'student') return baseReport;
    return {
      ...mockInternalReport,
      ...baseReport,
      facultyNotes: [...mockInternalReport.facultyNotes],
    };
  }
  if (role === 'student') {
    const { data } = await apiClient.get<PublicEvaluationReport>(`/projects/${projectId}/report/public`);
    return data;
  }
  const { data } = await apiClient.get<InternalEvaluationReport>(`/projects/${projectId}/report/internal`);
  return data;
};

// ─── Review Actions ────────────────────────────────────────────────────────────
export const overrideScore = async (
  projectId: string,
  dimension: string,
  newValue: number,
  comment: string
): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.patch(`/projects/${projectId}/scores`, { dimension, newValue, comment });
};

export const addFacultyNote = async (projectId: string, text: string): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.post(`/projects/${projectId}/notes`, { text });
};

export const publishReview = async (projectId: string): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.post(`/projects/${projectId}/publish`);
};

// ─── Viva ─────────────────────────────────────────────────────────────────────
export const generateVivaQuestions = async (projectId: string): Promise<VivaQuestion[]> => {
  if (USE_MOCK) { await delay(1000); return mockVivaQuestions; }
  const { data } = await apiClient.post<VivaQuestion[]>('/viva/generate', { projectId });
  return data;
};

export const submitVivaAnswer = async (
  sessionId: string,
  questionId: string,
  answer: string
): Promise<VivaAnswerResult> => {
  if (USE_MOCK) { await delay(800); return mockVivaAnswer(questionId, answer); }
  const { data } = await apiClient.post<VivaAnswerResult>('/viva/answer', { sessionId, questionId, answer });
  return data;
};

// ─── Appeals ─────────────────────────────────────────────────────────────────
export const getMyAppeals = async (): Promise<Appeal[]> => {
  if (USE_MOCK) { await delay(); return mockAppeals; }
  const { data } = await apiClient.get<Appeal[]>('/appeals/my');
  return data;
};

export const getAllAppeals = async (): Promise<Appeal[]> => {
  if (USE_MOCK) { await delay(); return mockAppeals; }
  const { data } = await apiClient.get<Appeal[]>('/appeals');
  return data;
};

export const submitAppeal = async (
  projectId: string,
  dimension: string,
  justification: string
): Promise<{ appealId: string }> => {
  if (USE_MOCK) { await delay(); return { appealId: `ap_${Date.now()}` }; }
  const { data } = await apiClient.post('/appeals', { projectId, dimension, justification });
  return data;
};

export const resolveAppeal = async (
  appealId: string,
  action: 'approve' | 'reject' | 'override',
  newScore?: number,
  response?: string
): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.patch(`/appeals/${appealId}`, { action, newScore, response });
};

// ─── Rubrics ─────────────────────────────────────────────────────────────────
export const getRubrics = async (): Promise<Rubric[]> => {
  if (USE_MOCK) { await delay(); return [mockRubric]; }
  const { data } = await apiClient.get<Rubric[]>('/rubrics');
  return data;
};

export const createRubric = async (rubric: Omit<Rubric, 'rubricId' | 'createdAt'>): Promise<Rubric> => {
  if (USE_MOCK) { await delay(); return { ...rubric, rubricId: `r_${Date.now()}`, createdAt: new Date().toISOString() }; }
  const { data } = await apiClient.post<Rubric>('/rubrics', rubric);
  return data;
};

export const approveRubric = async (rubricId: string): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.post(`/rubrics/${rubricId}/approve`);
};

// ─── Leaderboard ─────────────────────────────────────────────────────────────
export const getLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  if (USE_MOCK) { await delay(); return mockLeaderboard; }
  const { data } = await apiClient.get<LeaderboardEntry[]>('/leaderboard');
  return data;
};

// ─── Batch Upload ─────────────────────────────────────────────────────────────
export const uploadBatch = async (formData: FormData): Promise<{ batchId: string }> => {
  if (USE_MOCK) { await delay(1500); return { batchId: `batch_${Date.now()}` }; }
  const { data } = await apiClient.post('/projects/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const getBatchStatus = async (batchId: string): Promise<BatchJobStatus> => {
  if (USE_MOCK) {
    await delay(400);
    return {
      batchId,
      totalFiles: 12,
      processed: Math.min(12, Math.floor(Date.now() / 1000) % 13),
      failed: 0,
      status: 'processing',
      startedAt: new Date().toISOString(),
      projects: mockProjects,
    };
  }
  const { data } = await apiClient.get<BatchJobStatus>(`/batch/${batchId}/status`);
  return data;
};

// ─── Benchmarking ────────────────────────────────────────────────────────────
export const getBenchmarks = async (): Promise<SemesterBenchmark[]> => {
  if (USE_MOCK) { await delay(); return mockBenchmarks; }
  const { data } = await apiClient.get<SemesterBenchmark[]>('/benchmarks');
  return data;
};

// ─── Faculty Dashboard ────────────────────────────────────────────────────────
export const getFacultyDashboard = async (): Promise<FacultyDashboardStats> => {
  if (USE_MOCK) { await delay(); return mockFacultyDashboard; }
  const { data } = await apiClient.get<FacultyDashboardStats>('/dashboard/faculty');
  return data;
};

// ─── HOD ─────────────────────────────────────────────────────────────────────
export const getHODStats = async (): Promise<HODDeptStats> => {
  if (USE_MOCK) { await delay(); return mockHODStats; }
  const { data } = await apiClient.get<HODDeptStats>('/dashboard/hod');
  return data;
};

export const getUsers = async (): Promise<User[]> => {
  if (USE_MOCK) {
    await delay();
    return [...mockUsers.students, ...mockUsers.faculty, ...mockUsers.hod];
  }
  const { data } = await apiClient.get<User[]>('/users');
  return data;
};

export const updateUserRole = async (userId: string, role: string): Promise<void> => {
  if (USE_MOCK) { await delay(); return; }
  await apiClient.patch(`/users/${userId}`, { role });
};
