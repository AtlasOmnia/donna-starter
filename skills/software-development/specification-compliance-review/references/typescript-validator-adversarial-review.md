# TypeScript validator adversarial review notes

Use this reference when reviewing a recursive JSON-schema-like validator that accepts `unknown` JavaScript values.

## Hidden-own-property reproduction

A validator that uses `Object.keys(value)` for closed-object checks ignores non-enumerable own properties:

```ts
const plan = { version: 1, outcome: "inspect", reason: "x", reads: [] };
Object.defineProperty(plan, "operations", {
  value: [{ kind: "write_values" }],
  enumerable: false,
});
```

The validator must reject this as a forbidden cross-outcome field. Repeat the probe on a nested closed object with an unknown hidden field. Decide explicitly whether symbol properties are rejected and include them in enumeration if the input boundary is broader than parsed JSON.

## Bounds proof

Source branches for `maxErrors` and `maxDepth` are not proof. Add tests that:

1. construct more independent failures than the configured error cap;
2. assert the returned errors are capped, content-free, and canonically ordered;
3. exercise the deepest schema/reference path and a controlled recursive-reference fixture where supported;
4. verify the validator returns a structured failure rather than throwing or recursing indefinitely.

## Canonical ordering

Do not use default `localeCompare()` for a protocol-facing error order. Locale and ICU data can vary across hosts. Use a locale-independent comparator and include paths containing non-ASCII names, `/`, and `~` so pointer escaping and ordering are both covered.

## Evidence classification

Classify cap behavior as **implemented and tested**, **implemented but untested**, or **confirmed failure**. A reported green suite does not close a clause that has no adversarial test, and a static source branch does not substitute for a triggerable proof.
