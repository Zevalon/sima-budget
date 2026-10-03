import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DashboardPage } from "../src/features/dashboard/pages/DashboardPage";

describe("DashboardPage", () => {
  it("renders foundation status", () => {
    render(<DashboardPage />);
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("Foundation Active")).toBeInTheDocument();
  });
});
