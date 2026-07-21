import React, { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { uploadBatch, getBatchStatus } from '../../api/endpoints';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../../components/FileUploader';
import Badge from '../../components/Badge';
import { Package, CheckCircle, Loader2, Cpu } from 'lucide-react';
import type { BatchJobStatus } from '../../types';

const UploadBatch: React.FC = () => {
  const navigate = useNavigate();
  const [batchId, setBatchId] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [batchStatus, setBatchStatus] = useState<BatchJobStatus | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const uploadMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      files.forEach(f => fd.append('files', f));
      return uploadBatch(fd);
    },
    onSuccess: ({ batchId: id }) => {
      setBatchId(id);
    },
  });

  // Poll batch status
  useEffect(() => {
    if (!batchId) return;
    pollingRef.current = setInterval(async () => {
      const status = await getBatchStatus(batchId);
      setBatchStatus(status);
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(pollingRef.current!);
      }
    }, 2000);
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, [batchId]);

  const progressPct = batchStatus ? Math.round((batchStatus.processed / batchStatus.totalFiles) * 100) : 0;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-navy-900">Batch Upload</h1>
        <p className="text-slate-500 mt-1">Upload 30–60 project files at once for bulk AI evaluation via the Celery queue</p>
      </div>

      {!batchId ? (
        <div className="card space-y-6">
          <div className="bg-teal-50 rounded-xl p-4 border border-teal-100">
            <p className="text-sm text-teal-700 font-medium">💡 Batch upload guidelines:</p>
            <ul className="text-xs text-teal-600 mt-2 space-y-1 list-disc list-inside">
              <li>Upload PDF, DOCX, or PPTX files — one per student</li>
              <li>Files are processed via a Celery task queue asynchronously</li>
              <li>You'll see a live progress bar as each file completes</li>
              <li>Recommended: 30–60 files per batch for optimal performance</li>
            </ul>
          </div>

          <FileUploader
            accept={['.pdf', '.docx', '.pptx']}
            multiple
            maxSize={50}
            onFilesSelected={setFiles}
            label="Drop all project files here (30–60 files)"
            hint="PDF, DOCX, PPTX · Up to 60 files per batch"
          />

          <button
            onClick={() => uploadMutation.mutate()}
            disabled={uploadMutation.isPending || files.length === 0}
            className="btn-primary w-full justify-center py-3"
          >
            {uploadMutation.isPending
              ? <><Loader2 size={16} className="animate-spin" /> Submitting to Queue...</>
              : <><Package size={16} /> Submit {files.length > 0 ? `${files.length} files` : 'Batch'} for Processing</>}
          </button>
        </div>
      ) : (
        <div className="card space-y-6">
          <div className="flex items-center gap-3">
            {batchStatus?.status === 'completed' ? (
              <div className="w-12 h-12 rounded-xl bg-teal-50 flex items-center justify-center">
                <CheckCircle size={24} className="text-teal-500" />
              </div>
            ) : (
              <div className="w-12 h-12 rounded-xl bg-navy-50 flex items-center justify-center">
                <Cpu size={24} className="text-navy-900 animate-pulse-soft" />
              </div>
            )}
            <div>
              <h2 className="font-semibold text-navy-900">
                {batchStatus?.status === 'completed' ? 'Batch Processing Complete!' : 'Processing Batch...'}
              </h2>
              <p className="text-sm text-slate-500">
                {batchStatus ? `${batchStatus.processed} / ${batchStatus.totalFiles} files processed` : 'Starting Celery queue...'}
              </p>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
              <span>Progress</span>
              <span>{progressPct}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3">
              <div
                className="bg-teal-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>

          {batchStatus && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 text-center">
                <p className="text-2xl font-bold text-navy-900">{batchStatus.totalFiles}</p>
                <p className="text-xs text-slate-400">Total Files</p>
              </div>
              <div className="bg-teal-50 rounded-xl p-3 border border-teal-100 text-center">
                <p className="text-2xl font-bold text-teal-700">{batchStatus.processed}</p>
                <p className="text-xs text-teal-500">Processed</p>
              </div>
              <div className="bg-red-50 rounded-xl p-3 border border-red-100 text-center">
                <p className="text-2xl font-bold text-red-700">{batchStatus.failed}</p>
                <p className="text-xs text-red-500">Failed</p>
              </div>
            </div>
          )}

          {batchStatus?.status === 'completed' && (
            <div className="flex gap-3">
              <button onClick={() => navigate('/faculty/comparison')} className="btn-primary">
                View Comparison Table
              </button>
              <button onClick={() => { setBatchId(null); setBatchStatus(null); setFiles([]); }} className="btn-outline">
                Upload Another Batch
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadBatch;
