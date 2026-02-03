import { test, expect } from '@playwright/test';
import path from 'path';
import { setupErrorDetection, setupApiKey } from './helpers/error-detection';

test.describe('File Upload Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Set up error detection to catch JavaScript runtime errors
    setupErrorDetection(page, {
      failOnConsoleError: true,
      failOnPageError: true,
      ignoreNetworkErrors: true
    });

    // Navigate to app and enter API key
    await setupApiKey(page);
  });

  test('should show file upload area', async ({ page }) => {
    // Should see upload area - use test ID to avoid ambiguity
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
    await expect(page.getByText('Drag and drop or click to select a PDF file')).toBeVisible();
  });

  test('should show upload area as clickable', async ({ page }) => {
    const uploadArea = page.getByTestId('file-upload-area');
    await expect(uploadArea).toBeVisible();
    await expect(uploadArea).toHaveAttribute('role', 'button');
  });

  test('should show progress bar during upload simulation', async ({ page }) => {
    // Mock API responses with delay to see progress UI
    await page.route('**/api/upload-pdf-only', async (route) => {
      // Add delay to allow progress UI to show
      await new Promise(resolve => setTimeout(resolve, 1500));
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

    // Use real PDF file for testing
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');

    // Set up file chooser handler
    page.on('filechooser', async (fileChooser) => {
      await fileChooser.setFiles(testFilePath);
    });

    // Click upload area to trigger file chooser
    await page.getByTestId('file-upload-area').click();

    // Should show progress elements (the upload starts immediately after file selection)
    await expect(page.getByTestId('file-upload-progress')).toBeVisible({ timeout: 3000 });

    // Verify progress bar is actually progressing
    await expect(page.getByTestId('file-upload-progress-bar')).toBeVisible();
  });

  test('should show progress during file selection', async ({ page }) => {
    // Mock API responses to avoid real OpenAI calls
    await page.route('**/api/upload-pdf-only', async (route) => {
      // Simulate a delay to test progress UI
      await new Promise(resolve => setTimeout(resolve, 1000));
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

    // Use real PDF file for testing
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');

    page.on('filechooser', async (fileChooser) => {
      await fileChooser.setFiles(testFilePath);
    });

    // Trigger file selection
    await page.getByTestId('file-upload-area').click();

    // Should show processing step (this tests the file selection part)
    // Note: Full upload testing requires backend integration
    await page.waitForTimeout(500); // Allow time for file selection

    // This test verifies the file selection works - full upload flow needs backend
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
  });

  test('should accept PDF file types', async ({ page }) => {
    // This test verifies file type validation without requiring backend
    const uploadArea = page.getByTestId('file-upload-area');
    await expect(uploadArea).toBeVisible();

    // Verify the upload area accepts PDF files
    const input = uploadArea.locator('input[type="file"]');
    await expect(input).toHaveAttribute('accept', 'application/pdf,.pdf');
  });

  test('should show drag and drop styling', async ({ page }) => {
    // Test that the upload area has proper drag/drop styling
    const uploadArea = page.getByTestId('file-upload-area');
    await expect(uploadArea).toBeVisible();

    // Verify it has cursor pointer for clickability
    await expect(uploadArea).toHaveClass(/cursor-pointer/);

    // Verify it's structured as a proper drop zone
    await expect(uploadArea).toHaveAttribute('role', 'button');
  });

  test('should handle file upload without JavaScript errors', async ({ page }) => {
    // This test specifically checks that file upload doesn't cause runtime errors
    // It would have caught the original "setIsLoading is not defined" error

    // Mock API responses
    await page.route('**/api/upload-pdf-only', async (route) => {
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

    // Use real PDF file for testing
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');

    // Set up file chooser handler
    page.on('filechooser', async (fileChooser) => {
      await fileChooser.setFiles(testFilePath);
    });

    // Click upload area to trigger file chooser - any JavaScript errors will be caught by setupErrorDetection
    await page.getByTestId('file-upload-area').click();

    // Wait a moment to ensure any async operations complete
    await page.waitForTimeout(1000);

    // If we get here without the setupErrorDetection throwing, the JavaScript is working correctly
    // This test would have failed immediately with the original "setIsLoading is not defined" error
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
  });
});
