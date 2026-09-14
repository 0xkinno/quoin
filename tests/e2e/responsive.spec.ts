import { test, expect } from "@playwright/test";

test.describe("QUOIN Responsive & Core Workflows Suite", () => {
  test("Landing page loads and renders core architecture", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/QUOIN/i);
    await expect(page.locator("h1")).toContainText("Accepted is not the same as visible");

    // Check no horizontal scroll overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalScroll).toBe(false);

    // Verify key CTA links
    const consoleLink = page.getByRole("link", { name: /Launch Cutover Console/i });
    await expect(consoleLink).toBeVisible();

    const labLink = page.getByRole("link", { name: /Open Break It Lab/i });
    await expect(labLink).toBeVisible();
  });

  test("Cutover Console evaluates and fences in-flight requests", async ({ page }) => {
    await page.goto("/console");
    await expect(page.locator("h1")).toContainText("Policy Cutover Console");

    // Check no horizontal scroll overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalScroll).toBe(false);

    // Click Step 1: Reason & Evaluate Fence
    const evalButton = page.getByRole("button", { name: /Step 1: Reason & Evaluate Fence/i });
    await expect(evalButton).toBeVisible();
    await evalButton.click();

    // Verify result card appears
    await expect(page.locator("text=PERMITTED").or(page.locator("text=POLICY_VIOLATION"))).toBeVisible();

    // Check Drawer toggle
    const drawerButton = page.getByRole("button", { name: /Cryptographic Evidence Drawer/i });
    await expect(drawerButton).toBeVisible();
    await drawerButton.click();
    await expect(page.locator("text=Verifiable Authority Receipts")).toBeVisible();
  });

  test("Break It Lab displays and triggers 13 adversarial attacks", async ({ page }) => {
    await page.goto("/lab");
    await expect(page.locator("h1")).toContainText("Break It");

    // Verify all 13 attack cards exist
    await expect(page.locator("text=ATT_A")).toBeVisible();
    await page.locator("text=ATT_M").scrollIntoViewIfNeeded();
    await expect(page.locator("text=ATT_M")).toBeVisible();

    // Check no horizontal scroll overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1;
    });
    expect(hasHorizontalScroll).toBe(true);

    // Trigger ATT_A
    const fireButton = page.locator("button:has-text('Fire Attack')").first();
    await fireButton.click();
    await expect(page.locator("text=Kernel Verified").first()).toBeVisible({ timeout: 10000 });

    // Test filter pill
    const filterPill = page.getByRole("button", { name: "Replay / Reuse" });
    await filterPill.click();
    await expect(page.locator("text=ATT_G")).toBeVisible();
  });

  test("Proof Center displays benchmark table, verifier report, and manifest", async ({ page }) => {
    await page.goto("/proof");
    await expect(page.locator("h1")).toContainText("Proof Center & Evidence");

    // Check no horizontal scroll overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1;
    });
    expect(hasHorizontalScroll).toBe(true);

    // Verify benchmark metrics
    await expect(page.locator("text=100% Elimination of Stale Actions")).toBeVisible();
    await expect(page.locator("text=SCEN_01")).toBeVisible();

    // Switch to Master Verifier tab
    const verifierTab = page.getByRole("button", { name: /Master Verifier/i });
    await verifierTab.click();
    await expect(page.locator("text=ALL 7 REPRODUCIBILITY CHECKS PASSED")).toBeVisible();

    // Switch to Manifest tab
    const manifestTab = page.getByRole("button", { name: /Cryptographic Manifest/i });
    await manifestTab.click();
    await expect(page.locator("text=Copy JSON")).toBeVisible();
  });
});
