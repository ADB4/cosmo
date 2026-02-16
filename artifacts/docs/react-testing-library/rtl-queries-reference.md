<!--
Topics: React Testing Library queries, getBy, queryBy, findBy, getAllBy, queryAllBy, findAllBy, query priority, getByRole, getByLabelText, getByText, getByPlaceholderText, getByDisplayValue, getByAltText, getByTitle, getByTestId, TextMatch, regex matching, screen queries, accessible queries, semantic queries
Keywords: find element in test, query priority order, which query to use, accessible queries, semantic queries, test id, how to find button, how to find input, how to find text, waiting for element, async queries, query vs get vs find, query selector
-->
# React Testing Library — Queries Reference

<!-- Source: queries-about.md -->



## Overview
<!-- Topics: query types, getBy vs queryBy vs findBy, single vs multiple elements, async queries -->

Queries are the methods that Testing Library gives you to find elements on the
page. There are several [types of queries](#types-of-queries) ("get", "find",
"query"); the difference between them is whether the query will throw an error
if no element is found or if it will return a Promise and retry. Depending on
what page content you are selecting, different queries may be more or less
appropriate. See the [priority guide](#priority) for recommendations on how to
make use of semantic queries to test your page in the most accessible way.

After selecting an element, you can use the
[Events API](dom-testing-library/api-events.mdx) or
[user-event](user-event/intro.mdx) to fire events and simulate user interactions
with the page, or use Jest and [jest-dom](ecosystem-jest-dom.mdx) to make
assertions about the element.

There are Testing Library helper methods that work with queries. As elements
appear and disappear in response to actions,
[Async APIs](dom-testing-library/api-async.mdx) like
[`waitFor`](dom-testing-library/api-async.mdx#waitfor) or
[`findBy` queries](dom-testing-library/api-async.mdx#findby-queries) can be used
to await the changes in the DOM. To find only elements that are children of a
specific element, you can use [`within`](dom-testing-library/api-within.mdx). If
necessary, there are also a few options you can
[configure](dom-testing-library/api-configuration.mdx), like the timeout for
retries and the default testID attribute.

## Example

```jsx

test('should show login form', () => {
  render(<Login />)
  const input = screen.getByLabelText('Username')
  // Events and assertions...
})
```

## Types of Queries
<!-- Topics: getBy, queryBy, findBy, getAllBy, queryAllBy, findAllBy, single element, multiple elements, async queries, error handling -->

- Single Elements
  - `getBy...`: Returns the matching node for a query, and throw a descriptive
    error if no elements match _or_ if more than one match is found (use
    `getAllBy` instead if more than one element is expected).
  - `queryBy...`: Returns the matching node for a query, and return `null` if no
    elements match. This is useful for asserting an element that is not present.
    Throws an error if more than one match is found (use `queryAllBy` instead if
    this is OK).
  - `findBy...`: Returns a Promise which resolves when an element is found which
    matches the given query. The promise is rejected if no element is found or
    if more than one element is found after a default timeout of 1000ms. If you
    need to find more than one element, use `findAllBy`.
- Multiple Elements
  - `getAllBy...`: Returns an array of all matching nodes for a query, and
    throws an error if no elements match.
  - `queryAllBy...`: Returns an array of all matching nodes for a query, and
    return an empty array (`[]`) if no elements match.
  - `findAllBy...`: Returns a promise which resolves to an array of elements
    when any elements are found which match the given query. The promise is
    rejected if no elements are found after a default timeout of `1000`ms.
    - `findBy` methods are a combination of `getBy*` queries and
      [`waitFor`](../dom-testing-library/api-async.mdx#waitfor). They accept the
      `waitFor` options as the last argument (i.e.
      `await screen.findByText('text', queryOptions, waitForOptions)`)




| Type of Query         | 0 Matches     | 1 Match        | >1 Matches   | Retry (Async/Await) |
| --------------------- | ------------- | -------------- | ------------ | :-----------------: |
| **Single Element**    |               |                |              |                     |
| `getBy...`            | Throw error   | Return element | Throw error  |         No          |
| `queryBy...`          | Return `null` | Return element | Throw error  |         No          |
| `findBy...`           | Throw error   | Return element | Throw error  |         Yes         |
| **Multiple Elements** |               |                |              |                     |
| `getAllBy...`         | Throw error   | Return array   | Return array |         No          |
| `queryAllBy...`       | Return `[]`   | Return array   | Return array |         No          |
| `findAllBy...`        | Throw error   | Return array   | Return array |         Yes         |


## Priority
<!-- Topics: query priority order, getByRole, getByLabelText, getByText, getByPlaceholderText, getByDisplayValue, getByAltText, getByTitle, getByTestId, accessible queries, semantic queries, test IDs, which query to use -->

Based on [the Guiding Principles](guiding-principles.mdx), your test should
resemble how users interact with your code (component, page, etc.) as much as
possible. With this in mind, we recommend this order of priority:

1. **Queries Accessible to Everyone** Queries that reflect the experience of
   visual/mouse users as well as those that use assistive technology.
   1. `getByRole`: This can be used to query every element that is exposed in
      the
      [accessibility tree](https://developer.mozilla.org/en-US/docs/Glossary/AOM).
      With the `name` option you can filter the returned elements by their
      [accessible name](https://www.w3.org/TR/accname-1.1/). This should be your
      top preference for just about everything. There's not much you can't get
      with this (if you can't, it's possible your UI is inaccessible). Most
      often, this will be used with the `name` option like so:
      `getByRole('button', {name: /submit/i})`. Check the
      [list of roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques#Roles).
   1. `getByLabelText`: This method is really good for form fields. When
      navigating through a website form, users find elements using label text.
      This method emulates that behavior, so it should be your top preference.
   1. `getByPlaceholderText`:
      [A placeholder is not a substitute for a label](https://www.nngroup.com/articles/form-design-placeholders/).
      But if that's all you have, then it's better than alternatives.
   1. `getByText`: Outside of forms, text content is the main way users find
      elements. This method can be used to find non-interactive elements (like
      divs, spans, and paragraphs).
   1. `getByDisplayValue`: The current value of a form element can be useful
      when navigating a page with filled-in values.
1. **Semantic Queries** HTML5 and ARIA compliant selectors. Note that the user
   experience of interacting with these attributes varies greatly across
   browsers and assistive technology.
   1. `getByAltText`: If your element is one which supports `alt` text (`img`,
      `area`, `input`, and any custom element), then you can use this to find
      that element.
   1. `getByTitle`: The title attribute is not consistently read by
      screenreaders, and is not visible by default for sighted users
1. **Test IDs**
   1. `getByTestId`: The user cannot see (or hear) these, so this is only
      recommended for cases where you can't match by role or text or it doesn't
      make sense (e.g. the text is dynamic).

## Using Queries
<!-- Topics: screen object, container, query options, TextMatch -->

The base queries from DOM Testing Library require you to pass a `container` as
the first argument. Most framework-implementations of Testing Library provide a
pre-bound version of these queries when you render your components with them
which means you _do not have to provide a container_. In addition, if you just
want to query `document.body` then you can use the [`screen`](#screen) export as
demonstrated below (using `screen` is recommended).

The primary argument to a query can be a _string_, _regular expression_, or
_function_. There are also options to adjust how node text is parsed. See
[TextMatch](#textmatch) for documentation on what can be passed to a query.

Given the following DOM elements (which can be rendered by React, Vue, Angular,
or plain HTML code):

```js
<body>
  <div id="app">
    <label for="username-input">Username</label>
    <input id="username-input" />
  </div>
</body>
```

You can use a query to find an element (byLabelText, in this case):

```js

// With screen:
const inputNode1 = screen.getByLabelText('Username')

// Without screen, you need to provide a container:
const container = document.querySelector('#app')
const inputNode2 = getByLabelText(container, 'Username')
```

### `queryOptions`

You can pass a `queryOptions` object with the query type. See the docs for each
query type to see available options, e.g. [byRole API](queries/byrole.mdx#api).

### `screen`

All of the queries exported by DOM Testing Library accept a `container` as the
first argument. Because querying the entire `document.body` is very common, DOM
Testing Library also exports a `screen` object which has every query that is
pre-bound to `document.body` (using the
[`within`](dom-testing-library/api-within.mdx) functionality). Wrappers such as
React Testing Library re-export `screen` so you can use it the same way.

Here's how you use it:


> **Note**
>
> You need a global DOM environment to use `screen`. If you're using jest, with
> the
> [testEnvironment](https://jestjs.io/docs/en/configuration#testenvironment-string)
> set to `jsdom`, a global DOM environment will be available for you.
>
> If you're loading your test with a `script` tag, make sure it comes after the
> `body`. An example can be seen
> [here](https://github.com/testing-library/dom-testing-library/issues/700#issuecomment-692218886).

## `TextMatch`
<!-- Topics: TextMatch, string matching, regex matching, function matching, exact match, substring match, case insensitive -->

Most of the query APIs take a `TextMatch` as an argument, which means the
argument can be either a _string_, _regex_, or a _function_ of signature
`(content?: string, element?: Element | null) => boolean` which returns `true`
for a match and `false` for a mismatch.

### TextMatch Examples

Given the following HTML:

```html
<div>Hello World</div>
```

**_Will_ find the div:**

```javascript
// Matching a string:
screen.getByText('Hello World') // full string match
screen.getByText('llo Worl', {exact: false}) // substring match
screen.getByText('hello world', {exact: false}) // ignore case

// Matching a regex:
screen.getByText(/World/) // substring match
screen.getByText(/world/i) // substring match, ignore case
screen.getByText(/^hello world$/i) // full string match, ignore case
screen.getByText(/Hello W?oRlD/i) // substring match, ignore case, searches for "hello world" or "hello orld"

// Matching with a custom function:
screen.getByText((content, element) => content.startsWith('Hello'))
```

**_Will not_ find the div:**

```javascript
// full string does not match
screen.getByText('Goodbye World')

// case-sensitive regex with different case
screen.getByText(/hello world/)

// function looking for a span when it's actually a div:
screen.getByText((content, element) => {
  return element.tagName.toLowerCase() === 'span' && content.startsWith('Hello')
})
```

### Precision

Queries that take a `TextMatch` also accept an object as the final argument that
can contain options that affect the precision of string matching:

- `exact`: Defaults to `true`; matches full strings, case-sensitive. When false,
  matches substrings and is not case-sensitive.
  - it has no effect when used together with `regex` or `function` arguments.
  - in most cases, using a regex instead of a string combined with `{ exact: false }`
    gives you more control over fuzzy matching so it should be preferred.
- `normalizer`: An optional function which overrides normalization behavior. See
  [`Normalization`](#normalization).

### Normalization

Before running any matching logic against text in the DOM, `DOM Testing Library`
automatically normalizes that text. By default, normalization consists of
trimming whitespace from the start and end of text, and **collapsing multiple
adjacent whitespace characters within the string into a single space**.

If you want to prevent that normalization, or provide alternative normalization
(e.g. to remove Unicode control characters), you can provide a `normalizer`
function in the options object. This function will be given a string and is
expected to return a normalized version of that string.

> **Note**
>
> Specifying a value for `normalizer` _replaces_ the built-in normalization, but
> you can call `getDefaultNormalizer` to obtain a built-in normalizer, either to
> adjust that normalization or to call it from your own normalizer.

`getDefaultNormalizer` takes an options object which allows the selection of
behaviour:

- `trim`: Defaults to `true`. Trims leading and trailing whitespace
- `collapseWhitespace`: Defaults to `true`. Collapses inner whitespace
  (newlines, tabs, repeated spaces) into a single space.

#### Normalization Examples

To perform a match against text without trimming:

```javascript
screen.getByText('text', {
  normalizer: getDefaultNormalizer({trim: false}),
})
```

To override normalization to remove some Unicode characters whilst keeping some
(but not all) of the built-in normalization behavior:

```javascript
screen.getByText('text', {
  normalizer: str =>
    getDefaultNormalizer({trim: false})(str).replace(/[\u200E-\u200F]*/g, ''),
})
```

## Manual Queries
<!-- Topics: querySelector, escape hatch, non-semantic queries, data attributes -->

On top of the queries provided by the testing library, you can use the regular
[`querySelector` DOM API](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector)
to query elements. Note that using this as an escape hatch to query by class or
id is not recommended because they are invisible to the user. Use a testid if
you have to, to make your intention to fall back to non-semantic queries clear
and establish a stable API contract in the HTML.

```jsx
// @testing-library/react
const {container} = render(<MyComponent />)
const foo = container.querySelector('[data-foo="bar"]')
```

## Browser extension

Do you still have problems knowing how to use Testing Library queries?

There is a very cool Browser extension for Chrome named
[Testing Playground](https://chrome.google.com/webstore/detail/testing-playground/hejbmebodbijjdhflfknehhcgaklhano),
and it helps you find the best queries to select elements. It allows you to
inspect the element hierarchies in the Browser's Developer Tools, and provides
you with suggestions on how to select them, while encouraging good testing
practices.

## Playground

If you want to get more familiar with these queries, you can try them out on
[testing-playground.com](https://testing-playground.com). Testing Playground is
an interactive sandbox where you can run different queries against your own
html, and get visual feedback matching the rules mentioned above.

## ByRole
<!-- Topics: getByRole, role queries, accessible name, ARIA roles, accessibility tree, name option -->

<!-- Source: queries-byrole.md -->



> getByRole, queryByRole, getAllByRole, queryAllByRole, findByRole,
> findAllByRole

## API

```typescript
getByRole(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  role: string,
  options?: {
    hidden?: boolean = false,
    name?: TextMatch,
    description?: TextMatch,
    selected?: boolean,
    busy?: boolean,
    checked?: boolean,
    pressed?: boolean,
    suggest?: boolean,
    current?: boolean | string,
    expanded?: boolean,
    queryFallbacks?: boolean,
    level?: number,
    value?: {
      min?: number,
      max?: number,
      now?: number,
      text?: TextMatch,
    }
  }): HTMLElement
```

Queries for elements with the given role (and it also accepts a
[`TextMatch`](queries/about.mdx#textmatch)). Default roles are taken into
consideration e.g. `<button />` has the `button` role without explicitly setting
the `role` attribute. Here you can see
[a table of HTML elements with their default and desired roles](https://www.w3.org/TR/html-aria/#docconformance).

Please note that setting a `role` and/or `aria-*` attribute that matches the
implicit ARIA semantics is unnecessary and is **not recommended** as these
properties are already set by the browser, and we must not use the `role` and
`aria-*` attributes in a manner that conflicts with the semantics described. For
example, a `button` element can't have the `role` attribute of `heading`,
because the `button` element has default characteristics that conflict with the
`heading` role.

> Roles are matched literally by string equality, without inheriting from the
> ARIA role hierarchy. As a result, querying a superclass role like `checkbox`
> will not include elements with a subclass role like `switch`.

You can query the returned element(s) by their
[accessible name or description](https://www.w3.org/TR/accname-1.1/). The
accessible name is for simple cases equal to e.g. the label of a form element,
or the text content of a button, or the value of the `aria-label` attribute. It
can be used to query a specific element if multiple elements with the same role
are present on the rendered content. For an in-depth guide check out
["What is an accessible name?" from TPGi](https://www.tpgi.com/what-is-an-accessible-name/).
If you only query for a single element with `getByText('The name')` it's
oftentimes better to use `getByRole(expectedRole, { name: 'The name' })`. The
accessible name query does not replace other queries such as `*ByAlt` or
`*ByTitle`. While the accessible name can be equal to these attributes, it does
not replace the functionality of these attributes. For example
`<img aria-label="fancy image" src="fancy.jpg" />` will be returned for
`getByRole('img', { name: 'fancy image' })`. However, the image will not display
its description if `fancy.jpg` could not be loaded. Whether you want to assert
this functionality in your test or not is up to you.

> **Tip:** input type password

Unfortunately, the spec defines that `<input type="password" />` has no implicit
role. This means that in order to query this type of element we must fallback to
a less powerful query such as [`ByLabelText`](queries/bylabeltext.mdx).



## Options

### `hidden`

If you set `hidden` to `true` elements that are normally excluded from the
accessibility tree are considered for the query as well. The default behavior
follows https://www.w3.org/TR/wai-aria-1.2/#tree_exclusion with the exception of
`role="none"` and `role="presentation"` which are considered in the query in any
case. For example in

```html
<body>
  <main aria-hidden="true">
    <button>Open dialog</button>
  </main>
  <div role="dialog">
    <button>Close dialog</button>
  </div>
</body>
```

`getByRole('button')` would only return the `Close dialog`-button. To make
assertions about the `Open dialog`-button you would need to use
`getAllByRole('button', { hidden: true })`.

The default value for `hidden` can
[be configured](../dom-testing-library/api-configuration.mdx#configuration).

### `selected`

You can filter the returned elements by their selected state by setting
`selected: true` or `selected: false`.

For example in

```html
<body>
  <div role="tablist">
    <button role="tab" aria-selected="true">Native</button>
    <button role="tab" aria-selected="false">React</button>
    <button role="tab" aria-selected="false">Cypress</button>
  </div>
</body>
```

you can get the "Native"-tab by calling `getByRole('tab', { selected: true })`.
To learn more about the selected state and which elements can have this state
see [ARIA `aria-selected`](https://www.w3.org/TR/wai-aria-1.2/#aria-selected).

### `busy`

You can filter the returned elements by their busy state by setting `busy: true`
or `busy: false`.

For example in

```html
<body>
  <section>
    <div role="alert" aria-busy="false">Login failed</div>
    <div role="alert" aria-busy="true">Error: Loading message...</div>
  </section>
</body>
```

you can get the "Login failed" alert by calling
`getByRole('alert', { busy: false })`. To learn more about the busy state see
[ARIA `aria-busy`](https://www.w3.org/TR/wai-aria-1.2/#aria-busy) and
[MDN `aria-busy` attribute](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-busy).

### `checked`

You can filter the returned elements by their checked state by setting
`checked: true` or `checked: false`.

For example in

```html
<body>
  <section>
    <button role="checkbox" aria-checked="true">Sugar</button>
    <button role="checkbox" aria-checked="false">Gummy bears</button>
    <button role="checkbox" aria-checked="false">Whipped cream</button>
  </section>
</body>
```

you can get the "Sugar" option by calling
`getByRole('checkbox', { checked: true })`. To learn more about the checked
state and which elements can have this state see
[ARIA `aria-checked`](https://www.w3.org/TR/wai-aria-1.2/#aria-checked).

> **Note**
>
> Checkboxes have a "mixed" state, which is considered neither checked nor
> unchecked (details [here](https://www.w3.org/TR/html-aam-1.0/#details-id-56)).

### `current`

You can filter the returned elements by their current state by setting
`current: boolean | string`. Note that no `aria-current` attribute will match
`current: false` since `false` is the default value for `aria-current`.

For example in

```html
<body>
  <nav>
    <a href="current/page" aria-current="page">👍</a>
    <a href="another/page">👎</a>
  </nav>
</body>
```

you can get the "👍" link by calling `getByRole('link', { current: 'page' })`
and the "👎" by calling `getByRole('link', { current: false })`. To learn more
about the current state see
[ARIA `aria-current`](https://www.w3.org/TR/wai-aria-1.2/#aria-current).

### `pressed`

Buttons can have a pressed state. You can filter the returned elements by their
pressed state by setting `pressed: true` or `pressed: false`.

For example in

```html
<body>
  <section>
    <button aria-pressed="true">👍</button>
    <button aria-pressed="false">👎</button>
  </section>
</body>
```

you can get the "👍" button by calling `getByRole('button', { pressed: true })`.
To learn more about the pressed state see
[ARIA `aria-pressed`](https://www.w3.org/TR/wai-aria-1.2/#aria-pressed).

### `suggest`

You can disable the ability to
[throw suggestions](../dom-testing-library/api-configuration.mdx#throwsuggestions-experimental)
for a specific query by setting this value to `false`.  
Setting this value to `true` will throw suggestions for the specific query.

### `expanded`

You can filter the returned elements by their expanded state by setting
`expanded: true` or `expanded: false`.

For example in

```html
<body>
  <nav>
    <ul>
      <li>
        <a aria-expanded="false" aria-haspopup="true" href="..."
          >Expandable Menu Item</a
        >
        <ul>
          <li><a href="#">Submenu Item 1</a></li>
          <li><a href="#">Submenu Item 1</a></li>
        </ul>
      </li>
      <li><a href="#">Regular Menu Item</a></li>
    </ul>
  </nav>
</body>
```

you can get the "Expandable Menu Item" link by calling
`getByRole('link', { expanded: false })`. To learn more about the expanded state
and which elements can have this state see
[ARIA `aria-expanded`](https://www.w3.org/TR/wai-aria-1.2/#aria-expanded).

```html
<div role="dialog">...</div>
```


### `queryFallbacks`

By default, it's assumed that the first role of each element is supported, so
only the first role can be queried. If you need to query an element by any of
its fallback roles instead, you can use `queryFallbacks: true`.

For example, `getByRole('switch')` would always match
`<div role="switch checkbox" />` because it's the first role, while
`getByRole('checkbox')` would not. However,
`getByRole('checkbox', { queryFallbacks: true })` would enable all fallback
roles and therefore match the same element.

> An element doesn't have multiple roles in a given environment. It has a single
> one. Multiple roles in the attribute are evaluated from left to right until
> the environment finds the first role it understands. This is useful when new
> roles get introduced and you want to start supporting those as well as older
> environments that don't understand that role (yet).

### `level`

An element with the `heading` role can be queried by any heading level
`getByRole('heading')` or by a specific heading level using the `level` option
`getByRole('heading', { level: 2 })`.

The `level` option queries the element(s) with the `heading` role matching the
indicated level determined by the semantic HTML heading elements `<h1>-<h6>` or
matching the `aria-level` attribute.

Given the example below,

```html
<body>
  <section>
    <h1>Heading Level One</h1>
    <h2>First Heading Level Two</h2>
    <h3>Heading Level Three</h3>
    <div role="heading" aria-level="2">Second Heading Level Two</div>
  </section>
</body>
```

you can query the `Heading Level Three` heading using
`getByRole('heading', { level: 3 })`.

```js
getByRole('heading', {level: 1})
// <h1>Heading Level One</h1>

getAllByRole('heading', {level: 2})
// [
//   <h2>First Heading Level Two</h2>,
//   <div role="heading" aria-level="2">Second Heading Level Two</div>
// ]
```

While it is possible to explicitly set `role="heading"` and `aria-level`
attribute on an element, it is **strongly encouraged** to use the semantic HTML
headings `<h1>-<h6>`.

To learn more about the `aria-level` property, see
[ARIA `aria-level`](https://www.w3.org/TR/wai-aria-1.2/#aria-level).

> The `level` option is _only_ applicable to the `heading` role. An error will
> be thrown when used with any other role.

### `value`

A range widget can be queried by any value `getByRole('spinbutton')` or by a
specific value using the `level` option
`getByRole('spinbutton', { value: { now: 5, min: 0, max: 10, text: 'medium' } })`.

Note that you don't have to specify all properties in `value`. A subset is
sufficient e.g.
`getByRole('spinbutton', { value: { now: 5, text: 'medium' } })`.

Given the example below,

```html
<body>
  <section>
    <button
      role="spinbutton"
      aria-valuenow="5"
      aria-valuemin="0"
      aria-valuemax="10"
      aria-valuetext="medium"
    >
      Volume
    </button>
    <button
      role="spinbutton"
      aria-valuenow="3"
      aria-valuemin="0"
      aria-valuemax="10"
      aria-valuetext="medium"
    >
      Pitch
    </button>
  </section>
</body>
```

you can query specific spinbutton(s) with the following queries,

```js
getByRole('spinbutton', {value: {now: 5}})
// <button>Volume</button>

getAllByRole('spinbutton', {value: {min: 0}})
// [
//   <button>Volume</button>,
//   <button>Pitch</button>
// ]
```

> Every specified property in `value` must match. For example, if you query for
> `{value: {min: 0, now: 3}}` `aria-valuemin` must be equal to 0 **AND** >
> `aria-valuenow` must be equal to 3

> The `value` option is _only_ applicable to certain roles (check the linked MDN
> pages below for applicable roles). An error will be thrown when used with any
> other role.

To learn more about the `aria-value*` properties, see
[MDN `aria-valuemin`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-valuemin),
[MDN `aria-valuemax`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-valuemax),
[MDN `aria-valuenow`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-valuenow),
[MDN `aria-valuetext`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-valuetext).

### `description`

You can filter the returned elements by their
[accessible description](https://www.w3.org/TR/accname-1.1/#mapping_additional_nd_description)
for those cases where you have several elements with the same role and they
be the case for elements with
[alertdialog](https://www.w3.org/TR/wai-aria-1.1/#alertdialog) role, where the
`aria-describedby` attribute is used to describe the element's content.

For example in

```html
<body>
  <ul>
    <li role="alertdialog" aria-describedby="notification-id-1">
      <div><button>Close</button></div>
      <div id="notification-id-1">You have unread emails</div>
    </li>
    <li role="alertdialog" aria-describedby="notification-id-2">
      <div><button>Close</button></div>
      <div id="notification-id-2">Your session is about to expire</div>
    </li>
  </ul>
</body>
```

You can query a specific element like this

```js
getByRole('alertdialog', {description: 'Your session is about to expire'})
```

## Performance

`getByRole` is the most preferred query to use as it most closely resembles the
user experience, however the calculations it must perform to provide this
confidence can be expensive (particularly with large DOM trees).

Where test performance is a concern it may be desirable to trade some of this
confidence for improved performance.

`getByRole` performance can be improved by setting the option
[`hidden`](#hidden) to `true` and thereby avoid expensive visibility checks.
Note that in doing so inaccessible elements will now be included in the result.

Another option may be to substitute `getByRole` for simpler `getByLabelText` and
`getByText` queries which can be significantly faster though less robust
alternatives.

## ByLabelText
<!-- Topics: getByLabelText, form field queries, label text, input labels -->

<!-- Source: queries-bylabeltext.md -->



> getByLabelText, queryByLabelText, getAllByLabelText, queryAllByLabelText,
> findByLabelText, findAllByLabelText

## API

```typescript
getByLabelText(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  text: TextMatch,
  options?: {
    selector?: string = '*',
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

This will search for the label that matches the given
[`TextMatch`](queries/about.mdx#textmatch), then find the element associated
with that label.

The example below will find the input node for the following DOM structures:

```js
// for/htmlFor relationship between label and form element id
<label for="username-input">Username</label>
<input id="username-input" />

// The aria-labelledby attribute with form elements
<label id="username-label">Username</label>
<input aria-labelledby="username-label" />

// Wrapper labels
<label>Username <input /></label>

// Wrapper labels where the label text is in another child element
<label>
  <span>Username</span>
  <input />
</label>

// aria-label attributes
// Take care because this is not a label that users can see on the page,
// so the purpose of your input must be obvious to visual users.
<input aria-label="Username" />
```


## Options

### `name`

The example above does NOT find the input node for label text broken up by
elements. You can use `getByRole('textbox', { name: 'Username' })` instead which
is robust against switching to `aria-label` or `aria-labelledby`.

### `selector`

If it is important that you query a specific element (e.g. an `<input>`) you can
provide a `selector` in the options:

```js
// Multiple elements labelled via aria-labelledby
<label id="username">Username</label>
<input aria-labelledby="username" />
<span aria-labelledby="username">Please enter your username</span>

// Multiple labels with the same text
<label>
  Username
  <input />
</label>
<label>
  Username
  <textarea></textarea>
</label>
```

```js
const inputNode = screen.getByLabelText('Username', {selector: 'input'})
```

> **Note**
>
> `getByLabelText` will not work in the case where a `for` attribute on a
> `<label>` element matches an `id` attribute on a non-form element.

```js
// This case is not valid
// for/htmlFor between label and an element that is not a form element
<section id="photos-section">
  <label for="photos-section">Photos</label>
</section>
```

## ByPlaceholderText
<!-- Topics: getByPlaceholderText, placeholder queries, placeholder text -->

<!-- Source: queries-byplaceholdertext.md -->



> getByPlaceholderText, queryByPlaceholderText, getAllByPlaceholderText,
> queryAllByPlaceholderText, findByPlaceholderText, findAllByPlaceholderText

## API

```typescript
getByPlaceholderText(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  text: TextMatch,
  options?: {
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

This will search for all elements with a placeholder attribute and find one that
matches the given [`TextMatch`](queries/about.mdx#textmatch).

```html
<input placeholder="Username" />
```


> **Note**
>
> A placeholder is not a good substitute for a label so you should generally use
> `getByLabelText` instead.

## Options

[TextMatch](queries/about.mdx#textmatch) options

## ByText
<!-- Topics: getByText, text content queries, find by text, non-interactive elements -->

<!-- Source: queries-bytext.md -->



> getByText, queryByText, getAllByText, queryAllByText, findByText,
> findAllByText

## API

```typescript
getByText(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  text: TextMatch,
  options?: {
    selector?: string = '*',
    exact?: boolean = true,
    ignore?: string|boolean = 'script, style',
    normalizer?: NormalizerFn,
  }): HTMLElement
```

This will search for all elements that have a text node with `textContent`
matching the given [`TextMatch`](queries/about.mdx#textmatch).

```html
<a href="/about">About ℹ️</a>
```


It also works with `input`s whose `type` attribute is either `submit` or
`button`:

```js
<input type="submit" value="Send data" />
```

## Options

[TextMatch](queries/about.mdx#textmatch) options, plus the following:

### `selector`

> **Note**
>
> See [`getByLabelText`](queries/bylabeltext.mdx#selector) for more details on
> how and when to use the `selector` option

### `ignore`

The `ignore` option accepts a query selector. If the
[`node.matches`](https://developer.mozilla.org/en-US/docs/Web/API/Element/matches)
returns true for that selector, the node will be ignored. This defaults to
`'script, style'` because generally you don't want to select these tags, but if
your content is in an inline script file, then the script tag could be returned.

If you'd rather disable this behavior, set `ignore` to `false`.

## ByAltText
<!-- Topics: getByAltText, alt text queries, image alt, area alt, input alt -->

<!-- Source: queries-byalttext.md -->



> getByAltText, queryByAltText, getAllByAltText, queryAllByAltText,
> findByAltText, findAllByAltText

## API

```typescript
getByAltText(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  text: TextMatch,
  options?: {
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

This will return the element (normally an `<img>`) that has the given `alt`
text. Note that it only supports elements which accept an `alt` attribute or
[custom elements](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_custom_elements)
(since we don't know if a custom element implements `alt` or not):
[`<img>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img),
[`<input>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input),
and [`<area>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area)
(intentionally excluding
[`<applet>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/applet)
as it's deprecated).

```html
<img alt="Incredibles 2 Poster" src="/incredibles-2.png" />
```


## Options

[TextMatch](queries/about.mdx#textmatch) options

## ByTitle
<!-- Topics: getByTitle, title attribute queries, title text -->

<!-- Source: queries-bytitle.md -->



> getByTitle, queryByTitle, getAllByTitle, queryAllByTitle, findByTitle,
> findAllByTitle

## API

```typescript
getByTitle(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  title: TextMatch,
  options?: {
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

Returns the element that has the matching `title` attribute.

Will also find a `title` element within an SVG.

```html
<span title="Delete" id="2"></span>
<svg>
  <title>Close</title>
  <g><path /></g>
</svg>
```


## Options

[TextMatch](queries/about.mdx#textmatch) options

## ByDisplayValue
<!-- Topics: getByDisplayValue, form value queries, current value, filled inputs -->

<!-- Source: queries-bydisplayvalue.md -->



> getByDisplayValue, queryByDisplayValue, getAllByDisplayValue,
> queryAllByDisplayValue, findByDisplayValue, findAllByDisplayValue

## API

```typescript
getByDisplayValue(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  value: TextMatch,
  options?: {
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

Returns the `input`, `textarea`, or `select` element that has the matching
display value.

### `input` tags

```html
<input type="text" id="lastName" />
```

```js
document.getElementById('lastName').value = 'Norris'
```


### `textarea` tags

```html
<textarea id="messageTextArea" />
```

```js
document.getElementById('messageTextArea').value = 'Hello World'
```


### `select` tags

In case of `select`, this will search for a `<select>` whose selected `<option>`
matches the given [`TextMatch`](queries/about.mdx#textmatch).

```html
<select>
  <option value="">State</option>
  <option value="AL">Alabama</option>
  <option selected value="AK">Alaska</option>
  <option value="AZ">Arizona</option>
</select>
```


## Options

[TextMatch](queries/about.mdx#textmatch) options

## ByTestId
<!-- Topics: getByTestId, test id queries, data-testid, test identifiers -->

<!-- Source: queries-bytestid.md -->



> getByTestId, queryByTestId, getAllByTestId, queryAllByTestId, findByTestId,
> findAllByTestId

## API

```typescript
getByTestId(
  // If you're using `screen`, then skip the container argument:
  container: HTMLElement,
  text: TextMatch,
  options?: {
    exact?: boolean = true,
    normalizer?: NormalizerFn,
  }): HTMLElement
```

A shortcut to `` container.querySelector(`[data-testid="${yourId}"]`) `` (and it
also accepts a [`TextMatch`](queries/about.mdx#textmatch)).

```html
<div data-testid="custom-element" />
```


> In the spirit of [the guiding principles](guiding-principles.mdx), it is
> recommended to use this only after the other queries don't work for your use
> case. Using data-testid attributes do not resemble how your software is used
> and should be avoided if possible. That said, they are _way_ better than
> querying based on DOM structure or styling css class names. Learn more about
> `data-testid`s from the blog post
> ["Making your UI tests resilient to change"](https://kentcdodds.com/blog/making-your-ui-tests-resilient-to-change)

## Options

[TextMatch](queries/about.mdx#textmatch) options

## Overriding `data-testid`

The `...ByTestId` functions in `DOM Testing Library` use the attribute
`data-testid` by default, following the precedent set by
[React Native Web](https://github.com/testing-library/react-testing-library/issues/1)
which uses a `testID` prop to emit a `data-testid` attribute on the element, and
we recommend you adopt that attribute where possible. But if you already have an
existing codebase that uses a different attribute for this purpose, you can
override this value via
`configure({testIdAttribute: 'data-my-test-attribute'})`.
