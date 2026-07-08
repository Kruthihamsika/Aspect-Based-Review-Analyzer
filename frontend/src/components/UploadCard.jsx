import {
  AlertCircle,
  CheckCircle2,
  FileText,
  Loader2,
  UploadCloud,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import api from "../api/api";

function UploadCard({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);

  useEffect(() => {
    return () => {
      if (toastTimer.current) {
        clearTimeout(toastTimer.current);
      }
    };
  }, []);

  const showToast = (type, message) => {
    setToast({ type, message });

    if (toastTimer.current) {
      clearTimeout(toastTimer.current);
    }

    toastTimer.current = setTimeout(() => {
      setToast(null);
    }, 3500);
  };

  const selectFile = (selectedFile) => {
    if (!selectedFile) {
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      showToast("error", "Please choose a CSV file.");
      return;
    }

    setFile(selectedFile);
    setUploadProgress(0);
  };

  const uploadFile = async () => {
    if (!file) {
      showToast("error", "Choose a CSV file before uploading.");
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (!progressEvent.total) {
            return;
          }

          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );

          setUploadProgress(percent);
        },
      });

      setUploadProgress(100);
      setFile(null);
      showToast(
        "success",
        response.data.message || "Dataset uploaded successfully."
      );
      onUploadSuccess?.();
    } catch (err) {
      console.log(err);
      showToast("error", "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    selectFile(event.dataTransfer.files[0]);
  };

  return (
    <div className="relative mb-8 rounded-xl bg-white p-8 shadow-lg">
      {toast && (
        <div
          className={`absolute right-6 top-6 z-10 flex max-w-sm items-start gap-3 rounded-xl border px-4 py-3 shadow-lg ${
            toast.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-rose-200 bg-rose-50 text-rose-800"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircle2 size={20} />
          ) : (
            <AlertCircle size={20} />
          )}

          <p className="text-sm font-semibold">{toast.message}</p>

          <button
            type="button"
            onClick={() => setToast(null)}
            className="ml-1 rounded-full bg-transparent p-0 text-current shadow-none hover:bg-transparent"
            aria-label="Dismiss notification"
          >
            <X size={16} />
          </button>
        </div>
      )}

      <div className="flex items-center gap-3">
        <UploadCloud size={35} />

        <h2 className="text-2xl font-bold">Upload Review Dataset</h2>
      </div>

      <label
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/60"
        }`}
      >
        <UploadCloud className="text-blue-600" size={42} />

        <span className="mt-4 text-base font-semibold text-slate-900">
          Drag and drop your CSV file here
        </span>

        <span className="mt-1 text-sm text-slate-500">
          or click to browse from your computer
        </span>

        <input
          type="file"
          accept=".csv"
          onChange={(event) => selectFile(event.target.files[0])}
          className="sr-only"
        />
      </label>

      {file && (
        <div className="mt-5 flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <FileText className="text-blue-600" size={22} />

          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-900">
              {file.name}
            </p>

            <p className="text-xs text-slate-500">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
      )}

      {isUploading && (
        <div className="mt-5">
          <div className="mb-2 flex items-center justify-between text-sm font-semibold text-slate-600">
            <span>Uploading</span>
            <span>{uploadProgress}%</span>
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-blue-600 transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      <button
        onClick={uploadFile}
        disabled={isUploading}
        className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {isUploading && <Loader2 className="animate-spin" size={18} />}
        {isUploading ? "Uploading..." : "Upload CSV"}
      </button>
    </div>
  );
}

export default UploadCard;
