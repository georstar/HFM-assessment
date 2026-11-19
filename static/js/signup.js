"use strict";

(function () {
  const form = document.getElementById("signup-form");
  const configElement = document.getElementById("signup-config");
  if (!form || !configElement) {
    return;
  }

  const config = JSON.parse(configElement.textContent);
  const { countries, messages } = config;

  // Same rules as accounts/validators.py and the model's RegexValidators.
  const NAME_PATTERN = /^\p{L}+(?:[ '\-]\p{L}+)*$/u;
  const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const CODE_PATTERN = /^[0-9]{1,4}$/;
  const PHONE_PATTERN = /^[0-9]{6,15}$/;
  const UPPERCASE_PATTERN = /[A-Z]/;
  const NUMBER_PATTERN = /[0-9]/;
  const SYMBOL_PATTERN = /[^A-Za-z0-9\s]/;

  const countrySelect = form.elements.country;
  const codeInput = form.elements.phone_country_code;

  // ---- Rules: each returns a list of messages, empty when valid ----

  function validateName(input) {
    const name = input.value.trim();
    if (!name) return [messages.required];
    if (name.length < config.nameMinLength) return [messages.nameTooShort];
    if (!NAME_PATTERN.test(name)) return [messages.nameInvalid];
    return [];
  }

  function validateCountry(input) {
    return input.value ? [] : [messages.required];
  }

  function validateCode(input) {
    if (!countrySelect.value) return [];
    const code = input.value.trim();
    if (!code) return [messages.required];
    if (!CODE_PATTERN.test(code)) return [messages.codeNotNumeric];

    const country = countries[countrySelect.value];
    if (country && code !== country.code) {
      return [
        messages.codeMismatch
          .replace("%(country)s", country.name)
          .replace("%(code)s", country.code),
      ];
    }
    return [];
  }

  function validatePhone(input) {
    const phone = input.value.trim();
    if (!phone) return [messages.required];
    if (!PHONE_PATTERN.test(phone)) return [messages.phoneInvalid];
    return [];
  }

  function validateEmail(input) {
    const email = input.value.trim();
    if (!email) return [messages.required];
    if (!EMAIL_PATTERN.test(email)) return [messages.emailInvalid];
    return [];
  }

  function validatePassword(input) {
    const password = input.value;
    if (!password) return [messages.required];

    const errors = [];
    if (password.length < config.passwordMinLength) errors.push(messages.passwordTooShort);
    if (!UPPERCASE_PATTERN.test(password)) errors.push(messages.passwordNoUpper);
    if (!NUMBER_PATTERN.test(password)) errors.push(messages.passwordNoNumber);
    if (!SYMBOL_PATTERN.test(password)) errors.push(messages.passwordNoSymbol);
    return errors;
  }

  function validateTerms(input) {
    return input.checked ? [] : [messages.termsRequired];
  }

  const validators = {
    first_name: validateName,
    last_name: validateName,
    country: validateCountry,
    phone_country_code: validateCode,
    phone_number: validatePhone,
    email: validateEmail,
    password: validatePassword,
    accept_terms: validateTerms,
  };

  // ---- Showing and clearing errors ----

  function showErrors(input, errors) {
    const errorId = `${input.id}_error`;
    let list = document.getElementById(errorId);

    if (errors.length === 0) {
      if (list) list.remove();
      input.removeAttribute("aria-invalid");
      input.removeAttribute("aria-describedby");
      return;
    }

    if (!list) {
      list = document.createElement("ul");
      list.id = errorId;
      list.className = "errorlist";
      input.closest(".field").append(list);    
    }
    list.replaceChildren(
      ...errors.map((message) => {
        const item = document.createElement("li");
        item.textContent = message;
        return item;
      })
    );
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", errorId);
  }

  function validateField(input) {
    const errors = validators[input.name](input);
    showErrors(input, errors);
    return errors.length === 0;
  }

  // ---- Country -> code autofill ----

  function fillCountryCode() {
    const country = countries[countrySelect.value];
    codeInput.value = country ? country.code : "";
    if (codeInput.hasAttribute("aria-invalid")) {
      validateField(codeInput);
    }
  }

  codeInput.readOnly = true;
  countrySelect.addEventListener("change", fillCountryCode);
  if (countrySelect.value) {
    fillCountryCode();
  }

  // ---- When to validate ----

  for (const name of Object.keys(validators)) {
    const input = form.elements[name];

    // Leaving a field: check it, unless it was skipped while still empty.
    input.addEventListener("blur", () => {
      if (input.type !== "checkbox" && input.value.trim() !== "") {
        validateField(input);
      }
    });

    // While fixing a field that already shows an error: re-check as they type.
    input.addEventListener("input", () => {
      if (input.hasAttribute("aria-invalid")) {
        validateField(input);
      }
    });
  }

  form.addEventListener("submit", (event) => {
    let firstInvalid = null;
    for (const name of Object.keys(validators)) {
      const input = form.elements[name];
      if (!validateField(input) && firstInvalid === null) {
        firstInvalid = input;
      }
    }
    if (firstInvalid !== null) {
      event.preventDefault();
      firstInvalid.focus();
    }
  });
})();