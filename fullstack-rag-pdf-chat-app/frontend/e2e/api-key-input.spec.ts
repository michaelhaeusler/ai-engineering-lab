import { test, expect } from '@playwright/test';

test.describe('API Key Input Flow', () => {
  test('should show API key input screen on first visit', async ({ page }) => {
    await page.goto('/');

    // Should see the API key input screen
    await expect(page.getByText('RAG Chat')).toBeVisible();
    await expect(page.getByText('Enter your OpenAI API key to continue')).toBeVisible();
    await expect(page.getByTestId('api-key-input-field')).toBeVisible();
    await expect(page.getByTestId('api-key-continue-button')).toBeVisible();
  });

  test('should disable continue button when API key is empty', async ({ page }) => {
    await page.goto('/');

    const continueButton = page.getByTestId('api-key-continue-button');
    await expect(continueButton).toBeDisabled();
  });

  test('should enable continue button when API key is entered', async ({ page }) => {
    await page.goto('/');

    const apiKeyInput = page.getByTestId('api-key-input-field');
    const continueButton = page.getByTestId('api-key-continue-button');

    // Use type() instead of fill() for WebKit compatibility
    await apiKeyInput.click();
    await apiKeyInput.type('sk-test-api-key-for-testing');

    // Wait for the button to be enabled
    await expect(continueButton).toBeEnabled({ timeout: 2000 });
  });

  test('should proceed to main app when continue is clicked', async ({ page }) => {
    await page.goto('/');

    // Use type() for WebKit compatibility
    const apiKeyInput = page.getByTestId('api-key-input-field');
    await apiKeyInput.click();
    await apiKeyInput.type('sk-test-api-key-for-testing');

    // Wait for button to be enabled, then click
    const continueButton = page.getByTestId('api-key-continue-button');
    await expect(continueButton).toBeEnabled({ timeout: 2000 });
    await continueButton.click();

    // Should see the main app interface
    await expect(page.getByText('AI-powered document chat')).toBeVisible();
    await expect(page.getByTestId('file-upload-area')).toBeVisible();
    await expect(page.getByText('Start a conversation')).toBeVisible();
  });
});
