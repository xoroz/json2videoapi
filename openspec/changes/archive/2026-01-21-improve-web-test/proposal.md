# Change: Improve Web Test

## Why
We need an easy way for non-technical users to test the API through a graphical interface.

## What Changes
- Create `tests/test.html` containing a form to input JSON and trigger video generation.
- Use JavaScript in the browser to handle the POST request and show progress/result.

## Impact
- Affected specs: `testing`
- Affected code: `tests/test.html`
