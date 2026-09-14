import { test } from "@playwright/test";
import * as path from "path";

test.describe("QUOIN Visual Screenshot Generation", () => {
  test.use({ viewport: { width: 1440, height: 900 } });

  test("Capture 4 core product views for README and evidence", async ({ page }) => {
    // 1. Landing Page
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(__dirname, "../../evidence/screenshots/landing.png"),
      fullPage: false,
    });

    // 2. Console Page
    await page.goto("/console");
    await page.waitForLoadState("networkidle");
    // Trigger evaluation so state is active and visible
    const evalButton = page.getByRole("button", { name: /Step 1: Reason & Evaluate Fence/i });
    if (await evalButton.isVisible()) {
      await evalButton.click();
      await page.waitForTimeout(500);
    }
    await page.screenshot({
      path: path.join(__dirname, "../../evidence/screenshots/console.png"),
      fullPage: false,
    });

    // 3. Lab Page
    await page.goto("/lab");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(__dirname, "../../evidence/screenshots/lab.png"),
      fullPage: false,
    });

    // 4. Proof Center
    await page.goto("/proof");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(__dirname, "../../evidence/screenshots/proof.png"),
      fullPage: false,
    });
  });
});
