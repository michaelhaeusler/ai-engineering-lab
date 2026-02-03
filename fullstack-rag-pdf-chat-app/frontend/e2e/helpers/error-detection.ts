/**
 * E2E Test Error Detection Helper
 * 
 * Provides utilities to catch JavaScript runtime errors, console errors,
 * and other issues that could indicate broken functionality during E2E testing.
 */

import { Page } from '@playwright/test';

export interface ErrorCollector {
  consoleErrors: string[]
  pageErrors: string[]
  getErrorSummary: () => string
  hasErrors: () => boolean
}

/**
 * Sets up comprehensive error detection for a Playwright page
 * This will catch:
 * - JavaScript runtime errors (unhandled exceptions)
 * - Console errors
 * - Network request failures (optional)
 */
export function setupErrorDetection(page: Page, options: {
  failOnConsoleError?: boolean
  failOnPageError?: boolean
  ignoreNetworkErrors?: boolean
} = {}): ErrorCollector {

  const consoleErrors: string[] = []
  const pageErrors: string[] = []

  const {
    failOnConsoleError = true,
    failOnPageError = true,
    ignoreNetworkErrors = true
  } = options

  // Capture console errors and warnings
  page.on('console', (msg) => {
    const type = msg.type()
    const text = msg.text()

    // Skip common noise that's not actually errors
    if (text.includes('Download the React DevTools') ||
      text.includes('Warning: ReactDOM.render is no longer supported')) {
      return
    }

    if (type === 'error') {
      consoleErrors.push(`Console Error: ${text}`)
      if (failOnConsoleError) {
        throw new Error(`Console error detected: ${text}`)
      }
    }

    // Also capture warnings that might indicate issues
    if (type === 'warning' && text.includes('Warning:')) {
      consoleErrors.push(`Console Warning: ${text}`)
    }
  })

  // Capture unhandled JavaScript errors
  page.on('pageerror', (error) => {
    const errorMsg = `Unhandled page error: ${error.name}: ${error.message}`
    pageErrors.push(errorMsg)

    if (failOnPageError) {
      throw new Error(errorMsg)
    }
  })

  // Optionally capture request failures
  if (!ignoreNetworkErrors) {
    page.on('requestfailed', (request) => {
      const errorMsg = `Request failed: ${request.method()} ${request.url()} - ${request.failure()?.errorText}`
      consoleErrors.push(errorMsg)
    })
  }

  return {
    consoleErrors,
    pageErrors,
    getErrorSummary: () => {
      const allErrors = [...consoleErrors, ...pageErrors]
      return allErrors.length > 0
        ? `Errors detected:\n${allErrors.join('\n')}`
        : 'No errors detected'
    },
    hasErrors: () => consoleErrors.length > 0 || pageErrors.length > 0
  }
}

/**
 * API Key setup helper for tests
 * Handles the common pattern of entering API key and navigating to main app
 */
export async function setupApiKey(page: Page, apiKey: string = 'sk-test-api-key-for-testing') {
  await page.goto('/')

  // Use type() for WebKit compatibility
  const apiKeyInput = page.getByTestId('api-key-input-field')
  await apiKeyInput.click()
  await apiKeyInput.type(apiKey)

  // Wait for button to be enabled, then click
  const continueButton = page.getByTestId('api-key-continue-button')
  await continueButton.waitFor({ state: 'visible' })
  await continueButton.click()
}
