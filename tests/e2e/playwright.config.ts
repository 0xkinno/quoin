import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "../",
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "Mobile Small (360px)",
      use: { viewport: { width: 360, height: 640 } },
    },
    {
      name: "iPhone Standard (390px)",
      use: { viewport: { width: 390, height: 844 } },
    },
    {
      name: "iPhone Pro Max (430px)",
      use: { viewport: { width: 430, height: 932 } },
    },
    {
      name: "iPad Portrait (768px)",
      use: { viewport: { width: 768, height: 1024 } },
    },
    {
      name: "iPad Air (820px)",
      use: { viewport: { width: 820, height: 1180 } },
    },
    {
      name: "iPad Landscape / Small Desktop (1024px)",
      use: { viewport: { width: 1024, height: 768 } },
    },
    {
      name: "Desktop Standard (1280px)",
      use: { viewport: { width: 1280, height: 800 } },
    },
    {
      name: "Desktop Wide (1440px)",
      use: { viewport: { width: 1440, height: 900 } },
    },
    {
      name: "Desktop Large (1728px)",
      use: { viewport: { width: 1728, height: 1080 } },
    },
  ],
  webServer: {
    command: "npm run start",
    cwd: "apps/web",
    port: 3000,
    reuseExistingServer: true,
    timeout: 60000,
  },
});
