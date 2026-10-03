import { expect, test } from "@playwright/test";

test("anonymous user is redirected to the SIMA login page", async ({ page }) => {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({
        detail: "Session autentikasi tidak tersedia.",
      }),
    });
  });

  await page.goto("/app/dashboard");

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "Masuk ke SIMA" })).toBeVisible();
  await expect(page.getByLabel("Username atau email")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
  await expect(page.getByRole("button", { name: "Masuk" })).toBeVisible();
});
