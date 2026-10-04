import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";

import { useAuth } from "../auth/auth-context";
import { listFiscalYears } from "./api/budgetFoundation";
import type { FiscalYear } from "./types";

type FiscalYearContextValue = {
  fiscalYears: FiscalYear[];
  selectedFiscalYear: FiscalYear | null;
  selectedFiscalYearId: string;
  setSelectedFiscalYearId: (value: string) => void;
  loading: boolean;
  refreshFiscalYears: () => Promise<void>;
};

const FiscalYearContext = createContext<FiscalYearContextValue | null>(null);
const STORAGE_KEY = "sima.selectedFiscalYearId";

export function FiscalYearProvider({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const canView = (auth.user?.permissions ?? []).includes("fiscal_years.view");
  const [fiscalYears, setFiscalYears] = useState<FiscalYear[]>([]);
  const [selectedFiscalYearId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(canView);

  useEffect(() => {
    if (!canView) return;

    let active = true;
    void listFiscalYears()
      .then((items) => {
        if (!active) return;
        setFiscalYears(items);
        const stored = window.localStorage.getItem(STORAGE_KEY);
        const storedMatch = items.find((item) => item.id === stored);
        const preferred =
          storedMatch ??
          items.find((item) => item.status === "ACTIVE") ??
          items.find((item) => item.status === "PLANNING") ??
          items[0];
        setSelectedId(preferred?.id ?? "");
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [canView]);

  const selectedFiscalYear = useMemo(
    () => fiscalYears.find((item) => item.id === selectedFiscalYearId) ?? null,
    [fiscalYears, selectedFiscalYearId],
  );

  async function refreshFiscalYears() {
    if (!canView) return;
    const items = await listFiscalYears();
    setFiscalYears(items);
    setSelectedId((current) => {
      const currentMatch = items.find((item) => item.id === current);
      const preferred =
        currentMatch ??
        items.find((item) => item.status === "ACTIVE") ??
        items.find((item) => item.status === "PLANNING") ??
        items[0];
      const nextId = preferred?.id ?? "";
      if (nextId) {
        window.localStorage.setItem(STORAGE_KEY, nextId);
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
      return nextId;
    });
  }

  function setSelectedFiscalYearId(value: string) {
    setSelectedId(value);
    if (value) {
      window.localStorage.setItem(STORAGE_KEY, value);
    } else {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }

  return (
    <FiscalYearContext.Provider
      value={{
        fiscalYears,
        selectedFiscalYear,
        selectedFiscalYearId,
        setSelectedFiscalYearId,
        loading,
        refreshFiscalYears,
      }}
    >
      {children}
    </FiscalYearContext.Provider>
  );
}

export function useFiscalYear() {
  const context = useContext(FiscalYearContext);
  if (!context) {
    throw new Error("useFiscalYear harus digunakan di dalam FiscalYearProvider.");
  }
  return context;
}
