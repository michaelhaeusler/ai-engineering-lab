import { test, expect } from '@playwright/test';

test.describe('Settings Modal', () => {
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

  test('should open settings modal when settings button is clicked', async ({ page }) => {
    // Click settings button
    await page.getByTestId('header-settings-button').click();

    // Should see settings modal
    await expect(page.getByText('Settings')).toBeVisible();
    await expect(page.getByText('Language Model')).toBeVisible();
    await expect(page.getByText('Theme Color')).toBeVisible();
  });

  test('should show available models in settings', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Should see model options - use test IDs
    await expect(page.getByTestId('settings-model-gpt-4o-mini')).toBeVisible();
    await expect(page.getByTestId('settings-model-gpt-4o')).toBeVisible();
    await expect(page.getByTestId('settings-model-gpt-3.5-turbo')).toBeVisible();
  });

  test('should show available colors in settings', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Should see color options - use test IDs
    await expect(page.getByTestId('settings-color-blue')).toBeVisible();
    await expect(page.getByTestId('settings-color-emerald')).toBeVisible();
    await expect(page.getByTestId('settings-color-purple')).toBeVisible();
  });

  test('should allow model selection', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Click on GPT-4o model - use test ID
    await page.getByTestId('settings-model-gpt-4o').click();

    // Should be selected (visual indication)
    const gpt4Button = page.getByTestId('settings-model-gpt-4o');
    await expect(gpt4Button).toHaveClass(/border-.*-300/);
  });

  test('should allow color selection', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Click on Purple color - use test ID
    await page.getByTestId('settings-color-purple').click();

    // Should be selected (visual indication)
    const purpleButton = page.getByTestId('settings-color-purple');
    await expect(purpleButton).toHaveClass(/border-purple-300/);
  });

  test('should close settings modal when done button is clicked', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Click done button - use test ID
    await page.getByTestId('settings-modal-done-button').click();

    // Settings modal should be closed
    await expect(page.getByText('Language Model')).not.toBeVisible();
  });

  test('should close settings modal when X button is clicked', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Click X button - use test ID
    await page.getByTestId('settings-modal-close-button').click();

    // Settings modal should be closed
    await expect(page.getByText('Language Model')).not.toBeVisible();
  });

  test('should persist color selection after modal close', async ({ page }) => {
    await page.getByTestId('header-settings-button').click();

    // Select blue color - use test ID
    await page.getByTestId('settings-color-blue').click();
    await page.getByTestId('settings-modal-done-button').click();

    // Reopen settings
    await page.getByTestId('header-settings-button').click();

    // Blue should still be selected
    const blueButton = page.getByTestId('settings-color-blue');
    await expect(blueButton).toHaveClass(/border-blue-300/);
  });
});
