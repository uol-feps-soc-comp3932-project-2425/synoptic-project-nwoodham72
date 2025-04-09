// Form validation constants
const MIN_TITLE_LENGTH = 10;
const MIN_DESCRIPTION_LENGTH = 100;
const MIN_EXPECTED_LENGTH = 30;
const MIN_ADDITIONAL_COMMENTS_LENGTH = 30;

// DOM elements
let elements = {};

// Initialize the form and all event listeners
document.addEventListener('DOMContentLoaded', function() {
  // Get all form elements
  initializeElements();
  
  // Set up event listeners
  setupFormListeners();
  
  // Remove placeholder options in select fields after selection
  setupSelectPlaceholders();
});

function initializeElements() {
  elements = {
    title: document.getElementById('title'),
    role: document.getElementById('role'),
    page: document.getElementById('page'),
    description: document.getElementById('description'),
    expected: document.getElementById('expected'),
    additionalComments: document.getElementById('additionalComments'),
    submitBtn: document.getElementById('submit-btn'),
    overrideBtn: document.getElementById('override-btn'),
    formStepsInner: document.getElementById('formStepsInner')
  };
}

function setupFormListeners() {
  // Text input field validation
  setupTextFieldValidation(elements.title, MIN_TITLE_LENGTH);
  setupTextFieldValidation(elements.description, MIN_DESCRIPTION_LENGTH);
  setupTextFieldValidation(elements.expected, MIN_EXPECTED_LENGTH);
  setupTextFieldValidation(elements.additionalComments, MIN_ADDITIONAL_COMMENTS_LENGTH);
  
  // Select field validation
  setupSelectFieldValidation(elements.role);
  setupSelectFieldValidation(elements.page);
  
  // Enable submit buttons when expected/additional fields meet requirements
  setupButtonEnabling(elements.expected, elements.submitBtn, MIN_EXPECTED_LENGTH);
  setupButtonEnabling(elements.additionalComments, elements.overrideBtn, MIN_ADDITIONAL_COMMENTS_LENGTH);
}

// Set up validation for text fields
function setupTextFieldValidation(field, minLength) {
  if (!field) return;
  
  // Live validation as user types
  field.addEventListener('input', function() {
    const value = field.value.trim();
    
    if (value.length > 0 && value.length < minLength) {
      field.classList.remove('is-invalid', 'is-valid');
      field.classList.add('is-warning');
    } else if (value.length >= minLength) {
      field.classList.remove('is-invalid', 'is-warning');
      field.classList.add('is-valid');
    } else {
      field.classList.remove('is-invalid', 'is-warning', 'is-valid');
    }
  });
  
  // Validation when user leaves the field
  field.addEventListener('blur', function() {
    const value = field.value.trim();
    if (value.length > 0 && value.length < minLength) {
      field.classList.remove('is-warning');
      field.classList.add('is-invalid');
    }
  });
}

// Set up validation for select fields
function setupSelectFieldValidation(field) {
  if (!field) return;
  
  field.addEventListener('change', function() {
    const value = field.value;
    
    // Check if the value is empty, 'None' or the placeholder (first option)
    if (!value || value === '' || value === 'None' || field.selectedIndex === 0) {
      field.classList.remove('is-valid');
      field.classList.add('is-invalid');
    } else {
      field.classList.remove('is-invalid');
      field.classList.add('is-valid');
    }
  });
}

// Set up buttons to enable when field meets requirements
function setupButtonEnabling(field, button, minLength) {
  if (!field || !button) return;
  
  field.addEventListener('input', function() {
    const value = field.value.trim();
    button.disabled = value.length < minLength;
    
    if (value.length >= minLength) {
      field.classList.remove('is-warning', 'is-invalid');
      field.classList.add('is-valid');
    } else {
      field.classList.remove('is-valid');
      field.classList.add('is-warning');
    }
  });
}

// Remove placeholder options after selection
function setupSelectPlaceholders() {
  document.querySelectorAll('.form-select').forEach(select => {
    select.addEventListener('change', () => {
      const placeholder = select.querySelector("option[value='']");
      if (placeholder && select.value !== "") {
        placeholder.remove();
      }
    });
  });
}

// Step 1 validation and navigation
function validateStep1() {
  let valid = true;
  
  // Validate Title
  if (elements.title.value.trim().length < MIN_TITLE_LENGTH) {
    elements.title.classList.add('is-invalid');
    elements.title.classList.remove('is-valid');
    valid = false;
  } else {
    elements.title.classList.remove('is-invalid');
    elements.title.classList.add('is-valid');
  }
  
  // Validate Role
  // Check for empty, placeholder text, or first option (index 0)
  if (!elements.role.value || elements.role.value === "" || elements.role.value === "None" || elements.role.selectedIndex === 0) {
    elements.role.classList.add('is-invalid');
    elements.role.classList.remove('is-valid');
    valid = false;
  } else {
    elements.role.classList.remove('is-invalid');
    elements.role.classList.add('is-valid');
  }
  
  // Validate Page
  // Check for empty, placeholder text, or first option (index 0)
  if (!elements.page.value || elements.page.value === "" || elements.page.value === "None" || elements.page.selectedIndex === 0) {
    elements.page.classList.add('is-invalid');
    elements.page.classList.remove('is-valid');
    valid = false;
  } else {
    elements.page.classList.remove('is-invalid');
    elements.page.classList.add('is-valid');
  }
  
  // Validate Description
  if (elements.description.value.trim().length < MIN_DESCRIPTION_LENGTH) {
    elements.description.classList.add('is-invalid');
    elements.description.classList.remove('is-valid');
    valid = false;
  } else {
    elements.description.classList.remove('is-invalid');
    elements.description.classList.add('is-valid');
  }
  
  if (valid) {
    nextStep();
  }
}

// Form navigation
function nextStep() {
  elements.formStepsInner.style.transform = 'translateX(-50%)';
}

function prevStep() {
  elements.formStepsInner.style.transform = 'translateX(0)';
}

// Handle additional comments for bug submission
function submitWithExtra() {
  const comment = elements.additionalComments.value.trim();
  const hiddenInput = document.createElement('input');
  hiddenInput.type = 'hidden';
  hiddenInput.name = 'additional_comments';
  hiddenInput.value = comment;
  document.querySelector('form').appendChild(hiddenInput);
  document.querySelector('form').submit();
}