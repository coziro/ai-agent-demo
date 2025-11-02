/**
 * Chainlit IME Support - Phase 1
 *
 * Problem: Enter key during IME composition sends message prematurely on Chrome/Safari macOS
 * Root Cause: React's async state updates conflicting with browser IME event ordering
 * Solution: Intercept Enter key in capture phase during IME composition only
 *
 * Approach: Classi method (simple) + Triple safety detection
 * - Maintains Enter-to-send functionality (after IME composition completes)
 * - Blocks Enter only during IME composition
 *
 * Reference: https://tech.classi.jp/entry/2024/04/23/183000
 */

(function() {
  'use strict';

  console.log('[Chainlit IME Fix] Custom JS loaded');

  // Track IME state with global variable (most reliable)
  let isComposing = false;

  // compositionstart: IME composition begins
  document.addEventListener('compositionstart', function(e) {
    isComposing = true;
    console.log('[IME Fix] Composition started');
  }, true);

  // compositionend: IME composition ends
  document.addEventListener('compositionend', function(e) {
    isComposing = false;
    console.log('[IME Fix] Composition ended');
  }, true);

  // keydown: Intercept Enter key in capture phase
  document.addEventListener('keydown', function(e) {
    // Triple safety detection for IME composition state
    if (
      e.key === 'Enter' && (
        isComposing ||           // Custom flag (most reliable)
        e.isComposing ||         // Standard property (Chrome/Firefox)
        e.keyCode === 229        // Safari workaround (deprecated but necessary)
      )
    ) {
      console.log('[IME Fix] Blocked Enter during IME composition', {
        isComposing: isComposing,
        'e.isComposing': e.isComposing,
        'e.keyCode': e.keyCode
      });
      e.preventDefault();
      e.stopImmediatePropagation();
      return false;
    }
  }, true); // ← Capture phase (critical!)

  console.log('[Chainlit IME Fix] Event listeners registered');
})();
