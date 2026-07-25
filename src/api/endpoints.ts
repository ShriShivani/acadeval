import apiClient from './client';
import type {
  LoginRequest, LoginResponse, ProjectSummary, PublicEvaluationReport,
  InternalEvaluationReport, VivaQuestion, VivaAnswerResult, Appeal,
  Rubric, LeaderboardEntry, BatchJobStatus, SemesterBenchmark,
  FacultyDashboardStats, HODDeptStats, User, SubmissionType,
} from '../types';
import type { NoveltyReportData } from '../components/NoveltyReportView';
import {
  mockProjects, mockPublicReport, mockInternalReport, mockLeaderboard,
  mockVivaQuestions, mockVivaAnswer, mockAppeals, mockFacultyDashboard,
  mockRubric, mockBenchmarks, mockHODStats, mockUsers, mockNoveltyReport,
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

// ─── AcadEval+ Graph-Based Novelty Engine ─────────────────────────────────────
export const getNoveltyReport = async (projectId: string, abstract: string): Promise<NoveltyReportData> => {
  if (USE_MOCK) { await delay(900); return mockNoveltyReport(projectId); }
  const { data } = await apiClient.get<NoveltyReportData>(`/v1/acadeval/report/${projectId}`, {
    params: { abstract },
  });
  return data;
};

export const submitFacultyNoveltyReview = async (
  projectId: string,
  facultyScore: number,
  systemScore: number,
  overrideReason?: string
): Promise<void> => {
  if (USE_MOCK) { await delay(500); return; }
  await apiClient.post('/v1/acadeval/faculty-review', {
    project_id: projectId,
    faculty_score: facultyScore,
    system_score: systemScore,
    override_reason: overrideReason || null,
  });
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

// ─── Module 3 \u2014 Entity Knowledge Base & Pending Review ─────────────────────────

export const getKnowledgeBase = async (params?: {
  category?: string; search?: string; limit?: number; offset?: number;
}) => {
  if (USE_MOCK) {
    await delay(400);
    // Return a handful of mock KB entries
    const mockKB = [
      { name: 'CNN', category: 'algorithm', aliases: ['Convolutional Neural Network', 'ConvNet'], first_seen_year: 1989 },
      { name: 'YOLO', category: 'algorithm', aliases: ['You Only Look Once'], first_seen_year: 2015 },
      { name: 'TensorFlow', category: 'framework', aliases: ['TF'], first_seen_year: 2015 },
      { name: 'PyTorch', category: 'framework', aliases: [], first_seen_year: 2016 },
      { name: 'COCO', category: 'dataset', aliases: ['MS COCO'], first_seen_year: 2014 },
      { name: 'Raspberry Pi', category: 'hardware', aliases: ['RPi'], first_seen_year: 2012 },
      { name: 'F1-Score', category: 'metric', aliases: ['F1', 'F-measure'], first_seen_year: 1992 },
    ];
    const filtered = mockKB.filter(e =>
      (!params?.category || e.category === params.category) &&
      (!params?.search || e.name.toLowerCase().includes(params.search.toLowerCase()))
    );
    return { total: filtered.length, offset: 0, limit: 100, entries: filtered };
  }
  const { data } = await apiClient.get('/entities/knowledge-base', { params });
  return data;
};

export const getProjectEntities = async (projectId: string) => {
  if (USE_MOCK) {
    await delay(300);
    return {
      project_id: projectId,
      title: 'Sample Project',
      extracted_entities: {
        algorithms: ['CNN', 'SVM'],
        technologies: ['Edge Computing', 'REST API'],
        frameworks: ['TensorFlow'],
        libraries: ['OpenCV', 'NumPy'],
        datasets: ['COCO'],
        applications: ['Medical Diagnosis'],
        hardware: ['Raspberry Pi'],
        metrics: ['F1-Score', 'Accuracy'],
        unmatched_spans: [],
        all_extracted: [],
      },
      has_been_extracted: true,
    };
  }
  const { data } = await apiClient.get(`/entities/project/${projectId}`);
  return data;
};

export const getPendingReviewEntities = async () => {
  if (USE_MOCK) {
    await delay(300);
    return {
      total: 2,
      items: [
        { name: 'EfficientDet', category: 'algorithm', source_project_id: 'mock-proj-001' },
        { name: 'Coral Edge TPU', category: 'hardware', source_project_id: 'mock-proj-002' },
      ],
    };
  }
  const { data } = await apiClient.get('/entities/pending-review');
  return data;
};

export const approveEntityReview = async (name: string, payload: object) => {
  if (USE_MOCK) { await delay(500); return { status: 'approved', entry: { name }, pending_remaining: 1 }; }
  const { data } = await apiClient.post(`/entities/pending-review/${encodeURIComponent(name)}/approve`, payload);
  return data;
};

export const rejectEntityReview = async (name: string) => {
  if (USE_MOCK) { await delay(300); return { status: 'rejected', removed: name, pending_remaining: 1 }; }
  const { data } = await apiClient.post(`/entities/pending-review/${encodeURIComponent(name)}/reject`);
  return data;
};

// ─── Module 4 Knowledge Graph ────────────────────────────────────────────────
export const getGraphSummary = async (refresh = false) => {
  if (USE_MOCK) {
    await delay(300);
    return {
      status: 'ok',
      metrics: {
        nodes_count: 42,
        edges_count: 128,
        density: 0.074,
        node_type_distribution: { Project: 8, Algorithm: 12, Technology: 10, Dataset: 5, Application: 4, Metric: 3 },
        relationship_distribution: { HAS_DOMAIN: 8, USES_ALGORITHM: 24, USES_TECHNOLOGY: 32, CO_OCCURS: 64 },
        top_centrality_nodes: [
          { id: 1, name: 'CNN', type: 'Algorithm', degree: 14, centrality_score: 0.34 },
          { id: 2, name: 'PyTorch', type: 'Technology', degree: 11, centrality_score: 0.26 },
          { id: 3, name: 'Medical Diagnosis', type: 'Application', degree: 9, centrality_score: 0.21 },
        ],
      },
    };
  }
  const { data } = await apiClient.get(`/graph/summary${refresh ? '?refresh=true' : ''}`);
  return data;
};

export const getGraphVisualization = async (limit = 300, nodeTypes?: string) => {
  if (USE_MOCK) {
    await delay(400);
    return {
      status: 'ok',
      total_graph_nodes: 25,
      total_graph_edges: 40,
      returned_nodes: 25,
      returned_links: 40,
      nodes: [
        { id: 1, name: 'Brain MRI Tumor Segmentation', type: 'Project', degree: 8 },
        { id: 2, name: '3D U-Net', type: 'Algorithm', degree: 6 },
        { id: 3, name: 'PyTorch', type: 'Technology', degree: 10 },
        { id: 4, name: 'BraTS 2021', type: 'Dataset', degree: 4 },
        { id: 5, name: 'Dice Score', type: 'Metric', degree: 3 },
        { id: 6, name: 'Oncology Diagnostics', type: 'Application', degree: 5 },
      ],
      links: [
        { source: 1, target: 2, relationship: 'USES_ALGORITHM', confidence: 1.0 },
        { source: 1, target: 3, relationship: 'USES_TECHNOLOGY', confidence: 1.0 },
        { source: 1, target: 4, relationship: 'USES_DATASET', confidence: 1.0 },
        { source: 1, target: 5, relationship: 'EVALUATED_BY', confidence: 1.0 },
        { source: 1, target: 6, relationship: 'TARGETS_APPLICATION', confidence: 1.0 },
        { source: 2, target: 3, relationship: 'CO_OCCURS', confidence: 1.0 },
        { source: 2, target: 4, relationship: 'CO_OCCURS', confidence: 1.0 },
      ],
    };
  }
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit.toString());
  if (nodeTypes) params.append('node_types', nodeTypes);
  const { data } = await apiClient.get(`/graph/visualization?${params.toString()}`);
  return data;
};

export const getNodeNeighborhood = async (query: string, radius = 1) => {
  if (USE_MOCK) {
    await delay(300);
    return {
      status: 'ok',
      target_node: { id: 2, name: '3D U-Net', type: 'Algorithm', degree: 6 },
      radius,
      neighborhood_nodes: 5,
      graph: {
        nodes: [
          { id: 2, name: '3D U-Net', type: 'Algorithm', degree: 6 },
          { id: 1, name: 'Brain MRI Tumor Segmentation', type: 'Project', degree: 8 },
          { id: 3, name: 'PyTorch', type: 'Technology', degree: 10 },
        ],
        links: [
          { source: 1, target: 2, relationship: 'USES_ALGORITHM' },
          { source: 2, target: 3, relationship: 'CO_OCCURS' },
        ],
      },
    };
  }
  const { data } = await apiClient.get(`/graph/node/${encodeURIComponent(query)}?radius=${radius}`);
  return data;
};

export const rebuildKnowledgeGraph = async () => {
  if (USE_MOCK) {
    await delay(600);
    return { status: 'rebuilt', result: { projects_processed: 8, relational_nodes: 42, relational_edges: 128 } };
  }
  const { data } = await apiClient.post('/graph/rebuild');
  return data;
};

