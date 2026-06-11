import { test, expect } from '@playwright/test';

const BE = 'http://127.0.0.1:11050';
const FE = 'http://127.0.0.1:11051';

test.describe('Fleet Audit — ros-mcp', () => {
    test('Backend health', async ({ request }) => {
        const resp = await request.get(BE + '/health');
        expect(resp.status()).toBe(200);
    });

    test('Frontend loads', async ({ page }) => {
        await page.goto(FE, { timeout: 15000 });
        await page.waitForTimeout(3000);
        await expect(page.locator('#root')).toBeAttached();
    });

    test('No console errors', async ({ page }) => {
        const errors: string[] = [];
        page.on('console', (msg) => {
            if (msg.type() === 'error') errors.push(msg.text());
        });
        await page.goto(FE, { timeout: 15000 });
        await page.waitForTimeout(3000);
        expect(errors.length).toBe(0);
    });

    test('Navigation sidebar works', async ({ page }) => {
        await page.goto(FE, { timeout: 15000 });
        await page.waitForTimeout(2000);
        await expect(page.locator('nav')).toBeAttached();
        await page.locator('nav a').nth(1).click();
        await page.waitForTimeout(1000);
        await expect(page.locator('h1')).toContainText('Topics');
    });

    test('Dashboard loads with KPIs', async ({ page }) => {
        await page.goto(FE, { timeout: 15000 });
        await page.waitForTimeout(3000);
        await expect(page.locator('h1')).toContainText('Dashboard');
        const kpis = page.locator('.grid.grid-cols-4 > div');
        await expect(kpis).toHaveCount(4);
    });

    test('Topics page has list area', async ({ page }) => {
        await page.goto(FE + '/topics', { timeout: 15000 });
        await page.waitForTimeout(2000);
        await expect(page.locator('h1')).toContainText('Topics');
        await expect(page.locator('h2').first()).toContainText('Topic Browser');
    });

    test('Services page renders', async ({ page }) => {
        await page.goto(FE + '/services', { timeout: 15000 });
        await page.waitForTimeout(2000);
        await expect(page.locator('h1')).toContainText('Services');
        await expect(page.locator('h2').first()).toContainText('Service List');
    });
});
