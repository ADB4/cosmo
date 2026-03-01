<!--
Topics: React Testing Library API, render, cleanup, act, renderHook, screen, rerender, unmount, container, baseElement, wrapper, configure, within, guiding principles, setup, disappearance, waitFor, waitForElementToBeRemoved, cheatsheet, FAQ
Keywords: render component, test react component, rtl api, screen object, rerender component, test hooks, renderHook, waitFor, wait for element, cleanup, act, test wrapper, testing library setup
-->
# React Testing Library — Core Reference

<!-- Source: guiding-principles.md -->

sidebar_label: Guiding Principles

> [The more your tests resemble the way your software is used, the more
> confidence they can give you.][guiding-principle]

We try to only expose methods and utilities that encourage you to write tests
that closely resemble how your web pages are used.

Utilities are included in this project based on the following guiding
principles:

1.  If it relates to rendering components, then it should deal with DOM nodes
    rather than component instances, and it should not encourage dealing with
    component instances.
2.  It should be generally useful for testing the application components in the
    way the user would use it. We _are_ making some trade-offs here because
    we're using a computer and often a simulated browser environment, but in
    general, utilities should encourage tests that use the components the way
    they're intended to be used.
3.  Utility implementations and APIs should be simple and flexible.

At the end of the day, what we want is for this library to be pretty
light-weight, simple, and understandable.

<!--
Links:
-->

<!-- prettier-ignore-start -->

[guiding-principle]: https://twitter.com/kentcdodds/status/977018512689455106

<!-- prettier-ignore-end -->

## API
<!-- Topics: render, screen, cleanup, act, renderHook, rerender, unmount, container, within, configure -->

<!-- Source: react-api.md -->


`React Testing Library` re-exports everything from `DOM Testing Library` as well
as these methods:

- [`render`](#render)
- [`render` Options](#render-options)
  - [`container`](#container)
  - [`baseElement`](#baseelement)
  - [`hydrate`](#hydrate)
  - [`legacyRoot`](#legacyroot)
  - [`onCaughtError`](#oncaughterror)
  - [`onRecoverableError`](#onrecoverableerror)
  - [`wrapper`](#wrapper)
  - [`queries`](#queries)
  - [`reactStrictMode`](#render-options-reactstrictmode)
- [`render` Result](#render-result)
  - [`...queries`](#queries-1)
  - [`container`](#container-1)
  - [`baseElement`](#baseelement-1)
  - [`debug`](#debug)
  - [`rerender`](#rerender)
  - [`unmount`](#unmount)
  - [`asFragment`](#asfragment)
- [`cleanup`](#cleanup)
- [`act`](#act)
- [`renderHook`](#renderhook)
- [`renderHook` Options](#renderhook-options)
  - [`initialProps`](#initialprops)
  - [`onCaughtError`](#oncaughterror)
  - [`onRecoverableError`](#onrecoverableerror)
  - [`wrapper`](#renderhook-options-wrapper)
  - [`reactStrictMode`](#renderhook-options-reactstrictmode)
- [`renderHook` Result](#renderhook-result)
  - [`result`](#result)
  - [`rerender`](#rerender-1)
  - [`unmount`](#unmount-1)
- [`configure`](#configure)
- [`configure` Options](#configure-options)


## `render`

```typescript
function render(
  ui: React.ReactElement<any>,
  options?: {
    /* You won't often use this, expand below for docs on options */
  },
): RenderResult
```

Render into a container which is appended to `document.body`.

```jsx

render(<div />)
```

```jsx
import '@testing-library/jest-dom'

test('renders a message', () => {
  const {asFragment, getByText} = render(<Greeting />)
  expect(getByText('Hello, world!')).toBeInTheDocument()
  expect(asFragment()).toMatchInlineSnapshot(`
    <h1>Hello, World!</h1>
  `)
})
```

## `render` Options

You won't often need to specify options, but if you ever do, here are the
available options which you could provide as a second argument to `render`.

### `container`

By default, `React Testing Library` will create a `div` and append that `div` to
the `document.body` and this is where your React component will be rendered. If
you provide your own HTMLElement `container` via this option, it will not be
appended to the `document.body` automatically.

For example: If you are unit testing a `tablebody` element, it cannot be a child
of a `div`. In this case, you can specify a `table` as the render `container`.

```jsx
const table = document.createElement('table')

const {container} = render(<TableBody {...props} />, {
  container: document.body.appendChild(table),
})
```

### `baseElement`

If the `container` is specified, then this defaults to that, otherwise this
defaults to `document.body`. This is used as the base element for the queries as
well as what is printed when you use `debug()`.

### `hydrate`

If hydrate is set to true, then it will render with
[ReactDOM.hydrate](https://react.dev/reference/react-dom/hydrate#hydrate). This may be
useful if you are using server-side rendering and use ReactDOM.hydrate to mount
your components.

### `legacyRoot`

> **Warning:**

This option is only available when tests run with React 18 and earlier.



By default we'll render with support for concurrent features (i.e.
[`ReactDOMClient.createRoot`](https://react.dev/reference/react-dom/client/createRoot)).
However, if you're dealing with a legacy app that requires rendering like in
React 17 (i.e.
[`ReactDOM.render`](https://react.dev/reference/react-dom/render)) then you
should enable this option by setting `legacyRoot: true`.

### `onCaughtError`

Callback called when React catches an error in an Error Boundary.
Behaves the same as [`onCaughtError` in `ReactDOMClient.createRoot`](https://react.dev/reference/react-dom/client/createRoot#parameters).

### `onRecoverableError`

Callback called when React automatically recovers from errors. 
Behaves the same as [`onRecoverableError` in `ReactDOMClient.createRoot`](https://react.dev/reference/react-dom/client/createRoot#parameters).

### `wrapper`

Pass a React Component as the `wrapper` option to have it rendered around the
inner element. This is most useful for creating reusable custom render functions
for common data providers. See [setup](setup.mdx#custom-render) for examples.

### `queries`

Queries to bind. Overrides the default set from `DOM Testing Library` unless
merged.

```jsx
// Example, a function to traverse table contents

const {getByRowColumn, getByText} = render(<MyTable />, {
  queries: {...queries, ...tableQueries},
})
```

See [helpers](dom-testing-library/api-custom-queries.mdx) for guidance on using
utility functions to create custom queries.

Custom queries can also be added globally by following the
[custom render guide](setup.mdx#custom-render).

### `render` Options `reactStrictMode`

When enabled, [`<StrictMode>`](https://react.dev/reference/react/StrictMode) is rendered around the inner element.
If defined, overrides the value of `reactStrictMode` set in [`configure`](https://testing-library.com/docs/react-testing-library/api/#configure-options).

## `render` Result

The `render` method returns an object that has a few properties:

### `...queries`

The most important feature of `render` is that the queries from
[DOM Testing Library](queries/about.mdx) are automatically returned with their
first argument bound to the [baseElement](#baseelement), which defaults to
`document.body`.

See [Queries](queries/about.mdx) for a complete list.

**Example**

```jsx
const {getByLabelText, queryAllByTestId} = render(<Component />)
```

### `container`

The containing DOM node of your rendered React Element (rendered using
`ReactDOM.render`). It's a `div`. This is a regular DOM node, so you can call
`container.querySelector` etc. to inspect the children.

> Tip: To get the root element of your rendered element, use
> `container.firstChild`.
>
> NOTE: When that root element is a
> [React Fragment](https://react.dev/reference/react/Fragment),
> `container.firstChild` will only get the first child of that Fragment, not the
> Fragment itself.

> 🚨 If you find yourself using `container` to query for rendered elements then
> you should reconsider! The other queries are designed to be more resilient to
> changes that will be made to the component you're testing. Avoid using
> `container` to query for elements!

### `baseElement`

The containing DOM node where your React Element is rendered in the container.
If you don't specify the `baseElement` in the options of `render`, it will
default to `document.body`.

This is useful when the component you want to test renders something outside the
container div, e.g. when you want to snapshot test your portal component which
renders its HTML directly in the body.

> Note: the queries returned by the `render` looks into baseElement, so you can
> use queries to test your portal component without the baseElement.

### `debug`

> NOTE: It's recommended to use [`screen.debug`](queries/about.mdx#screendebug)
> instead.

This method is a shortcut for `console.log(prettyDOM(baseElement))`.

```jsx

const HelloWorld = () => <h1>Hello World</h1>
const {debug} = render(<HelloWorld />)
debug()
// <div>
//   <h1>Hello World</h1>
// </div>
// you can also pass an element: debug(getByTestId('messages'))
// and you can pass all the same arguments to debug as you can
// to prettyDOM:
// const maxLengthToPrint = 10000
// debug(getByTestId('messages'), maxLengthToPrint, {highlight: false})
```

This is a simple wrapper around `prettyDOM` which is also exposed and comes from
[`DOM Testing Library`](dom-testing-library/api-debugging.mdx#prettydom).

### `rerender`

It'd probably be better if you test the component that's doing the prop updating
to ensure that the props are being updated correctly (see
[the Guiding Principles section](guiding-principles.mdx)). That said, if you'd
prefer to update the props of a rendered component in your test, this function
can be used to update props of the rendered component.

```jsx

const {rerender} = render(<NumberDisplay number={1} />)

// re-render the same component with different props
rerender(<NumberDisplay number={2} />)
```

[See the examples page](example-update-props.mdx)

### `unmount`

This will cause the rendered component to be unmounted. This is useful for
testing what happens when your component is removed from the page (like testing
that you don't leave event handlers hanging around causing memory leaks).

> This method is a pretty small abstraction over
> `ReactDOM.unmountComponentAtNode`

```jsx

const {container, unmount} = render(<Login />)
unmount()
// your component has been unmounted and now: container.innerHTML === ''
```

### `asFragment`

Returns a `DocumentFragment` of your rendered component. This can be useful if
you need to avoid live bindings and see how your component reacts to events.

```jsx

const TestComponent = () => {
  const [count, setCounter] = useState(0)

  return (
    <button onClick={() => setCounter(count => count + 1)}>
      Click to increase: {count}
    </button>
  )
}

const {getByText, asFragment} = render(<TestComponent />)
const firstRender = asFragment()

fireEvent.click(getByText(/Click to increase/))

// This will snapshot only the difference between the first render, and the
// state of the DOM after the click event.
// See https://github.com/jest-community/snapshot-diff
expect(firstRender).toMatchDiffSnapshot(asFragment())
```


## `cleanup`

Unmounts React trees that were mounted with [render](#render).

> This is called automatically if your testing framework (such as mocha, Jest or
> Jasmine) injects a global `afterEach()` function into the testing environment.
> If not, you will need to call `cleanup()` after each test.

For example, if you're using the [ava](https://github.com/avajs/ava) testing
framework, then you would need to use the `test.afterEach` hook like so:

```jsx

test.afterEach(cleanup)

test('renders into document', () => {
  render(<div />)
  // ...
})

// ... more tests ...
```

Failing to call `cleanup` when you've called `render` could result in a memory
leak and tests which are not "idempotent" (which can lead to difficult to debug
errors in your tests).


## `act`

This is a light wrapper around the
[`react` `act` function](https://react.dev/reference/react/act).
All it does is forward all arguments to the act function if your version of
react supports `act`. It is recommended to use the import from
`@testing-library/react` over `react` for consistency reasons.

## `renderHook`

This is a convenience wrapper around `render` with a custom test component. The
API emerged from a popular testing pattern and is mostly interesting for
libraries publishing hooks. You should prefer `render` since a custom test
component results in more readable and robust tests since the thing you want to
test is not hidden behind an abstraction.

```typescript
function renderHook<
  Result,
  Props,
  Q extends Queries = typeof queries,
  Container extends Element | DocumentFragment = HTMLElement,
  BaseElement extends Element | DocumentFragment = Container
>(
  render: (initialProps: Props) => Result,
  options?: RenderHookOptions<Props, Q, Container, BaseElement>,
): RenderHookResult<Result, Props>
```

Example:

```jsx

test('returns logged in user', () => {
  const {result} = renderHook(() => useLoggedInUser())
  expect(result.current).toEqual({name: 'Alice'})
})
```

## `renderHook` Options

### `renderHook` Options `initialProps`

Declares the props that are passed to the render-callback when first invoked.
These will **not** be passed if you call `rerender` without props.

```jsx

test('returns logged in user', () => {
  const {result, rerender} = renderHook((props = {}) => props, {
    initialProps: {name: 'Alice'},
  })
  expect(result.current).toEqual({name: 'Alice'})
  rerender()
  expect(result.current).toEqual({name: undefined})
})
```

> NOTE: When using `renderHook` in conjunction with the `wrapper` and
> `initialProps` options, the `initialProps` are not passed to the `wrapper`
> component. To provide props to the `wrapper` component, consider a solution
> like this:
>
> ```js
> const createWrapper = (Wrapper, props) => {
>   return function CreatedWrapper({ children }) {
>     return <Wrapper {...props}>{children}</Wrapper>;
>   };
> };
>
> ...
>
> {
>   wrapper: createWrapper(Wrapper, { value: 'foo' }),
> }
> ```

### `onCaughtError`

Callback called when React catches an error in an Error Boundary.
Behaves the same as [`onCaughtError` in `ReactDOMClient.createRoot`](https://react.dev/reference/react-dom/client/createRoot#parameters).

### `onRecoverableError`

Callback called when React automatically recovers from errors. 
Behaves the same as [`onRecoverableError` in `ReactDOMClient.createRoot`](https://react.dev/reference/react-dom/client/createRoot#parameters).

### `renderHook` Options `wrapper`

See [`wrapper` option for `render`](#wrapper)


### `renderHook` Options `reactStrictMode`

See [`reactStrictMode` option for `render`](#render-options-reactstrictmode)

## `renderHook` Result

The `renderHook` method returns an object that has a few properties:

### `result`

Holds the value of the most recently **committed** return value of the
render-callback:

```jsx

const {result} = renderHook(() => {
  const [name, setName] = useState('')
  React.useEffect(() => {
    setName('Alice')
  }, [])

  return name
})

expect(result.current).toBe('Alice')
```

Note that the value is held in `result.current`. Think of `result` as a
[ref](https://react.dev/learn/referencing-values-with-refs) for the most recently
**committed** value.

### `rerender`

Renders the previously rendered render-callback with the new props:

```jsx

const {rerender} = renderHook(({name = 'Alice'} = {}) => name)

// re-render the same hook with different props
rerender({name: 'Bob'})
```

### `unmount`

Unmounts the test hook.

```jsx

const {unmount} = renderHook(({name = 'Alice'} = {}) => name)

unmount()
```

## `configure`

Changes global options. Basic usage can be seen at
[Configuration Options](dom-testing-library/api-configuration.mdx).

React Testing Library also has dedicated options.

```typescript

configure({reactStrictMode: true})
```

## `configure` Options

### `reactStrictMode`

When enabled, [`<StrictMode>`](https://react.dev/reference/react/StrictMode) is
rendered around the inner element. Defaults to `false`.

This setting can be changed for a single test by providing `reactStrictMode` in the options argument of the [`render`](#render-options-reactstrictmode) function. 
## Setup
<!-- Topics: React Testing Library setup, installation, configuration, test environment -->

<!-- Source: react-setup.md -->

sidebar_label: Setup


`React Testing Library` does not require any configuration to be used. However,
there are some things you can do when configuring your testing framework to
reduce some boilerplate. In these docs we'll demonstrate configuring Jest, but
you should be able to do similar things with
[any testing framework](#using-without-jest) (React Testing Library does not
require that you use Jest).

## Global Config

Adding options to your global test config can simplify the setup and teardown of
tests in individual files.

## Custom Render

It's often useful to define a custom render method that includes things like
global context providers, data stores, etc. To make this available globally, one
approach is to define a utility file that re-exports everything from
`React Testing Library`. You can replace React Testing Library with this file in
all your imports. See [below](#configuring-jest-with-test-utils) for a way to
make your test util file accessible without using relative paths.

The example below sets up data providers using the [`wrapper`](api.mdx#wrapper)
option to `render`.


> **Note**
>
> Babel versions lower than 7 throw an error when trying to override the named
> export in the example above. See
> [#169](https://github.com/testing-library/react-testing-library/issues/169)
> and the workaround below.



You can use CommonJS modules instead of ES modules, which should work in Node:

```js title="test-utils.js"
const rtl = require('@testing-library/react')

const customRender = (ui, options) =>
  rtl.render(ui, {
    myDefaultOption: 'something',
    ...options,
  })

module.exports = {
  ...rtl,
  render: customRender,
}
```


### Add custom queries

> **Note**
>
> Generally you should not need to create custom queries for
> react-testing-library. Where you do use it, you should consider whether your
> new queries encourage you to test in a user-centric way, without testing
> implementation details.

You can define your own custom queries as described in the
[Custom Queries](dom-testing-library/api-custom-queries.mdx) documentation, or
via the
[`buildQueries`](dom-testing-library/api-custom-queries.mdx#buildqueries)
helper. Then you can use them in any render call using the `queries` option. To
make the custom queries available globally, you can add them to your custom
render method as shown below.

In the example below, a new set of query variants are created for getting
elements by `data-cy`, a "test ID" convention mentioned in the
[Cypress.io](https://docs.cypress.io/guides/references/best-practices.html#Selecting-Elements)
documentation.


You can then override and append the new queries via the render function by
passing a [`queries`](api.mdx#render-options) option.

If you want to add custom queries globally, you can do this by defining your
customized `render`, `screen` and `within` methods:


You can then use your custom queries as you would any other query:

```js
const {getByDataCy} = render(<Component />)

expect(getByDataCy('my-component')).toHaveTextContent('Hello')
```

### Configuring Jest with Test Utils

To make your custom test file accessible in your Jest test files without using
relative imports (`../../test-utils`), add the folder containing the file to the
Jest `moduleDirectories` option.

This will make all the `.js` files in the test-utils directory importable
without `../`.

```diff title="my-component.test.js"
- import { render, fireEvent } from '../test-utils';
+ import { render, fireEvent } from 'test-utils';
```

```diff title="jest.config.js"
module.exports = {
  moduleDirectories: [
    'node_modules',
+   // add the directory with the test-utils.js file, for example:
+   'utils', // a utility folder
+    __dirname, // the root directory
  ],
  // ... other options ...
}
```

If you're using TypeScript, merge this into your `tsconfig.json`. If you're
using Create React App without TypeScript, save this to `jsconfig.json` instead.

```json title="tsconfig.json"
{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "test-utils": ["./utils/test-utils"]
    }
  }
}
```

### Jest 28

If you're using Jest 28 or later, jest-environment-jsdom package now must be
installed separately.

```bash npm2yarn
npm install --save-dev jest-environment-jsdom
```

`jsdom` is also no longer the default environment. You can enable `jsdom`
globally by editing `jest.config.js`:

```diff title="jest.config.js"
 module.exports = {
+  testEnvironment: 'jsdom',
   // ... other options ...
 }
```

Or if you only need `jsdom` in some of your tests, you can enable it as and when
needed using
[docblocks](https://jestjs.io/docs/configuration#testenvironment-string):

```js
/**
 * @jest-environment jsdom
 */
```

### Jest 27

If you're using a recent version of Jest (27), `jsdom` is no longer the default
environment. You can enable `jsdom` globally by editing `jest.config.js`:

```diff title="jest.config.js"
 module.exports = {
+  testEnvironment: 'jest-environment-jsdom',
   // ... other options ...
 }
```

Or if you only need `jsdom` in some of your tests, you can enable it as and when
needed using
[docblocks](https://jestjs.io/docs/configuration#testenvironment-string):

```js
/**
 * @jest-environment jsdom
 */
```

### Jest 24 (or lower) and defaults

If you're using the Jest testing framework version 24 or lower with the default
configuration, it's recommended to use `jest-environment-jsdom-fifteen` package
as Jest uses a version of the jsdom environment that misses some features and
fixes, required by React Testing Library.

First, install `jest-environment-jsdom-fifteen`.

```bash npm2yarn
npm install --save-dev jest-environment-jsdom-fifteen
```

Then specify `jest-environment-jsdom-fifteen` as the `testEnvironment`:

```diff title="jest.config.js"
 module.exports = {
+  testEnvironment: 'jest-environment-jsdom-fifteen',
   // ... other options ...
 }
```

## Using without Jest

If you're running your tests in the browser bundled with webpack (or similar)
then `React Testing Library` should work out of the box for you. However, most
people using React Testing Library are using it with the Jest testing framework
with the `testEnvironment` set to `jest-environment-jsdom` (which is the default
configuration with Jest 26 and earlier).

`jsdom` is a pure JavaScript implementation of the DOM and browser APIs that
runs in Node. If you're not using Jest and you would like to run your tests in
Node, then you must install jsdom yourself. There's also a package called
`global-jsdom` which can be used to setup the global environment to simulate the
browser APIs.

First, install `jsdom` and `global-jsdom`.

```bash npm2yarn
npm install --save-dev jsdom global-jsdom
```

With mocha, the test command would look something like this:

```
mocha --require global-jsdom/register
```

### Skipping Auto Cleanup

[`Cleanup`](api.mdx#cleanup) is called after each test automatically by default
if the testing framework you're using supports the `afterEach` global (like
mocha, Jest, and Jasmine). However, you may choose to skip the auto cleanup by
setting the `RTL_SKIP_AUTO_CLEANUP` env variable to 'true'. You can do this with
[`cross-env`](https://github.com/kentcdodds/cross-env) like so:

```
cross-env RTL_SKIP_AUTO_CLEANUP=true jest
```

To make this even easier, you can also simply import
`@testing-library/react/dont-cleanup-after-each` which will do the same thing.
Just make sure you do this before importing `@testing-library/react`. You could
do this with Jest's `setupFiles` configuration:

```js
{
  // ... other jest config
  setupFiles: ['@testing-library/react/dont-cleanup-after-each']
}
```

Or with mocha's `-r` flag:

```
mocha --require @testing-library/react/dont-cleanup-after-each
```

Alternatively, you could import `@testing-library/react/pure` in all your tests
that you don't want the `cleanup` to run and the `afterEach` won't be setup
automatically.

### Auto Cleanup in Mocha's watch mode

When using Mocha in watch mode, the globally registered cleanup is run only the
first time after each test. Therefore, subsequent runs will most likely fail
with a _TestingLibraryElementError: Found multiple elements_ error.

To enable automatic cleanup in Mocha's watch mode, add a cleanup
[root hook](https://mochajs.org/#root-hook-plugins). Create a
`mocha-watch-cleanup-after-each.js` file with the following contents:

```js title="mocha-watch-cleanup-after-each.js"
const {cleanup} = require('@testing-library/react')

exports.mochaHooks = {
  afterEach() {
    cleanup()
  },
}
```

And register it using mocha's `-r` flag:

```
mocha --require ./mocha-watch-cleanup-after-each.js
```

### Auto Cleanup in Vitest

If you're using Vitest and want automatic cleanup to work, you can
[enable globals](https://vitest.dev/config/#globals) through its configuration
file:

```ts title="vitest.config.ts"

export default defineConfig({
  test: {
    globals: true,
  },
})
```

If you don't want to enable globals, you can import `cleanup` and call it
manually in a top-level `afterEach` hook:

```ts title="vitest.config.ts"

export default defineConfig({
  test: {
    setupFiles: ['vitest-cleanup-after-each.ts'],
  },
})
```

```ts title="vitest-cleanup-after-each.ts"

afterEach(() => {
  cleanup()
})
```

## Appearance and Disappearance
<!-- Topics: waitFor, waitForElementToBeRemoved, findBy queries, async queries, element appearance, element removal -->

<!-- Source: guide-disappearance.md -->


Sometimes you need to test that an element is present and then disappears or
vice versa.

## Waiting for appearance

If you need to wait for an element to appear, the [async wait
utilities][async-api] allow you to wait for an assertion to be satisfied before
proceeding. The wait utilities retry until the query passes or times out. _The
async methods return a Promise, so you must always use `await` or `.then(done)`
when calling them._

### 1. Using `findBy` Queries

```jsx
test('movie title appears', async () => {
  // element is initially not present...
  // wait for appearance and return the element
  const movie = await findByText('the lion king')
})
```

### 2. Using `waitFor`

```jsx
test('movie title appears', async () => {
  // element is initially not present...

  // wait for appearance inside an assertion
  await waitFor(() => {
    expect(getByText('the lion king')).toBeInTheDocument()
  })
})
```

## Waiting for disappearance

The `waitForElementToBeRemoved` [async helper][async-api] function uses a
callback to query for the element on each DOM mutation and resolves to `true`
when the element is removed.

```jsx
test('movie title no longer present in DOM', async () => {
  // element is removed
  await waitForElementToBeRemoved(() => queryByText('the mummy'))
})
```

Using
[`MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
is more efficient than polling the DOM at regular intervals with `waitFor`.

The `waitFor` [async helper][async-api] function retries until the wrapped
function stops throwing an error. This can be used to assert that an element
disappears from the page.

```jsx
test('movie title goes away', async () => {
  // element is initially present...
  // note use of queryBy instead of getBy to return null
  // instead of throwing in the query itself
  await waitFor(() => {
    expect(queryByText('i, robot')).not.toBeInTheDocument()
  })
})
```

## Asserting elements are not present

The standard `getBy` methods throw an error when they can't find an element, so
if you want to make an assertion that an element is _not_ present in the DOM,
you can use `queryBy` APIs instead:

```javascript
const submitButton = screen.queryByText('submit')
expect(submitButton).toBeNull() // it doesn't exist
```

The `queryAll` APIs version return an array of matching nodes. The length of the
array can be useful for assertions after elements are added or removed from the
DOM.

```javascript
const submitButtons = screen.queryAllByText('submit')
expect(submitButtons).toHaveLength(0) // expect no elements
```

### `not.toBeInTheDocument`

The [`jest-dom`](ecosystem-jest-dom.mdx) utility library provides the
`.toBeInTheDocument()` matcher, which can be used to assert that an element is
in the body of the document, or not. This can be more meaningful than asserting
a query result is `null`.

```javascript
import '@testing-library/jest-dom'
// use `queryBy` to avoid throwing an error with `getBy`
const submitButton = screen.queryByText('submit')
expect(submitButton).not.toBeInTheDocument()
```

[async-api]: dom-testing-library/api-async.mdx

## Cheatsheet
<!-- Topics: RTL cheatsheet, common patterns, query examples, testing patterns -->

<!-- Source: react-cheatsheet.md -->


**[Get the printable cheat sheet][cheatsheet]**

A short guide to all the exported functions in `React Testing Library`

- **render** `const {/* */} = render(Component)` returns:
  - `unmount` function to unmount the component
  - `container` reference to the DOM node where the component is mounted
  - all the queries from `DOM Testing Library`, bound to the document so there
    is no need to pass a node as the first argument (usually, you can use the
    `screen` import instead)

```jsx

test('loads items eventually', async () => {
  render(<Page />)

  // Click button
  fireEvent.click(screen.getByText('Load'))

  // Wait for page to update with query text
  const items = await screen.findAllByText(/Item #[0-9]: /)
  expect(items).toHaveLength(10)
})
```

## Queries

> **Difference from DOM Testing Library**
>
> The queries returned from `render` in `React Testing Library` are the same as
> `DOM Testing Library` except they have the first argument bound to the
> document, so instead of `getByText(node, 'text')` you do `getByText('text')`

See [Which query should I use?](queries/about.mdx#priority)

|                | No Match | 1 Match | 1+ Match | Await? |
| -------------- | -------- | ------- | -------- | ------ |
| **getBy**      | throw    | return  | throw    | No     |
| **findBy**     | throw    | return  | throw    | Yes    |
| **queryBy**    | null     | return  | throw    | No     |
| **getAllBy**   | throw    | array   | array    | No     |
| **findAllBy**  | throw    | array   | array    | Yes    |
| **queryAllBy** | []       | array   | array    | No     |

- **ByLabelText** find by label or aria-label text content
  - getByLabelText
  - queryByLabelText
  - getAllByLabelText
  - queryAllByLabelText
  - findByLabelText
  - findAllByLabelText
- **ByPlaceholderText** find by input placeholder value
  - getByPlaceholderText
  - queryByPlaceholderText
  - getAllByPlaceholderText
  - queryAllByPlaceholderText
  - findByPlaceholderText
  - findAllByPlaceholderText
- **ByText** find by element text content
  - getByText
  - queryByText
  - getAllByText
  - queryAllByText
  - findByText
  - findAllByText
- **ByDisplayValue** find by form element current value
  - getByDisplayValue
  - queryByDisplayValue
  - getAllByDisplayValue
  - queryAllByDisplayValue
  - findByDisplayValue
  - findAllByDisplayValue
- **ByAltText** find by img alt attribute
  - getByAltText
  - queryByAltText
  - getAllByAltText
  - queryAllByAltText
  - findByAltText
  - findAllByAltText
- **ByTitle** find by title attribute or svg title tag
  - getByTitle
  - queryByTitle
  - getAllByTitle
  - queryAllByTitle
  - findByTitle
  - findAllByTitle
- **ByRole** find by aria role
  - getByRole
  - queryByRole
  - getAllByRole
  - queryAllByRole
  - findByRole
  - findAllByRole
- **ByTestId** find by data-testid attribute
  - getByTestId
  - queryByTestId
  - getAllByTestId
  - queryAllByTestId
  - findByTestId
  - findAllByTestId

## Async

The [dom-testing-library Async API](dom-testing-library/api-async.mdx) is
re-exported from React Testing Library.

- **waitFor** (Promise) retry the function within until it stops throwing or
  times out
- **waitForElementToBeRemoved** (Promise) retry the function until it no longer
  returns a DOM node

## Events

See [Events API](dom-testing-library/api-events.mdx)

- **fireEvent** trigger DOM event: `fireEvent(node, event)`
- **fireEvent.\*** helpers for default event types
  - **click** `fireEvent.click(node)`
  - [See all supported events](https://github.com/testing-library/dom-testing-library/blob/master/src/event-map.js)
- **act** wrapper around
  [react act](https://react.dev/reference/react/act);
  React Testing Library wraps render and fireEvent in a call to `act` already so
  most cases should not require using it manually

## Other

See [Querying Within Elements](dom-testing-library/api-within.mdx),
[Config API](react-testing-library/api.mdx#configure),
[Cleanup](react-testing-library/api.mdx#cleanup),

- **within** take a node and return an object with all the queries bound to the
  node (used to return the queries from `React Testing Library`'s render
  method): `within(node).getByText("hello")`
- **configure** change global options:
  `configure({testIdAttribute: 'my-data-test-id'})`
- **cleanup** clears the DOM
  ([use with `afterEach`](react-testing-library/api.mdx#cleanup) to reset DOM
  between tests)

## Text Match Options

Given the following HTML:

```html
<div>Hello World</div>
```

**_Will_ find the div:**

```javascript
// Matching a string:
getByText('Hello World') // full string match
getByText('llo Worl', {exact: false}) // substring match
getByText('hello world', {exact: false}) // ignore case

// Matching a regex:
getByText(/World/) // substring match
getByText(/world/i) // substring match, ignore case
getByText(/^hello world$/i) // full string match, ignore case
getByText(/Hello W?oRlD/i) // advanced regex

// Matching with a custom function:
getByText((content, element) => content.startsWith('Hello'))
```

**[Get the printable cheat sheet][cheatsheet]**

[cheatsheet]:
  https://github.com/testing-library/react-testing-library/raw/main/other/cheat-sheet.pdf

## FAQ
<!-- Topics: React Testing Library FAQ, common questions, troubleshooting, best practices -->

<!-- Source: react-faq.md -->


See also the [main FAQ](dom-testing-library/faq.mdx) for questions not specific
to React testing.



TL;DR:
[Go to the `on-change.js` example](https://codesandbox.io/s/github/kentcdodds/react-testing-library-examples/tree/main/?module=%2Fsrc%2F__tests__%2Fon-change.js&previewwindow=tests)

In summary:

```jsx

test('change values via the fireEvent.change method', () => {
  const handleChange = jest.fn()
  const {container} = render(<input type="text" onChange={handleChange} />)
  const input = container.firstChild
  fireEvent.change(input, {target: {value: 'a'}})
  expect(handleChange).toHaveBeenCalledTimes(1)
  expect(input.value).toBe('a')
})

test('select drop-downs must use the fireEvent.change', () => {
  const handleChange = jest.fn()
  const {container} = render(
    <select onChange={handleChange}>
      <option value="1">1</option>
      <option value="2">2</option>
    </select>,
  )
  const select = container.firstChild
  const option1 = container.getElementsByTagName('option').item(0)
  const option2 = container.getElementsByTagName('option').item(1)

  fireEvent.change(select, {target: {value: '2'}})

  expect(handleChange).toHaveBeenCalledTimes(1)
  expect(option1.selected).toBe(false)
  expect(option2.selected).toBe(true)
})

test('checkboxes (and radios) must use fireEvent.click', () => {
  const handleChange = jest.fn()
  const {container} = render(<input type="checkbox" onChange={handleChange} />)
  const checkbox = container.firstChild
  fireEvent.click(checkbox)
  expect(handleChange).toHaveBeenCalledTimes(1)
  expect(checkbox.checked).toBe(true)
})
```

If you've used enzyme or React's TestUtils, you may be accustomed to changing
inputs like so:

```javascript
input.value = 'a'
Simulate.change(input)
```

We can't do this with React Testing Library because React actually keeps track
of any time you assign the `value` property on an `input` and so when you fire
the `change` event, React thinks that the value hasn't actually been changed.

This works for Simulate because they use internal APIs to fire special simulated
events. With React Testing Library, we try to avoid implementation details to
make your tests more resilient.

So we have it worked out for the change event handler to set the property for
you in a way that's not trackable by React. This is why you must pass the value
as part of the `change` method call.




To test if an error boundary successfully catches an error, you should make sure that if the fallback of the boundary is displayed when a child threw.

Here's an example of how you can test an error boundary:

```jsx

class ErrorBoundary extends React.Component {
  state = {error: null}
  static getDerivedStateFromError(error) {
    return {error}
  }
  render() {
    const {error} = this.state
    if (error) {
      return <div>Something went wrong</div>
    }
    return this.props.children
  }
}

test('error boundary catches error', () => {
  const {container} = render(
    <ErrorBoundary>
      <BrokenComponent />
    </ErrorBoundary>,
  )
  expect(container.textContent).toEqual('Something went wrong.')
})
```

If the error boundary did not catch the error, the test would fail since the `render` call would throw the error the Component produced.


info

React 18 will call `console.error` with an extended error message.
React 19 will call `console.warn` with an extended error message.

To disable the additional `console.warn` call in React 19, you can provide a custom `onCaughtError` callback e.g. `render(<App />, {onCaughtError: () => {}})`
`onCaughtError` is not supported in React 18.






Definitely yes! You can write unit and integration tests with this library. See
below for more on how to mock dependencies (because this library intentionally
does NOT support shallow rendering) if you want to unit test a high level
component. The tests in this project show several examples of unit testing with
this library.

As you write your tests, keep in mind:

> The more your tests resemble the way your software is used, the more
> confidence they can give you. - [17 Feb 2018][guiding-principle]




If a component throws during render, the origin of the state update will throw if wrapped in `act`.
By default, `render` and `fireEvent` are wrapped in `act`.
You can just wrap it in a try-catch or use dedicated matchers if your test runner supports these.
For example, in Jest you can use `toThrow`:

```jsx
function Thrower() {
  throw new Error('I throw')
}

test('it throws', () => {
  expect(() => render(<Thrower />)).toThrow('I throw')
})
```

The same applies to Hooks and `renderHook`:

```jsx
function useThrower() {
  throw new Error('I throw')
}

test('it throws', () => {
  expect(() => renderHook(useThrower)).toThrow('I throw')
})
```

info

React 18 will call `console.error` with an extended error message.
React 19 will call `console.warn` with an extended error message unless the state update is wrapped in `act`.
`render`, `renderHook` and `fireEvent` are wrapped in `act` by default.





  If I can't use shallow rendering, how do I mock out components in tests?

In general, you should avoid mocking out components (see
[the Guiding Principles section](guiding-principles.mdx)). However, if you need
to, then try to use
[Jest's mocking feature](https://facebook.github.io/jest/docs/en/manual-mocks.html).
One case where I've found mocking to be especially useful is for animation
libraries. I don't want my tests to wait for animations to end.

```jsx
jest.mock('react-transition-group', () => {
  const FakeTransition = jest.fn(({children}) => children)
  const FakeCSSTransition = jest.fn(props =>
    props.in ? <FakeTransition>{props.children}</FakeTransition> : null,
  )
  return {CSSTransition: FakeCSSTransition, Transition: FakeTransition}
})

test('you can mock things with jest.mock', () => {
  const {getByTestId, queryByTestId} = render(
    <HiddenMessage initialShow={true} />,
  )
  expect(queryByTestId('hidden-message')).toBeTruthy() // we just care it exists
  // hide the message
  fireEvent.click(getByTestId('toggle-message'))
  // in the real world, the CSSTransition component would take some time
  // before finishing the animation which would actually hide the message.
  // So we've mocked it out for our tests to make it happen instantly
  expect(queryByTestId('hidden-message')).toBeNull() // we just care it doesn't exist
})
```

Note that because they're Jest mock functions (`jest.fn()`), you could also make
assertions on those as well if you wanted.

[Open full test](example-react-transition-group.mdx) for the full example.

This looks like more work than shallow rendering (and it is), but it gives you
more confidence so long as your mock resembles the thing you're mocking closely
enough.

If you want to make things more like shallow rendering, then you could do
something more [like this](example-react-transition-group.mdx).

Learn more about how Jest mocks work from my blog post:
["But really, what is a JavaScript mock?"](https://kentcdodds.com/blog/but-really-what-is-a-javascript-mock)



  What about enzyme is "bloated with complexity and features" and "encourage
  poor testing practices"?

Most of the damaging features have to do with encouraging testing implementation
details. Primarily, these are
[shallow rendering](http://airbnb.io/enzyme/docs/api/shallow.html), APIs which
allow selecting rendered elements by component constructors, and APIs which
allow you to get and interact with component instances (and their
state/properties) (most of enzyme's wrapper APIs allow this).

The guiding principle for this library is:

> The more your tests resemble the way your software is used, the more
> confidence they can give you. - [17 Feb 2018][guiding-principle]

Because users can't directly interact with your app's component instances,
assert on their internal state or what components they render, or call their
internal methods, doing those things in your tests reduce the confidence they're
able to give you.

That's not to say that there's never a use case for doing those things, so they
should be possible to accomplish, just not the default and natural way to test
react components.




If you use the [snapshot-diff](https://github.com/jest-community/snapshot-diff)
library to save snapshot diffs, it won't work out of the box because this
library uses the DOM which is mutable. Changes don't return new objects so
snapshot-diff will think it's the same object and avoid diffing it.

Luckily there's an easy way to make it work: clone the DOM when passing it into
snapshot-diff. It looks like this:

```js
const firstVersion = container.cloneNode(true)
// Do some changes
snapshotDiff(firstVersion, container.cloneNode(true))
```


  

This warning is usually caused by an async operation causing an update after the
test has already finished. There are 2 approaches to resolve it:

1. Wait for the result of the operation in your test by using one of
   [the async utilities](dom-testing-library/api-async.mdx) like
   [waitFor](dom-testing-library/api-async.mdx#waitfor) or a
   [`find*` query](queries/about.mdx#types-of-queries). For example:
   `const userAddress = await findByLabel(/address/i)`.
2. Mocking out the asynchronous operation so that it doesn't trigger state
   updates.

Generally speaking, approach 1 is preferred since it better matches the
expectations of a user interacting with your app.

In addition, you may find
[this blog post](https://kentcdodds.com/blog/write-fewer-longer-tests) helpful
as you consider how best to write tests that give you confidence and avoid these
warnings.


  

Following the guiding principle of this library, it is useful to break down how
tests are organized around how the user experiences and interacts with
application functionality rather than around specific components themselves. In
some cases, for example for reusable component libraries, it might be useful to
include developers in the list of users to test for and test each of the
reusable components individually. Other times, the specific break down of a
component tree is just an implementation detail and testing every component
within that tree individually can cause issues (see
https://kentcdodds.com/blog/avoid-the-test-user).

In practice this means that it is often preferable to test high enough up the
component tree to simulate realistic user interactions. The question of whether
it is worth additionally testing at a higher or lower level on top of this comes
down to a question of tradeoffs and what will provide enough value for the cost
(see https://kentcdodds.com/blog/unit-vs-integration-vs-e2e-tests on more info
on different levels of testing).

For a more in-depth discussion of this topic see
[this video](https://youtu.be/0qmPdcV-rN8).


<!--
Links:
-->

<!-- prettier-ignore-start -->

[guiding-principle]: https://twitter.com/kentcdodds/status/977018512689455106

<!-- prettier-ignore-end -->
