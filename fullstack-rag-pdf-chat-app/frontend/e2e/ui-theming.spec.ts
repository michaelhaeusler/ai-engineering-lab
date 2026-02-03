import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('UI Theming and Visual Elements', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app and enter API key
    await page.goto('/');

    // Use type() for WebKit compatibility
    const apiKeyInput = page.getByTestId('api-key-input-field');
    await apiKeyInput.click();
    await apiKeyInput.type('sk-test-api-key-for-testing');

    // Wait for button to be enabled, then click
    const continueButton = page.getByTestId('api-key-continue-button');
    await expect(continueButton).toBeEnabled({ timeout: 2000 });
    await continueButton.click();
  });

  test('should apply theme color to UI elements', async ({ page }) => {
    // Open settings and select blue theme
    await page.getByTestId('header-settings-button').click();
    await page.getByTestId('settings-color-blue').click();
    await page.getByTestId('settings-modal-done-button').click();

    // Check that send button has blue styling
    const sendButton = page.getByTestId('chat-send-button');
    await expect(sendButton).toHaveClass(/bg-blue-600/);
  });

  test('should persist theme selection across page reloads', async ({ page }) => {
    // Select purple theme
    await page.getByTestId('header-settings-button').click();
    await page.getByTestId('settings-color-purple').click();
    await page.getByTestId('settings-modal-done-button').click();

    // Reload page
    await page.reload();

    // Enter API key again (since it's not persisted in tests)
    // Use type() for WebKit compatibility
    const apiKeyInput = page.getByTestId('api-key-input-field');
    await apiKeyInput.click();
    await apiKeyInput.type('sk-test-api-key-for-testing');

    const continueButton = page.getByTestId('api-key-continue-button');
    await expect(continueButton).toBeEnabled({ timeout: 2000 });
    await continueButton.click();

    // Check that purple theme is still applied
    await page.getByTestId('header-settings-button').click();
    const purpleButton = page.getByTestId('settings-color-purple');
    await expect(purpleButton).toHaveClass(/border-purple-300/);
  });

  test('should show progress bar with theme color', async ({ page }) => {
    // Select emerald theme
    await page.getByTestId('header-settings-button').click();
    await page.getByTestId('settings-color-emerald').click();
    await page.getByTestId('settings-modal-done-button').click();

    // Mock API responses to avoid real OpenAI calls
    await page.route('**/api/upload-pdf-only', async (route) => {
      // Delay response to see progress bar
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Document processed successfully' }),
      });
    });

    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/plain',
        body: 'Mock document summary for testing',
      });
    });

    // Trigger upload
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');
    page.on('filechooser', async (fileChooser) => {
      await fileChooser.setFiles(testFilePath);
    });

    await page.getByTestId('file-upload-area').click();

    // Should see progress bar with emerald color
    const progressBar = page.getByTestId('file-upload-progress-bar');
    await expect(progressBar).toBeVisible({ timeout: 5000 });
    await expect(progressBar.locator('[data-slot="progress-indicator"]')).toHaveClass(/bg-emerald-600/);
  });

  test('should show proper visual hierarchy', async ({ page }) => {
    // Check header elements
    await expect(page.getByText('RAG Chat')).toBeVisible();
    await expect(page.getByText('AI-powered document chat')).toBeVisible();

    // Check main content areas
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
    await expect(page.getByText('Start a conversation')).toBeVisible();

    // Check that elements have proper styling classes
    const header = page.locator('h1:has-text("RAG Chat")');
    await expect(header).toHaveClass(/text-xl.*font-semibold/);
  });

  test('should show loading states with theme colors', async ({ page }) => {
    // Select red theme
    await page.getByTestId('header-settings-button').click();
    await page.getByTestId('settings-color-red').click();
    await page.getByTestId('settings-modal-done-button').click();

    // Mock delayed chat response
    await page.route('**/api/chat', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'text/plain',
        body: 'Response',
      });
    });

    // Send message to trigger loading
    const messageInput = page.getByTestId('chat-input-field');
    await messageInput.fill('Test message');
    await messageInput.press('Enter');

    // Should show loading with red theme
    const loadingIndicator = page.getByTestId('chat-loading-indicator');
    await expect(loadingIndicator).toBeVisible();
    await expect(loadingIndicator.locator('.animate-spin')).toHaveClass(/text-red-600/);
  });

  test('should handle responsive design elements', async ({ page }) => {
    // Test with different viewport sizes
    await page.setViewportSize({ width: 768, height: 1024 }); // Tablet size

    // Elements should still be visible and properly arranged
    await expect(page.getByText('RAG Chat')).toBeVisible();
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
    await expect(page.getByTestId('chat-input-field')).toBeVisible();

    // Test mobile size
    await page.setViewportSize({ width: 375, height: 667 }); // Mobile size

    // Should still work on mobile
    await expect(page.getByText('RAG Chat')).toBeVisible();
    await expect(page.getByTestId('chat-input-field')).toBeVisible();
  });

  test('should show proper focus states', async ({ page }) => {
    const messageInput = page.getByTestId('chat-input-field');

    // Focus the input
    await messageInput.focus();

    // Should have focus styling
    await expect(messageInput).toBeFocused();
    await expect(messageInput).toHaveClass(/focus:border-neutral-400/);
  });
});
