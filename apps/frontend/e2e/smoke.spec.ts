import { expect, test } from "@playwright/test";

test("SIMA phase 0 dashboard renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("SIMA", { exact: true })).toBeVisible();
});
