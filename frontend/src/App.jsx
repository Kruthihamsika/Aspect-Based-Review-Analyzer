import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import DatasetLibrary from "./pages/DatasetLibrary";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DatasetLibrary />} />
        <Route path="/dashboard/:uploadId" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
