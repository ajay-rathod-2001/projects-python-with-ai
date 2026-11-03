export interface Transaction {
  id: string;
  date: string;
  merchant: string;
  amount: number;
  category: string;
  status: string;
}

export interface SkippedLine {
  line_number: number;
  raw_content: string;
  reason: string;
}

export interface ExpenseForecast {
  daily_average: number;
  projected_3_months: number;
  projected_6_months: number;
  projected_1_year: number;
  projected_2_years: number;
  projected_5_years: number;
}

export interface ExpenseSummary {
  total_spent: number;
  budget_limit: number;                    // Monthly budget limit
  yearly_budget_limit: number;             // Yearly budget limit
  is_over_budget: boolean;                 // Monthly breach
  over_budget_amount: number;
  utilization_percentage: number;
  is_over_yearly_budget: boolean;          // Yearly breach
  yearly_over_budget_amount: number;
  yearly_utilization_percentage: number;
  category_totals: Record<string, number>;
  top_category: string;
  top_category_amount: number;
  monthly_breakdown: Record<string, number>;
  yearly_breakdown: Record<string, number>;
  forecast?: ExpenseForecast;
  highest_expense?: Transaction;
}

export interface ReportMeta {
  filename: string;
  total_lines: number;
  valid_count: number;
  skipped_count: number;
  processed_at?: string;
}

export interface AnalysisReport {
  status: "success" | "error" | "empty" | "cancelled";
  message?: string;
  meta: ReportMeta;
  summary: ExpenseSummary;
  transactions: Transaction[];
  skipped_lines: SkippedLine[];
}
