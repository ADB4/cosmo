---
title: Mui Breakpoints And Responsive
source: mui.com/material-ui
syllabus_weeks: [9]
topics: [breakpoints, useMediaQuery, responsive values, container queries, up, down, between, custom breakpoints]
---



# Breakpoints

# Breakpoints

API that enables the use of breakpoints in a wide variety of contexts.

For optimal user experience, Material Design interfaces need to be able to adapt their layout at various breakpoints.
Material UI uses a **simplified** implementation of the original [specification](https://m2.material.io/design/layout/responsive-layout-grid.html#breakpoints).

The breakpoints are used internally in various components to make them responsive,
but you can also take advantage of them
for controlling the layout of your application through the [Grid](/material-ui/react-grid/) component.

## Default breakpoints

Each breakpoint (a key) matches with a _fixed_ screen width (a value):

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

- **xs,** extra-small: 0px
- **sm,** small: 600px
- **md,** medium: 900px
- **lg,** large: 1200px
- **xl,** extra-large: 1536px

These values can be [customized](#custom-breakpoints).

## CSS Media Queries

CSS media queries are the idiomatic approach to make your UI responsive.
The theme provides five styles helpers to do so:

- [theme.breakpoints.up(key)](#theme-breakpoints-up-key-media-query)
- [theme.breakpoints.down(key)](#theme-breakpoints-down-key-media-query)
- [theme.breakpoints.only(key)](#theme-breakpoints-only-key-media-query)
- [theme.breakpoints.not(key)](#theme-breakpoints-not-key-media-query)
- [theme.breakpoints.between(start, end)](#theme-breakpoints-between-start-end-media-query)

In the following demo, we change the background color (red, blue & green) based on the screen width.

```jsx
const styles = (theme) => ({
  root: {
    padding: theme.spacing(1),
    [theme.breakpoints.down('md')]: {
      backgroundColor: theme.palette.secondary.main,
    },
    [theme.breakpoints.up('md')]: {
      backgroundColor: theme.palette.primary.main,
    },
    [theme.breakpoints.up('lg')]: {
      backgroundColor: green[500],
    },
  },
});
```


## JavaScript Media Queries

Sometimes, using CSS isn't enough.
You might want to change the React rendering tree based on the breakpoint value, in JavaScript.

### useMediaQuery hook

You can learn more on the [useMediaQuery](/material-ui/react-use-media-query/) page.

## Custom breakpoints

You define your project's breakpoints in the `theme.breakpoints` section of your theme.

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

- [`theme.breakpoints.values`](/material-ui/customization/default-theme/?expand-path=$.breakpoints.values): Default to the [above values](#default-breakpoints). The keys are your screen names, and the values are the min-width where that breakpoint should start.
- `theme.breakpoints.unit`: Default to `'px'`. The unit used for the breakpoint's values.
- `theme.breakpoints.step`: Default to `5`. The increment divided by 100 used to implement exclusive breakpoints.
  For example, `{ step: 5 }` means that `down(500)` will result in `'(max-width: 499.95px)'`.

If you change the default breakpoints's values, you need to provide them all:

```jsx
const theme = createTheme({
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
});
```

Feel free to have as few or as many breakpoints as you want, naming them in whatever way you'd prefer for your project.

```js
const theme = createTheme({
  breakpoints: {
    values: {
      mobile: 0,
      tablet: 640,
      laptop: 1024,
      desktop: 1200,
    },
  },
});
```

If you are using TypeScript, you would also need to use [module augmentation](/material-ui/guides/typescript/#customization-of-theme) for the theme to accept the above values.

<!-- Tested with packages/mui-material/test/typescript/breakpointsOverrides.augmentation.tsconfig.json -->

```ts
declare module '@mui/material/styles' {
  interface BreakpointOverrides {
    xs: false; // removes the `xs` breakpoint
    sm: false;
    md: false;
    lg: false;
    xl: false;
    mobile: true; // adds the `mobile` breakpoint
    tablet: true;
    laptop: true;
    desktop: true;
  }
}
```

## API

### `theme.breakpoints.up(key) => media query`

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

#### Arguments

1. `key` (_string_ | _number_): A breakpoint key (`xs`, `sm`, etc.) or a screen width number in px.

#### Returns

`media query`: A media query string ready to be used with most styling solutions, which matches screen widths greater than the screen size given by the breakpoint key (inclusive).

#### Examples

```js
const styles = (theme) => ({
  root: {
    backgroundColor: 'blue',
    // Match [md, ∞)
    //       [900px, ∞)
    [theme.breakpoints.up('md')]: {
      backgroundColor: 'red',
    },
  },
});
```

### `theme.breakpoints.down(key) => media query`

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

#### Arguments

1. `key` (_string_ | _number_): A breakpoint key (`xs`, `sm`, etc.) or a screen width number in px.

#### Returns

`media query`: A media query string ready to be used with most styling solutions, which matches screen widths less than the screen size given by the breakpoint key (exclusive).

#### Examples

```js
const styles = (theme) => ({
  root: {
    backgroundColor: 'blue',
    // Match [0, md)
    //       [0, 900px)
    [theme.breakpoints.down('md')]: {
      backgroundColor: 'red',
    },
  },
});
```

### `theme.breakpoints.only(key) => media query`

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

#### Arguments

1. `key` (_string_): A breakpoint key (`xs`, `sm`, etc.).

#### Returns

`media query`: A media query string ready to be used with most styling solutions, which matches screen widths starting from the screen size given by the breakpoint key (inclusive) and stopping at the screen size given by the next breakpoint key (exclusive).

#### Examples

```js
const styles = (theme) => ({
  root: {
    backgroundColor: 'blue',
    // Match [md, md + 1)
    //       [md, lg)
    //       [900px, 1200px)
    [theme.breakpoints.only('md')]: {
      backgroundColor: 'red',
    },
  },
});
```

### `theme.breakpoints.not(key) => media query`

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

#### Arguments

1. `key` (_string_): A breakpoint key (`xs`, `sm`, etc.).

#### Returns

`media query`: A media query string ready to be used with most styling solutions, which matches screen widths stopping at the screen size given by the breakpoint key (exclusive) and starting at the screen size given by the next breakpoint key (inclusive).

#### Examples

```js
const styles = (theme) => ({
  root: {
    backgroundColor: 'blue',
    // Match [xs, md) and [md + 1, ∞)
    //       [xs, md) and [lg, ∞)
    //       [0px, 900px) and [1200px, ∞)
    [theme.breakpoints.not('md')]: {
      backgroundColor: 'red',
    },
  },
});
```

### `theme.breakpoints.between(start, end) => media query`

<!-- Keep in sync with packages/mui-system/src/createTheme/createBreakpoints.d.ts -->

#### Arguments

1. `start` (_string_): A breakpoint key (`xs`, `sm`, etc.) or a screen width number in px.
2. `end` (_string_): A breakpoint key (`xs`, `sm`, etc.) or a screen width number in px.

#### Returns

`media query`: A media query string ready to be used with most styling solutions, which matches screen widths greater than the screen size given by the breakpoint key in the first argument (inclusive) and less than the screen size given by the breakpoint key in the second argument (exclusive).

#### Examples

```js
const styles = (theme) => ({
  root: {
    backgroundColor: 'blue',
    // Match [sm, md)
    //       [600px, 900px)
    [theme.breakpoints.between('sm', 'md')]: {
      backgroundColor: 'red',
    },
  },
});
```

## Default values

You can explore the default values of the breakpoints using [the theme explorer](/material-ui/customization/default-theme/?expand-path=$.breakpoints) or by opening the dev tools console on this page (`window.theme.breakpoints`).


# Container Queries

# Container queries

Material UI provides a utility function for creating CSS container queries based on theme breakpoints.

## Usage

To create [CSS container queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries), use `theme.containerQueries` with any method available in the [`theme.breakpoints`](/material-ui/customization/breakpoints/#api).
The value can be unitless (in which case it'll be rendered in pixels), a string, or a breakpoint key. For example:

```js
theme.containerQueries.up('sm'); // => '@container (min-width: 600px)'
```


> **Info:**
>
> One of the ancestors must have the CSS container type specified.


### Named containment contexts

To refer to a [containment context](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries#naming_containment_contexts), call the `containerQueries` method with the name of the container for access to all breakpoint methods:

```js
theme.containerQueries('sidebar').up('500px'); // => '@container sidebar (min-width: 500px)'
```

## Shorthand syntax

When adding styles using the `sx` prop, use the `@<size>` or `@<size>/<name>` notation to apply container queries without referring to the theme.

- `<size>`: a width or a breakpoint key.
- `<name>` (optional): a named containment context.


### Caveats

- The `@` prefix with a unitless value renders as `px`, so `@500` is equivalent to `500px`—but `@500px` is incorrect syntax and won't render correctly.
- `@` with no number renders as `0px`.
- Container queries must share the same units (the sizes can be defined in any order), as shown below:

  ```js
  // ✅ These container queries will be sorted correctly.
  padding: {
    '@40em': 4,
    '@20em': 2,
    '@': 0,
  }

  // ❌ These container queries won't be sorted correctly
  //    because 40em is typically greater than 50px
  //    and the units don't match.
  padding: {
    '@40em': 4,
    '@50': 2,
    '@': 0,
  }
  ```

## API

CSS container queries support all the methods available in [the breakpoints API](/material-ui/customization/breakpoints/#api).

```js
// For default breakpoints
theme.containerQueries.up('sm'); // => '@container (min-width: 600px)'
theme.containerQueries.down('md'); // => '@container (max-width: 900px)'
theme.containerQueries.only('md'); // => '@container (min-width: 600px) and (max-width: 900px)'
theme.containerQueries.between('sm', 'lg'); // => '@container (min-width: 600px) and (max-width: 1200px)'
theme.containerQueries.not('sm'); // => '@container (max-width: 600px)'
```


# Use Media Query

---
productId: material-ui
title: Media queries in React for responsive design
githubLabel: 'hook: useMediaQuery'
githubSource: packages/mui-material/src/useMediaQuery
---

# useMediaQuery

This React hook listens for matches to a CSS media query. It allows the rendering of components based on whether the query matches or not.

Some of the key features:

- ⚛️ It has an idiomatic React API.
- 🚀 It's performant, it observes the document to detect when its media queries change, instead of polling the values periodically.
- 📦 [1.1 kB gzipped](https://bundlephobia.com/package/@mui/material).
- 🤖 It supports server-side rendering.


## Basic media query

You should provide a media query to the first argument of the hook.
The media query string can be any valid CSS media query, for example [`'(prefers-color-scheme: dark)'`](/material-ui/customization/dark-mode/#system-preference).


> **Warning:**
>
> Using the query `'print'` to modify a document for printing is not supported, as changes made in re-rendering may not be accurately reflected.
> You can use the `sx` prop's `displayPrint` field for this purpose instead.
> See [MUI System—Display in print](/system/display/#display-in-print) for more details.


## Using breakpoint helpers

You can use Material UI's [breakpoint helpers](/material-ui/customization/breakpoints/) as follows:

```jsx
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

function MyComponent() {
  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up('sm'));

  return <span>{`theme.breakpoints.up('sm') matches: ${matches}`}</span>;
}
```


Alternatively, you can use a callback function, accepting the theme as a first argument:

```jsx
import useMediaQuery from '@mui/material/useMediaQuery';

function MyComponent() {
  const matches = useMediaQuery((theme) => theme.breakpoints.up('sm'));

  return <span>{`theme.breakpoints.up('sm') matches: ${matches}`}</span>;
}
```

⚠️ There is **no default** theme support, you have to inject it in a parent theme provider.

## Using JavaScript syntax

You can use [json2mq](https://github.com/akiran/json2mq) to generate media query string from a JavaScript object.


## Testing

You need an implementation of [matchMedia](https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia) in your test environment.

For instance, [jsdom doesn't support it yet](https://jestjs.io/docs/manual-mocks#mocking-methods-which-are-not-implemented-in-jsdom). You should polyfill it.
Using [css-mediaquery](https://github.com/ericf/css-mediaquery) to emulate it is recommended.

```js
import mediaQuery from 'css-mediaquery';

function createMatchMedia(width) {
  return (query) => ({
    matches: mediaQuery.match(query, {
      width,
    }),
    addEventListener: () => {},
    removeEventListener: () => {},
  });
}

describe('MyTests', () => {
  beforeAll(() => {
    window.matchMedia = createMatchMedia(window.innerWidth);
  });
});
```

## Client-side only rendering

To perform the server-side hydration, the hook needs to render twice.
A first time with `defaultMatches`, the value of the server, and a second time with the resolved value.
This double pass rendering cycle comes with a drawback: it's slower.
You can set the `noSsr` option to `true` if you use the returned value **only** client-side.

```js
const matches = useMediaQuery('(min-width:600px)', { noSsr: true });
```

or it can turn it on globally with the theme:

```js
const theme = createTheme({
  components: {
    MuiUseMediaQuery: {
      defaultProps: {
        noSsr: true,
      },
    },
  },
});
```

> **Info:**
>
> Note that `noSsr` has no effects when using the `createRoot()` API (the client-side only API introduced in React 18).


## Server-side rendering

> **Warning:**
>
> Server-side rendering and client-side media queries are fundamentally at odds.
> Be aware of the tradeoff. The support can only be partial.


Try relying on client-side CSS media queries first.
For instance, you could use:

- [`<Box display>`](/system/display/#hiding-elements)
- [`themes.breakpoints.up(x)`](/material-ui/customization/breakpoints/#css-media-queries)
- or [`sx prop`](/system/getting-started/the-sx-prop/)

If none of the above alternatives are an option, you can proceed reading this section of the documentation.

First, you need to guess the characteristics of the client request, from the server.
You have the choice between using:

- **User agent**. Parse the user agent string of the client to extract information. Using [ua-parser-js](https://github.com/faisalman/ua-parser-js) to parse the user agent is recommended.
- **Client hints**. Read the hints the client is sending to the server. Be aware that this feature is [not supported everywhere](https://caniuse.com/#search=client%20hint).

Finally, you need to provide an implementation of [matchMedia](https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia) to the `useMediaQuery` with the previously guessed characteristics.
Using [css-mediaquery](https://github.com/ericf/css-mediaquery) to emulate matchMedia is recommended.

For instance on the server-side:

```js
import * as ReactDOMServer from 'react-dom/server';
import parser from 'ua-parser-js';
import mediaQuery from 'css-mediaquery';
import { createTheme, ThemeProvider } from '@mui/material/styles';

function handleRender(req, res) {
  const deviceType = parser(req.headers['user-agent']).device.type || 'desktop';
  const ssrMatchMedia = (query) => ({
    matches: mediaQuery.match(query, {
      // The estimated CSS width of the browser.
      width: deviceType === 'mobile' ? '0px' : '1024px',
    }),
  });

  const theme = createTheme({
    components: {
      // Change the default options of useMediaQuery
      MuiUseMediaQuery: {
        defaultProps: {
          ssrMatchMedia,
        },
      },
    },
  });

  const html = ReactDOMServer.renderToString(
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>,
  );

  // …
}
```


Make sure you provide the same custom match media implementation to the client-side to guarantee a hydration match.

## Migrating from `withWidth()`

The `withWidth()` higher-order component injects the screen width of the page.
You can reproduce the same behavior with a `useWidth` hook:


## API

### `useMediaQuery(query, [options]) => matches`

#### Arguments

1. `query` (_string_ | _func_): A string representing the media query to handle or a callback function accepting the theme (in the context) that returns a string.
2. `options` (_object_ [optional]):

- `options.defaultMatches` (_bool_ [optional]):
  As `window.matchMedia()` is unavailable on the server,
  it returns a default matches during the first mount. The default value is `false`.
- `options.matchMedia` (_func_ [optional]): You can provide your own implementation of _matchMedia_. This can be used for handling an iframe content window.
- `options.noSsr` (_bool_ [optional]): Defaults to `false`.
  To perform the server-side hydration, the hook needs to render twice.
  A first time with `defaultMatches`, the value of the server, and a second time with the resolved value.
  This double pass rendering cycle comes with a drawback: it's slower.
  You can set this option to `true` if you use the returned value **only** client-side.
- `options.ssrMatchMedia` (_func_ [optional]): You can provide your own implementation of _matchMedia_, it's used when rendering server-side.

Note: You can change the default options using the [`default props`](/material-ui/customization/theme-components/#theme-default-props) feature of the theme with the `MuiUseMediaQuery` key.

#### Returns

`matches`: Matches is `true` if the document currently matches the media query and `false` when it does not.

#### Examples

```jsx
import * as React from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';

export default function SimpleMediaQuery() {
  const matches = useMediaQuery('(min-width:600px)');

  return <span>{`(min-width:600px) matches: ${matches}`}</span>;
}
```


# Responsive Ui

# Responsive UI

Material Design layouts encourage consistency across platforms, environments, and screen sizes by using uniform elements and spacing.

[Responsive layouts](https://m2.material.io/design/layout/responsive-layout-grid.html) in Material Design adapt to any possible screen size.
We provide the following helpers to make the UI responsive:

- [Grid](/material-ui/react-grid/): The Material Design responsive layout grid adapts to screen size and orientation, ensuring consistency across layouts.
- [Container](/material-ui/react-container/): The container centers your content horizontally. It's the most basic layout element.
- [Breakpoints](/material-ui/customization/breakpoints/): API that enables the use of breakpoints in a wide variety of contexts.
- [useMediaQuery](/material-ui/react-use-media-query/): This is a CSS media query hook for React. It listens for matches to a CSS media query.
