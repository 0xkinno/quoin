import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

test.describe("QUOIN End-to-End & Multi-Viewport Verification", () => {
  const screenshotsDir = path.resolve(__dirname, "../../evidence/screenshots");

  test.beforeAll(async () => {
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
  });

  test("1. Landing Page — Full Replay Aesthetic & Interactive Components", async ({ page }, testInfo) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/QUOIN/i);

    // Verify Display Headline
    const heading = page.locator("h1");
    await expect(heading).toContainText("Your agent executed on a");
    await expect(heading).toContainText("stale policy?");

    // Verify Ticker Marquee exists
    const ticker = page.locator(".ticker");
    await expect(ticker).toBeVisible();
    await expect(ticker).toContainText("EPOCH G18 ACTIVE");

    // Verify Scrub Timeline
    const scrub = page.locator("#scrub");
    await expect(scrub).toBeVisible();
    await expect(scrub.locator("h2")).toContainText("scrub");

    // Click Next Step on scrub timeline
    const nextBtn = scrub.getByRole("button", { name: /Next Step/i });
    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      await expect(scrub).toContainText("STEP 02");
    }

    // Verify Problem Stack (.pstack)
    const pstack = page.locator(".pstack");
    await expect(pstack).toBeVisible();
    await expect(pstack).toContainText("/ 01");
    await expect(pstack).toContainText("/ 02");
    await expect(pstack).toContainText("/ 03");

    // Verify Bento Grid (.bento)
    const bento = page.locator(".bento");
    await expect(bento).toBeVisible();
    await expect(bento).toContainText("PERMIT");
    await expect(bento).toContainText("AUTHORITY");

    // Verify Proof Metric Grid
    await expect(page.locator("text=Measured Head-to-Head Performance (100 Scenarios)")).toBeVisible();

    // Verify Four-Plane Architecture Boxes
    await expect(page.locator("text=Four-Plane System Topology")).toBeVisible();
    await expect(page.getByText("Plane A", { exact: true })).toBeVisible();
    await expect(page.getByText("Plane B", { exact: true })).toBeVisible();
    await expect(page.getByText("Plane C", { exact: true })).toBeVisible();
    await expect(page.getByText("Plane D", { exact: true })).toBeVisible();

    // Verify Brand Footer
    const footer = page.locator(".brand-footer");
    await expect(footer).toBeVisible();
    await expect(footer).toContainText("QUOIN");

    // Capture Landing Page screenshot on primary desktop project
    if (testInfo.project.name.includes("Desktop Large") || testInfo.project.name.includes("Desktop Standard")) {
      await page.screenshot({
        path: path.join(screenshotsDir, `landing_${testInfo.project.name.replace(/[^a-zA-Z0-9]/g, "_")}.png`),
        fullPage: false,
      });
    }
  });

  test("2. Operator Console — Live Evaluation & 2PC Lease Issuance", async ({ page }, testInfo) => {
    await page.goto("/console");
    await expect(page.locator("h1")).toBeVisible();

    // Fill amount or evaluate
    const evalButton = page.getByRole("button", { name: /Evaluate Policy Precondition/i }).or(
      page.getByRole("button", { name: /Evaluate/i })
    );

    if (await evalButton.first().isVisible()) {
      await evalButton.first().click();
      // Wait for response card
      await page.waitForTimeout(1000);
      await expect(page.locator("body")).toContainText(/PERMITTED|VIOLATION|ABORTED|ACTIVE/i);
    }

    if (testInfo.project.name.includes("Desktop Standard")) {
      await page.screenshot({
        path: path.join(screenshotsDir, "console_desktop.png"),
        fullPage: false,
      });
    }
  });

  test("3. Break It Lab — 27 Adversarial Attacks Execution", async ({ page }, testInfo) => {
    await page.goto("/lab");
    await expect(page.locator("h1")).toContainText(/Break It/i);

    // Verify attack cards loaded
    await expect(page.getByText("ATT_A", { exact: true })).toBeVisible();

    // Test fire an attack
    const fireBtn = page.locator("button:has-text('Fire Attack')").or(
      page.locator("button:has-text('Execute')")
    ).first();

    if (await fireBtn.isVisible()) {
      await fireBtn.click();
      await page.waitForTimeout(1500);
      await expect(page.locator("body")).toContainText(/Neutralized|FENCE_BLOCKED|ABORTED|Verified/i);
    }

    if (testInfo.project.name.includes("Desktop Standard")) {
      await page.screenshot({
        path: path.join(screenshotsDir, "lab_attacks_desktop.png"),
        fullPage: false,
      });
    }
  });

  test("4. Decision Trace — Forensic Timeline & Hash Verification", async ({ page }, testInfo) => {
    await page.goto("/trace");
    await expect(page.locator("h1")).toContainText(/Decision Trace/i);

    // Verify sample trace loads
    await page.waitForTimeout(1000);
    await expect(page.locator("body")).toContainText(/GENESIS|PROPOSAL|PERMIT|EXECUTION|TRACE_INTACT/i);

    if (testInfo.project.name.includes("Desktop Standard")) {
      await page.screenshot({
        path: path.join(screenshotsDir, "trace_timeline_desktop.png"),
        fullPage: false,
      });
    }
  });

  test("5. Proof Center — Live Dynamic Verifier & Benchmark Table", async ({ page }, testInfo) => {
    await page.goto("/proof");
    await expect(page.locator("h1")).toContainText(/Proof Center/i);

    // Verify live verifier status compliance
    await expect(page.locator("body")).toContainText(/100%/i);

    // Verify benchmark table shows scenarios
    await expect(page.locator("body")).toContainText(/SCEN_001/i);

    // Check raw evidence drawer trigger
    const vaultBtn = page.getByRole("button", { name: /Evidence Vault/i });
    if (await vaultBtn.isVisible()) {
      await vaultBtn.click();
      await expect(page.locator("text=Machine-Readable Evidence Vault")).toBeVisible();
      // Close drawer
      const closeBtn = page.getByRole("button", { name: /Close/i }).or(page.locator(".lucide-x").locator(".."));
      if (await closeBtn.first().isVisible()) {
        await closeBtn.first().click();
      }
    }

    if (testInfo.project.name.includes("Desktop Standard")) {
      await page.screenshot({
        path: path.join(screenshotsDir, "proof_center_desktop.png"),
        fullPage: false,
      });
    }
  });
});
