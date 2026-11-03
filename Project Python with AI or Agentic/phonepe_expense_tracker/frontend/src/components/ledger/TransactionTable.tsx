import React, { useState, useMemo } from "react";
import { Search, ArrowUpDown, Filter } from "lucide-react";
import { Transaction } from "../../types/expense";
import { CATEGORY_COLORS, DEFAULT_COLOR } from "../../lib/constants";
import { formatINR, formatDate } from "../../lib/formatters";

interface TransactionTableProps {
  transactions: Transaction[];
}

export const TransactionTable: React.FC<TransactionTableProps> = ({ transactions }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");

  // Extract unique categories present in the data
  const availableCategories = useMemo(() => {
    const cats = new Set(transactions.map((t) => t.category));
    return ["All", ...Array.from(cats)];
  }, [transactions]);

  // Filter and sort transactions
  const filteredTransactions = useMemo(() => {
    return transactions
      .filter((t) => {
        const matchesSearch =
          t.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.date.includes(searchTerm) ||
          t.amount.toString().includes(searchTerm);
        const matchesCategory =
          selectedCategory === "All" || t.category === selectedCategory;
        return matchesSearch && matchesCategory;
      })
      .sort((a, b) => {
        if (sortOrder === "desc") {
          return b.amount - a.amount;
        } else {
          return a.amount - b.amount;
        }
      });
  }, [transactions, searchTerm, selectedCategory, sortOrder]);

  return (
    <div className="glass-card rounded-xl border border-phonepe-border overflow-hidden">
      {/* Table Controls Header */}
      <div className="p-4 border-b border-phonepe-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Transaction Ledger
          </h3>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 text-slate-400 font-mono">
            {filteredTransactions.length} of {transactions.length}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search merchant or date..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-phonepe-dark/60 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-phonepe-accent w-48 sm:w-56"
            />
          </div>

          {/* Sort Toggle */}
          <button
            onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white transition-colors"
            title="Sort by amount"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-phonepe-accent" />
            <span>Amount ({sortOrder === "desc" ? "High to Low" : "Low to High"})</span>
          </button>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="px-4 py-2.5 bg-black/20 border-b border-phonepe-border/40 flex items-center gap-1.5 overflow-x-auto text-xs">
        <span className="flex items-center gap-1 text-[11px] text-slate-500 font-medium mr-1 flex-shrink-0">
          <Filter className="w-3 h-3" />
          <span>Category:</span>
        </span>
        {availableCategories.map((cat) => {
          const isSelected = selectedCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all flex-shrink-0 ${
                isSelected
                  ? "bg-phonepe-purple text-white shadow-md shadow-purple-500/20"
                  : "bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200"
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Table Body */}
      <div className="max-h-72 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-phonepe-card/95 backdrop-blur-sm text-slate-400 font-semibold border-b border-white/5">
            <tr>
              <th className="py-2.5 px-4">Date</th>
              <th className="py-2.5 px-4">Merchant / Description</th>
              <th className="py-2.5 px-4">Category</th>
              <th className="py-2.5 px-4 text-right">Amount</th>
              <th className="py-2.5 px-4 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {filteredTransactions.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-500">
                  No transactions match your current search or filter.
                </td>
              </tr>
            ) : (
              filteredTransactions.map((tx) => {
                const color = CATEGORY_COLORS[tx.category] || DEFAULT_COLOR;
                return (
                  <tr
                    key={tx.id}
                    className="hover:bg-white/[0.02] transition-colors group"
                  >
                    <td className="py-2.5 px-4 text-slate-400 font-mono text-[11px]">
                      {formatDate(tx.date)}
                    </td>
                    <td className="py-2.5 px-4 font-medium text-slate-200 group-hover:text-white">
                      {tx.merchant}
                    </td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${color.bg} ${color.text} ${color.border}`}
                      >
                        {tx.category}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right font-semibold text-slate-100 font-mono">
                      {formatINR(tx.amount)}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                        Verified
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

