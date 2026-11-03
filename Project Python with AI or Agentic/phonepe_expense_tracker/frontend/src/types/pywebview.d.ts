import { AnalysisReport } from "./expense";

export interface PyWebViewApi {
  get_initial_data: () => Promise<AnalysisReport>;
  analyze_file_path: (filePath: string) => Promise<AnalysisReport>;
  analyze_raw_text: (content: string, filename?: string) => Promise<AnalysisReport>;
  open_file_dialog: () => Promise<AnalysisReport>;
  update_budget_limit: (monthlyLimit: number, yearlyLimit?: number) => Promise<AnalysisReport>;
  add_category_keyword: (category: string, keyword: string) => Promise<AnalysisReport>;
  minimize_window: () => Promise<void>;
  maximize_window: () => Promise<void>;
  close_window: () => Promise<void>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };
  }
}
