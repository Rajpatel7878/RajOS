"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search as SearchIcon,
  X,
  Loader2,
  AlertTriangle,
  RefreshCw,
  Clock,
  ArrowUpRight,
  CheckSquare,
  StickyNote,
  FileText,
  MessageSquare,
  BrainCircuit,
  BookOpen,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  History,
  Sparkles,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  searchWorkspace,
  getSearchSuggestions,
  getSearchHistory,
  clearSearchHistory,
  type ResourceType,
  type SortOption,
  type SearchItem,
  type SearchPagination,
  type ProviderStatus,
  type SearchSuggestion,
  type SearchHistoryItem,
} from "@/services/api/search";

const PAGE_SIZE = 20;

const RESOURCE_META: Record<
  ResourceType,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    text: string;
    border: string;
    bg: string;
  }
> = {
  tasks: {
    label: "Tasks",
    icon: CheckSquare,
    text: "text-sky-400",
    border: "border-sky-400/30",
    bg: "bg-sky-400/10",
  },
  notes: {
    label: "Notes",
    icon: StickyNote,
    text: "text-amber-400",
    border: "border-amber-400/30",
    bg: "bg-amber-400/10",
  },
  documents: {
    label: "Documents",
    icon: FileText,
    text: "text-emerald-400",
    border: "border-emerald-400/30",
    bg: "bg-emerald-400/10",
  },
  conversations: {
    label: "Conversations",
    icon: MessageSquare,
    text: "text-violet-400",
    border: "border-violet-400/30",
    bg: "bg-violet-400/10",
  },
  memories: {
    label: "Memories",
    icon: BrainCircuit,
    text: "text-rose-400",
    border: "border-rose-400/30",
    bg: "bg-rose-400/10",
  },
  knowledge: {
    label: "Knowledge",
    icon: BookOpen,
    text: "text-cyan-400",
    border: "border-cyan-400/30",
    bg: "bg-cyan-400/10",
  },
};

const RESOURCE_TYPES = Object.keys(RESOURCE_META) as ResourceType[];

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: "relevance", label: "Best match" },
  { value: "newest", label: "Newest first" },
  { value: "oldest", label: "Oldest first" },
];

const SAFE_DESTINATIONS = new Set(["/tasks", "/notes", "/documents", "/chat", "/memory"]);

function isSafeDestination(url: string | null | undefined): url is string {
  return Boolean(url && SAFE_DESTINATIONS.has(url));
}

function formatDate(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function metaChips(item: SearchItem): string[] {
  const chips: string[] = [];
  const metadata = item.metadata ?? {};

  if (item.resource_type === "tasks") {
    if (metadata.completed === true) chips.push("Completed");
    if (typeof metadata.priority === "string" && metadata.priority !== "normal") {
      chips.push(`Priority: ${metadata.priority}`);
    }
    if (typeof metadata.category === "string" && metadata.category) {
      chips.push(metadata.category);
    }
  }
  if (item.resource_type === "documents" && typeof metadata.filename === "string") {
    chips.push(metadata.filename);
  }
  if (item.resource_type === "memories" && typeof metadata.memory_type === "string") {
    chips.push(metadata.memory_type);
  }
  if (item.resource_type === "knowledge" && typeof metadata.filename === "string") {
    chips.push(metadata.filename);
  }
  return chips.slice(0, 3);
}

export default function UnifiedSearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [items, setItems] = useState<SearchItem[]>([]);
  const [pagination, setPagination] = useState<SearchPagination | null>(null);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [tookMs, setTookMs] = useState<number | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<SortOption>("relevance");
  const [selectedTypes, setSelectedTypes] = useState<ResourceType[]>([]);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [semantic, setSemantic] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const lastSuggestionKey = useRef("");

  const typesKey = useMemo(() => selectedTypes.join(","), [selectedTypes]);

  // Load recent searches for the empty state.
  useEffect(() => {
    let cancelled = false;
    getSearchHistory(8)
      .then((rows) => {
        if (!cancelled) setHistory(rows);
      })
      .catch(() => {
        // History is an enhancement; failing to load it must not block search.
      })
      .finally(() => {
        if (!cancelled) setHistoryLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Focus the search input when the workspace opens.
  useEffect(() => {
    const timer = setTimeout(() => inputRef.current?.focus(), 60);
    return () => clearTimeout(timer);
  }, []);

  // Debounced suggestions, with duplicate-query suppression and abort cleanup.
  useEffect(() => {
    if (!showSuggestions) return;

    const trimmed = query.trim();
    if (!trimmed) {
      setSuggestions([]);
      return;
    }

    const key = trimmed.toLowerCase();
    if (key === lastSuggestionKey.current) return;

    const controller = new AbortController();
    const timer = setTimeout(() => {
      getSearchSuggestions(trimmed, 6, controller.signal)
        .then((rows) => {
          lastSuggestionKey.current = key;
          setSuggestions(rows);
        })
        .catch(() => {
          // Suggestions are best-effort.
        });
    }, 250);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, showSuggestions]);

  // Run the search whenever the submitted query, filters or page change.
  useEffect(() => {
    if (!submittedQuery) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    searchWorkspace(
      {
        q: submittedQuery,
        types: selectedTypes,
        sort,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page,
        limit: PAGE_SIZE,
        semantic,
      },
      controller.signal
    )
      .then((response) => {
        setItems(response.items);
        setPagination(response.pagination);
        setProviders(response.providers);
        setTookMs(response.took_ms);

        getSearchHistory(8)
          .then(setHistory)
          .catch(() => {});
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Search failed");
        setItems([]);
        setPagination(null);
        setProviders([]);
        setTookMs(null);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [submittedQuery, selectedTypes, sort, dateFrom, dateTo, page, semantic, reloadKey]);

  const submitSearch = useCallback(
    (value?: string) => {
      const next = (value ?? query).trim();
      setShowSuggestions(false);
      setActiveSuggestion(-1);

      if (!next) {
        setSubmittedQuery("");
        setItems([]);
        setPagination(null);
        setProviders([]);
        setTookMs(null);
        setError(null);
        return;
      }

      setQuery(next);
      setPage(1);
      if (next === submittedQuery) {
        setReloadKey((key) => key + 1);
      } else {
        setSubmittedQuery(next);
      }
    },
    [query, submittedQuery]
  );

  const toggleType = (type: ResourceType) => {
    setSelectedTypes((current) =>
      current.includes(type) ? current.filter((entry) => entry !== type) : [...current, type]
    );
    setPage(1);
  };

  const handleClearHistory = async () => {
    try {
      await clearSearchHistory();
      setHistory([]);
    } catch {
      // Non-critical.
    }
  };

  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowDown" && suggestions.length > 0) {
      event.preventDefault();
      setShowSuggestions(true);
      setActiveSuggestion((current) => (current + 1) % suggestions.length);
      return;
    }
    if (event.key === "ArrowUp" && suggestions.length > 0) {
      event.preventDefault();
      setShowSuggestions(true);
      setActiveSuggestion((current) =>
        current <= 0 ? suggestions.length - 1 : current - 1
      );
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      if (showSuggestions && activeSuggestion >= 0 && suggestions[activeSuggestion]) {
        submitSearch(suggestions[activeSuggestion].text);
      } else {
        submitSearch();
      }
      return;
    }
    if (event.key === "Escape") {
      if (showSuggestions) {
        setShowSuggestions(false);
        setActiveSuggestion(-1);
      } else if (query) {
        setQuery("");
        setSuggestions([]);
      }
    }
  };

  const okProviders = providers.filter((provider) => provider.status === "ok");
  const failedProviders = providers.filter((provider) => provider.status === "error");
  const disabledProviders = providers.filter(
    (provider) => provider.status === "disabled" && provider.resource_type === "knowledge"
  );

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-white">Unified Workspace</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Search tasks, notes, documents, conversations, memories and knowledge in one place.
        </p>
      </div>

      {/* ── Search bar ── */}
      <div className="relative z-30">
        <form
          role="search"
          onSubmit={(event) => {
            event.preventDefault();
            submitSearch();
          }}
        >
          <div
            className={cn(
              "group relative flex items-center gap-3 rounded-2xl border px-4 py-3",
              "border-white/[0.08] bg-black/50 backdrop-blur-2xl transition-all duration-200",
              "shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]",
              "focus-within:border-sky-400/40 focus-within:shadow-[0_0_24px_rgba(56,189,248,0.15)]"
            )}
          >
            <SearchIcon
              aria-hidden
              className="h-5 w-5 shrink-0 text-muted-foreground group-focus-within:text-sky-400"
            />
            <label htmlFor="workspace-search" className="sr-only">
              Search your workspace
            </label>
            <Input
              id="workspace-search"
              ref={inputRef}
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setActiveSuggestion(-1);
                setShowSuggestions(true);
                lastSuggestionKey.current = "";
              }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => {
                // Delay so a click on a suggestion still registers.
                setTimeout(() => setShowSuggestions(false), 150);
              }}
              onKeyDown={handleInputKeyDown}
              placeholder="Search tasks, notes, documents, conversations, memories..."
              role="combobox"
              aria-expanded={showSuggestions && suggestions.length > 0}
              aria-controls="search-suggestions"
              aria-autocomplete="list"
              aria-activedescendant={
                activeSuggestion >= 0 ? `search-suggestion-${activeSuggestion}` : undefined
              }
              autoComplete="off"
              maxLength={200}
              className="h-9 border-0 bg-transparent px-0 text-[15px] text-white shadow-none placeholder:text-muted-foreground/60 focus-visible:ring-0"
            />
            {query && (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  setSuggestions([]);
                  setActiveSuggestion(-1);
                  inputRef.current?.focus();
                }}
                aria-label="Clear search query"
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-white/10 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            )}
            <Button
              type="submit"
              size="sm"
              className="gap-1.5 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
            >
              <SearchIcon className="h-3.5 w-3.5" />
              Search
            </Button>
          </div>
        </form>

        {/* ── Suggestions ── */}
        <AnimatePresence>
          {showSuggestions && query.trim() && suggestions.length > 0 && (
            <motion.ul
              id="search-suggestions"
              role="listbox"
              aria-label="Search suggestions"
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.15 }}
              className="absolute left-0 right-0 top-full z-40 mt-2 overflow-hidden rounded-xl border border-white/10 bg-[#060b14]/95 py-1 shadow-2xl backdrop-blur-2xl"
            >
              {suggestions.map((suggestion, index) => {
                const meta = suggestion.resource_type
                  ? RESOURCE_META[suggestion.resource_type]
                  : null;
                const Icon = meta?.icon ?? Clock;
                return (
                  <li
                    key={`${suggestion.kind}-${suggestion.text}-${index}`}
                    id={`search-suggestion-${index}`}
                    role="option"
                    aria-selected={index === activeSuggestion}
                  >
                    <button
                      type="button"
                      onMouseEnter={() => setActiveSuggestion(index)}
                      onClick={() => submitSearch(suggestion.text)}
                      className={cn(
                        "flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors",
                        index === activeSuggestion
                          ? "bg-sky-500/15 text-white"
                          : "text-muted-foreground hover:bg-white/[0.05] hover:text-white"
                      )}
                    >
                      <Icon className={cn("h-4 w-4 shrink-0", meta?.text ?? "text-muted-foreground")} />
                      <span className="min-w-0 flex-1 truncate">{suggestion.text}</span>
                      <span className="shrink-0 text-[10px] uppercase tracking-wide text-muted-foreground/70">
                        {suggestion.kind === "history" ? "Recent" : meta?.label}
                      </span>
                    </button>
                  </li>
                );
              })}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>

      {/* ── Filters ── */}
      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setSelectedTypes([]);
              setPage(1);
            }}
            aria-pressed={selectedTypes.length === 0}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs font-medium transition-all",
              selectedTypes.length === 0
                ? "border-sky-400/40 bg-sky-400/10 text-sky-300"
                : "border-white/10 bg-white/[0.02] text-muted-foreground hover:border-white/20 hover:text-white"
            )}
          >
            All
          </button>

          {RESOURCE_TYPES.map((type) => {
            const meta = RESOURCE_META[type];
            const Icon = meta.icon;
            const active = selectedTypes.includes(type);
            return (
              <button
                key={type}
                type="button"
                onClick={() => toggleType(type)}
                aria-pressed={active}
                className={cn(
                  "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all",
                  active
                    ? `${meta.border} ${meta.bg} ${meta.text}`
                    : "border-white/10 bg-white/[0.02] text-muted-foreground hover:border-white/20 hover:text-white"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {meta.label}
              </button>
            );
          })}

          <button
            type="button"
            onClick={() => setShowFilters((value) => !value)}
            aria-expanded={showFilters}
            className={cn(
              "ml-auto flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all",
              showFilters
                ? "border-sky-400/40 bg-sky-400/10 text-sky-300"
                : "border-white/10 bg-white/[0.02] text-muted-foreground hover:text-white"
            )}
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Sort & dates
          </button>
        </div>

        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <GlassCard hover={false} className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <label
                    htmlFor="search-sort"
                    className="mb-1 block text-[11px] uppercase tracking-wide text-muted-foreground"
                  >
                    Sort by
                  </label>
                  <select
                    id="search-sort"
                    value={sort}
                    onChange={(event) => {
                      setSort(event.target.value as SortOption);
                      setPage(1);
                    }}
                    className="h-9 w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 text-sm text-white focus:border-sky-400/50 focus:outline-none"
                  >
                    {SORT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value} className="bg-slate-950">
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="search-date-from"
                    className="mb-1 block text-[11px] uppercase tracking-wide text-muted-foreground"
                  >
                    Updated after
                  </label>
                  <Input
                    id="search-date-from"
                    type="date"
                    value={dateFrom}
                    onChange={(event) => {
                      setDateFrom(event.target.value);
                      setPage(1);
                    }}
                    className="border-white/[0.08] bg-white/[0.03] text-sm text-white"
                  />
                </div>

                <div>
                  <label
                    htmlFor="search-date-to"
                    className="mb-1 block text-[11px] uppercase tracking-wide text-muted-foreground"
                  >
                    Updated before
                  </label>
                  <Input
                    id="search-date-to"
                    type="date"
                    value={dateTo}
                    onChange={(event) => {
                      setDateTo(event.target.value);
                      setPage(1);
                    }}
                    className="border-white/[0.08] bg-white/[0.03] text-sm text-white"
                  />
                </div>

                <div className="flex items-end">
                  <label
                    htmlFor="search-semantic"
                    className="flex h-9 w-full cursor-pointer items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 text-sm text-muted-foreground"
                  >
                    <input
                      id="search-semantic"
                      type="checkbox"
                      checked={semantic}
                      onChange={(event) => {
                        setSemantic(event.target.checked);
                        setPage(1);
                      }}
                      className="h-4 w-4 rounded border-white/20 bg-transparent accent-sky-500"
                    />
                    Include knowledge base
                  </label>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── Results / states ── */}
      <div className="mt-6">
        {!submittedQuery ? (
          <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
            <GlassCard hover={false} className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                  <History className="h-4 w-4 text-sky-400" />
                  Recent searches
                </h2>
                {history.length > 0 && (
                  <button
                    type="button"
                    onClick={handleClearHistory}
                    className="text-xs text-muted-foreground transition-colors hover:text-rose-300"
                  >
                    Clear history
                  </button>
                )}
              </div>

              {historyLoading ? (
                <div className="space-y-2" aria-hidden>
                  {[0, 1, 2].map((row) => (
                    <div key={row} className="h-9 animate-pulse rounded-lg bg-white/[0.03]" />
                  ))}
                </div>
              ) : history.length === 0 ? (
                <p className="py-6 text-sm text-muted-foreground">
                  No recent searches yet. Try “roadmap”, “meeting notes” or a document name.
                </p>
              ) : (
                <ul className="space-y-1">
                  {history.map((entry) => (
                    <li key={entry.id}>
                      <button
                        type="button"
                        onClick={() => submitSearch(entry.query)}
                        className="flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-white/[0.04] hover:text-white"
                      >
                        <Clock className="h-4 w-4 shrink-0 text-muted-foreground/60" />
                        <span className="min-w-0 flex-1 truncate">{entry.query}</span>
                        <span className="shrink-0 text-[10px] text-muted-foreground/60">
                          {formatDate(entry.searched_at)}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </GlassCard>

            <GlassCard hover={false} className="p-5">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                <Sparkles className="h-4 w-4 text-cyan-400" />
                Search everything
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Results are ranked by title matches first, then content relevance, with a small
                recency signal. Enable the knowledge base to add semantic passages.
              </p>
              <div className="mt-4 grid grid-cols-2 gap-2">
                {RESOURCE_TYPES.map((type) => {
                  const meta = RESOURCE_META[type];
                  const Icon = meta.icon;
                  return (
                    <div
                      key={type}
                      className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-xs text-muted-foreground"
                    >
                      <Icon className={cn("h-4 w-4", meta.text)} />
                      {meta.label}
                    </div>
                  );
                })}
              </div>
            </GlassCard>
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
              <div className="text-sm text-muted-foreground">
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                    Searching your workspace...
                  </span>
                ) : pagination ? (
                  <span aria-live="polite">
                    <span className="font-semibold text-white">{pagination.total}</span>{" "}
                    {pagination.total === 1 ? "result" : "results"} for{" "}
                    <span className="text-white">“{submittedQuery}”</span>
                    {tookMs !== null && (
                      <span className="ml-2 text-xs text-muted-foreground/60">{tookMs} ms</span>
                    )}
                  </span>
                ) : null}
              </div>

              {!loading && okProviders.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-muted-foreground/70">
                  {okProviders
                    .filter((provider) => provider.result_count > 0)
                    .map((provider) => (
                      <span
                        key={provider.resource_type}
                        className="rounded-full border border-white/[0.06] bg-white/[0.02] px-2 py-0.5"
                      >
                        {provider.display_name} {provider.result_count}
                      </span>
                    ))}
                </div>
              )}
            </div>

            {(failedProviders.length > 0 || disabledProviders.length > 0) && (
              <div className="mb-4 space-y-1 rounded-xl border border-amber-400/20 bg-amber-400/[0.06] px-4 py-3 text-xs text-amber-200/90">
                {failedProviders.map((provider) => (
                  <p key={`${provider.resource_type}-error`} className="flex items-center gap-2">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    {provider.display_name} could not be searched. Other results are unaffected.
                  </p>
                ))}
                {disabledProviders.map((provider) => (
                  <p key={`${provider.resource_type}-disabled`} className="flex items-center gap-2">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    {provider.error ?? "Semantic knowledge search is off."}
                  </p>
                ))}
              </div>
            )}

            {error ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-rose-500/20 bg-rose-500/[0.06] px-6 py-14 text-center">
                <AlertTriangle className="mb-3 h-7 w-7 text-rose-400" />
                <h3 className="font-semibold text-white">Search failed</h3>
                <p className="mt-1 max-w-md text-sm text-rose-200/80">{error}</p>
                <Button
                  onClick={() => setReloadKey((key) => key + 1)}
                  className="mt-4 gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
                >
                  <RefreshCw className="h-4 w-4" />
                  Try again
                </Button>
              </div>
            ) : loading ? (
              <div className="space-y-3">
                {[0, 1, 2, 3].map((row) => (
                  <div
                    key={row}
                    className="h-24 animate-pulse rounded-2xl border border-white/[0.05] bg-white/[0.02]"
                  />
                ))}
              </div>
            ) : items.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-white/[0.06] bg-white/[0.02] px-6 py-16 text-center">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
                  <SearchIcon className="h-6 w-6 text-muted-foreground" />
                </div>
                <h3 className="font-semibold text-white">No results found</h3>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Nothing matched “{submittedQuery}”. Try a shorter query, remove filters, or
                  broaden the date range.
                </p>
              </div>
            ) : (
              <ul className="space-y-3">
                {items.map((item, index) => {
                  const meta = RESOURCE_META[item.resource_type] ?? RESOURCE_META.tasks;
                  const Icon = meta.icon;
                  const updated = formatDate(item.updated_at ?? item.created_at);
                  const chips = metaChips(item);
                  const safe = isSafeDestination(item.url);

                  const content = (
                    <GlassCard
                      hover={safe}
                      delay={Math.min(index * 0.03, 0.3)}
                      className="p-4"
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={cn(
                            "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border",
                            meta.border,
                            meta.bg,
                            meta.text
                          )}
                        >
                          <Icon className="h-4 w-4" />
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <p className="truncate text-sm font-semibold text-white">
                                {item.title}
                              </p>
                              <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[10px] text-muted-foreground/70">
                                <span className={cn("uppercase tracking-wide", meta.text)}>
                                  {meta.label}
                                </span>
                                {updated && (
                                  <>
                                    <span aria-hidden>·</span>
                                    <span>Updated {updated}</span>
                                  </>
                                )}
                                {item.matched_fields.length > 0 && (
                                  <>
                                    <span aria-hidden>·</span>
                                    <span>
                                      matched{" "}
                                      {item.matched_fields
                                        .filter((field) => field !== "semantic")
                                        .join(", ")}
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>

                            {safe ? (
                              <ArrowUpRight className="h-4 w-4 shrink-0 text-muted-foreground/50 transition-colors group-hover:text-sky-400" />
                            ) : (
                              <span className="shrink-0 rounded-full border border-white/10 px-2 py-0.5 text-[9px] uppercase tracking-wide text-muted-foreground/60">
                                No page yet
                              </span>
                            )}
                          </div>

                          {item.snippet && (
                            <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-muted-foreground">
                              {item.snippet}
                            </p>
                          )}

                          {chips.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {chips.map((chip) => (
                                <span
                                  key={chip}
                                  className="rounded-full border border-white/[0.06] bg-white/[0.02] px-2 py-0.5 text-[10px] text-muted-foreground/80"
                                >
                                  {chip}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </GlassCard>
                  );

                  return (
                    <li key={item.id}>
                      {safe ? (
                        <Link
                          href={item.url as string}
                          className="block rounded-2xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500/60"
                          aria-label={`Open ${item.title} in ${meta.label}`}
                        >
                          {content}
                        </Link>
                      ) : (
                        <div title="No destination page exists for this resource yet">
                          {content}
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && !loading && !error && (
              <nav
                aria-label="Search result pages"
                className="mt-6 flex items-center justify-center gap-3"
              >
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!pagination.has_previous}
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  className="gap-1 border-white/10 text-white"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <span className="text-xs text-muted-foreground">
                  Page {pagination.page} of {pagination.total_pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!pagination.has_next}
                  onClick={() => setPage((current) => current + 1)}
                  className="gap-1 border-white/10 text-white"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </nav>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}

