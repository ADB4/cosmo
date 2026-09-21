---
title: Mui Css Variables And Dark Mode
source: mui.com/material-ui
syllabus_weeks: [9]
topics: [CSS theme variables, cssVarsMode, dark mode, color schemes, InitColorSchemeScript, applyStyles, system preference, toggling, flicker prevention]
---



# Overview

# CSS theme variables

An overview of adopting CSS theme variables in Material UI.

[CSS variables](https://www.w3.org/TR/css-variables-1/) are a modern cross-browser feature that let you declare variables in CSS and reuse them in other properties.
You can implement them to improve Material UI's theming and customization experience.

> **Info:**
>
> If this is your first time encountering CSS variables, you should check out [the MDN Web Docs on CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties) before continuing here.


## Introduction

CSS theme variables replace raw values in Material UI components for a better developer experience because, in the browser dev tool, you will see which theme token is used as a value.

In addition with these variables, you can inject a theme into your app's stylesheet _at build time_ to apply the user's selected settings before the whole app is rendered.

## Advantages

- It lets you prevent [dark-mode SSR flickering](https://github.com/mui/material-ui/issues/27651).
- You can create unlimited color schemes beyond `light` and `dark`.
- It offers a better debugging experience not only for developers but also designers on your team.
- The color scheme of your website is automatically synced between browser tabs.
- It simplifies integration with third-party tools because CSS theme variables are available globally.
- It reduces the need for a nested theme when you want to apply dark styles to a specific part of your application.

## Trade-offs

For server-side applications, there are some trade-offs to consider:

|                                                              | Compare to the default method | Reason                                                                                                         |
| :----------------------------------------------------------- | :---------------------------- | :------------------------------------------------------------------------------------------------------------- |
| HTML size                                                    | Bigger                        | CSS variables are generated for both light and dark mode at build time.                                        |
| [First Contentful Paint (FCP)](https://web.dev/articles/fcp) | Longer                        | Since the HTML size is bigger, the time to download the HTML before showing the content is a bit longer.       |
| [Time to Interactive (TTI)](https://web.dev/articles/tti)    | Shorter (for dark mode)       | Stylesheets are not regenerated between light and dark mode, a lot less time is spent running JavaScript code. |

> **Warning:**
>
> The comparison described in the table above may not be applicable to large and complex applications since there are so many factors that can impact performance metrics.


## What's next

- To start a new project with CSS theme variables, check out the [basic usage guide](/material-ui/customization/css-theme-variables/usage/).
- For theming and customization, check out the [how-to guide](/material-ui/customization/css-theme-variables/configuration/).


# Usage

# CSS theme variables - Usage

Learn how to adopt CSS theme variables.

## Getting started

To use CSS theme variables, create a theme with `cssVariables: true` and wrap your app with `ThemeProvider`.

After rendering, you'll see CSS variables in the `:root` stylesheet of your HTML document.
By default, these variables are flattened and prefixed with `--mui`:

<codeblock>

```jsx JSX
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({ cssVariables: true });

function App() {
  return <ThemeProvider theme={theme}>{/* ...your app */}</ThemeProvider>;
}
```

```css CSS
:root {
  --mui-palette-primary-main: #1976d2;
  --mui-palette-primary-light: #42a5f5;
  --mui-palette-primary-dark: #1565c0;
  --mui-palette-primary-contrastText: #fff;
  /* ...other variables */
}
```

</codeblock>

> **Info:**
>
> If you're using the experimental `CssVarsProvider` API, replace it with `ThemeProvider`.
> All features that were previously available to the `CssVarsProvider` are now available with the `ThemeProvider`.


## Light and dark modes

When the [built-in dark color scheme](/material-ui/customization/dark-mode/#built-in-support) and `cssVariables` are enabled, both light and dark CSS variables are generated with the default CSS media `prefers-color-scheme` method.

This method works with server-side rendering without extra configuration. However, users won't be able to toggle between modes because the styles are based on the browser media.

If you want to be able to manually toggle modes, see the guide to [toggling dark mode manually](/material-ui/customization/css-theme-variables/configuration/#toggling-dark-mode-manually).

## Applying dark styles

To customize styles for dark mode, use the [`theme.applyStyles()` function](/material-ui/customization/dark-mode/#styling-in-dark-mode).

The example below shows how to customize the Card component for dark mode:

```js
import Card from '@mui/material/Card';

<Card
  sx={[
    (theme) => ({
      backgroundColor: theme.vars.palette.background.default,
    }),
    (theme) =>
      theme.applyStyles('dark', {
        backgroundColor: theme.vars.palette.grey[900],
      }),
  ]}
/>;
```

> **Warning:**
>
> Do not use `theme.palette.mode` to switch between light and dark styles—this produces an [unwanted flickering effect](/material-ui/customization/css-theme-variables/configuration/#preventing-ssr-flickering).


## Using theme variables

When the CSS variables feature is enabled, the `vars` node is added to the theme.
This `vars` object mirrors the structure of a serializable theme, with each value corresponding to a CSS variable.

- `theme.vars` (recommended): an object that refers to the CSS theme variables.

  ```js
  const Button = styled('button')(({ theme }) => ({
    backgroundColor: theme.vars.palette.primary.main, // var(--mui-palette-primary-main)
    color: theme.vars.palette.primary.contrastText, // var(--mui-palette-primary-contrastText)
  }));
  ```

  For **TypeScript**, the typings are not enabled by default.
  Follow the [TypeScript setup](#typescript) to enable the typings.

  > **Success:**
>
> If the components need to render outside of the `CssVarsProvider`, add fallback to the theme object.
> 
>   ```js
>   backgroundColor: (theme.vars || theme).palette.primary.main;
>   ```
> 
>   :::
> 
> - **Native CSS**: if you can't access the theme object, for example in a pure CSS file, you can use [`var()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/var) directly:
> 
>   ```css
>   /* external-scope.css */
>   .external-section {
>     background-color: var(--mui-palette-grey-50);
>   }
>   ```
> 
> ## Color channel tokens
> 
> Enabling `cssVariables` automatically generates channel tokens which are used to create translucent colors.
> These tokens consist of color space channels without the alpha component, separated by spaces.
> 
> The colors are suffixed with `Channel`—for example:
> 
> ```js
> const theme = createTheme({ cssVariables: true });
> 
> console.log(theme.palette.primary.mainChannel); // '25 118 210'
> // This token is generated from `theme.colorSchemes.light.palette.primary.main`.
> ```
> 
> You can use the channel tokens to create a translucent color like this:
> 
> ```js
> const theme = createTheme({
>   cssVariables: true,
>   components: {
>     MuiChip: {
>       styleOverrides: {
>         root: ({ theme }) => ({
>           variants: [
>             {
>               props: { variant: 'outlined', color: 'primary' },
>               style: {
>                 backgroundColor: `rgba(${theme.vars.palette.primary.mainChannel} / 0.12)`,
>               },
>             },
>           ],
>         }),
>       },
>     },
>   },
> });
> ```
warning
Don't use a comma (`,`) as a separator because the channel colors use empty spaces to define [transparency](https://www.w3.org/TR/css-color-4/#transparency):

```js
`rgba(${theme.vars.palette.primary.mainChannel}, 0.12)`, // 🚫 this does not work
`rgba(${theme.vars.palette.primary.mainChannel} / 0.12)`, // ✅ always use `/`
```

:::

## Adding new theme tokens

You can add other key-value pairs to the theme input which will be generated as a part of the CSS theme variables:

```js
const theme = createTheme({
  cssVariables: true,
  colorSchemes: {
    light: {
      palette: {
        // The best part is that you can refer to the variables wherever you like 🤩
        gradient:
          'linear-gradient(to left, var(--mui-palette-primary-main), var(--mui-palette-primary-dark))',
        border: {
          subtle: 'var(--mui-palette-neutral-200)',
        },
      },
    },
    dark: {
      palette: {
        gradient:
          'linear-gradient(to left, var(--mui-palette-primary-light), var(--mui-palette-primary-main))',
        border: {
          subtle: 'var(--mui-palette-neutral-600)',
        },
      },
    },
  },
});

function App() {
  return <ThemeProvider theme={theme}>...</ThemeProvider>;
}
```

Then, you can access those variables from the `theme.vars` object:

```js
const Divider = styled('hr')(({ theme }) => ({
  height: 1,
  border: '1px solid',
  borderColor: theme.vars.palette.border.subtle,
  backgroundColor: theme.vars.palette.gradient,
}));
```

Or use `var()` to refer to the CSS variable directly:

```css
/* global.css */
.external-section {
  background-color: var(--mui-palette-gradient);
}
```

> **Warning:**
>
> If you're using a [custom prefix](/material-ui/customization/css-theme-variables/configuration/#customizing-variable-prefix), make sure to replace the default `--mui`.


For **TypeScript**, you need to augment the [palette interfaces](#palette-interfaces).

## TypeScript

The theme variables type is not enabled by default. You need to import the module augmentation to enable the typings:

```ts
// The import can be in any file that is included in your `tsconfig.json`
import type {} from '@mui/material/themeCssVarsAugmentation';
import { styled } from '@mui/material/styles';

const StyledComponent = styled('button')(({ theme }) => ({
  // ✅ typed-safe
  color: theme.vars.palette.primary.main,
}));
```

### Palette interfaces

To add new tokens to the theme palette, you need to augment the `PaletteOptions` and `Palette` interfaces:

```ts
declare module '@mui/material/styles' {
  interface PaletteOptions {
    gradient: string;
    border: {
      subtle: string;
    };
  }
  interface Palette {
    gradient: string;
    border: {
      subtle: string;
    };
  }
}
```

## Next steps

If you need to support system preference and manual selection, check out the [advanced configuration](/material-ui/customization/css-theme-variables/configuration/)


# Configuration

# CSS theme variables - Configuration

A guide for configuring CSS theme variables in Material UI.

## Customizing variable prefix

To change the default variable prefix (`--mui`), provide a string to `cssVarPrefix` property, as shown below:

```js
createTheme({ cssVariables: { cssVarPrefix: 'any' } });

// generated stylesheet:
// --any-palette-primary-main: ...;
```

To remove the prefix, use an empty string as a value:

```js
createTheme({ cssVariables: { cssVarPrefix: '' } });

// generated stylesheet:
// --palette-primary-main: ...;
```

## Toggling dark mode manually

To toggle between modes manually, set the `colorSchemeSelector` with one of the following selectors:

- `class`: adds a class to the `<html>` element.

  ```js class
  createTheme({
    colorSchemes: { light: true, dark: true },
    cssVariables: {
      colorSchemeSelector: 'class'
    }
  });

  // CSS Result
  .light { ... }
  .dark { ... }
  ```

- `data`: adds a data attribute to the `<html>` element.

  ```js data
  createTheme({
    colorSchemes: { light: true, dark: true },
    cssVariables: {
      colorSchemeSelector: 'data'
    }
  });

  // CSS Result
  [data-light] { ... }
  [data-dark] { ... }
  ```

- `string`: adds a custom selector to the `<html>` element.

  ```js string
  // The value must start with dot (.) for class or square brackets ([]) for data
  createTheme({
    colorSchemes: { light: true, dark: true },
    cssVariables: {
      colorSchemeSelector: '.theme-%s'
    }
  });

  // CSS Result
  .theme-light { ... }
  .theme-dark { ... }
  ```

Then, use `useColorScheme` hook to switch between modes:

```jsx
import { useColorScheme } from '@mui/material/styles';

function ModeSwitcher() {
  const { mode, setMode } = useColorScheme();

  if (!mode) {
    return null;
  }

  return (
    <select
      value={mode}
      onChange={(event) => {
        setMode(event.target.value);
        // For TypeScript, cast `event.target.value as 'light' | 'dark' | 'system'`:
      }}
    >
      <option value="system">System</option>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  );
}
```

> **Success:**
>
> After React hydrates the tree, the mode is set to `system` to follow the user's preference.


### Determining the system mode

To determine if the system mode is `light` or `dark`, use the `systemMode` property:

```js
const { mode, systemMode } = useColorScheme();

console.log(mode); // 'system'
console.log(systemMode); // 'light' | 'dark'
```

However, if the mode is **not** `system`, the `systemMode` will be `undefined`.

```js
const { mode, systemMode } = useColorScheme();

console.log(mode); // 'light' | 'dark'
console.log(systemMode); // undefined
```

### Preventing SSR flickering

For SSR (server-side rendering) applications, Material UI can not detected user-selected mode on the server, causing the screen to flicker from light to dark during the hydration phase on the client.

To prevent the issue, you need to ensure that there is no usage of `theme.palette.mode === 'dark'` in your code base.

If you have such a condition, replace it with the [`theme.applyStyles()` function](/material-ui/customization/dark-mode/#styling-in-dark-mode):

```diff
 import Card from '@mui/material/Card';

 function App() {
   return (
     <Card
-      sx={(theme) => ({
-        backgroundColor: theme.palette.mode === 'dark' ? '#000' : '#fff',
-        '&:hover': {
-          backgroundColor: theme.palette.mode === 'dark' ? '#333' : '#f5f5f5',
-        },
-      })}
+      sx={[
+        {
+          backgroundColor: '#fff',
+          '&:hover': {
+            backgroundColor: '#f5f5f5',
+          },
+        },
+        (theme) =>
+          theme.applyStyles('dark', {
+            backgroundColor: '#000',
+            '&:hover': {
+              backgroundColor: '#333',
+            },
+          }),
+      ]}
     />
   );
 }
```

Next, if you have a custom selector that is **not** `media`, add the [`InitColorSchemeScript`](/material-ui/react-init-color-scheme-script/) component based on the framework that you are using:

> **Success:**
>
> The `attribute` has to be the same as the one you set in the `colorSchemeSelector` property:
> 
> ```js
> createTheme({
>   cssVariables: {
>     colorSchemeSelector: 'class'
>   }
> })
> 
> <InitColorSchemeScript attribute="class" />
> ```


### Next.js App Router

Add the following code to the [root layout](https://nextjs.org/docs/app/api-reference/file-conventions/layout#root-layouts) file:

```jsx title="app/layout.js"
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';

export default function RootLayout(props) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        {/* must come before the <main> element */}
        <InitColorSchemeScript attribute="class" />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

> **Warning:**
>
> If you don't add `suppressHydrationWarning` to your `<html>` tag, you will see warnings about `"Extra attributes from the server"` because `InitColorSchemeScript` updates that element.


### Next.js Pages Router

Add the following code to the custom [`pages/_document.js`](https://nextjs.org/docs/pages/building-your-application/routing/custom-document) file:

```jsx title="pages/_document.js"
import Document, { Html, Head, Main, NextScript } from 'next/document';
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';

export default class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>...</Head>
        <body>
          {/* must come before the <Main> element */}
          <InitColorSchemeScript attribute="class" />
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}
```

### Gatsby

Place the script in your [`gatsby-ssr.js`](https://www.gatsbyjs.com/docs/reference/config-files/gatsby-ssr/) file:

```jsx
import * as React from 'react';
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';

export function onRenderBody({ setPreBodyComponents }) {
  setPreBodyComponents([<InitColorSchemeScript attribute="class" />]);
}
```

## Forcing a specific color scheme

To force a specific color scheme for some part of your application, set the selector to the component or HTML element directly.

In the example below, all the components inside the `div` will always be dark:

<codeblock>

```js class
// if the selector is '.mode-%s'
<div className=".mode-dark">
  <Paper sx={{ p: 2 }}>
    <TextField label="Email" type="email" margin="normal" />
    <TextField label="Password" type="password" margin="normal" />
    <Button>Sign in</Button>
  </Paper>
  {/* other components */}
</div>
```

```js data-attribute
// if the selector is '[data-mode-%s]'
<div data-mode-dark>
  <Paper sx={{ p: 2 }}>
    <TextField label="Email" type="email" margin="normal" />
    <TextField label="Password" type="password" margin="normal" />
    <Button>Sign in</Button>
  </Paper>
  {/* other components */}
</div>
```

</codeblock>

## Disabling CSS color scheme

By default, `createTheme()` attaches a [CSS `color-scheme` property](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme) based on the palette mode.
You can disable this by setting `disableCssColorScheme` to `true`:

```js
createTheme({
  cssVariables: { disableCssColorScheme: true },
});
```

The generated CSS will not include the `color-scheme` property:

```diff
 @media (prefers-color-scheme: dark) {
   :root {
-    color-scheme: dark;
     --mui-palette-primary-main: #90caf9;
     ...
   }
 }
```

## Instant transition between color schemes

To disable CSS transitions when switching between modes, apply the `disableTransitionOnChange` prop:

```js
<ThemeProvider disableTransitionOnChange />
```


## Force theme recalculation between modes

By default, the `ThemeProvider` does not re-render when switching between light and dark modes when `cssVariables: true` is set in the theme.

If you want to opt-out from this behavior, use the `forceThemeRerender` prop in the ThemeProvider:

```js
<ThemeProvider forceThemeRerender />
```


# Native Color

# CSS theme variables - Native color

Learn how to use native color with CSS theme variables.

> **Warning:**
>
> This feature only works in modern browsers. Please check the [browser support](https://caniuse.com/css-relative-colors) before using it.


## Benefits

- No need to use JavaScript to manipulate colors.
- Supports modern color spaces such as `oklch`, `oklab`, and `display-p3`.
- Supports color aliases to external CSS variables.
- Automatically calculates contrast text from the main color.

## Usage

Set `cssVariables` with `nativeColor: true` in the theme options.
Material UI will start using CSS color-mix and relative color instead of the JavaScript color manipulation.

> **Success:**
>
> Try inspecting the demo below to see the calculated values of the color tokens.


```js
const theme = createTheme({
  cssVariables: {
    nativeColor: true,
  },
});
```


## Modern color spaces

The theme palette supports all modern color spaces, including `oklch`, `oklab`, and `display-p3`.

```js
const theme = createTheme({
  cssVariables: { nativeColor: true },
  palette: {
    primary: {
      main: 'color(display-p3 0.5 0.8 0.2)',
    },
  },
});
```


## Aliasing color variables

If you're using CSS variables to define colors, you can provide the values to the theme palette options.

```js
const theme = createTheme({
  cssVariables: {
    nativeColor: true,
  },
  palette: {
    primary: {
      main: 'var(--colors-brand-primary)',
    },
  },
});
```


## Theme color functions

The theme object contains these color utilities: `alpha()`, `lighten()`, and `darken()`.

When native color is enabled, these functions use CSS `color-mix()` and relative color instead of the JavaScript color manipulation.


> **Info:**
>
> The theme color functions are backward compatible.
> If native color is not enabled, they will fall back to the JavaScript color manipulation.


## Contrast color function

The `theme.palette.getContrastText()` function produces the contrast color.
The demo below shows the result of the `theme.palette.getContrastText()` function, which produces the text color based on the selected background.


> **Info:**
>
> The CSS variables `--__l` and `--__a` are internal variables set globally by Material UI.
> 
> To learn more about the formulas used, see [this article on color contrast from Lea Verou](https://lea.verou.me/blog/2024/contrast-color/).


## Caveats

- Because of the differences in how contrast is calculated between CSS and JavaScript, the resulting CSS colors may not exactly match the corresponding JavaScript colors to be replaced.
- In the future, the relative color contrast will be replaced by the native [CSS `contrast-color()` function](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/contrast-color) when browser support is improved.
- For relative color contrast, the color space is automatically set to `oklch` internally. Currently it's not possible to change this, but please [open an issue](https://github.com/mui/material-ui/issues/new/) if you have a use case that calls for it.


# Dark Mode

# Dark mode

Material UI comes with two palette modes: light (the default) and dark.

## Dark mode only

You can make your application use the dark theme as the default—regardless of the user's preference—by adding `mode: 'dark'` to the `createTheme()` helper:

```js
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

export default function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <main>This app is using the dark mode</main>
    </ThemeProvider>
  );
}
```

Adding `mode: 'dark'` to the `createTheme()` helper modifies several palette values, as shown in the following demo:


Adding `<CssBaseline />` inside of the `<ThemeProvider>` component will also enable dark mode for the app's background.

> **Warning:**
>
> Setting the dark mode this way only works if you are using [the default palette](/material-ui/customization/default-theme/). If you have a custom palette, make sure that you have the correct values based on the `mode`. The next section explains how to do this.


### Overriding the dark palette

To override the default palette, provide a [palette object](/material-ui/customization/palette/#default-colors) with custom colors in hex, RGB, or HSL format:

```jsx
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ff5252',
    },
  },
});
```

Learn more about palette structure in the [Palette documentation](/material-ui/customization/palette/).

## System preference

Some users set a preference for light or dark mode through their operating system—either systemwide, or for individual user agents.
The following sections explain how to apply these preferences to an app's theme.

### Built-in support

Use the `colorSchemes` node to build an application with multiple color schemes.
The built-in color schemes are `light` and `dark` which can be enabled by setting the value to `true`.

The light color scheme is enabled by default, so you only need to set the dark color scheme:

```js
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  colorSchemes: {
    dark: true,
  },
});

function App() {
  return <ThemeProvider theme={theme}>...</ThemeProvider>;
}
```

When `colorSchemes` is provided, the following features are activated:

- Automatic switching between light and dark color schemes based on the user's preference
- Synchronization between window tabs—changes to the color scheme in one tab are applied to all other tabs
- An option to [disable transitions](#disable-transitions) when the color scheme changes

> **Info:**
>
> The `colorSchemes` API is an enhanced version of the earlier and more limited `palette` API—the aforementioned features are only accessible with the `colorSchemes` API, so we recommend using it over the `palette` API.
> If both `colorSchemes` and `palette` are provided, `palette` will take precedence.


> **Success:**
>
> To test the system preference feature, follow the guide on [emulating the CSS media feature `prefers-color-scheme`](https://developer.chrome.com/docs/devtools/rendering/emulate-css#emulate_css_media_feature_prefers-color-scheme).


### Accessing media prefers-color-scheme

You can make use of this preference with the [`useMediaQuery`](/material-ui/react-use-media-query/) hook and the [`prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme) media query.

The following demo shows how to check the user's preference in their OS or browser settings:

```jsx
import * as React from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

function App() {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  return <div>prefersDarkMode: {prefersDarkMode.toString()}</div>;
}
```

## Toggling color mode

To give your users a way to toggle between modes for [built-in support](#built-in-support), use the `useColorScheme` hook to read and update the mode.

> **Info:**
>
> The `mode` is always `undefined` on first render, so make sure to handle this case as shown in the demo below—otherwise you may encounter a hydration mismatch error.



## Storage manager

By default, the [built-in support](#built-in-support) for color schemes uses the browser's `localStorage` API to store the user's mode and scheme preference.

To use a different storage manager, create a custom function with this signature:

```ts
type Unsubscribe = () => void;

function storageManager(params: { key: string }): {
  get: (defaultValue: any) => any;
  set: (value: any) => void;
  subscribe: (handler: (value: any) => void) => Unsubscribe;
};
```

Then pass it to the `storageManager` prop of the `ThemeProvider` component:

```tsx
import { ThemeProvider, createTheme } from '@mui/material/styles';
import type { StorageManager } from '@mui/material/styles';

const theme = createTheme({
  colorSchemes: {
    dark: true,
  },
});

function storageManager(params): StorageManager {
  return {
    get: (defaultValue) => {
      // Your implementation
    },
    set: (value) => {
      // Your implementation
    },
    subscribe: (handler) => {
      // Your implementation
      return () => {
        // cleanup
      };
    },
  };
}

function App() {
  return (
    <ThemeProvider theme={theme} storageManager={storageManager}>
      ...
    </ThemeProvider>
  );
}
```

> **Warning:**
>
> If you are using the `InitColorSchemeScript` component to [prevent SSR flickering](/material-ui/customization/css-theme-variables/configuration/#preventing-ssr-flickering), you have to include the `localStorage` implementation in your custom storage manager.


### Disable storage

To disable the storage manager, pass `null` to the `storageManager` prop:

```tsx
<ThemeProvider theme={theme} storageManager={null}>
  ...
</ThemeProvider>
```

> **Warning:**
>
> Disabling the storage manager will cause the app to reset to its default mode whenever the user refreshes the page.


## Disable transitions

To instantly switch between color schemes with no transition, apply the `disableTransitionOnChange` prop to the `ThemeProvider` component:

```jsx
<ThemeProvider theme={theme} disableTransitionOnChange>
  ...
</ThemeProvider>
```

## Disable double rendering

By default, the `ThemeProvider` rerenders when the theme contains light **and** dark color schemes to prevent SSR hydration mismatches.

To disable this behavior, use the `noSsr` prop:

```jsx
<ThemeProvider theme={theme} noSsr>
```

`noSsr` is useful if you are building:

- A client-only application, such as a single-page application (SPA). This prop will optimize the performance and prevent the dark mode flickering when users refresh the page.
- A server-rendered application with [Suspense](https://react.dev/reference/react/Suspense). However, you must ensure that the server render output matches the initial render output on the client.

## Setting the default mode

When `colorSchemes` is provided, the default mode is `system`, which means the app uses the system preference when users first visit the site.

To set a different default mode, pass the `defaultMode` prop to the ThemeProvider component:

```js
<ThemeProvider theme={theme} defaultMode="dark">
```

> **Info:**
>
> The `defaultMode` value can be `'light'`, `'dark'`, or `'system'`.


### InitColorSchemeScript component

If you are using the `InitColorSchemeScript` component to [prevent SSR flicker](/material-ui/customization/css-theme-variables/configuration/#preventing-ssr-flickering), you have to set the `defaultMode` with the same value you passed to the `ThemeProvider` component:

```js
<InitColorSchemeScript defaultMode="dark">
```

## Styling in dark mode

Use the `theme.applyStyles()` utility to apply styles for a specific mode.

We recommend using this function over checking `theme.palette.mode` to switch between styles as it has more benefits:

<!-- #target-branch-reference -->

- It can be used with [Pigment CSS](https://github.com/mui/material-ui/tree/master/packages/pigment-css-react), our in-house zero-runtime CSS-in-JS solution.
- It is generally more readable and maintainable.
- It is slightly more performant as it doesn't require to do style recalculation but the bundle size of SSR generated styles is larger.

### Usage

With the `styled` function:

```jsx
import { styled } from '@mui/material/styles';

const MyComponent = styled('div')(({ theme }) => [
  {
    color: '#fff',
    backgroundColor: theme.palette.primary.main,
    '&:hover': {
      boxShadow: theme.shadows[3],
      backgroundColor: theme.palette.primary.dark,
    },
  },
  theme.applyStyles('dark', {
    backgroundColor: theme.palette.secondary.main,
    '&:hover': {
      backgroundColor: theme.palette.secondary.dark,
    },
  }),
]);
```

With the `sx` prop:

```jsx
import Button from '@mui/material/Button';

<Button
  sx={[
    (theme) => ({
      color: '#fff',
      backgroundColor: theme.palette.primary.main,
      '&:hover': {
        boxShadow: theme.shadows[3],
        backgroundColor: theme.palette.primary.dark,
      },
    }),
    (theme) =>
      theme.applyStyles('dark', {
        backgroundColor: theme.palette.secondary.main,
        '&:hover': {
          backgroundColor: theme.palette.secondary.dark,
        },
      }),
  ]}
>
  Submit
</Button>;
```

> **Warning:**
>
> When `cssVariables: true`, styles applied with `theme.applyStyles()` have higher specificity than those defined outside of it.
> So if you need to override styles, you must also use `theme.applyStyles()` as shown below:
> 
> ```jsx
> const BaseButton = styled('button')(({ theme }) =>
>   theme.applyStyles('dark', {
>     backgroundColor: 'white',
>   }),
> );
> 
> const AliceblueButton = styled(BaseButton)({
>   backgroundColor: 'aliceblue', // In dark mode, backgroundColor will be white as theme.applyStyles() has higher specificity
> });
> 
> const PinkButton = styled(BaseButton)(({ theme }) =>
>   theme.applyStyles('dark', {
>     backgroundColor: 'pink', // In dark mode, backgroundColor will be pink
>   }),
> );
> ```


### API

`theme.applyStyles(mode, styles) => CSSObject`

Apply styles for a specific mode.

#### Arguments

- `mode` (`'light' | 'dark'`) - The mode for which the styles should be applied.
- `styles` (`CSSObject`) - An object that contains the styles to be applied for the specified mode.

#### Overriding applyStyles

You can override `theme.applyStyles()` with a custom function to gain complete control over the values it returns.
Please review the [source code](https://github.com/mui/material-ui/blob/HEAD/packages/mui-system/src/createTheme/applyStyles.ts) to understand how the default implementation works before overriding it.
For instance, if you need the function to return a string instead of an object so it can be used inside template literals:

```js
const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: '.mode-%s',
  },
  colorSchemes: {
    dark: {},
    light: {},
  },
  applyStyles: function (key: string, styles: any) {
    // return a string instead of an object
    return `*:where(.mode-${key}) & {${styles}}`;
  },
});

const StyledButton = styled('button')`
  ${theme.applyStyles(
    'dark', `
      background: white;
    `
  )}
`;
```

### Codemod

We provide codemods to migrate your codebase from using `theme.palette.mode` to use `theme.applyStyles()`.
You can run each codemod below or all of them at once.

```bash
npx @mui/codemod@latest v6.0.0/styled <path/to/folder-or-file>
npx @mui/codemod@latest v6.0.0/sx-prop <path/to/folder-or-file>
npx @mui/codemod@latest v6.0.0/theme-v6 <path/to/theme-file>
```

> Run `v6.0.0/theme-v6` against the file that contains the custom `styleOverrides`. Ignore this codemod if you don't have a custom theme.

## Dark mode flicker

### The problem

Server-rendered apps are built before they reach the user's device.
This means they can't automatically adjust to the user's preferred color scheme when first loaded.

Here's what typically happens:

1. You load the app and set it to dark mode.
2. You refresh the page.
3. The app briefly appears in light mode (the default).
4. Then it switches back to dark mode once the app fully loads.

This "flash" of light mode happens every time you open the app, as long as your browser remembers your dark mode preference.

This sudden change can be jarring, especially in low-light environments.
It can strain your eyes and disrupt your experience, particularly if you interact with the app during this transition.

To better understand this issue, take a look at the animated image below:

<img src="/static/joy-ui/dark-mode/dark-mode-flicker.gif" style="width: 814px; border-radius: 8px;" alt="An example video that shows a page that initially loads correctly in dark mode but quickly flickers to light mode." width="1628" height="400" />

### The solution: CSS variables

Solving this problem requires a novel approach to styling and theming.
(See this [RFC on CSS variables support](https://github.com/mui/material-ui/issues/27651) to learn more about the implementation of this feature.)

For applications that need to support light and dark mode using CSS media `prefers-color-scheme`, enabling the [CSS variables feature](/material-ui/customization/css-theme-variables/usage/#light-and-dark-modes) fixes the issue.

But if you want to be able to toggle between modes manually, avoiding the flicker requires a combination of CSS variables and the `InitColorSchemeScript` component.
Check out the [Preventing SSR flicker](/material-ui/customization/css-theme-variables/configuration/#preventing-ssr-flickering) section for more details.


# Init Color Scheme Script

---
productId: material-ui
title: InitColorSchemeScript component
components: InitColorSchemeScript
githubSource: packages/mui-material/src/InitColorSchemeScript
---

# InitColorSchemeScript

The InitColorSchemeScript component eliminates dark mode flickering in server-side-rendered applications.

## Introduction

The `InitColorSchemeScript` component is used to remove the dark mode flicker that can occur in server-side-rendered (SSR) applications.
This script runs before React to attach an attribute based on the user preference so that the correct color mode is applied on first render.

For the best user experience, you should implement this component in any server-rendered Material UI app that supports both light and dark modes.

## Basics

First, enable CSS variables with `colorSchemeSelector: 'data'` in your theme.

```js
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'data',
  },
});

function App() {
  return <ThemeProvider theme={theme}>{/* Your app */}</ThemeProvider>;
}
```

Then, render the `InitColorSchemeScript` component as the first child of the `<body>` tag.

The sections below detail where to render the `InitColorSchemeScript` component when working with Next.js.

### Next.js App Router

Place the `InitColorSchemeScript` component in the root `layout` file:

```js title="src/app/layout.tsx"
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';

export default function RootLayout(props: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <InitColorSchemeScript attribute="data" />
        {props.children}
      </body>
    </html>
  );
}
```

### Next.js Pages Router

Place the `InitColorSchemeScript` component in a custom `_document` file:

```js title="pages/_document.tsx"
import { Html, Head, Main, NextScript } from 'next/document';
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';

export default function MyDocument(props) {
  return (
    <Html lang="en">
      <Head>{/* tags */}</Head>
      <body>
        <InitColorSchemeScript attribute="data" />
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

## Customization

### Class attribute

To attach classes to DOM elements, set the `attribute` prop to `"class"`.

```js
<InitColorSchemeScript attribute="class" />
```

This sets the class name on the color scheme node (which defaults to `<html>`) according to the user's system preference.

```html
<html class="dark"></html>
```

### Arbitrary attribute

To attach arbitrary attributes to DOM elements, use `%s` as a placeholder on the `attribute` prop.

```js
<InitColorSchemeScript attribute="[data-theme='%s']" /> // <html data-theme="dark">
<InitColorSchemeScript attribute=".mode-%s" /> // <html class="mode-dark">
```

### Default mode

Set the `defaultMode` prop to specify the default mode when the user first visits the page.

For example, if you want users to see the dark mode on their first visit, set the `defaultMode` prop to `"dark"`.

```js
<InitColorSchemeScript defaultMode="dark" />
```

## Caveats

### Attribute

When customizing the `attribute` prop, make sure to set the `colorSchemeSelector` in the theme to match the attribute you are using.

```js
const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'same value as the `attribute` prop',
  },
});
```

### Default mode

When customizing the `defaultMode` prop, make sure to do the same with the `ThemeProvider` component:

```js
<ThemeProvider theme={theme} defaultMode="dark">
```
