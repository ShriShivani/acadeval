import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, Video, Film, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'done' | 'error';
}

interface FileUploaderProps {
  accept?: string[];
  multiple?: boolean;
  maxSize?: number; // MB
  onFilesSelected?: (files: File[]) => void;
  label?: string;
  hint?: string;
  className?: string;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  'application/pdf': <FileText size={20} className="text-red-500" />,
  'video/mp4': <Video size={20} className="text-purple-500" />,
  'video/quicktime': <Film size={20} className="text-purple-500" />,
  default: <FileText size={20} className="text-teal-500" />,
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const FileUploader: React.FC<FileUploaderProps> = ({
  accept = ['.pdf', '.docx', '.pptx'],
  multiple = false,
  maxSize = 50,
  onFilesSelected,
  label = 'Drop files here or click to browse',
  hint,
  className,
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFiles = useCallback((newFiles: File[]) => {
    setError(null);
    const valid: File[] = [];
    for (const file of newFiles) {
      if (file.size > maxSize * 1024 * 1024) {
        setError(`"${file.name}" exceeds the ${maxSize}MB size limit.`);
        continue;
      }
      valid.push(file);
    }
    if (!valid.length) return;

    const uploadedFiles: UploadedFile[] = valid.map(f => ({
      file: f,
      id: `${f.name}-${Date.now()}`,
      progress: 0,
      status: 'pending',
    }));

    setFiles(prev => multiple ? [...prev, ...uploadedFiles] : uploadedFiles);
    onFilesSelected?.(valid);

    // Simulate upload progress
    uploadedFiles.forEach(uf => {
      let prog = 0;
      const interval = setInterval(() => {
        prog += Math.random() * 20;
        if (prog >= 100) {
          prog = 100;
          clearInterval(interval);
          setFiles(prev => prev.map(f => f.id === uf.id ? { ...f, progress: 100, status: 'done' } : f));
        } else {
          setFiles(prev => prev.map(f => f.id === uf.id ? { ...f, progress: Math.floor(prog), status: 'uploading' } : f));
        }
      }, 150);
    });
  }, [maxSize, multiple, onFilesSelected]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    processFiles(Array.from(e.dataTransfer.files));
  }, [processFiles]);

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  return (
    <div className={clsx('space-y-3', className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
        className={clsx(
          'relative border-2 border-dashed rounded-2xl p-10 cursor-pointer transition-all duration-200',
          'flex flex-col items-center justify-center text-center gap-3',
          isDragging
            ? 'border-teal-400 bg-teal-50'
            : 'border-slate-200 bg-slate-50/50 hover:border-teal-300 hover:bg-teal-50/30'
        )}
      >
        <div className={clsx(
          'w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-200',
          isDragging ? 'bg-teal-100' : 'bg-white shadow-sm'
        )}>
          <Upload size={24} className={isDragging ? 'text-teal-600' : 'text-slate-400'} />
        </div>
        <div>
          <p className="font-semibold text-slate-700">{label}</p>
          <p className="text-sm text-slate-500 mt-1">
            {hint || `Accepted: ${accept.join(', ')} • Max size: ${maxSize}MB`}
          </p>
        </div>
        <input
          id="file-input"
          type="file"
          className="hidden"
          accept={accept.join(',')}
          multiple={multiple}
          onChange={(e) => processFiles(Array.from(e.target.files || []))}
        />
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 px-4 py-3 rounded-xl border border-red-100">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map(uf => (
            <div key={uf.id} className="bg-white rounded-xl border border-slate-100 p-3 flex items-center gap-3">
              {ICON_MAP[uf.file.type] || ICON_MAP.default}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-medium text-slate-700 truncate">{uf.file.name}</p>
                  <span className="text-xs text-slate-400 ml-2 flex-shrink-0">{formatFileSize(uf.file.size)}</span>
                </div>
                {uf.status === 'uploading' && (
                  <div className="w-full bg-slate-100 rounded-full h-1.5">
                    <div
                      className="bg-teal-500 h-1.5 rounded-full transition-all duration-200"
                      style={{ width: `${uf.progress}%` }}
                    />
                  </div>
                )}
                {uf.status === 'done' && (
                  <p className="text-xs text-teal-600 flex items-center gap-1"><CheckCircle size={11} /> Ready</p>
                )}
              </div>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); removeFile(uf.id); }}
                className="p-1 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
