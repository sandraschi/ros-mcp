import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './e2e',
    timeout: 60000,
    retries: 1,
    use: {
        baseURL: 'http://localhost:11051',
        headless: true,
        screenshot: 'only-on-failure',
    },
    webServer: [
        {
            command: 'uv run python -m web_sota.backend.server --port 11050',
            port: 11050,
            cwd: '../',
            timeout: 30000,
            reuseExistingServer: false,
        },
        {
            command: 'npx vite --port 11051 --host',
            port: 11051,
            cwd: '.',
            timeout: 30000,
            reuseExistingServer: false,
        },
    ],
});
