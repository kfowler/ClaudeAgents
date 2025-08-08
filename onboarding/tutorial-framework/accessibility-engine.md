# Tutorial Accessibility Engine

## Overview

The Tutorial Accessibility Engine provides comprehensive accessibility support for all onboarding content, ensuring that users with disabilities can successfully learn and use Claude Code 2.0.

## Core Accessibility Features

### Screen Reader Support

#### ARIA Implementation
```html
<!-- Tutorial section structure -->
<main role="main" aria-labelledby="tutorial-title">
  <h1 id="tutorial-title">Module 1: Getting Started with Claude Code 2.0</h1>
  
  <nav aria-label="Tutorial progress" role="navigation">
    <ol class="progress-steps">
      <li aria-current="step" class="current">
        <span class="step-number">1</span>
        <span class="step-title">Setup and Installation</span>
      </li>
      <li class="upcoming">
        <span class="step-number">2</span>
        <span class="step-title">First AI Request</span>
      </li>
    </ol>
  </nav>
  
  <section aria-labelledby="step-title" role="region">
    <h2 id="step-title">Step 1: Setup and Installation</h2>
    <div role="timer" aria-live="polite" aria-atomic="true">
      Estimated time: <span id="time-remaining">5 minutes</span>
    </div>
    
    <div class="tutorial-content" aria-describedby="step-instructions">
      <p id="step-instructions">In this step, you'll install Claude Code 2.0 and enable AI features.</p>
      
      <!-- Interactive code example -->
      <div role="group" aria-labelledby="code-example-title">
        <h3 id="code-example-title">Installation Command</h3>
        <pre role="code" aria-label="Installation command" tabindex="0">
          <code>curl -sSL https://claude.ai/install | bash</code>
        </pre>
        <button type="button" aria-describedby="copy-description" onclick="copyCode()">
          Copy Command
        </button>
        <div id="copy-description" class="sr-only">
          Copies the installation command to your clipboard
        </div>
      </div>
    </div>
    
    <div class="tutorial-actions" role="group" aria-label="Tutorial navigation">
      <button type="button" disabled aria-describedby="prev-disabled">Previous</button>
      <div id="prev-disabled" class="sr-only">Previous step not available - you're at the beginning</div>
      
      <button type="button" onclick="nextStep()" aria-describedby="next-description">
        Next: First AI Request
      </button>
      <div id="next-description" class="sr-only">
        Continue to step 2 where you'll make your first AI-enhanced request
      </div>
    </div>
  </section>
</main>
```

#### Screen Reader Announcements
```javascript
// Screen reader friendly progress updates
function announceProgress(currentStep, totalSteps, stepTitle) {
  const announcement = `Step ${currentStep} of ${totalSteps}: ${stepTitle}`;
  
  // Update live region for screen reader announcement
  document.getElementById('progress-announcement').textContent = announcement;
  
  // Update page title for screen reader navigation
  document.title = `${announcement} - Claude Code 2.0 Tutorial`;
}

// Success announcements
function announceSuccess(message) {
  const successRegion = document.getElementById('success-announcements');
  successRegion.textContent = message;
  
  // Clear after announcement to prevent repetition
  setTimeout(() => {
    successRegion.textContent = '';
  }, 1000);
}

// Error handling with clear descriptions
function announceError(errorType, solution) {
  const errorRegion = document.getElementById('error-announcements');
  errorRegion.innerHTML = `
    <div role="alert">
      <h4>Issue Encountered: ${errorType}</h4>
      <p>Solution: ${solution}</p>
      <p>Press F1 for additional help, or Tab to continue with alternatives.</p>
    </div>
  `;
}
```

### Keyboard Navigation

#### Focus Management
```javascript
class TutorialKeyboardManager {
  constructor() {
    this.trapFocus = false;
    this.focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    this.setupKeyboardShortcuts();
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Tutorial-specific shortcuts
      switch(e.key) {
        case 'F1':
          e.preventDefault();
          this.showContextHelp();
          break;
        case 'Escape':
          e.preventDefault();
          this.closeModals();
          break;
        case 'Enter':
          if (e.target.classList.contains('tutorial-step')) {
            e.preventDefault();
            this.activateStep(e.target);
          }
          break;
        case 'ArrowRight':
          if (e.altKey) {
            e.preventDefault();
            this.nextStep();
          }
          break;
        case 'ArrowLeft':
          if (e.altKey) {
            e.preventDefault();
            this.previousStep();
          }
          break;
      }
    });
  }
  
  trapFocusInDialog(dialogElement) {
    const focusableElements = dialogElement.querySelectorAll(this.focusableElements);
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    dialogElement.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
          }
        } else {
          // Tab
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
          }
        }
      }
    });
    
    firstFocusable.focus();
  }
}
```

#### Skip Links and Shortcuts
```html
<!-- Skip navigation for efficient screen reader use -->
<div class="skip-links">
  <a href="#tutorial-content" class="skip-link">Skip to tutorial content</a>
  <a href="#tutorial-actions" class="skip-link">Skip to tutorial actions</a>
  <a href="#help-resources" class="skip-link">Skip to help resources</a>
</div>

<!-- Keyboard shortcut reference -->
<div id="keyboard-shortcuts" class="help-panel" hidden>
  <h2>Keyboard Shortcuts</h2>
  <dl>
    <dt>F1</dt>
    <dd>Show contextual help for current step</dd>
    
    <dt>Alt + Right Arrow</dt>
    <dd>Go to next tutorial step</dd>
    
    <dt>Alt + Left Arrow</dt>
    <dd>Go to previous tutorial step</dd>
    
    <dt>Escape</dt>
    <dd>Close dialogs and help panels</dd>
    
    <dt>Tab</dt>
    <dd>Navigate to next interactive element</dd>
    
    <dt>Shift + Tab</dt>
    <dd>Navigate to previous interactive element</dd>
  </dl>
  <button type="button" onclick="closeShortcuts()">Close (Escape)</button>
</div>
```

### Visual Accessibility

#### High Contrast and Color Support
```css
/* Base styles with high contrast ratios */
:root {
  --text-primary: #000000;         /* 21:1 contrast on white */
  --text-secondary: #2e2e2e;       /* 12:1 contrast on white */
  --background: #ffffff;
  --accent-primary: #0056b3;       /* 4.5:1 contrast minimum */
  --accent-secondary: #6c757d;
  --success: #155724;              /* 7.4:1 contrast on white */
  --warning: #856404;              /* 4.7:1 contrast on white */
  --error: #721c24;                /* 8.2:1 contrast on white */
  --focus-ring: #005fcc;           /* High contrast focus indicator */
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --text-primary: #000000;
    --background: #ffffff;
    --accent-primary: #0000ff;      /* Pure blue for maximum contrast */
    --focus-ring: #ff0000;          /* Red focus ring for visibility */
  }
  
  .tutorial-step {
    border: 2px solid var(--text-primary);
  }
  
  .tutorial-step:focus {
    outline: 3px solid var(--focus-ring);
    outline-offset: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .tutorial-transition,
  .progress-animation,
  .success-indicator {
    animation: none !important;
    transition: none !important;
  }
  
  .loading-spinner {
    animation: none;
  }
  
  .loading-spinner::after {
    content: "Loading...";
  }
}

/* Focus indicators */
.tutorial-step:focus,
.tutorial-action:focus,
button:focus,
a:focus {
  outline: 3px solid var(--focus-ring);
  outline-offset: 2px;
  box-shadow: 0 0 0 1px var(--background);
}

/* Color blindness support - use patterns in addition to colors */
.status-success::before {
  content: "✓ ";
  font-weight: bold;
}

.status-warning::before {
  content: "⚠ ";
  font-weight: bold;
}

.status-error::before {
  content: "✗ ";
  font-weight: bold;
}
```

#### Text and Typography
```css
/* Readable typography with proper spacing */
.tutorial-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;               /* Minimum readable size */
  line-height: 1.6;              /* Optimal for reading */
  color: var(--text-primary);
  max-width: 70ch;               /* Optimal line length for reading */
}

/* Heading hierarchy for screen readers */
.tutorial-content h1 { font-size: 2.5rem; margin-bottom: 1rem; }
.tutorial-content h2 { font-size: 2rem; margin-bottom: 0.875rem; }
.tutorial-content h3 { font-size: 1.5rem; margin-bottom: 0.75rem; }
.tutorial-content h4 { font-size: 1.25rem; margin-bottom: 0.625rem; }

/* Code blocks with proper contrast */
pre, code {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 0.5rem;
}

pre {
  padding: 1rem;
  overflow-x: auto;
  tab-size: 2;
}

/* Responsive text scaling */
@media (max-width: 768px) {
  .tutorial-content {
    font-size: 18px;              /* Larger on mobile for readability */
  }
}

/* User can override text size */
.text-size-small { font-size: 14px; }
.text-size-medium { font-size: 16px; }
.text-size-large { font-size: 20px; }
.text-size-extra-large { font-size: 24px; }
```

### Motor Accessibility

#### Touch and Click Targets
```css
/* Minimum touch target sizes (44px minimum) */
.tutorial-action,
.progress-step,
button,
.interactive-element {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem 1rem;
  margin: 0.25rem;
  position: relative;
}

/* Increased spacing for motor difficulties */
.motor-assistance .tutorial-action,
.motor-assistance button {
  min-height: 60px;
  min-width: 60px;
  margin: 0.5rem;
}

/* Hover delays for accidental activation prevention */
.tutorial-action {
  transition-delay: 0.1s;
}

.motor-assistance .tutorial-action {
  transition-delay: 0.3s;        /* Longer delay for motor difficulties */
}

/* Drag and drop alternatives */
.drag-alternative {
  display: none;
}

.no-drag .drag-alternative {
  display: block;
}

.no-drag .drag-interface {
  display: none;
}
```

#### Timeout and Timing Controls
```javascript
class TutorialAccessibilityTimer {
  constructor() {
    this.defaultTimeout = 300000;  // 5 minutes default
    this.userTimeout = this.getUserTimeout();
    this.warningTime = 60000;      // 1 minute warning
  }
  
  getUserTimeout() {
    // Check user preferences for extended time
    const userPreference = localStorage.getItem('tutorial-timeout');
    const extendedTime = localStorage.getItem('extended-time-needed');
    
    if (extendedTime === 'true') {
      return this.defaultTimeout * 3;  // 15 minutes for users who need more time
    }
    
    return userPreference ? parseInt(userPreference) : this.defaultTimeout;
  }
  
  startStepTimer(stepId) {
    this.clearExistingTimer();
    
    this.timer = setTimeout(() => {
      this.showTimeWarning(stepId);
    }, this.userTimeout - this.warningTime);
  }
  
  showTimeWarning(stepId) {
    const dialog = document.createElement('div');
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-labelledby', 'timeout-title');
    dialog.setAttribute('aria-describedby', 'timeout-description');
    
    dialog.innerHTML = `
      <h2 id="timeout-title">Time Extension Available</h2>
      <p id="timeout-description">
        You've been working on this step for a while. 
        Would you like more time to complete it?
      </p>
      <button onclick="extendTime()" autofocus>
        Yes, give me more time
      </button>
      <button onclick="continueWithoutExtension()">
        No, I'm ready to continue
      </button>
    `;
    
    document.body.appendChild(dialog);
    this.trapFocusInDialog(dialog);
  }
}
```

### Cognitive Accessibility

#### Content Simplification
```javascript
class CognitiveSupportEngine {
  constructor() {
    this.simplificationLevel = this.getUserSimplificationLevel();
    this.setupProgressTracking();
    this.enableDistrationReduction();
  }
  
  getUserSimplificationLevel() {
    // Check user preferences for cognitive support needs
    return localStorage.getItem('cognitive-support-level') || 'standard';
  }
  
  simplifyContent(element) {
    const level = this.simplificationLevel;
    
    switch(level) {
      case 'maximum':
        this.useSimplestLanguage(element);
        this.breakIntoSmallerSteps(element);
        this.addVisualCues(element);
        this.reduceChoices(element);
        break;
      case 'moderate':
        this.clarifyInstructions(element);
        this.addProgressIndicators(element);
        break;
      case 'standard':
      default:
        // No modifications needed
        break;
    }
  }
  
  useSimplestLanguage(element) {
    // Replace complex terms with simpler alternatives
    const simplifications = {
      'initialize': 'set up',
      'configuration': 'settings',
      'authentication': 'login',
      'repository': 'project folder',
      'deployment': 'publishing your app'
    };
    
    let content = element.innerHTML;
    Object.entries(simplifications).forEach(([complex, simple]) => {
      content = content.replace(new RegExp(complex, 'gi'), simple);
    });
    element.innerHTML = content;
  }
  
  breakIntoSmallerSteps(element) {
    // Find long paragraphs and break them down
    const paragraphs = element.querySelectorAll('p');
    paragraphs.forEach(p => {
      if (p.textContent.length > 100) {
        this.createStepByStepVersion(p);
      }
    });
  }
  
  addVisualCues(element) {
    // Add icons and visual indicators
    const actions = element.querySelectorAll('.action-item');
    actions.forEach(action => {
      const icon = document.createElement('span');
      icon.className = 'visual-cue';
      icon.setAttribute('aria-hidden', 'true');
      icon.textContent = '👉 ';  // Pointing finger for actions
      action.prepend(icon);
    });
  }
  
  reduceChoices(element) {
    // Show fewer options at once for decision-making support
    const choiceGroups = element.querySelectorAll('.choice-group');
    choiceGroups.forEach(group => {
      if (group.children.length > 3) {
        this.createProgressiveDisclosure(group);
      }
    });
  }
}
```

#### Memory and Attention Support
```javascript
// Progress persistence and reminder system
class TutorialMemorySupport {
  constructor() {
    this.savedProgress = this.loadProgress();
    this.setupReminders();
    this.enableBookmarking();
  }
  
  saveProgress(stepId, stepData) {
    this.savedProgress[stepId] = {
      ...stepData,
      timestamp: new Date().toISOString(),
      completed: stepData.completed || false
    };
    
    localStorage.setItem('tutorial-progress', JSON.stringify(this.savedProgress));
    this.announceProgressSaved();
  }
  
  loadProgress() {
    const saved = localStorage.getItem('tutorial-progress');
    return saved ? JSON.parse(saved) : {};
  }
  
  createResumePoint() {
    const currentStep = this.getCurrentStepId();
    const resumeData = {
      stepId: currentStep,
      scrollPosition: window.scrollY,
      formData: this.gatherFormData(),
      userChoices: this.gatherUserChoices()
    };
    
    localStorage.setItem('tutorial-resume-point', JSON.stringify(resumeData));
    
    // Visual indicator that progress is saved
    this.showSaveIndicator();
  }
  
  offerResume() {
    const resumePoint = localStorage.getItem('tutorial-resume-point');
    if (resumePoint) {
      const data = JSON.parse(resumePoint);
      const timeSince = new Date() - new Date(data.timestamp);
      
      if (timeSince < 24 * 60 * 60 * 1000) { // Within 24 hours
        this.showResumeDialog(data);
      }
    }
  }
  
  showResumeDialog(resumeData) {
    const dialog = document.createElement('div');
    dialog.setAttribute('role', 'dialog');
    dialog.innerHTML = `
      <h2>Continue Where You Left Off?</h2>
      <p>We found that you were working on: ${resumeData.stepTitle}</p>
      <p>Would you like to continue from there, or start over?</p>
      <button onclick="resumeFromSave('${resumeData.stepId}')" autofocus>
        Continue from step ${resumeData.stepNumber}
      </button>
      <button onclick="startOver()">
        Start from the beginning
      </button>
    `;
    
    document.body.appendChild(dialog);
  }
}
```

## Implementation Integration

### Tutorial Engine API
```javascript
// Main tutorial accessibility engine
class TutorialAccessibilityEngine {
  constructor(options = {}) {
    this.keyboardManager = new TutorialKeyboardManager();
    this.timerManager = new TutorialAccessibilityTimer();
    this.cognitiveSupport = new CognitiveSupportEngine();
    this.memorySupport = new TutorialMemorySupport();
    
    this.initializeAccessibilityFeatures();
    this.setupUserPreferences();
    this.enableProgressTracking();
  }
  
  initializeAccessibilityFeatures() {
    // Set up live regions for screen reader announcements
    this.createLiveRegions();
    
    // Initialize focus management
    this.keyboardManager.setupInitialFocus();
    
    // Apply user's accessibility preferences
    this.applyUserPreferences();
    
    // Start progress tracking
    this.memorySupport.offerResume();
  }
  
  createLiveRegions() {
    const liveRegions = [
      { id: 'progress-announcement', level: 'polite' },
      { id: 'success-announcements', level: 'polite' },
      { id: 'error-announcements', level: 'assertive' },
      { id: 'help-announcements', level: 'polite' }
    ];
    
    liveRegions.forEach(region => {
      const element = document.createElement('div');
      element.id = region.id;
      element.setAttribute('aria-live', region.level);
      element.setAttribute('aria-atomic', 'true');
      element.className = 'sr-only';
      document.body.appendChild(element);
    });
  }
  
  applyUserPreferences() {
    const preferences = this.getUserPreferences();
    
    // Apply visual preferences
    if (preferences.highContrast) {
      document.body.classList.add('high-contrast');
    }
    
    if (preferences.reducedMotion) {
      document.body.classList.add('reduced-motion');
    }
    
    if (preferences.textSize) {
      document.body.classList.add(`text-size-${preferences.textSize}`);
    }
    
    // Apply motor accessibility preferences
    if (preferences.motorAssistance) {
      document.body.classList.add('motor-assistance');
    }
    
    if (preferences.noDrag) {
      document.body.classList.add('no-drag');
    }
    
    // Apply cognitive support preferences
    if (preferences.cognitiveSupport) {
      this.cognitiveSupport.simplificationLevel = preferences.cognitiveSupport;
      document.body.classList.add(`cognitive-support-${preferences.cognitiveSupport}`);
    }
  }
  
  getUserPreferences() {
    // Load from localStorage with sensible defaults
    const defaults = {
      highContrast: false,
      reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      textSize: 'medium',
      motorAssistance: false,
      noDrag: false,
      cognitiveSupport: 'standard',
      extendedTime: false,
      screenReader: this.detectScreenReader()
    };
    
    const saved = localStorage.getItem('accessibility-preferences');
    return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
  }
  
  detectScreenReader() {
    // Simple screen reader detection
    return !!(
      window.navigator.userAgent.match(/NVDA|JAWS|VoiceOver|TalkBack|Orca/i) ||
      window.speechSynthesis ||
      navigator.userAgent.includes('aural')
    );
  }
  
  // Public API for tutorial developers
  announceToScreenReader(message, priority = 'polite') {
    const regionId = priority === 'assertive' ? 'error-announcements' : 'progress-announcement';
    document.getElementById(regionId).textContent = message;
  }
  
  focusElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.focus();
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  
  saveUserProgress(stepId, data) {
    this.memorySupport.saveProgress(stepId, data);
  }
  
  enableStepTimer(stepId) {
    this.timerManager.startStepTimer(stepId);
  }
}

// Global instance for tutorial pages
window.tutorialAccessibility = new TutorialAccessibilityEngine();
```

## Testing and Validation

### Automated Accessibility Testing
```javascript
// Automated accessibility testing for tutorial content
class TutorialAccessibilityTester {
  constructor() {
    this.axeConfig = {
      tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
      rules: {
        'color-contrast': { enabled: true },
        'keyboard': { enabled: true },
        'focus-order-semantics': { enabled: true }
      }
    };
  }
  
  async testTutorialStep(stepElement) {
    try {
      const results = await axe.run(stepElement, this.axeConfig);
      
      if (results.violations.length > 0) {
        console.error('Accessibility violations found:', results.violations);
        return false;
      }
      
      return this.performManualChecks(stepElement);
    } catch (error) {
      console.error('Accessibility testing failed:', error);
      return false;
    }
  }
  
  performManualChecks(stepElement) {
    const checks = [
      this.checkKeyboardNavigation(stepElement),
      this.checkFocusManagement(stepElement),
      this.checkScreenReaderContent(stepElement),
      this.checkTimingRequirements(stepElement)
    ];
    
    return checks.every(check => check === true);
  }
  
  generateAccessibilityReport(results) {
    return {
      timestamp: new Date().toISOString(),
      passedTests: results.filter(r => r.passed).length,
      failedTests: results.filter(r => !r.passed).length,
      recommendations: this.generateRecommendations(results),
      overallScore: this.calculateAccessibilityScore(results)
    };
  }
}
```

This accessibility engine ensures that all tutorial content is usable by people with diverse abilities while maintaining a high-quality learning experience for everyone.